**Title & Citation**  
*Traversing Narrow Paths: A Two‑Stage Reinforcement Learning Framework for Robust and Safe Humanoid Walking* (Huang et al., 2025)  

---

## Abstract  
Traversing narrow paths (beam‐like terrains) is difficult for humanoid robots because footholds are sparse and any deviation can cause a fall. Pure template‑based or end‑to‑end RL methods each suffer on such terrain: template models do not adapt well to model error and contact uncertainty, whereas end‑to‑end learning overfits to simulator assumptions and loses interpretability.  
This paper proposes a two‑stage training framework that couples a physics‑guided Linear Inverted Pendulum Model (LIPM) foothold planner with two learned modules:  
1. **Stage‑I** – a low‑level foothold tracker that learns to robustly follow footholds even under small target disturbances (trained on flat ground).  
2. **Stage‑II** – a high‑level foothold modifier that refines the planner’s target with a small body‑frame residual only for the swinging foot (trained on narrow paths).  

The architecture uses only a compact anterior terrain height map (11×17 samples, 0.1 m resolution) and the robot’s onboard IMU/joint signals, thus keeping sensing lightweight and enabling seamless sim‑to‑real transfer.  
On the Unitree G1 humanoid, the learned policies traverse a 0.20 m‑wide, 3 m‑long beam in 20 trials with 100 % success, outperforming template‑only and RL‑only baselines (0 % success).

---

## Introduction & Motivation  
- Narrow path traversal requires **accurate foothold placement** and **robust control**, because any lateral or vertical slip instantly removes the recovery margin.  
- Existing methods fall into two families:  
  * **Template‑based planners** (ZMP preview, MPC, ICP, etc.) provide rules for where to step but are brittle on sparse support due to modeling/latency errors.  
  * **End‑to‑end RL** (e.g., BeamDojo) trains policies end‑to‑end but may overfit the simulator and give little interpretability for safety‑critical tasks.  
- A **residual‑learning** philosophy has shown promise: keep a physics skeleton and let RL learn a corrective term. This paper adopts that approach, adding **stage‑specific curricula** (flat → narrow).  

---

## Methods / Approach  

### Overview (Fig. 2)  
1. **3D‑LIPM Foothold Planner**  
   * Computes Instantaneous Capture Point (ICP) and maps it → initial foothold `u_init`.  
   * Only uses CoM position/velocity (`x,y, ˙x, ˙y`) and desired command velocity & heading.  

2. **Stage‑I Foothold Tracker**  
   * Observation: IMU, joint states, phase.  
   * Action: joint desired positions (PD at 1 kHz).  
   * During simulation rollouts counter‑perturbations `ε` are added to `u_init` (∆x,∆y,∆ψ) to train robustness. >  
   * Reward: tracking accuracy, velocity, heading, base orientation, joint regularization, actuation rate, safety limits.  

3. **Stage‑II Foothold Modifier**  
   * Observation: same as Stage‑I + flattened anterior terrain map (22× digit).  
   * Action: body‑frame residual `Δu = (Δx,Δy,Δψ)` restricted to small bounded values `S`.  
   * Final foothold: `u_final = u_init ⊕ Δu`.  
   * Reward & safety focuses:  
     * **Foothold Safety** – penalize positions outside beam, penalize local flatness via local patch `N(u_final)`.  
     * **Beam Balance** – Gaussian penalty on lateral deviation from centerline.  
     * **Forward Progress** – reward moving forward only.  
     * **Face Forward** – encourage orientation close to forward direction.  
     * **Feet Proximity** – avoid leg interference.  

### Training Details  
- **Stage‑I** : PPO, 24 minibatches, learning rate schedule, 4096 parallel envs, 5000 updates.  
- **Stage‑II** : PPO, 10‑epoch schedule, residual action space limited by `dim=3`.  
- Domain randomization: added noise to IMU, joints, height map; varied payload and external push intervals, friction and restitution.  

---

## Experiments / Data / Results  

| **Setting** | **Method** | **Success %** | **Centerline dev.** (m) | **Foot‑placement RMSE** (m) |
|-------------|------------|---------------|------------------------|----------------------------|
| Beams 0.15, 0.20, 0.25 m × 3–5 m | No‑Modifier | 15 | 0.0469 | 0.0196 |
| | RL‑Only | 0 | – | – |
| | **Ours** | **100** | 0.0164 | 0.0263 |

**Ablation Study (0.20 m beam)**  
| **Config** | **Success %** | **Centerline dev.** | **FP‑RMSE** |
|------------|---------------|----------------------|--------------|
| w/o Stage‑I perturbations | 50 | 0.097 | 0.0547 |
| **Ours** | **100** | 0.0164 | 0.0263 |

**Sim‑to‑Real Validation (Unitree G1)**  
* 20 trials on a wooden beam 0.20 m × 3 m.  
* Method baseline: BeamDojo (Early 2025).  
* Successful when all footholds lie in beam with no fall/edge event.  

| **Comparison** | **Success %** | **Traversal rate %** |
|---------------|----------------|---------------------|
| BeamDojo [3] | 80 | 88.2 |
| **Ours** | **100** | **100** |

*Note:* Height‑estimation bias near beam boundary was mitigated by median outlier rejection and temporal smoothing.

---

## Discussion & Analysis  

1. **Foothold Disturbances in Stage‑I** – crucial for tracking robustness; removing them degraded Stage‑I tracker and caused off‑beam footholds.  
2. **Minimal Perturbations in Stage‑II** – produce safe feet placement; large residuals cause collisions or instability.  
3. **Compact Terrain Map** – sufficient for S-shaped beams; more complex terrains (curved, stepping stones) may need local perception of more extended area.  
4. **Failure Mode** – when yaw oscillation shrinks local support set, the modifier pushes the foothold to its saturation bound but still cannot lift it into beam, causing failure.  

---

## Conclusions  

- The two‑stage RL framework generalizes to narrow‑path traversal while preserving physics‑based interpretability.  
- Stage‑I tracker with disturbance curriculum improves robustness on narrow terrain.  
- Stage‑II residual modifier yields higher success, tighter centerline adherence and safety margins.  
- Only a lightweight 3D height map is needed; no heavy vision pipeline.  
- Future work: expand to irregular sparse terrains, include 3‑D vertical profile for stairs and unevenness.

---

## Key Claims & Contributions  

- **Claim 1:** A low‑level tracker trained with random foothold perturbations is essential to achieve accurate foot placement on narrow beams.  
  *Evidence:* Ablation study: success drops from 100 % to 50 % when perturbations removed.  

- **Claim 2:** A high‑level residual modifier based on a lightweight anterior terrain map ensures safe and precise footholds while preserving the interpretability of an LIPM planner.  
  *Evidence:* Stage‑II achieves 100 % success vs 0 % for RL‑Only and 15 % for No‑Modifier.  

- **Claim 3:** The combined framework transfers seamlessly from simulation to the real Unitree G1, outperforming BeamDojo.  
  *Evidence:* 100 % success vs BeamDojo 80 % with 5–8 % lower traversal rate.  

---

## Definitions & Key Terms  

- **LIPM (Linear Inverted Pendulum Model)** – reduced‑order representation of the robot’s center‑of‑mass dynamics with constant height.  
- **Foothold Planner (3D‑LIPM)** – generates initial swing‑foot target `u_init` by mapping the ICP (`ξx, ξy`) and command velocity/heading into a 3‑D pose (`x,y,ψ`).  
- **Foothold Tracker** – Stage‑I RL policy that outputs joint positions, following the `u_init` (or `u_final`).  
- **Foothold Modifier** – Stage‑II RL policy that computes a residual `Δu` just for the swing foot when a step transition occurs.  
- **Body‑frame Residual `Δu`** – 3‑dim vector (Δx,Δy,Δψ) expressed in robot’s forward‑left‑heading frame.  
- **Foothold Safety Term** – penalizes footholds falling below a safe height threshold (`-0.20 m`) and with poor local flatness measured through neighbourhood patch `N(u_final)`.  
- **Beam Balance Term** – Gaussian reward on lateral deviation from beam centerline.  

---

## Important Figures & Tables  

| **Figure** | **Description** |
|------------|-----------------|
| Fig. 1 | Overview of framework: 3D‑LIPM → mid‑level tracker → end‑level modifier, forming full control loop (shown in red). |
| Fig. 2 | Detailed architecture of stage‑I tracker and stage‑II modifier, showing observation/action spaces, relative frequencies (100 Hz tracker, event‑driven modifier). |
| Fig. 3 | Illustration of foothold modification on a beam: planner output `u_init` (dashed polygon) vs final foothold `u_final` (solid polygons), Gaussian beam‑balance penalty. |
| Fig. 4 | Top‑view of real‑time terrain map constructed from onboard LiDAR: 0.1 m resolution grid covering `[x:0.1–1.1] × [y:-0.8–0.8]`. |

---

## Limitations & Open Questions  

1. **Only beam‑type narrow paths** were evaluated; performance on curved, stepping‑stone, or uneven terrain remains to be validated.  
2. **Fixed 3‑D residual** may be insufficient for highly vertical variations (stairs, climbing).  
3. **Simple map representation** (height only) could fail under complex occlusions or variable lighting; integration of RGB‑D might be needed.  
4. **Yaw/heading**, while continuously encouraged, may still drift under persistent disturbances leading to support shrinkage; future work could include explicit heading tracking.  

---

## References to Original Sections  

- Methods – Sec. III.A–III.C (Figures, reward equations).  
- Experiments – Sec. IV.A–IV.C (Tables I–III).  
- Discussion – Sec. V—the conclusions section.  

---

**Executive Summary (Key Takeaways)** –  

* Two‑stage RL + physics‑based LIPM yields robust, safe humanoid narrow‑path traversal.  
* Stage‑I tracker trained with perturbations is key to handling narrow support.  
* Stage‑II residual modifier uses only a compact height map and learns to stay on beam centerline with minimal adjustment.  
* Achieved 100 % success on a 0.20 m beam on unitree G1; beats BeamDojo baseline.  
* Sim‑to‑real transfer demanded no heavy vision; only onboard IMU/joints + 22‑dim map.  

---