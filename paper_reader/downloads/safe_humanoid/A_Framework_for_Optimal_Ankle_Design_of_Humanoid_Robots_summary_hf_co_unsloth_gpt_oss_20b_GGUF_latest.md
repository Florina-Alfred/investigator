**Title & Citation**  
*A Framework for Optimal Ankle Design of Humanoid Robots* – Guglielmo Cervettini, Roberto Mauceri, Alex Coppola, Fabio Bergonti, Luca Fiorio, Marco Maggiali, Daniele Pucci.  
Conference / Journal not specified (publication year 2025).  

---

## Abstract
The ankle of a humanoid robot is pivotal for safe, efficient ground interaction. Mechanical compliance (back‑drivability) and mass distribution motivate the use of parallel mechanisms. Selecting the best configuration, however, depends on the available actuators and the task set. The authors present a **unified framework** that (1) synthesises the geometry of two representative parallel ankle architectures (SPU – Spherical‑Prismatic‑Universal with linear actuators, and RSU – Revolute‑Spherical‑Universal with rotary actuators); (2) derives closed‑form inverse kinematics; (3) introduces an RSU re‑parameterisation that guarantees workspace feasibility; (4) carries out a multi‑objective optimisation (peak force & velocity) for each actuator‑architecture pair; (5) evaluates the Pareto populations with a scalar, normalised cost that aggregates seven performance metrics (speed, torque, back‑drivability, manipulability, compactness, actuation mass, CoM height).  
Applying the framework to redesign the ankle of an existing humanoid robot, the optimized RSU outperformed the serial baseline (−41 %) and a conventionally engineered RSU (−14 %).  

---

## Introduction & Motivation
- **Humanoid agility** hinges on joint **mass distribution** and **mechanical compliance** (back‑drivability) [1]–[5].  
- **Ankles** are the first contact point with ground; improving them can yield large gains in locomotion.  
- **Parallel mechanisms** shift heavy actuators to the proximal side, reducing distal mass, and increase rigidity & precision [3]–[5].  
- Designing such mechanisms is difficult due to the need for *global* optimization of many geometric parameters and the coupling of actuator limits (force, velocity, size).  
- Existing surveys [16]–[17] list candidate architectures but provide no quantitative comparison criteria.  
- This paper proposes a **systematic pipeline** that can be applied to any architecture/actuator combination, enabling *cross‑architecture* and *cross‑actuator* rankings.

---

## Methods / Approach
The design pipeline has two main stages:

| Stage | Goal | Key Steps |
|---|---|---|
| **1. Geometry optimisation** | Find Pareto‑optimal sets of mechanisms for each actuator/architecture pair. | • Formulate multi‑objective optimisation (eq. (10)) to minimise **peak actuator force** and **peak actuator velocity** over a set of reference tasks (Eq. (11)). <br>• Variables: geometric parameters π (lengths, positions) and re‑parameterisation variables γ, δ that control viable crank/rod dimensions (Sec. III‑C). <br>• Constraints: actuator limits, collision avoidance, geometric feasibility (for SPU: actuator stroke limits; for RSU: existence of valid IK solutions). <br>• Solution method: NSGA‑II with the *Tunny* plugin for Grasshopper (Sec. IV‑A). |
| **2. Performance evaluation** | Rank mechanisms across architectures using a unified metric. | • Define 7 high‑level metrics (speed, torque, back‑driving torque, manipulability ratio, compactness, actuation mass, CoM height) (Sec. IV‑B). <br>• For metrics varying across the operational region (including speed/torque/manipulability), compute a weighted **mean (µ)** and **variance (σ²)** over a grid of foot orientations using a core/extended region weighting (raised‑cosine taper). <br>• Normalise each metric by min–max scaling over all candidate mechanisms. <br>• Combine all metrics into a scalar cost ξ via weighted sum (Eq. (11); weights η_j can be tuned). |

**Key modelling steps** within the pipeline:

1. **Closed‑form inverse kinematics** for SPU (Sec. III‑A) – analytic expression for prismatic displacements ζ1, ζ2 computed from geometry (Eq. (6)–(8)).  
2. **Closed‑form inverse kinematics** for RSU (Sec. III‑B) – analytic expression for revolute angles α1, α2 through solving a 2‑equation system; existence condition (Eq. (9)) ensures solvability.  
3. **Re‑parameterisation** of RSU (Sec. III‑C) – express crank length c_i as a function of γ_i ∈ [0,1], ensuring existence region always inside configuration space; similarly express rod length r_i via δ_i ∈ [0,1].  

**Reference tasks** (Sec. V‑B):
- Dynamic walking trajectory from experimental data.
- Simulated walking on a 20 % incline.
- Simulated step‑down/up (20 cm step) (Fig. 5).  

**Operational region**: [−35°, 35°] roll × [−70°, 30°] pitch; core | smaller | used for weighting.

**Actuators** selected from commercial catalogue (SPU: Wittenstein AL32; RSU: Maxon HEJ 70‑48‑50, MyActuator RMD‑X6P20‑60, Synapticon ACTILINK JD 10). The revolute actuators use planetary gearboxes (ratio 9:1–19:1) to preserve back‑drivability.

---

## Experiments / Data / Results

| Item | Result | Source |
|---|---|---|
| **RSU re‑parameterisation validation** | The desired operational region is always inside the “feasible” gray area; singularity curves touched only at γ, δ close to 0 (Fig. 4). | Fig. 4 |
| **Optimization output** | Pareto–fronts for RSU with Synapticon actuators shown in Fig. 7; cost distribution over all actuators in Fig. 8. | Fig. 7, 8 |
| **Evaluation metrics** | Best SPU vs RSU breakdown over 7 metrics in Fig. 9. RSU best in speed, torque, back‑drivability, compactness; SPU has lower variance but lower average. | Fig. 9 |
| **Cost comparison** | Optimised RSU cost lower than engineered RSU and serial baseline. RSU cost −14 % vs engineered RSU; RSU cost −41 % vs serial. | Fig. 8 (arrows/dashed line) |
| **Scalar cost function validation** | The cost function correctly reflects improvements across architectures. | Section V–C |

---

## Discussion & Analysis
- The **scalar cost function** effectively aggregates *task‑related* performance (through mean/variance) and *inherent* design aspects (mass, CoM, compactness).  
- The **manipulability ratio** highlights RSU’s more isotropic behavior in the desired region.  
- **Front variability** (σ²) shows SPU yields more consistent metrics across the region but with lower average values.  
- The **parameterisation** of RSU ensures that the inverse‑kinematic existence condition (Eq. (9)) is inherently satisfied, simplifying optimisation.  
- The multi‑objective optimisation did *not embed* the scalar cost; this allows re‑weighting afterwards (future work suggests embedding ξ directly into optimisation).  
- **Collision checking** over the operational region is still approximate; future work will enforce it fully.  
- The framework also applies to serial mechanisms as demonstrated in the baseline comparison (Fig. 8 dashed line).

---

## Conclusions
- Introduced a **unified framework** that integrates closed‑form kinematics, RSU re‑parameterisation, multi‑objective optimisation, and a scalar cost evaluation.  
- When applied to redesign the ankle of a humanoid robot, the optimized RSU architecture *outperformed* both the conventional RSU and the original serial design, reducing the cost by 41 % and 14 % respectively.  
- Demonstrated that the framework can compare any architecture/actuator combination by normalised metrics.  
- Future extensions: full‑region collision checking, directly embedding the scalar cost into optimisations.

---

## Key Claims & Contributions
| Claim | Evidence |
|---|---|
| **C1. Parallel ankle architectures provide measurable advantages over serial ones** – cost reduction 41 % quantified (Sec. V‑D). |
| **C2. RSU optimisation yields better overall performance than engineered RSU or SPU, despite higher variance** – comparative plots (Fig. 8–9). |
| **C3. RSU re‑parameterisation guarantees IK feasibility across the whole operational region** – validated in Fig. 4. |
| **C4. Multi‑objective optimisation yields Pareto fronts that can be ranked by a single scalar cost aggregating multiple metrics** – methodology in Sec. IV‑B, result in Fig. 8. |
| **C5. The proposed cost function can be re‑weighted without re‑optimising** – discussion in Sec. IV‑B. |

---

## Definitions & Key Terms
- **Parallel mechanism** – closed‑loop architecture with multiple kinematic chains connecting a base and an end effector.  
- **SPU** – spherical‑prismatic‑universal chain (linear actuators).  
- **RSU** – revolute‑spherical‑universal chain (rotary actuators).  
- **Closed‑form IK** – analytic expression for actuator variables given EE pose.  
- **Maniplability ratio** – λ_max/λ_min of Jacobian J Jᵀ, with λ eigenvalues of J Jᵀ.  
- **Compactness** – minimum radius of a vertical cylinder enclosing all mechanism points at neutral configuration.  
- **CoM height** – vertical distance from ground to centre of mass of the actuator pair.  
- **Back‑driving torque** – torque needed at ankle joint to overcome static friction of actuators.  

---

## Important Figures & Tables
- **Fig. 1** – Illustrates serial, SPU, RSU architectures.  
- **Fig. 2** – Connectivity graphs of SPU/RSU (link nodes & joint edges).  
- **Fig. 3** – Kinematic diagrams for SPU (a) and RSU (b).  
- **Fig. 4** – RSU re‑parameterisation test (red operational region inside gray feasible area).  
- **Fig. 5** – Example of step‑down trajectory in simulation.  
- **Fig. 6** – Core/extended region weighting map.  
- **Fig. 7** – Pareto front for Synapticon RSU.  
- **Fig. 8** – Cost distribution ξ for all actuator families; arrows for engineered/c serial.  
- **Fig. 9** – Comparative breakdown of best SPU vs RSU metrics.  

---

## Limitations & Open Questions
1. **Collision checking** is only local (verified at points of design space); full‑region enforcement future work.  
2. **Cost function not embedded** in optimisation loop – possible to bias search.  
3. **Application‑specific weighting**: optimal weight choices for η_j not investigated extensively.  
4. **Real‑time execution**: only evaluated off‑line (simulation).  
5. **Actuator catalogue**: limited to few actuators; extension to higher‑power or lower‑size actuators not shown.  

---

## References to Original Sections
- **Kinematics** modelling – Sections III‑A (SPU), III‑B (RSU).  
- **Re‑parameterisation** – Section III‑C.  
- **Optimization framework** – Section IV‑A.  
- **Evaluation metrics** – Section IV‑B.  
- **Results** – Section V (A–D).  
- **Conclusion** – Section VI.  

---

## Executive Summary (optional)
- Parallel ankle mechanisms shift heavy actuators proximally, improving back‑drivability and dynamics.  
- Presented a framework that automatically synthesises geometry, optimises motion tasks, and scores designs via a normalised cost.  
- Applied to two representative architectures (SPU, RSU); RSU achieved the best performance.  
- Optimised RSU reduced aggregated cost by 41 % vs baseline serial, 14 % vs conventionally engineered RSU.  
- Framework supports any architecture/actuator combination and can be re‑weighted post‑optimisation.  
- Future work will integrate collision checking and cost‑driven optimisation.