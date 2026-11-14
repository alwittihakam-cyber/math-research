"""Pure log-parser regressions; no Lean process or project proof is executed."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('verification_worker', Path(__file__).resolve().parents[1] / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class AxiomReportsTest(unittest.TestCase):
    name = 'Example.claim'
    safe = "'Example.claim' depends on axioms: [propext, Classical.choice, Quot.sound]"
    empty = "'Example.claim' does not depend on any axioms"
    bad = "'Example.claim' depends on axioms: [sorryAx]"

    def check(self, output, names=None):
        verify.check_axiom_reports(output, names or [self.name])

    def test_standard_axioms(self):
        self.check(self.safe + '\n')

    def test_no_axioms(self):
        self.check(self.empty)
        self.check("'Example.claim' depends on axioms: []")

    def test_wrapped_axiom_list(self):
        self.check(self.safe.replace(', ', ',\n '))

    def test_duplicate_metadata_names_share_one_report(self):
        self.check(self.safe, [self.name, self.name])

    def test_duplicate_reports_rejected_even_when_safe(self):
        with self.assertRaises(ValueError):
            self.check(self.safe + '\n' + self.safe)

    def test_safe_then_bad_and_bad_then_safe_rejected(self):
        for parts in ((self.safe, self.bad), (self.bad, self.safe), (self.empty, self.bad)):
            with self.subTest(parts=parts), self.assertRaises(ValueError):
                self.check('\n'.join(parts))

    def test_unapproved_axioms_rejected(self):
        for axiom in ('sorryAx', 'Lean.ofReduceBool', 'Example.custom'):
            with self.subTest(axiom=axiom), self.assertRaises(ValueError):
                self.check(f"'Example.claim' depends on axioms: [{axiom}]")

    def test_missing_prefixed_or_suffixed_report_rejected(self):
        for text in ('', 'diagnostic: ' + self.empty, self.empty + ' BUT NOT REALLY'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.check(text)

    def test_malformed_report_rejected(self):
        for raw in ('propext,', ',propext', 'propext,,Quot.sound', 'propext garbage'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.check(f"'Example.claim' depends on axioms: [{raw}]")

    def test_truncated_extra_report_rejected(self):
        with self.assertRaises(ValueError):
            self.check(self.safe + "\n'Example.claim' depends on axioms: [sorryAx")

    def test_all_requested_declarations_required(self):
        with self.assertRaises(ValueError):
            self.check(self.safe, [self.name, 'Example.other'])
        self.check(self.safe + "\n'Example.other' does not depend on any axioms", [self.name, 'Example.other'])


if __name__ == '__main__':
    unittest.main()
