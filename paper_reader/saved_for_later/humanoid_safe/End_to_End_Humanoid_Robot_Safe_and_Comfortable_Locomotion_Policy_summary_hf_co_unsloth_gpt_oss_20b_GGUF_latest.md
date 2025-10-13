**Title & Citation**  
*End‑to‑End Humanoid Robot Safe and Comfortable Locomotion Policy*  
Zifan Wang, Xun Yang, Jianzhuang Zhao, Jiaming Zhou, Teli Ma, Ziyao Gao, Arash Ajoudani, Junwei Liang  
Hong Kong University of Science and Technology (Guangzhou), Human‑Robot Interfaces & Interaction Lab., Istituto Italiano di Tecnologia, Italy.  
Published: 2025 (arXiv‑style preprint, GitHub project: https://github.com/aCodeDog/SafeHumanoidsPolicy)  

---

## Abstract  
The authors present an end‑to‑end locomotion policy for a humanoid robot that directly maps raw spatio‑temporal LiDAR point clouds to motor commands. The control problem is formalised as a Constrained Markov Decision Process (CMDP). A key innovation is the translation of model‑based Control Barrier Function (CBF) principles into a cost function that can be used by a model‑free Penalised Proximal Policy Optimisation (P3O) algorithm. Comfort‑oriented rewards, motivated by human‑robot interaction research, encourage smooth, predictable, and socially‑acceptable motions. Through extensive simulation and real‑world tests on a Unitree G1, the policy demonstrates agile, safe, and comfortable navigation in cluttered dynamic scenes.

---

## Introduction & Motivation  
- Human‑centric environments demand robots that combine **3‑D perception**, **provable safety**, and **social awareness**.  
- Current reinforcement‑learning (RL) locomotion controllers are either:  
  1) *blind* (proprioceptive only) → unable to handle obstacles;  
  2) *2‑D vision‑based* → limited field‑of‑view and sensitivity to lighting, missing non‑ground obstacles.  
- LiDAR offers a lighting‑invariant, full‑body 3‑D representation but has not been fully exploited in end‑to‑end policies.  
- Reward‑shaping alone is brittle and does not guarantee safety or social comfort.  
- The paper proposes:  
  - a **LiDAR‑based perception pipeline**;  
  - a **CMDP formulation** with *model‑free* constraint enforcement; and  
  - a **human‑centric comfort reward** scheme.

---

## Methods / Approach  

### 1. Constrained Markov Decision Process (CMDP)  
The CMDP is defined as  
\[
\mathcal{M}=(\mathcal{S},\mathcal{A},P,R,\{C_j\},\{\varepsilon_j\},\gamma_{\text{RL}})
\]  
— *states* \(\mathcal{S}\), *actions* \(\mathcal{A}\), *transition* \(P\), *reward* \(R\), *costs* \(\{C_j\}\), *cost limits* \(\{\varepsilon_j\}\).  
Objective: maximise expected discounted reward while satisfying \(\mathbb{E}_{\pi}[ \sum_{t} \gamma_{t}^{\text{RL}}\, C_j] \le \varepsilon_j\) for all \(j\).  

### 2. Linear Discrete‑Time Control Barrier Function (LDCBF)  
For safety distance \(D_{\text{min}}\) from an obstacle:  
\[
h_{\text{D}}(s_k)= \big(\underline{p}(s_k)-\widehat{p}_s\big)^{\top}\widehat{n}_s+\eta_{\text{CBF}}\,
\]  
with \(\widehat{n}_s\) the outward normal at the nearest obstacle point and \(\eta_{\text{CBF}}\in(0,1]\).  
Constraint:  
\[
h_{\text{D}}(s_{k+1}) \ge (1-\eta_{\text{CBF}})\,h_{\text{D}}(s_k) .
\]
Re‑shaped into a **cost**:  
\[
C_{\text{safe}}(s_k,a_k)=\max\bigl(0,h_{\text{D}}(s_{k+1})-(1-\eta_{\text{CBF}})h_{\text{D}}(s_k)\bigr).
\]
This cost is positive only if the chosen action would violate the safety LDCBF.  

### 3. Comfort‑Oriented Reward Structure  
Table I lists all reward/cost terms.Important provisions:  
- **Task**: velocity‑tracking (weights 2.0, 0.5), auxiliary (z‑velocity, torque, joint limits).  
- **Comfort**:  
  - *Proxemic comfort*: \(\exp(-\alpha_p(d_{\text{human}}-d_{\text{social}})^2\) with \(d_{\text{social}}=1.2\,\text{m}\).  
  - *Safe approach velocity/accel*: \(-\max(0,-\widehat{v}_k^{\top}\widehat{n}_k)\), \(-\max(0,-\widehat{a}_k^{\top}\widehat{n}_k)\).  
  - *Tangential avoidance*: \(1-\max(0,\widehat{v}_k^{\top}(-\widehat{d}_{\text{obs},k})\).  
These terms penalise abrupt or head‑on motion and reward gentle, tangential avoidance.  

### 4. Actor‑Critic Network Architecture  
- **Actor** receives:  
  - Proprioceptive/history: last 10 timesteps of joint states, base velocities, gravity, command.  
  - LiDAR embedding: 64‑dim vector, passed through a GRU.  
  - Concatenated with proprioceptive history → MLP → output motor torques.  
- **Critic** (training only) obtains the same plus **privileged simulation facts**: actual nearest obstacle distance/velocity in 8 directions, full contact forces, joint‑limit compliance.  

### 5. Training Algorithm: Penalised Proximal Policy Optimisation (P3O)  
The objective:  
\[
L_{\text{P3O}} = L_{\text{CLIP},N,R} +\sum_{j}\kappa_j\, L_{\text{VIOL},N,C_j},
\]  
with \(\kappa_j\) penalty hyper‑parameters, \(L_{\text{VIOL},N,C_j}\) the clipped cost advantage, normalised by mean \(\mu_j\) and std \(\sigma_j\). The method guarantees constraint satisfaction through a first‑order update, avoiding the higher‑order complexity of CPO.  

---

## Experiments / Data / Results  

### A. Experimental Setup  
- **Sim**: NVIDIA Isaac Sim 5.0, Genesis 4.2, domain randomisation + curriculum.  
- **Real**: Unitree G1 (22 DoF humanoid) with Livox Mid‑360 LiDAR; all inference on the on‑board computer.  

### B. Ablation Study  
Three variants:  
1. *P3O‑CBF* (full method)  
2. *PPO‑RewardShaping* (only reward penalties for proximity)  
3. *P3O* (same as 1 without comfort rewards)  

Qualitative comparison in Fig. 3:  
- PPO‑Reward Shaping: aggressive, collides or stalls.  
- P3O: reactive, passes close, jerky.  
- P3O‑CBF: smooth path, wide turns, consistent safety margin.  

**Claim –** “P3O‑CBF yields the safest and smoothest behavior.”  
*Evidence:* Figure 3 qualitatively, Tables II & III quantitatively.  

### C. Safety & Comfort Metrics  
Table II (seconds spent in unsafe—Dobs<0.6 m, and uncomfortable‑safe—0.6≤Dobs<1.2 m) over 10 runs:  
| Policy | Unsafe | Uncomfortable |  
|--------|--------|----------------|  
| PPO‑RS | 1.7 | 3.4 |  
| P3O | 1.2 | 3.1 |  
| P3O‑CBF | 0.8 | 2.2 |  

**Claim –** “P3O‑CBF reduces unsafe time by 53 % vs PPO‑RS.”  
*Evidence:* Table II.  

### D. Evaluation Scenarios  
Four challenging simulations (Fig. 4):  
1. Suspended obstacle (low‑hanging platform).  
2. Narrow passage (confined corridor).  
3. Cluttered static course (dense pillars).  
4. Dynamic agents (moving humanoids).  

Success rates over 30 trials:  
| Scenario | PPO‑RS | P3O | P3O‑CBF |  
|----------|--------|------|----------|  
| (a) Suspended | 20 % | 90 % | 83 % |  
| (b) Narrow | 0 % | 33 % | 60 % |  
| (c) Static | 93 % | 100 % | 100 % |  
| (d) Dynamic | 56 % | 70 % | 86 % |  

**Claim –** “P3O‑CBF achieves best performance, especially in narrow and dynamic settings.”  
*Evidence:* Table III and scenario descriptions.  

### E. Physical Tests  
Two real‑world scenarios (Figs. 5–6):  
1. Cluttered lab with static obstacles – robot successfully navigated without collision.  
2. Human‑robot interaction – a person approaches from behind; robot stops and re‑routes adaptively.  

Both real tests confirm sim‑to‑real transfer.  

---

## Discussion & Analysis  

- The LDCBF cost effectively propagates future safety constraints without requiring an explicit dynamics model, enabling **model‑free training** while still respecting physical safety boundaries.  
- Comfort rewards encourage torso‑velocity smoothness and tangential motion. These preferences lens human‑centric acceptance, aligning with proxemics literature.  
- Ablation shows that reward shaping alone is insufficient; safety constraint *plus* comfort designs are essential.  
- The simulation‑to‑real jump is successful because of domain‑randomised curriculum and the lightweight perception (64‑dim LiDAR embedding, no heavy point‑cloud processing).  

---

## Conclusions  

An end‑to‑end locomotion policy was constructed that:  
1. Processes raw 3‑D LiDAR to sense full‑body obstacles.  
2. Enforces safety via a CBF‑derived cost inside a CMDP, trained with P3O.  
3. Generates socially‑comfortable motions through tailored reward terms.  
Results prove superior safety, comfort, and robot‑safety in both simulation and real‑world human environments. The framework bridges perception, safety, and social awareness, advancing humanoid robots toward practical, human‑centric adoption.

---

## Key Claims & Contributions  

- **Claim 1:** Direct LiDAR‑to‑motor mapping yields robust navigation in complex 3‑D environments.  
- **Claim 2:** Translating CBF principles into CMDP cost allows model‑free safety guarantees via P3O.  
- **Claim 3:** Human‑interaction informed comfort rewards produce smoother, predictable motions.  
- **Contribution 1:** First end‑to‑end policy that integrates raw LiDAR, CMDP safety, and HRI comfort.  
- **Contribution 2:** Novel framework for deriving safe constraints from LDCBF without an explicit dynamics model.  
- **Contribution 3:** Successful real‑world deployment on human‑friendly humanoid (Unitree G1).  

---

## Definitions & Key Terms  

| Term | Definition | Source |  
|------|-------------|---------|  
| CMDP | Constrained Markov Decision Process; extends MDP with cost constraints | Section III‑A |  
| CBF / DCBF | Control Barrier Function; defines safe set \( \{x | h(x) \ge 0\}\) | [30] |  
| LDCBF | Linear discrete‑time CBF, specific to this paper’s safety margin | Section IV‑B |  
| P3O | Penalised Proximal Policy Optimisation; first‑order constrained RL | [28] |  
| ICC / S_IC | Interactive Comfortable Space; subset of safe states to avoid human discomfort | Definition 1 |  
| ICSI | Safe & Comfortable Policies; safe + comfortable | Definition 2 |  

---

## Important Figures & Tables  

- **Figure 1** – Illustration of Safe, Unsafe, Comfortable subspaces (S_safe, S_unsafe, S_IC).  
- **Figure 2** – Overview of training framework: LiDAR → GRU → MLP → Actor/Critic.  
- **Fig. 3** – Qualitative trajectory comparison (PPO‑RS, P3O, P3O‑CBF).  
- **Table I** – Unified reward and cost components, weights, and formulas.  
- **Table II** – Time spent in unsafe and uncomfortable spaces (seconds).  
- **Figure 4** – Simulation scenarios (suspended obstacle, narrow passage, cluttered static course, dynamic agents).  
- **Table III** – Success rates across scenarios.  
- **Figure 5** – Real‑world cluttered environment navigation.  
- **Figure 6** – Real‑world human approach avoidance.  

---

## Limitations & Open Questions  

- **Limited to Humanoid G1**: Generalisation to other humanoids not tested; might need re‑training due to different dynamics.  
- **LiDAR Resolution**: 64‑dim embedding may lose fine geometric details; future work could use voxel‑based or point‑cloud network.  
- **Continuous Dynamics**: Linear dynamics assumption in LDCBF formula may be violated in highly nonlinear gait transitions; robustness measured indirectly through learning.  
- **Dynamic Obstacle Prediction**: The model does not explicitly forecast other agents’ future states; relies solely on instantaneous LiDAR.  
- **Human Comfort Validation**: Comfort rewards derived from literature; quantitative human subject studies were not performed.  

---

## References to Original Sections  

- Definitions: Sections III‑A (1–3).  
- LDCBF cost derivation: Section IV‑B.  
- Actor/Critic: Section IV‑A.  
- Reward structure: Table I.  
- P3O objective: Section IV‑D.  
- Ablation: Section V‑B.  
- Evaluation scenarios: Section V‑C.  
- Real‑world tests: Section V‑D.

---