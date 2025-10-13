**Title & Citation**  
*Learning to Walk in Costume: Adversarial Motion Priors for Aesthetically Constrained Humanoids*  
Authors: Arturo Flores Alvarez, Fatemeh Zargarbashi, Havel Liu, Shiqi Wang, Liam Edwards, Jessica Anz, Alex Xu, Fan Shi, Stelian Coros, Dennis W. Hong.  
*Submitted to the 2025 IEEE Robotics & Automation* (Conference‑style proceedings, 2025).

---

## Abstract  
The paper introduces an RL‑based locomotion controller for **Cosmo**, a custom entertainment‑robot humanoid that carries distinctive aesthetic constraints: a 4 kg head (16 % of the 25 kg system mass), purely proprioceptive sensing, and protective shells that limit joint extents.  Adversarial Motion Priors (AMP) are leveraged to imbue the system with natural human‑like motion while preserving stability.  The authors design a full sim‑to‑real pipeline that includes domain randomization, a curated reward structure, and a novel motion‑retargeting method that moves CMU mocap data onto the Cosmo rig.  Experiments show that the AMP‑augmented policy can stand and walk stably, despite the extreme mass distribution, and that the policy remains safe for real hardware operation.

---

## 1. Introduction & Motivation  
- **Humanoid entertainment robotics** demands admirable anthropomorphism (story‑telling, audience engagement).  
- **Cosmo** exemplifies unconventional design: large head, aesthetic shells, limited joint freedom—classic *design‑over‑function* constraints.  
- Conventional model‑based control and RL‑only solutions typically require extensive tuning or produce jerky, unnatural motions.  
- **AMP** blends imitation learning (human reference via motion capture) with RL, allowing the robot to learn *style* while still optimizing for task reward.  
- **Key objectives**:  
  1. Develop a **stable, natural‑looking walker** on Cosmo.  
  2. Build a **robust sim‑to‑real transfer** pipeline that accounts for broken visual feedback, shell geometry, and mass distribution.  
  3. Demonstrate that **learning‑based control** can succeed where classic biped approaches struggle.

---

## 2. Related Work  
- **Model‑based control** (e.g., Atlas, Atlas‑style optimization) [5–6]; brittle under design deviations.  
- **Pure RL** – successes in running, parkour, whole‑body control [7–12] – but often lack human‑like style and demand heavy reward shaping.  
- **Imitation learning**: learns from demonstrations, providing visual verifiability.  
- **AMP** (Peng et al. [4]) introduces an adversarial discriminator to generate a *style reward* that substitutes for complex hand‑tuned reward terms.  
- Our work extends AMP to a **top‑heavy, shell‑constrained humanoid** with only proprioceptive sensing, a scope rarely tackled in literature.

---

## 3. Methods / Approach  

| Sub‑section | Core ideas | Key equations / formulas | Tools / libraries |
|--------------|-------------|---------------------------|--------------------|
| **A. Motion Retargeting** | Human mocap → Cosmo rig. Custom Blender rig; 10 DoF legs, 8 arms, 2 head joints. | Not explicitly formulated; explained qualitatively in the text. | Rokoko Studio live plugin for Blender [14]; CMU mocap dataset [16,17]. |
| **B. Imitation Learning with AMP** | Treat locomotion as POMDP. Policy \(\pi_\theta(a|s)\) maximizes discounted return \(\mathbb{E}[ \sum \gamma^t r_t ]\). Discriminator \(D_{\phi}(s)\) distinguishes samples from reference motions \(M\). | Loss: \(\mathcal{L}_D = \mathbb{E}\_{\pi_\theta}[ \log D_\phi(s)] + \mathbb{E}\_M[ \log(1-D_\phi(s))]\). <br> AMP reward: \(r_{\text{AMP}}(s_t) = \log D_\phi(s_t)\). | Isaac Gym and Isaac Sim for training (GPU‑accelerated). Policy nets: 3×(512,256,128). Critic / discriminator nets: 2×(256,128). |
| **C. Observation & Action Spaces** | State vector \(s = [v_{\text{base}}, \omega_{\text{base}}, q_{\text{norm}}, \dot{q}, g_{\text{proj}}, a_{prev}, h_{\text{base}}, c_{\text{cmd}}]\). Actions: target joint positions for 28 DoF actuated by high‑frequency PD controller. | See equations in §III.B (not reproduced fully here due to length). | EKF for base kinematics using proprioception only. |
| **D. Reward Structure** | Three groups: style, motion quality, safety + task. | **Table II** in the paper lists explicit formulas: e.g., joint‑rate reward = \(\exp(-(\dot{q}-\dot{q}_{\text{target}})^2 / \sigma^2\). Safety terms incorporate foot stumble and foot‑height to keep feet flat and clear of shell interference. | Adjusted coefficients allow curriculum learning. |
| **E. Hardware / PF- Constraints** | Cosmo mass: 25 kg in total, head 4 kg (16 %) sits atop the torso; only 28 DoF (“Westwood Robotics” Panda Bear Plus & Koala Bear Muscle Build actuators). Feet: spring steel flexures; shells protect but limit clearances. | No external visual cameras – purely proprioceptive. |
| **F. Simulation Suite** | Isaac Sim used for *static analysis* of candidate standing poses: support polygon defined by foot‑ground contacts. 4 candidate poses derived from human standing stance (arms at sides). Only 2 of 4 remained stable in simulation.  Fig. 6 shows main metric: Euclidean distance of center of mass from initial position. Cosmo exhibited \(30\,\text{mm}\) deviation vs ARTEMIS \(6\,\text{mm}\). | Engineering insight: chosen pose should maintain gravity vector inside support polygon at all times. |
| **G. Domain Randomization** | Randomization parameters in **Table III**: friction [0.2,1.1]; base mass ±1.5 kg; PD gains 0.75–1.13; actuator lag 4 steps; pushes (interval 4 s, linear push 0.5 m/s, angular 0.2 rad/s). | Aimed to bridge reality gap and harden policy to disturbances. |

---

## 4. Experiments / Data / Results  

### 4.1. Training Performance  
| Aspect | Findings | Caption references |
|--------|-----------|---------------------|
| **Tracking of balancing policy with varying head mass** | Optimal at **3.2 kg** (≈70 % of 4 kg nominal). Performance drops for higher mass and also for too light (2.2 kg); shows non‑linear dependency of mass distribution on policy success. | Table IV, “Balancing – Added Mass” section, Fig. 7 (stylized). |
| **Walking policy styles** | Three styles: 1) standing pose only, 2) hybrid with model-based walking data, 3) “swagg” Jeff’d human style. Achieves 0.5–0.7 m/s. | Fig. 7 (left‑right). |
| **Reward coefficient tuning** | Balanced grouping [0.35,0.35,0.4] gave best avg. reward 0.721, safety 0.693. Lower AMP style coefficient (0.4) gave best performance 0.733, safety 0.720 (The higher coefficient trades safety for unwelcome style fidelity). | Table IV, “Walking – Reward Structure” & “Amp Style Coefficient” sections. |

### 4.2. Sim‑to‑Real Transfer

- **Balance**: Fig. 8 shows joint tracking and disturbance rejection. Upper‑body remains stable; joint excursions stay within safe torque limits ±20 Nm; lower‑body ankle pitch oscillates with disturbance events. Body‑local velocities recover in ~2 s after disturbances.  
- **Walking**: Fig. 9 displays joint command tracking, body‑local velocity, and torque tracking for natural gait. Policy reproduced human‑like shoulder swings, subtle head oscillations, and commanded velocities peaked at \(0.4\,\text{m/s}\).  Safety: torques within ±20 Nm, consistent with design limits.  

### 4.3. Ablation Studies  

**Motion Reference Ablation**  
- *Without standing pose reference*: Fig. 10(a) shows vertical jumping, high center of mass, increased risk.  
- *Without model‑based reference*: Fig. 10(b) shows high‑frequency stepping, poor foot trajectory control; policy fails to accelerate smoothly from stand‑stand to “human‑like” gait.

**Reward Component Ablation**  
- Fig. 11 compares baseline (all rewards) vs two variants: missing stumble prevention and missing foot‑height rewards. Baseline achieves ~12 control ticks per step (roughly 1.9 Hz). Alternatives yield faster but unsafe spikes in ground reaction force, risking mechanical damage.  

---

## 5. Discussion & Analysis  

- **Learning vs. Classic Control**: Central claim—AMP with carefully curated motion references enables natural, stable locomotion on a highly asymmetrical robot without over‑tuning task reward.  
- **Specialized rewards** are essential for protecting shell‑protected joints (especially swing‑foot foot shell), as evidenced by ablation (Fig. 11).  
- **Multiple references**—standing pose + model‑based walking + human mocap—are crucial; each reference supplies missing information (e.g., amplitude, frequency).  
- **Domain randomization**: Physics & sensor noise (Table III) crucial for safe sim‑to‑real bridge.  Real‑world policy remained robust against pushes, demonstrating the method’s generality under high–mass distribution and limited sensing.  
- **Speed trade‑off**: Achieved 0.5–0.7 m/s, slower than prior RL‑only exps [8], but acceptable for entertainment robots where expressiveness outweighs speed.  
- **Future work**: Compare AMP to purely model‑based controllers, explore cross‑embodiment transfer of learned policies across different aesthetic motifs.

---

## 6. Conclusions  

- **AMP** provides a principled way to embed human‑style motion into RL training for robots whose **aesthetic constraints** compromise stability.  
- **Cosmo** demonstrates that a top‑heavy, shell‑constrained humanoid can walk stably and naturally using a **sim‑to‑real pipeline** that includes domain randomization, a tailored reward hedge, and motion‑retargeting.  
- **Key take‑aways**:  
  1. The head‑mass trade‑off matters, and a mid‑range mass (3.2 kg) is optimal.  
  2. Reward engineering around shell‑geometry protects mechanical parts.  
  3. Ablation confirms necessity of multi‑reference, not just style or task reward alone.  
  4. Resulting motion remains physically plausible while preserving entertainment and aesthetic demands.

---

## 7. Key Claims & Contributions  

- **Claim 1**: AMP‑based policy can produce stable standing and walking on Cosmo despite its disproportionate head mass.  
  *Evidence*: Table IV & Fig. 6 / usage of 28‑DoF PD control.  

- **Claim 2**: Domain randomization + reward tuning yields safe sim‑to‑real transfer without needing visual sensing or hardware‑specific tuning.  
  *Evidence*: Fig. 8 & 9 show sustained stability post-pushes.  

- **Claim 3**: Retargeting from CMU mocap + model‑based reference yields rich rotational dynamics necessary for entertainment‑style locomotion.  
  *Evidence*: Ablation results in Fig. 10.  

- **Claim 4**: Specialized foot‑safety rewards prevent shell damage during real motion.  
  *Evidence*: Fig. 11, torque limits compliance, and safe foot trajectories.  

---

## 8. Definitions & Key Terms  

| Term | Definition (as per paper) | Context |
|------|---------------------------|---------|
| **AMP** | *Adversarial Motion Priors* – a method that couples a reinforcement learner with a discriminator that compares states to a reference motion dataset to generate a learned style reward. | Used to generate human‑like walking from CMU mocap. |
| **POMDP** | Partially Observable Markov Decision Process – formal framework for RL when only partial state observations are available. | Light‑weight observation vector “s” includes proprioceptive info only. |
| **Support Polygon** | Convex hull formed by foot‑ground contact points; gravity vector must be inside for static stability. | Used in static pose analysis to choose standing pose. |
| **Invariant Extended Kalman Filter (EKF)** | Algorithm for state estimation that remains consistent under i­nvariant dynamics; used to estimate base linear/angular velocities. | Observations in state vector. |
| **Domain Randomization** | Randomizing simulation parameters (mass, friction, gain, sensor noise, actuator lag) to expose policy to diverse conditions. | Table III. |
| **Foot Calibrated Height Reward** | Penalizes foot height deviations from a predefined reference foot‑height to keep feet flat under shell geometry. | Reward component in Table II. |
| **Model‑Based Walking Data** | Whole‑body controller data generated by quadratic programming applied to Cosmo’s real hardware; included as motion reference. | Provides low‑speed, stable stepping for training. |

---

## 9. Important Figures & Tables  

| Fig / Table | What it shows | Relevance |
|-------------|----------------|-----------|
| **Fig. 1** | Cosmo CAD & real look; positions. | Visual context for aesthetic constraints. |
| **Fig. 2** | Arm range & mass distribution of Cosmo. | Highlights mass asymmetry. |
| **Fig. 3** | Sim‑to‑real pipeline diagram (retarget → train → validate → deploy). | Overview. |
| **Fig. 4** | Foot models & shell illustration. | Visualizes shell constraints. |
| **Fig. 5** | Full training framework diagram. | Summarizes AMP, reward terms. |
| **Fig. 6** | Stability of 4 candidate poses (center‑of‑mass deviation vs ARTEMIS). | Guided pose selection. |
| **Fig. 7** | Three walking styles; reward tuning results. | Shows style impact. |
| **Fig. 8** | Joint tracking & disturbance response on hardware. | Demonstrates balancing robustness. |
| **Fig. 9** | Joint command, body velocity, torque tracking for walking. | Demonstrates gait naturalness. |
| **Fig. 10** | Ablation of motion references (no standing, no model‑based). | Proves necessity of each reference. |
| **Fig. 11** | Foot height & contact force under different reward configs. | Shows effect of safety rewards. |
| **Table I** | Command ranges for \(c_{\text{cmd}}\). | Sets exploration limits. |
| **Table II** | Reward components & formulas. | Central to training objective. |
| **Table III** | Domain randomization ranges. | Config of sim‑to‑real randomization. |
| **Table IV** | Performance metrics vs head mass & reward choices. | Quantifies trade‑offs. |

---

## 10. Limitations & Open Questions  

1. **Generalizability** – Paper focuses solely on Cosmo; not evaluated on other robots or deformations without retraining.  
2. **Reward Weight Sensitivity** – While Table IV shows some robustness, the exact weight vector may change with different reference datasets or morphology variations.  
3. **Shell Modeling** – Collision meshes approximated; future work could integrate learned contact dynamics for more realistic shell physics.  
4. **Actuator Precision** – Real‑world PD controller saturations and delays may differ from simulation hyper‑parameters; more detailed sensitivity analysis could solidify bounds.  
5. **Transfer to Unstructured Terrain** – Experiments limited to flat planes; performance on stairs, slopes, or uneven terrains not shown.  

---

## 11. References to Original Sections (if available)  

- *Methodology*: §III (A–G)  
- *Reward design*: §III B (Table II)  
- *Sim‑to‑real pipeline*: §IV (G)  
- *Results*: §IV (A–C)  
- *Ablation*: §V (A–B)  
- *Discussion & conclusion*: §VI  

---

## 12. Executive Summary (Optional)  

1. **Problem**: Aesthetic humanoid with large head & shell constraints cannot be managed reliably by classic model‑based or pure RL controllers.  
2. **Solution**: Use AMP + domain randomization + multi‑source motion references (CMU mocap + model‑based walking).  
3. **Sim pipeline**: Isaac Sim for proving pose stability; Isaac Gym for massively parallel training.  
4. **Reward**: Style + motion quality + foot safety + task.  
5. **Results**: Stable standing & walking (0.5–0.7 m/s) on Cosmo; policy robust to 0.15 m/s disturbances; torques under ±20 Nm.  
6. **Ablation**: Each reference and safety reward essential for safe, expressive motion.  
7. **Conclusion**: AMP enables entertainment robots to walk naturally without sacrificing safety or requiring exhaustive manual tuning.

---

## 13. Supplementary Material (if present)  

- The paper references a **supplementary video** that demonstrates “natural walking” in the real world (see Fig. 1 bottom).  
- No additional appendices or openly provided code/data repositories are described in the extract.  

---