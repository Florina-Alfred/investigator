**Title & Citation**  
**Dexterous Safe Control for Humanoids in Cluttered Environments via Projected Safe Set Algorithm** – Rui Chen, Yifan Sun, Changliu Liu, *Robotics Institute, Carnegie Mellon University*. (Original conference/journal not specified; contact: {ruic3, yifansu2, cliu6}@andrew.cmu.edu).

---

## Abstract  
The paper tackles **dexterous safety** – the problem of enforcing limb‑level collision avoidance for humanoids in dense, cluttered settings. Existing indirect safe‑control algorithms (SSA, CBF, HJ reachability) rely on a single safety index and therefore struggle with the many local constraints that a humanoid faces in realistic scenarios. The authors identify three sources of infeasibility: inherent infeasibility (physical impossibility), method infeasibility (conflicting constraints), and kinematic infeasibility (actuation limits). They propose two variants of a *relaxed* safe control:

1. **r‑SSA** – adds weighted slack variables to the safety QP.  
2. **p‑SSA** – first projects the infeasible constraint set to the nearest feasible point, then solves a standard QP, guaranteeing feasibility and **no parameter tuning**.

Simulations on a 19‑body Unitree‑G1 humanoid (both fixed‑base and floating‑base variants) and hardware tele‑operation experiments demonstrate that **p‑SSA consistently reduces safety violations and matches r‑SSA performance with zero tuning**.

---

## Introduction & Motivation  

*Humanoids* possess high degrees of freedom but require fine‑grained geometry for safe operation in cluttered environments. Simplified bounding geometries are overly conservative. Existing safe‑control algorithms are indirect (model‑based) and derive a safety index ϕ that enforces \(\dotϕ \le -\eta\). When multiple constraints are present, a single ϕ cannot capture the interactions, leading to infeasible QPs. The paper emphasizes that **dexterous safety** is a *multi‑constraint, high‑dimensional* problem, and no existing approach provides persistent feasibility guarantees.

---

## Methods / Approach  

### System Model  
- Control‑affine dynamics: \(\dot x = f(x)+g(x)u\), with bounded control \(U=\{u: \|u\|_{\infty}\le u_{\rm max}\}\).  
- For this work, \(f(x)=0, g(x)=I\) (first‑order integrator).  
- State \(x\) contains all joint positions; control \(u\) are joint velocities.  

### Safety Specification  
- Each body \(j\) (19 volumes) and each obstacle/external shape \(k\) gives an **energy function**  
  \(\varphi_{0,i}= d_{\min,i}-d_i\), where \(d_i\) is the Euclidean distance between the body sphere centre and obstacle centre.  
- Multi‑constraint safety index: \(\varphi=\Xi^T\varphi_{0}\) where each row is a safety index of order \(n\ge 1\).  
- Control constraint (SSA): \(\dot\varphi\le -\eta\), with \(η_i>0\).  

### Problem Formulation  
- QP (6): minimize \(\|u-u_{\rm ref}\|^2_Q\) subject to safety constraints \(\dot\varphi_i(u)\le -η_i,\, i=1..M\) and control limits.  
- For highly constrained humanoid in clutter, **feasibility of QP deteriorates**.

### r‑SSA (Relaxed)  
- Introduce slack \(s\in\mathbb{R}^M\) only for safety constraints:  
  \(\dot\varphi_i+η_i\le s_i\).  
- Slack regularized in a weighted \(\|s\|_{p}\) norm: \(\min_{u,s}\|u-u_{\rm ref}\|^2_Q+ \|Q_{rssa}s\|_p^p\).  
- If \(s\) is small, the QP behaves like standard SSA; if large, QP becomes more feasible but safety is relaxed.

### p‑SSA (Projected)  
- **Phase I:** solve for slack \(s^*\) that minimally removes infeasibility:  
  \(\min_{s}\|s\|^p \) s.t. there exists a \(u\) satisfying \(\dot\varphi_i+η_i\le s_i\) with control bounds.  
- **Phase II:** once the necessary slack is known, re‑solve the standard QP:  
  \(\min_{u}\|u-u_{\rm ref}\|^2_Q\) s.t. \(\dot\varphi_i+η_i\le s^*_i\).  
- The two phases are decoupled, guaranteeing Phase II is feasible.  
- No tuning for safety vs performance trade‑off; only a mild weight matrix \(Q_{pssa}\) (often identity) to express relative importance among constraints.

### Implementation Details  
- Derive \(L_f \varphi(x)\), \(L_g \varphi(x)\) from the distance functions (see Appendix B).  
- For sphere–sphere distances: \(d_i=\|P_j(x)-P_k\|-R_j-R_k\).  
- Jacobians \(J_j = \partial P_j/\partial x\).  
- The control constraints become affine in \(u\): \(L_f \varphi_i + L_g \varphi_i u \le -η_i + s_i\).  

---

## Experiments / Data / Results  

| Test Case | DoFs | Bodies | Obsts | Self | Body‑Obs |
|---|---|---|---|---|---|
| G1WholeBody SO V0 | 20 | 19 | 50 | 29 | 950 |
| G1WholeBody SO V1 | 20 | 19 | 10 | 29 | 190 |
| G1WholeBody DO V0 | 20 | 19 | 50 | 29 | 950 |
| G1WholeBody DO V1 | 20 | 19 | 10 | 29 | 190 |
| G1FixedBase SO V0 | 17 | 19 | 10 | 29 | 190 |
| G1FixedBase SO V1 | 17 | 19 | 5 | 29 | 95 |
| G1FixedBase DO V0 | 17 | 19 | 10 | 29 | 190 |
| G1FixedBase DO V1 | 17 | 19 | 5 | 29 | 95 |

- **Dynamics**: first‑order integrator, 10–50‑s (simulation), 2000 time steps per run.  
- **Safety parameters**: \(d_{\min,env}=0.05\,\text{m}\), \(d_{\min,self}=0.01\,\text{m}\), \(\eta_i=0.5\).  
- **Safety methods compared**:  
  - **SSA**: plain SSA, no slack, passes \(u_{\rm ref}\) when QP infeasible.  
  - **r‑SSA**: slack weight \(Q_{rssa}=10I\) (p=2).  
  - **p‑SSA**: Phase‑I slack weight \(Q_{pssa}=I\) (p=2).  

### Key Metrics  
- **Tracking performance** \(J_{\rm arm}\).  
- **Constraint violation** \(C_{\rm env}/C_{\rm self}\): \(s_t=\sum_i s_{i,t}\).  
- **Direct safety margin** \(S_{\rm env}/S_{\rm self}\): average violation of \(ϕ\).  
- **Feasibility rate** \(R_{\rm Feas}\): proportion of steps where QP feasible.  

### Main Findings (Fig. 5–6)  
1. **Infeasibility Rate**: Dim fewer obstacles → higher \(R_{\rm Feas}\) (because simpler constraints). FixedBase models see more infeasibility than WholeBody because payload cannot reposition base. Dynamic obstacles lower \(R_{\rm Feas}\) because future collisions are harder to avoid with current QP.  
2. **Slack usage**: SSA yields very low \(C_{\rm env}\) (i.e., misses violations) because it simply gives up safety. r‑SSA and p‑SSA significantly lower violations.  
3. **p‑SSA vs r‑SSA**: p‑SSA consistently yields **smaller \(C, S\)** than r‑SSA. For every setting, p‑SSA outperforms r‑SSA in safety while retaining comparable tracking.  
4. **Performance vs Safety trade‑off**: r‑SSA shows a clear Pareto front across all tasks (Fig. 7–8). Optimal points require tedious tuning. p‑SSA automatically lands on the best trade‑off curve (no tuning).  

### Tele‑operation Experiments  
- Using Apple Vision Pro (AVP), a Unitree G1 in a cabinet scenario.  
- A nominal controller tracks human wrist positions; p‑SSA enforces safety by selectively relaxing constraints that would otherwise be violated by tight cabinet walls.  
- Simulation (MuJoCo) and real‑world hardware: p‑SSA prevented collisions even when the operator tried risky motions (claws approaching cabinet edges).  

---

## Discussion & Analysis  

*Theoretical Insight*: Multi‑constraint systems cannot be rendered feasible by a single safety index because constraints may conflict in high‑dimensional dynamics. The authors categorize infeasibility sources: inherent (actual physical impossibility), method (conflicting constraints), kinematic (actuation limits).  

*Practical Remedy*: r‑SSA is an intuitive generalization of SSA, but it suffers from a single scalar weight \(Q_{rssa}\) that balances safety vs tracking. When under‑tuned, r‑SSA can ignore safety for higher performance (or vice versa).  

*Projecting (p‑SSA)*: By solving a separate feasibility check (Min‑Slack Phase I), the algorithm guarantees that the subsequent optimization is always feasible – effectively extending the feasible set backwards. This approach is reminiscent of constrained‑optimization “slack projection” but without the need for external heuristics.  

*No‑parameter tuning*: Since the projection removes the need to guess a slack weight, p‑SSA delivers the best equilibrium between safety and nominal control automatically.  

*Empirical Observations*:  
- In high‑obstacle density (SO V0), almost no QP is ever feasible. Only p‑SSA can navigate.  
- Digital tele‑op demonstrates that p‑SSA is robust in real hardware: physical collision constraints are satisfied even when the control filter is applied underneath a PID joint‑velocity controller.  

---

## Key Claims & Contributions  

1. **Dexterous Safety** is defined as multi‑constraint safety with limb‑level geometries in cluttered environments; classical SSA fails due to infeasibility.  
2. **r‑SSA** was introduced to relax constraints with weighted slack; demonstrates that slack regularization can salvage feasibility but requires careful tuning.  
3. **p‑SSA** – a novel algorithm that first projects a set of infeasible constraints onto the nearest feasible point, then solves a standard QP; guarantees feasibility and eliminates the safety‑performance trade‑off.  
4. Extensive simulations on a 29‑body Unitree‑G1 (over 200 M constraints) confirm that p‑SSA outperforms SSA and r‑SSA.  
5. Tele‑operation experiments on a physical humanoid demonstrate practical applicability.  

---

## Definitions & Key Terms  

| Term | Definition |
|------|-------------|
| **Safety Index (ϕ)** | Piecewise‐smooth function whose sublevel set defines the safe set. |
| **SSA (Safe Set Algorithm)** | Indirect safe control method that enforces \(\dotϕ\le -η\). |
| **CBF (Control Barrier Function)** | Similar to SSA but may handle higher relative degree. |
| **d_{min,env/self}** | Minimum allowed distance from a body to an obstacle/self‑collision. |
| **η_i** | Safety margin constant applied to constraint i. |
| **Slack (s)** | Non‑negative variable added to safety constraints in r‑SSA. |
| **r‑SSA** | Relaxed SSA: adds slack with weighted penalty. |
| **p‑SSA** | Projected SSA: first projects constraints then solves. |
| **Feasibility Rate (R_Feat)** | Proportion of simulation steps where QP feasible. |
| **C_{env/self}** | Violation of control constraints. |
| **S_{env/self}** | Violation of safety constraints (distance margin). |

---

## Important Figures & Tables  

| Figure | Description |
|--------|-------------|
| **Fig. 1(a)** | Tele‑operation demo with Unitree G1 mimicking Apple Vision Pro data. |
| **Fig. 1(b‑1)** | p‑SSA blocks excessive squeezing near cabinet (frames 2–3). |
| **Fig. 1(b‑2)** | p‑SSA prevents collisions when both arms are inside cabinet. |
| **Fig. 2** | Three scenarios causing infeasibility: inherent, method, kinematic (illustrated with planes). |
| **Fig. 3** | Unitree G1 in MuJoCo performing wrist tracking, collision detection (spheres). |
| **Fig. 4** | Comparison of safe control methods (SSA, r‑SSA, p‑SSA) in a corridor experiment (QP infeasible). Shows less violation for p‑SSA (purple). |
| **Fig. 5** | Overall comparison: J_arm, C, S, R_Feat across all 8 test cases. |
| **Fig. 6** | Detailed comparison for G1FixedBase configuration (shows similar trends). |
| **Fig. 7–8** | Ablation study on r‑SSA: Pareto fronts (J_arm vs C_env) for all tasks; p‑SSA automatically occupies best edge. |
| **Fig. 9** | Real‑world tele‑operation: p‑SSA prevents collisions; purple lines show relaxed constraints. |
| **Fig. 10–12** | Appendix plots of ϕ, elbow and shoulder positions for scenario in Fig. 4 (show p‑SSA’s tighter bounding). |

| Table | Description |
|-------|--------------|
| **Table I** | Number of bodies, obstacles, constraints across test cases. |
| **Table II** | Self‑collision body pairs enumerated per joint. (Displayed for clarity but not reproduced fully in summary). |

---

## Limitations & Open Questions  

- **Unbounded Safety Violations**: Even with minimal slack, safety violations are non‑zero—no formal bound.  
- **Parameter Choice**: Even though p‑SSA uses \(Q_{pssa}=I\), future work could learn or adapt weights \(Q_{pssa}\) to prioritize critical constraints (e.g., collision with constrained environment boundaries).  
- **Dynamics Extension**: The method was tested with first‑order integrator; real humanoid dynamics could be higher order—future work to demonstrate with full first‑/second‑order plant.  
- **Real‑time Optimization**: While p‑SSA is solved quickly with standard QP solvers, very large \(M\) (hundreds of constraints) might still strain time‑critical systems.  

---

## References to Original Sections  

- **Section I** – Introduction and motivation.  
- **Section II** – Related works.  
- **Section III** – Problem formulation, pre‑liminaries, multi‑constraint extension, infeasibility analysis.  
- **Section IV** – Algorithms (r‑SSA, p‑SSA).  
- **Section V** – Experimental setup, metrics, results.  
- **Appendix IX** – Derivation of control constraints.  

---

## Key Claims (explicit)

| Claim | Supporting Evidence |
|-------|---------------------|
| *A single safety index cannot guarantee feasibility for dexterous safety.* | Section III.C (definition of QP) and examples in Fig. 2. |
| *p‑SSA guarantees feasibility of the safety QP for all tested tasks.* | Section V.E, Fig. 6 shows R_Feat≥0.99 for p‑SSA while r‑SSA often 0.6–0.8. |
| *p‑SSA achieves the best performance‑safety trade‑off without tuning.* | Ablation Fig. 8: every r‑SSA point lies inside p‑SSA Pareto front. |
| *p‑SSA generalizes to tele‑operation tasks.* | Section V.G, real‑world demo. |
| *r‑SSA can be tuned to match p‑SSA if aggressive weights are used.* | Ablation Fig. 7. |

---

## Executive Summary (Optional)

- Introduced *dexterous safety* to capture limb‑level collision avoidance in dense environments.  
- Identified three infeasibility sources and argued that no existing safe‑control can solve them.  
- Proposed **p‑SSA** – projects infeasible constraints to nearest feasible point, guaranteeing QP feasibility without parameter tuning.  
- Experiments on a 29‑body humanoid with thousands of constraints confirm that p‑SSA outperforms SSA and r‑SSA in safety and tracking, while r‑SSA requires careful weight tuning.  
- Tele‑operation experiments confirm real‑hardware applicability.  
- Limitations: safety violations are unbounded; future work: dynamic weight adaptation, full plant dynamics.  

---