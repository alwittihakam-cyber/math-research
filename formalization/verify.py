#!/usr/bin/env python3
"""Worker for verify.sh locally, or directly on the isolated GitHub CI runner."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
NAME = r"[A-Za-z_][A-Za-z_0-9']*(?:\.[A-Za-z_][A-Za-z_0-9']*)*"


def check_axiom_reports(output, declarations):
    """Require one unambiguous Lean axiom report per audited declaration.

    This is log validation, not a sandbox against arbitrary Lean metaprograms.
    In particular, never silently select the first of conflicting reports.
    """
    for name in dict.fromkeys(declarations):
        prefix = r"^'" + re.escape(name) + r"' "
        reports = re.findall(
            prefix + r"(?:depends on axioms: \[([^\]]*)\]|"
            r"(does not depend on any axioms))[ \t]*$", output, re.M)
        starts = re.findall(prefix + r"(?:depends on axioms:|does not depend on any axioms)",
                            output, re.M)
        if len(reports) != 1 or len(starts) != 1:
            raise ValueError(f"{name}: expected exactly one complete axiom report; "
                             f"found {len(reports)} complete and {len(starts)} report starts")
        raw, no_axioms = reports[0]
        if no_axioms:
            continue
        fields = [item.strip() for item in raw.split(",")]
        if raw.strip() and any(not re.fullmatch(NAME, item) for item in fields):
            raise ValueError(f"{name}: malformed axiom list")
        axioms = set(fields) if raw.strip() else set()
        if axioms - STANDARD_AXIOMS:
            raise ValueError(f"{name}: unapproved axioms {sorted(axioms - STANDARD_AXIOMS)}")


def module_name(path):
    parts = path.relative_to(ROOT).with_suffix("").parts
    for part in parts:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9'-]*", part):
            raise ValueError(f"Unsupported module path component: {part}")
    return ".".join(part if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*", part)
                    else "«" + part + "»" for part in parts)


def select_target(files, target):
    if target is None:
        return files
    target = target.removeprefix("./")
    matches = [path for path in files if target in {
        str(path), str(path.relative_to(ROOT)), str(path.relative_to(ROOT.parent)),
        module_name(path), ".".join(path.relative_to(ROOT).with_suffix("").parts)}]
    if len(matches) != 1:
        raise ValueError("--target must identify one existing claim module or Lean file")
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="save complete output to a new file (relative to repo root)")
    parser.add_argument("--recheck-sources", action="store_true",
                        help="explicitly re-elaborate selected sources after the incremental build")
    parser.add_argument("--target", help="check one module or Lean file and its cached dependencies")
    args = parser.parse_args()
    report = None
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        report = args.out.open("x")

    def emit(message):
        print(message, flush=True)
        if report:
            report.write(message + "\n")
            report.flush()

    def run(command):
        emit("$ " + " ".join(command))
        lines = []
        with subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            for line in process.stdout:
                emit(line.rstrip("\n"))
                lines.append(line)
            if process.wait():
                raise ValueError("Command failed")
        return "".join(lines)

    try:
        pins = [ROOT / name for name in ("lean-toolchain", "lakefile.lean", "lake-manifest.json")]
        before = {path: path.read_bytes() for path in pins}
        emit("Lean toolchain: " + pins[0].read_text().strip())
        for package in json.loads(pins[2].read_text())["packages"]:
            emit(f"Dependency: {package['name']} {package['rev']}")
        files = sorted(path for directory in ("claims", "third-party-claims")
                       for path in (ROOT / directory).rglob("*.lean"))
        files = select_target(files, args.target)
        emit("Scope: " + (module_name(files[0]) if args.target else "all claim modules"))
        declarations = []
        interface_names = set()
        interface_files = 0
        for path in files:
            source = path.read_text()
            header = re.match(r"\s*/-\s*\n(.*?)\n-/", source, re.S)
            if not header:
                raise ValueError(f"{path.relative_to(ROOT)}: missing claim header")
            fields = dict(re.findall(r"^(Claim|Source|Scope|Declarations): (.+)$", header[1], re.M))
            if set(fields) != {"Claim", "Source", "Scope", "Declarations"}:
                raise ValueError(f"{path.relative_to(ROOT)}: incomplete claim header")
            if not fields["Source"].startswith("https://") or "#" not in fields["Source"]:
                raise ValueError("Source must be an HTTPS notebook link with an anchor")
            names = fields["Declarations"].split()
            if not names or any(not re.fullmatch(NAME, name) for name in names):
                raise ValueError("Declarations must list fully qualified Lean names separated by spaces")
            declarations.extend(names)
            status = re.search(r"^Status: (.+)$", header[1], re.M)
            kind = re.search(r"^Kind: (.+)$", header[1], re.M)
            if status and status[1] != "statement-only":
                raise ValueError("Legacy Status field must be statement-only")
            if kind and kind[1] != "interface":
                raise ValueError("Optional Kind field must be interface")
            if kind or status:  # Keep historical headers readable.
                interface_files += 1
                interface_names.update(names)
            emit(f"Claim file: {path.relative_to(ROOT)}\n{header[1]}")
        run(["lake", "--wfail", "build"] + ([module_name(files[0])] if args.target else []))
        emit("Verification: incremental Lake build; types and axioms read from compiled modules.")
        if args.recheck_sources:
            for path in files:
                run(["lake", "env", "lean", "-DwarningAsError=true", str(path.relative_to(ROOT))])
        if files:
            imports = ["import " + module_name(path) for path in files]
            commands = []
            for name in dict.fromkeys(declarations):
                commands.extend(["#check @" + name,
                                 "#print axioms " + name])
                if name in interface_names:
                    commands.append("#print " + name)
            audit = "\n".join(imports + commands) + "\n"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", dir=ROOT / ".lake") as temp:
                temp.write(audit)
                temp.flush()
                output = run(["lake", "env", "lean", "-DwarningAsError=true", temp.name])
            check_axiom_reports(output, declarations)
        if any(path.read_bytes() != content for path, content in before.items()):
            raise ValueError("Dependency configuration changed during verification")
        emit(f"PASS: {len(files) - interface_files} proof files; {interface_files} interface files "
             f"(definitions, not claim-completion status); {len(declarations)} audited declarations."
             if files else "SETUP ONLY: build passed; no claim files exist and no research claim is verified.")
    except (ValueError, OSError) as error:
        emit("FAIL: " + str(error))
        return 1
    finally:
        if report:
            report.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
