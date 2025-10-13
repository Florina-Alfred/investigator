**Title & Citation**  
*Safe Whole-Body Task Space Control for Humanoid Robots* – Victor C. Paredes & Ayonga Hereid, Mechanical & Aerospace Engineering, Ohio State University, 2024.  

---

## Abstract  
Whole‑body control of humanoid robots must simultaneously enforce contact constraints, kinematic loops, and task‑space objectives while guaranteeing safety.  This paper proposes an **inverse‑dynamics control** formulated as a **quadratic program (QP)** that is augmented with **Exponential Control Barrier Functions (ECBFs)** to keep the robot inside user‑defined safe sets.  Unlike prior formulations, the authors avoid expensive mass‑matrix inversions by using an *Acceleration‑based ECBF (A‑ECBF)* that depends only on joint accelerations.  The approach explicitly includes closed‑loop kinematics, ZMP, friction cone, and torque limits, and respects safety constraints for arbitrary high‑relative‑degree sets.  Experiments on the 3‑D bipedal robot **Digit** in simulation and hardware demonstrate stable squat, bow, walking, and collision‑avoidance behavior while preserving the safe set.

---

## Introduction & Motivation  
- *Humanoid robots* can perform complex motions (walking, manipulation) but coordinating leg + arm dynamics is challenging because of tight coupling and floating bases.  
- *Safety* is critical: approaching joint limits, risking self‑collision, or generating unfeasible ZMP.  
- Existing methods (inverse‑dynamics, operational‑space control) do not all treat safety; most require solving constrained dynamics or involve expensive mass‑matrix inversions.  
- Control Barrier Functions (CBFs) provide a formal safety certificate; EB‑CBFs (exponential) allow arbitrary relative degree and are known in (Nguyen 2016).  
- This work extends **Reher et al. 2020** (inverse‑dynamics + CLF) by adding a **high‑relative‑degree safety layer** that is **acceleration‑only** and thus numerically efficient.

---

## Methods / Approach  

| Section | Key Idea | Key Equations / Variables |
|---|---|---|
| **II – Humanoid dynamics** | Floating base + contact + closed‑chain constraints | Euler–Lagrange: \(M(q)\ddot q + C(q,\dot q)\dot q + G(q) = B u + J^T(q)\lambda\)  (1) |
| **Closed‑chain** | encode holonomic constraints: \(n_k(q,\dot q,\ddot q)=0\) | Collect: \(J_{\text{chain}}(q)\ddot q = -\frac{\partial n_k}{\partial q} \ddot q\) (2) |
| **Contacts** | unilateral + friction cone + ZMP | Friction linear constraints \(0 \le \lambda_f^T\!F \lambda_f\); ZMP \(p_{x}^{zmp}=\frac{\lambda_{y}}{\lambda_{z}}\in P\) (3) |
| **III – Task‑space inverse‑dynamics** | Outputs \(y(q,t)\) (relative‑degree‑2) → desired dynamics \(\ddot y = -K_p(y-y_d) - K_d \dot y\) | QP:  minimize \(||J(q) \ddot q + C(q,\dot q)\dot q + G(q)-B u||^2 + \gamma||X||^2\) s.t. dynamics, constraints, torque limits | Decision vector \(X=[\ddot q^T\;u^T\;\lambda^T]^T\) |
| **ECBF / A‑ECBF** | Provide forward‑invariance of safe set \(C=\{x|h(x)\ge 0\}\) | Existing ECBF: \(L^rb f\,h(x)+L_g L^{rb-1}f\,h(x)\,u\ge -K_\alpha\,\eta\) (5) |
|  | Re‑formulated to only involve \(\ddot q\) (A‑ECBF) | \(J_{\eta}\ddot q + \dot J_{\eta}\dot q\ge -K_\alpha\,\eta\) (7) |
|  | Select \(K_\alpha\) roots \(p_i>0\) (critical or overdamped) | Guarantees \(h(x(t))\ge 0\) for any \(t\ge 0\) |  

**Overall controller**: QP augmenting inverse‑dynamics with: (i) torque limits, (ii) friction cone, (iii) ZMP, (iv) A‑ECBF equality constraints.

---

## Experiments / Data / Results  

| Experiment | Task | Safety Constraint | Key Observations | Section |
|---|---|---|---|---|
| **Squatting** | CoM height sinusoid (p_z=0.95 m) | None | Successful squat amplitude, good tracking (Fig. 7) | IV.A |
| **Bowing** | Torso pitch (θ_d=π/2 rad) | None | Accurate torso motion, arm joints fixed (Fig. 8) | IV.A |
| **Arm motion (height limit)** | Left arm lifted, safety enforced on left fist height | A‑ECBF on \(p_{Lz}\) | Left fist never violates safe set, right fist over‑shrugs – safety only for left (Fig. 9) | IV.B |
| **Walking (ALIP)** | ALIP‑planned swing foot and CoM, constant torso | None | Stable gait, 0.2 m/s, step time 0.35 s (Fig. 11) | IV.C |
| **Collision avoidance** | Lateral external force \(F_{\text{ext}}=-30 N\) -> leg collision | A‑ECBF on swing‑foot y‑distance to right foot | With A‑ECBF, right foot stops before collision (yellow circles), below collision (Fig. 12) | IV.D |

**Simulation platform** – MuJoCo; **Hardware** – Digit 45 kg, 30 joints, 20 motors, 3 closed chains per leg (Fig. 6).

---

## Discussion & Analysis  

- **Numerical Efficiency**: A‑ECBF eliminates mass‑matrix inversion; experiments run in real‑time on Digit hardware.  
- **Closed‑Loop Constraint Handling**: kinematic loops (four‑bar linkages) formulated as holonomic constraints and incorporated directly into QP.  
- **Safety Guarantees**: Forward invariance of safe set proved under Theorem 1; selected \(K_\alpha\) ensures critical/over‑damping.  
- **Barriers vs. Traditional Safety Filters**: Unlike post‑hoc filtering, barrier functions embed safety into the optimization objective, preventing infeasible joint commands.  
- **Scalability**: Design shown for 30 DOF—scaling to higher DOF would keep complexity linear in the number of decision variables.  

---

## Conclusions  

- Presented a **QP‑based whole‑body controller** for humanoid robots that respects closed‑loop kinematics, ZMP, friction cones, torque limits, and safety constraints via A‑ECBF.  
- **No constrained dynamics** or mass‑matrix inversion needed.  
- Demonstrated in hardware (Digit) stable squatting, bowing, walking, and collision avoidance while strictly keeping safety sets invariant.  
- **Future work**: Extending to reactive control, more complex terrains, or higher‑dimensional safety sets not explicitly addressed.

---

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|---|---|
| 1. **Inverse‑dynamics QP can avoid mass‑matrix inversion** | Decision variables include \(\ddot q\); QP constraints directly use \(\ddot q\) (Section III.A). |
| 2. **Closed‑loop kinematics, ZMP, friction, and torque limits can all be embedded in a single QP** | Section II shows constraints, Section III.A formulas. |
| 3. **An acceleration‑based ECBF (A‑ECBF) guarantees invariance of arbitrary high‑relative‑degree safe sets** | Theorem 1 and derived Condition (28) in Section III.B.2. |
| 4. **Controller achieves realistic trajectories on Digit with safety enforcement** | Experimental plots (Figs. 7–12) show safe behavior and accurate tracking. |

---

## Definitions & Key Terms  

| Term | Definition |
|---|---|
| **ECBF** – Exponential Control Barrier Function: inequality constraint guaranteeing forward invariance. |
| **A‑ECBF** – Acceleration‑based ECBF: reformulation that depends only on \(\ddot q\). |
| **Zero Moment Point (ZMP)** – projection of contact wrenches; must stay in support polygon. |
| **Friction Cone** – linear approximation of unilateral contact limits. |
| **QP** – Quadratic Programme that minimizes a cost subject to linear constraints. |
| **Soft‑Finger Contact** – additional constraint limiting normal moment in contact frame. |
| **ALIP** – Angular‑Momentum‑Based Linear Inverted Pendulum model. |
| **Closed‑Loop Kinematics** – holonomic constraints arising from links forming loops (e.g., four‑bar). |

---

## Important Figures & Tables  

| Fig. | Content | Significance |
|---|---|---|
| **Fig. 1** | Digit robot tasks: CoM, torso, arms | Illustrates full‑body motions. |
| **Fig. 2** | Model of floating base + contacts | Lays out coordinate sys. |
| **Fig. 3** | Closed‑chain example | Shows holonomic constraint construction. |
| **Fig. 4** | Contact ZMP projection | Shows ZMP expression. |
| **Fig. 5** | Controller architecture (tasks → barrier set → QP) | Visualises overall approach. |
| **Fig. 6** | Digit kinematic loops & contact frames | Source of constraints. |
| **Fig. 7** | Squat tracking (hardware & sim) | Validates QP objective. |
| **Fig. 8** | Bowing task | Demonstrates torso control. |
| **Fig. 9** | Arm trajectories with left‑fist safety | Highlights A‑ECBF effect. |
| **Fig. 10** | Joint tracking for arm task | Shows compliance with safety. |
| **Fig. 11** | Walking tracking (ALIP) | Shows gait stability. |
| **Fig. 12** | Collision avoidance under external push | Depicts A‑ECBF preventing collision. |

---

## Limitations & Open Questions  

- **Limited safety sets** were tested only for positions (e.g., fist height) and foot clearance; other dynamic safety aspects (e.g., joint velocity limits) remain untested.  
- **Computational Load**: While mass‑matrix inversion is removed, the QP still scales with DOF and number of constraints; room for analysis on worst‑case runtimes.  
- **Real‑world Disturbances**: External disturbance tests were limited to a single push; robustness to noisy contacts and unmodelled dynamics not fully quantified.  
- **Generalization to uneven terrain**: Experiments limited to flat ground; extension to variable‑height contact points not reported.  

---

## References to Original Sections  

- *Methodology* – Sections II–III (formulation of dynamics, constraints, QP, A‑ECBF).  
- *Experiments* – Section IV (tasks, safety examples).  
- *Discussion* – Section V (conclusion).  

---

## Executive Summary / Key Takeaways  

1. A whole‑body inverse‑dynamics QP that **includes A‑ECBF** can enforce arbitrary safety sets without heavy dynamics calculations.  
2. **Closed‑loop kinematics** are handled naturally by holonomic constraints in the QP.  
3. Applied to Digit, the controller achieves realistic walkers/squat/arm motions while respecting ZMP, friction, and safety barriers.  
4. The **A‑ECBF** design provides a **direct acceleration‑based** safety constraint, avoiding mass‑matrix inversion.  
5. The approach scales to the 30‑DOF Digit while running in real time.  

---