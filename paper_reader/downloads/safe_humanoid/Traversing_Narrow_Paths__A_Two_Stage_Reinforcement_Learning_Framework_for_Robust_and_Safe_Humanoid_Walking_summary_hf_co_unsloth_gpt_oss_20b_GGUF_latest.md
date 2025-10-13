**Title & Citation**  
**Title:** *Traversing Narrow Paths: A Two-Stage Reinforcement Learning Framework for Robust and Safe Humanoid Walking*  
**Authors:** Tianchen Huang, Runchen Xu, Yu Wang, Wei Gao, Shiwu Zhang  
**Venue:** IEEE/RSJ International Conference on Intelligent Robots & Systems, 2025  
**Citation (arXiv):** https://arxiv.org/abs/2502.10363  

---

## Abstract  
Traversing narrow paths is extremely demanding for bipedal robots because only a narrow strip of ground is available for footholds.  End‑to‑end reinforcement‑learning (RL) policies and purely physics‑based planners each struggle on such sparse terrains.  This paper introduces a **two‑stage RL framework** that keeps a *physics‑guided foothold planner* (Linear Inverted Pendulum Model, LIPM) in Stage‑I and adds a *low‑level foothold tracker* that learns to follow these feet.  In Stage‑II a lightweight *Foothold Modifier* (FM) refines the template priori with the help of a compact anterior height map.  The curriculum moves from flat ground to narrow beams, yielding a controller that is interpretable, generalizing efficiently and transferring to a real Unitree G1 humanoid.  On a 0.2 m‑wide, 3 m long beam the method succeeds in 20/20 trials, outperforming both a pure template and end‑to‑end RL baselines (100 % success vs. 15 % & 0 %).

---

## Introduction & Motivation  
- **Problem setting:** Narrow‑beam traversal demands *accurate foothold perception*, *precise placement*, and *robust control*; any delay or mis‑coverage can lead to falls.  
- **Existing paradigms:**  
  1. *Model‑based planners* (e.g., LIPM, ZMP preview, MPC) provide template footholds but are brittle to model mismatch and communication delays.  
  2. *End‑to‑end RL* learns both foothold selection and control but often overfits simulation physics and loses explainability.  
- **Gap:** Neither platform alone achieves high success on sparse terrains.  
- **Idea:** *Residual learning* – use a physics‑based template to keep the core foothold logic and let a RL module *correct* it only where needed.  

---

## Methods / Approach  

### A. Overall Framework  
```
LIPM  →  (u_init)  →  Stage‑I Tracker → (u_cmd)  →  Stage‑II Modifier → (u_final)
                                               ↘ PD Joint Controller
```
- **Foothold Planner:** 3‑D LIPM that, given COM state `(x,y,˙x,˙y)` and commanded velocities, outputs `u_init = (x_t,y_t,ψ_t)` for the swing foot.  
- **Foothold Tracker (Stage‑I):**   RL policy (PPO) that directly outputs desired joint positions, run at 100 Hz → PD controller at 1 kHz.  It receives “proprioception + step phase” and is trained with **random offset** `ε = (δx,δy,δψ)` applied to `u_init`.  
- **Foothold Modifier (Stage‑II):**   A second RL policy, queried only at step transitions, that predicts a *body‑frame residual* `Δu = (Δx,Δy,Δψ)` and applies `u_final = u_init ⊕ Δu`.  Constraints `||Δu|| ≤ S` (where `S` bounds the residual) keep the refinement minimal.  
- **Anters Terrain Height Map:** 11 × 17 grid sampled in the front body‑frame of the robot, 0.1 m resolution, coming from a LiDAR‑based mapper (real) or direct querying (sim).  

### B. Stage‑I Training Details  
| Component | Purpose | Reward Terms | Set‑ups |
|-----------|---------|--------------|---------|
| **Step‑tracking** | Enforce correct stance foot and accurate swing foot touchdown | `step_tracking = w_alt (I_R−I_L)s ϕ_1(‖δp‖²) ϕ_1(|δψ|)` | `w_alt=1, w_pos=5, a_p=1, w_yaw=0.5, a_ψ=1` |
| **Tracking lin vel** | Make base COM follow commanded linear velocity | `ϕ_2(‖v_cxy−v_xy‖/(1+|v_cxy|))` | `av=1` |
| **Base heading & orientation** | Keep heading and upright COM | `ϕ_1(|wrap(ψ_c−ψ)|)` , `ϕ_2(‖g_xy‖²)` | |
| **Joint regularization** | Keep joints near neutral | `Σ_j∈J ϕ_2(q_j)` | `a_q=1` |
| **Other penalities** | Linear and angular velocity limits, torques, actuation rate, etc. | As in Table IV |  

**Training hyper-parameters (Table VIII):** 4096 parallel roll‑outs, 5000 updates, learning rate 1e-5, PPO with clipping, etc.  

### C. Stage‑II Training Details  
| Component | Purpose | Reward Terms | Set‑ups |
|-----------|---------|--------------|---------|
| **Foothold safety** | Enforce footholds stay inside the beam & flat | `-5 Σ_{f∈{L,R}} 1{ h(p_f^t)<-0.20 }` | `f`: swing foot |
| **Beam balance** | Centerline adherence | `exp(-( |y-yc|/σ_y)² )` , `σ_y=0.1 m` | |
| **Forward progress** | Encourage forward movement only | `min(max(0, x_t−x_{t−1}))` |
| **Face forward** | Align foot orientation with forward direction | `max(0, 1−|wrap(ψ)|/π)` |
| **Feet proximity** | Avoid leg interference | `-min(x_R^L)+d` |
| **Action magnitude & smoothness** | Keep residual small & constant | `-‖r_t‖²`, `-‖r_t−r_{t−1}‖²` |  

**Training hyper‑parameters (Table IX):** 1024 roll‑outs, 10k updates, learning rate 1e-5, etc.  

**Domain randomization (Table VII):** Adds noise to joint positions, velocities, height maps, etc.  

### D. Observations & Control Loop  
- The **control loop** uses a PD controller at 1 kHz.  
- The **referenced operations**:  
  - Stage‑I policy to run at every 0.01 s,  
  - Stage‑II modifier only at step transition events.  
- Both policies share the same step‑phase features.  

---

## Experiments / Data / Results  

### A. Simulation Evaluation  

| Method | Success Rate | Centerline deviation (m) | FP‑RMSE (m) |
|--------|--------------|---------------------------|--------------|
| No‑Modifier (only LIPM + Tracker) | 15 % | 0.0469 | 0.0196 |
| RL‑Only (end‑to‑end) | 0 % | 0.1819 | — |
| Ours (Full two‑stage) | **100 %** | 0.0164 | 0.0263 |

*Table I* shows the full performance versus baselines.  The high success rate and low RMSE confirm that the residual modifier contributes significantly.

**Ablation Study** (Table II): removing Stage‑I target disturbances reduces success to 50 % and increases centerline dev. & RMSE.  

> **Claim:** Adding random offsets to LIPM footholds during Stage‑I yields a tracker that tolerates template variations, leading to 100 % success on narrow beams.  
> **Evidence:** Table II vs. ablation.  

### B. Hardware Validation  

**Hardware Setup:**  
- **Robot**: Unitree G1 (24‑DoF, 2 T/leg).  
- **Beams**: Wooden beams, 0.2 m wide, 3 m long, placed on flat ground.  
- **Trials**: 20 independent runs.  
- **Metric**: *Traversal Rate* = `min(1, d_trajectory / L_beam)` per trial.

| Setting | Success Rate (%) | Traversal Rate (%) |
|---------|------------------|---------------------|
| BeamDojo (previous state‑of‑the‑art) | 80 | 88.16 |
| Ours | **100** | **100** |

*Table III* shows our method beats the existing BeamDojo controller in real‑world tests.  

> **Claim:** The adopted LIPM–residual framework transfers efficiently to hardware, achieving perfect success on a lengthy, narrow beam.  
> **Evidence:** Table III and 20/20 trials.  

**Height Map Construction** (Fig. 4): On‑board LiDAR points were projected into the body‑frame, cropped to 1.1 m ahead, binned in a 0.1 m grid, and maximum height per bin recorded, giving a real‑time 11×17 vector.

**Failure Modes Investigated** (Section IV.C):  
- Height estimation bias near the beam edge could pull the foothold out of the usable area. Mitigated by robust median‑with‑outlier rejection and conservative residual bounds.

---

## Discussion & Analysis  

- The proposed two‑stage curriculum mirrors role of *physics* and *learning* in locomotion planning: the **physics** gives a trustworthy foothold template; **RL residual** supplies risk‑averse corrections.  
- **Interpretability**: The final foothold is `u_final = u_init ⊕ Δu`; the residual is always bounded, making it easy to debug.  
- **Robustness**: Stage‑I random perturbations provide a strong rehearsal to high‑variance target layouts, allowing the tracker to recover unseen perturbations during Stage‑II.  
- **Safety**: Foothold safety reward, beam‑balance, and proximity penalties prevent overshoot or leg interference.  
- **Ceasing Ghost Penalities**: Regularization terms ensure smooth motion, preventing abrupt joint torques.  

### Strengths  
1. **High success and centerline adherence** on real hardware.  
2. **Low sensor cost** – only LiDAR and IMU.  
3. **Small footprint RL** – Policy size < 10 kB.  
4. **Sim‑to‑real ease** – identical observation pipeline in simulation and real world.  

### Limitations & Open Questions  
- **Height estimation bias** still possible near beam edges; future work could involve 3‑D surface reconstruction or depth‑camera integration.  
- **Curved or discontinuous narrow paths** not tested; extension requires 3‑D foothold representation `z*`.  
- **Dynamic or moving environments** (e.g., moving beam) not yet considered.  
- **Actuator latency** not fully quantified; high‑speed PD at 1 kHz claims minimal lag but actual hardware latency may still affect foot placement.  

---

## Conclusions  

The paper demonstrates that a **two‑stage RL framework** – a template‑based LIPM foothold planner + a learned foothold tracker + a residual Foothold Modifier – achieves robust and safe narrow‑beam traversal on a real humanoid.  By coupling curriculum learning, compact terrain perception and residual correction, the controller surpasses purely physics‑based and purely RL baselines in success rate, centerline adherence, and safety margin.  Future directions include handling more complex sparse terrains and extending foothold representation to 3‑D for stairs and uneven mats.  

---

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
| **Physics‑guided RL with staged training yields 100 % success** on a 0.2 m beam. | Table III (hardware), Table I (simulation) |
| **Foothold tracking with random target perturbations is essential.** | Ablation study (Table II) |
| **Foothold modifier keeps residual within small bounds, making it interpretable and safe.** | Reward definition, residual magnitude penalty |
| **Only minimal terrain perception is required.** | 11×17 height map, no vision stack |

---

## Definitions & Key Terms  

| Term | Definition | Relevance |
|------|-------------|------------|
| **Linear Inverted Pendulum Model (LIPM)** | Reduced‑order model where COM rolls like an inverted pendulum of constant height `z0`. | Provides analytic foothold planner (`ICP` & `u_init`). |
| **Instantaneous Capture Point (ICP)** | `ξ = (x+˙x/ω0, y+˙y/ω0)` where `ω0 = sqrt(g/z0)`. | Guides next foot in LIPM planner. |
| **Foothold modifier (`Δu`)** | Body‑frame correction `(Δx,Δy,Δψ)` bounded by `S`. | Adjusts planner’s target to respect beam width. |
| **Terrain Height Map** | 11×17 grid of height samples in front body‑frame (0.1 m resolution). | Provides local perception for modifier. |
| **Success Rate** | % of trials that reach beam end within step/time limit, no falls, no safety guard fires. | Primary metric. |
| **Traversal Rate** | `min(1, d_i/L_beam)` per trial. | Secondary metric. |
| **Foothold safety reward** | Penalizes entries outside safe height range `(-0.2 m)`. | Keeps footholds bounded. |
| **Beam balance reward** | `exp(-(|y - y_c|/σ_y)^2)` – high reward near centerline. | Encourages centerline adherence. |
| **PD Controller** | Proportional‑Derivative joint controller applied at 1 kHz. | Implementation of policy outputs. |
| **PPO** | Proximal Policy Optimization – RL algorithm used for both stages. | Training method. |

---

## Important Figures & Tables  

| Figure | Description & Significance |
|--------|---------------------------|
| **Fig. 1** | High‑level overview of the two‑stage framework; illustrates LIPM planner → Stage‑I → Stage‑II. |
| **Fig. 2** | Detailed block diagram of the two‑stage policy system, colour‑coding execution frequencies. |
| **Fig. 3** | Visual of foothold adjustment: initial planner targets (dashed polygons) vs final modified targets (solid polygons). Shows Gaussian bias towards beam centreline. |
| **Fig. 4** | Illustrative LiDAR‑based terrain map reconstructed in body frame for hardware validation. |
| **Table I** | Baseline comparison in simulation (Success, Centerline dev., FP‑RMSE). |
| **Table II**| Ablation study (effect of Stage‑I disturbances). |
| **Table III**| Hardware comparison (BeamDojo vs. ours). |
| **Table IV**| Stage‑I reward components (full equations). |
| **Table V**| Stage‑II reward components (full equations). |
| **Table VI**| Symbol definitions used in rewards. |
| **Table VII**| Domain randomization parameters. |
| **Table VIII / IX**| Hyper‑parameters for Stage‑I / Stage‑II training. |

---

## Limitations & Open Questions  

- Height map bias near beam edges.  
- Curved or discontinuous narrow paths untested.  
- Moving or dynamic narrow structures (gaps, stepping stones) not evaluated.  
- Limit of residual bounding: might limit adaptation on very small footprints.  

---

## References to Original Sections  

*Section I.A*: Formulates problem & motivation.  
*Section II*: Reviews relevant physics‑based and RL approaches.  
*Section III.D*: Describes full network architecture and observation space.  
*Section IV*: Experiments – simulation (Tables I–II) and hardware (Table III).  
*Appendix*: Tables IV–IX provide detailed reward formulations, domain randomization and hyper‑parameters.  

---

## Executive Summary (optional)  

- Two‑stage RL: **Stage‑I tracker** + **Stage‑II modifier** built on **LIPM** template; **residual learning** ensures physical interpretability.  
- Curriculum from flat ground → narrow beam yields 100 % success on Unitree G1 (beam 0.2 m × 3 m).  
- Minimal perception: only LiDAR‑driven height map; no heavy vision.  
- Baselines (pure template or pure RL) fail dramatically (15 % & 0 %).  
- Strengths: interpretable, robust, safe; easily sim‑to‑real transfer.  
- Future work: extend to 3‑D foothold representation for stairs, uneven terrains; handle moving or curved narrow paths.  

---