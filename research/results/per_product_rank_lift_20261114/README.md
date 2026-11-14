# Per-product full-row-rank lifting: analytic audit

14 November 2026. Symbolic proof reviewed by two AI agents, not formally checked. No computation was run. No novelty claim or P versus NP result.

## Attribution and comparison

Setup: Kamil Braun, Noemesis, math-research, notebook entry `entry-2026-10-17-affine-indicator-kernel`, lemma `lem:affine-indicator-kernel`, consulted in public fork alwittihakam-cyber/math-research at commit `9ef864ca288651fc55d7df2c2b5bd838ff987234`.
Original source: https://github.com/kbr-/math-research . Research license: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . This is an AI-assisted independent continuation, not upstream endorsement. The upstream sufficient affine-indicator construction remains valid.

PR3 tested degree-two completeness on small product families. A separate analytic counterexample uses dependent rows. This note shows that per-product full row rank alone cannot repair unrestricted, all-degree completeness. It does not duplicate PR3 or solve the random/dense low-degree question.

## Setup

D_s={0,1,2}^s, x_i=[chi_i=1], y_i=[chi_i=2]. Work over characteristic two with omega^2+omega+1=0. The tensor basis {1,x_i,y_i} gives a unique expansion of every function on D_s. Junta degree counts nonconstant coordinate factors.
For binary nonempty row S, q_S=sum_{i in S} omega^{chi_i}. Products P_a=product_j(1+q_{S_aj}) have common zero set Z. K_d(Z) consists of functions of junta degree at most d supported on Z.
An affine-slice indicator is 1_A for A equal to D_s intersected with an affine subspace of the 2s one-hot bits. The contemplated spanning family includes only indicators themselves belonging to K_d(Z). Without this restriction, singleton indicators trivially span every supported space.

## Generic lifting lemma

Suppose every product has at most R factors. Add 2R auxiliary coordinates u_1,v_1,...,u_R,v_R. Replace row j of each product by S'_aj=S_aj union {u_j,v_j}. Adjoin 2R separate singleton products 1+q_{ {u_j} } and 1+q_{ {v_j} }.

1. Each padded product has full row rank: its u_j column is one precisely in its j-th row. Each forcing product has one nonzero row. This is PER-PRODUCT independence, not independence of all rows combined.
2. A singleton factor vanishes exactly at auxiliary color zero. On the resulting forced slice, each padded pair adds 1+1=0 to q. Thus the common zero set is Z'=Z times {0}^{2R}.
3. Let G=product_aux(1+x_aux+y_aux). Every function supported on Z' is uniquely Gh for a function h supported on Z.
4. For nonzero h, deg(Gh)=2R+deg(h). A highest-degree tensor monomial in h multiplied by x_aux in every auxiliary coordinate has its unchanged nonzero coefficient; disjoint coordinates prevent cancellation. The product expansion also gives the matching upper bound. Hence K_{d+2R}(Z')=G K_d(Z).
5. Failure of affine-indicator spanning lifts. If K_{d+2R}(Z') were spanned by affine-slice indicators 1_B within that degree, restrict their affine subspaces to the auxiliary-zero slice. Each restriction is an affine-slice indicator 1_A on the original variables (or zero). Since B is supported on Z', 1_B=G1_A. The degree identity implies deg(1_A)<=d. Restricting an assumed spanning expression for Gh would express every h in the original affine-indicator span, contradiction.

The lemma is purely algebraic and requires no enumeration or external theorem.

## Conditional application

The separate four-coordinate example has f=x1*y2+y1*x2+x3*y4+y3*x4 and Z={f=1}. Its base proof gives K_2(Z)=span(f), no nonzero affine-slice indicator in that space, and realization by 53 products of at most 15 factors. Conditional on that base proof and realization, R=15 above produces 34 coordinates and 83 products. Every product's rows are independent, and K_32(Z')=span(Gf) has no nonzero affine-slice indicator. The generic lemma does not depend on the base example's verification.

## Scope and remaining issue

This does not give a degree-two full-rank counterexample. It uses singleton forcing products and a sparse zero set, so does not address random dense ensembles, fixed factor counts, expansion assumptions, forbidden singleton products, or global row independence. Junta degree and ordinary polynomial degree in the upstream character realization are distinct; the latter can incur a factor of two.

This is an algebraic scope clarification, not a circuit lower bound, sampler construction, or solution of P versus NP. No claim of literature novelty has been checked. The unresolved research target should state its density, randomness, degree, and per-product/global rank hypotheses explicitly rather than adding full rank alone.

## Validation

An independent AI review checked the padding rank, guard degree, and affine restriction steps and emphasized the per-product and degree-restricted-spanning qualifications, incorporated above. No Lean check or test run is claimed. The upstream protected launcher is environment-specific and prior work reported missing watchdog support. This note does not bypass the launcher or run the blocked checker. Repository-wide research workflow and source audit are not represented as complete.
