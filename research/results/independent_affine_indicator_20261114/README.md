# Independent affine-indicator coverage audit

Attribution: setting and question from Kamil Braun/Noemesis,
`lem:affine-indicator-kernel` and its follow-up in the public notebook,
17 October 2026, upstream snapshot `9ef864ca288651fc55d7df2c2b5bd838ff987234`.
Original code here is an independent implementation. Retain repository MIT
license for software and CC BY 4.0 for research writing. No novelty claim.

## Precise question and scope

On the ternary one-hot domain `{0,1,2}^s`, write `x_i=[chi_i=1]`,
`y_i=[chi_i=2]`. For each nonempty binary row S define Z_S by
`sum_S x = sum_S y = 1+|S| (mod 2)`. Given M products, each with a list
of rows, let Z be the intersection of their unions of Z_S.

The degree-2 junta evaluation space is spanned by 1, the 2s one-hot
variables, and products on two distinct coordinates. We compare the exact
subspace of these functions supported inside Z with the span of indicators
of all intersections of at most two affine binary equations, restricted
to the one-hot domain and contained in Z. Coordinate conditions are included:
`chi_i=0` means `x_i+y_i=0` on this domain.

The audit enumerates ALL such affine indicators, but samples the product
instances (fixed seed). It found equal dimensions in all 1,000 instances
at s=4 and all 3,000 at s=5. This supports no universal completeness claim.
The rows were sampled without a full-rank or dense-support condition;
therefore these are not a replay of the notebook's dense full-rank sample.
No charged-quotient transfer or all-sector statement is tested here.

The functions {1,x_i,y_i} are independent on one ternary coordinate;
their tensor products form a basis on the full ternary domain. Thus the
selected monomial evaluation columns are independent. Products of affine
equations reduce to junta degree at most two using x_i^2=x_i, y_i^2=y_i
and x_i*y_i=0.

All arithmetic is exact over F2, with integer bitsets for elimination.
Extending the evaluation matrix from F2 to F4 preserves rank, so the
kernel dimension agrees with the split-field degree-2 function model.
Each enumerated indicator has degree at most two, hence its span lies
in that kernel. Equality of dimensions therefore proves equality of these
spaces for each tested instance, not merely existence of one indicator.

## Degree-one endpoint (elementary, no novelty asserted)

For EVERY Z, the degree-one supported-function kernel is spanned by
indicators of affine one-equation sets contained in Z. Indeed its binary
coefficient vectors are exactly the F2 nullspace of the evaluation matrix
on the complement of Z. Every such polynomial f is affine in the one-hot
bits and takes values in F2, so it equals the indicator of the set f=1.
That set is disjoint from the complement of Z. A basis of this nullspace
remains a kernel basis over any extension of F2. This argument does not
extend automatically to degree two: supports of quadratic functions need
not be affine one- or two-equation sets. The product-zero-set structure is
the unresolved additional ingredient in the general question.

## Reproduce

`python3 check.py --pairs 4 --trials 1000`

`python3 check.py --pairs 5 --trials 3000`

The latter enumerates 691,381 distinct nonempty affine-set indicators and
took about 54 seconds in the recorded environment. Results include elapsed
time, so timings are not deterministic. No Lean theorem, asymptotic lower
bound, general affine-kernel characterization, or P versus NP result is
claimed. No third-party executable code was run by this audit.
