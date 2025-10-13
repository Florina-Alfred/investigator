**Title & Citation**  
**End‑to‑End Humanoid Robot Safe and Comfortable Locomotion Policy**  
Zifan Wang, Xun Yang, Jianzhuang Zhao, Jiaming Zhou, Teli Ma, Ziyao Gao, Arash Ajoudani, Junwei Liang.  
Presented at (year not specified); project page: https://github.com/aCodeDog/SafeHumanoidsPolicy  

---  

### Abstract  
The authors present a reinforcement‑learning (RL) policy that maps **raw, spatio‑temporal LiDAR point clouds** directly to joint motor commands for a humanoid robot.  The control problem is formalised as a **Constrained Markov Decision Process (CMDP)**, thereby separating task rewards from safety constraints.  They propose a novel **translation of Control Barrier Function (CBF)** principles into a cost function suitable for the model‑free **Penalized Proximal Policy Optimization (P3O)** algorithm, enabling safety constraint enforcement during training.  Comfort‑oriented rewards, derived from human‑robot interaction (HRI) research, encourage smooth, predictable motions.  The authors demonstrate successful sim‑to‑real transfer on a Unitree G1 humanoid, achieving agile, collision‑free navigation among static and dynamic 3‑D obstacles while maintaining socially acceptable behaviour.

---  

### Introduction & Motivation  
- **Challenge**: Humanoids must navigate human‑centric spaces safely and efficiently, requiring *perception*, *principled safety*, and *social awareness*.  
- **Limitation of prior work**: Blind RL policies (proprioceptive only) cannot handle obstacles; 2‑D depth‑camera based height maps miss non‑ground obstacles (e.g., overhangs, upper bodies).  
- **Need for robust 3‑D perception**: LiDAR provides lighting‑invariant, volumetric data; however, its integration in end‑to‑end locomotion policies is rare.  
- **Safety and comfort**: Reward‑shaping for collisions is brittle; robots must also exhibit *predictable, fluid, non‑threatening* motion for human trust.  

**Contributions (Claim)**  
1. *LiDAR‑driven end‑to‑end policy* that consumes raw point clouds.  
2. *Principled safety framework*: CMDP + CBF‑based cost, trained with P3O.  
3. *Comfort‑oriented reward structure* inspired by proxemics and HRI literature.  
4. *Successful real‑world deployment* on a humanoid robot navigating complex environments.  

---  

### Methods / Approach  
#### A. Network Inputs & Architecture  
- **Actor (policy)**  
  - **Proprioceptive & command history**: last 10 timesteps of joint positions, velocities, accelerations, previous actions, base linear & angular velocities, base gravity vector, base height, and command (vx, vy, yaw).  
  - **LiDAR features**: 64‑dimensional embedding of the raw point cloud (capturing environment geometry).  
  - **Processing**: LiDAR feature history is fed through a Gated Recurrent Unit (GRU) to capture temporal dynamics; the GRU output concatenated with proprioceptive/history vector, then passed through a Multi‑Layer Perceptron (MLP) forming actor and critic networks.  

- **Critic** receives all actor‑inputs **plus privileged simulation information** (exact distance/velocity to nearest obstacle in 8 directions, link contact forces, joint limits, safety margin).  

#### B. Enforcing the Safe State Space via LDCBF Cost  
- **Safe set**: `S_safe = {x | h_D(x)≥0}`; `S_unsafe = {x | h_D(x)<0}`.  
- **Linear Discrete‑time CBF (LDCBF)**  
  - `h_D(s_k) = (p(s_k)−o_k)·η_k + d_margin`  
  - Imposes *minimum distance* `D_min` from each obstacle, using nearest point `o_k` and outward normal `η_k` derived from LiDAR.  
  - For linear dynamics `s_{k+1}=A_L s_k+B_L u_k`, safety constraint `h_D(s_{k+1}) ≥ (1−γ_CBF)h_D(s_k)` becomes linear in control input `u_k`:  
    `G_D(s_k)·u_k + γ_CBF·h_D(s_k) ≤ h_D(s_k)`.  

- **Cost formulation**:  
  `C_D(s_k,a_k) = δ( G_D·u_k + γ_CBF·h_D(s_k) - h_D(s_k) )` (positive if barrier would be violated).  

#### C. Rewards & Costs (Comfort‑oriented)  
| Trait | Formalisation | Weight | Notes |
|---|---|---|---|
| **Task‑Oriented** | `velocity tracking: exp(-α||v_k−v_cmd||²)`, `yaw tracking: exp(-α||ω_k−ω_cmd||²)` | `2.0`, `0.5` | Drive commanded velocities |
| **Auxiliary** | `z‑velocity`, `link torque penalty`, `joint torques/velocities/accelerations`, `action smoothing` | varied negative weights | Keep dynamics and energy under control |
| **Comfort‑Oriented** | **Proxemic Comfort**: `exp(-α(d_human−d_social)²)`, **Safe Approach Velocity**: `-max(0,-v_k·η_k)`, **Safe Approach Accel**: `-max(0,-a_k·η_k)`, **Tangential Avoidance**: `1−max(0, v_hat·(-d_obs_hat))` | `1.5`, `-1.0`, `-1.0`, `1.0` | Penalises approaching normal to obstacles; rewards tangential motion; aligns with research that smooth, tangential avoidance is perceived as comfortable |
| **Safety / Physical Costs** | `C_safe = 1 / (obs_dist < d_safe)`, `C_joint = sum(I_q > q_max)`, `C_self = 1 (link collision)` | hard thresholds `d_safe=0.8 m` | Hard safety constraints, used in P3O penalty |

#### D. Training: P3O  
- Objective: maximize RL clipped advantage while adding penalty for each cost:  

  `L_P3O = L_CLIP_NR(π) − Σ_j κ_j * L_VIOL_NC_j(π)`  
- `L_VIOL_NC_j` uses normalized cost advantage `(J_C_j - μ_C_j)/σ_C_j` clipped with threshold `d_j`.  
- `κ_j` tuned hyper‑parameters controlling penalty magnitude.  

The model‑free P3O algorithm (first‑order, normalized advantages) handles dynamic systems, is stable, and efficiently enforces CMDP constraints.  

---  

### Experiments / Data / Results  

#### A. Experimental Setup  
- **Robot**: Unitree G1 humanoid, Livox Mid‑360 LiDAR.  
- **Simulation**: NVIDIA Isaac Sim; domain randomisation; curriculum increasing obstacle complexity.  

#### B. Ablation Study (P3O‑CBF vs PPO‑RewardShaping vs P3O)  
- **Key findings**  
  - PPO‑RewardShaping fails to avoid obstacles effectively; P3O improves but remains reactive.  
  - P3O‑CBF (full framework) offers **proactive avoidance**: wider turns, consistent safety margin.  
- **Figure 3** (qualitative comparison) illustrates trajectories:  
  - **Orange (P‑RS)** aggressive path, frequent collisions or detours.  
  - **Green (P3O)** better but still close‑to‑obstacle.  
  - **Blue (P3O‑CBF)** smooth avoidance.  
- **Table II (Safety & Comfort Violation Times)**  
  - PPO‑RS: 1.7 s in unsafe zone, 3.4 s in uncomfortable zone.  
  - P3O: 1.2 s unsafe, 3.1 s uncomfortable.  
  - P3O‑CBF: **0.8 s unsafe, 2.2 s uncomfortable** (53% and 34% reductions vs PPO).  

**Claim**: *The CBF‑based cost leads to proactive, higher‑margin navigation that reduces unsafe and uncomfortable time.*  

#### C. Evaluation Scenarios (Table III)  
| Scenario | PPO‑RS | P3O | P3O‑CBF |
|---|---|---|---|
| (a) Suspended obstacle | 20 % | 90 % | 83 % |
| (b) Narrow passage | 0 % | 33 % | 60 % |
| (c) Cluttered static course | 93 % | 100 % | 100 % |
| (d) Dynamic agents | 56 % | 70 % | 86 % |

**Claim**: *P3O‑CBF achieves the highest success rates, especially in narrow passages and dynamic agent scenarios, confirming the importance of the comfort‑oriented reward preventing oscillations and over‑corrections.*  

#### D. Real‑world Tests  
- **Scenario 5**: Robot navigates cluttered lab with static obstacles, demonstrating collision‑free, smooth path.  
- **Scenario 6**: Human suddenly approaches from behind; policy reacts and maintains safe distance.  

**Claim**: *The policy transfers successfully from simulation to a physical Unitree G1 robot, confirming concrete robustness.*  

---  

### Discussion & Analysis  
- The *CBF‑in‑cost* approach extends model‑based safety guarantees to an entirely model‑free RL setting.  
- The *comfort‑oriented rewards* help maintain a **social distance** (`d_social = 1.2 m`) and encourage **tangential avoidance**.  
- The *LiDAR‑driven perception* overcomes limitations of 2‑D depth cameras (lighting, field‑of‑view, invisibility to overhangs).  
- The *P3O* RL algorithm demonstrates effective constraint handling and training stability across complex dynamics of the humanoid robot.  
- The *GRU* processing of LiDAR features captures temporal change in obstacle geometry, improving motion predictability.  
- The usage of *privileged information* (in critic) aids learning without affecting test‑time inference.  

**Limitations & Open Questions**  
- **Limited dynamic models**: LIN‑CBF assumes linear dynamics; for strongly nonlinear robot dynamics, approximation accuracy may degrade.  
- **Scalability to larger state spaces**: 64‑dim LiDAR embedding may not fully capture extremely cluttered environments; future work might integrate deep point‑cloud feature extractors (e.g., PointNet).  
- **Generalization across robot platforms**: Tested on Unitree G1; transferability to other humanoid designs not evaluated.  
- **Human comfort quantification**: Comfort‑reward weights set manually; optimization of these parameters remains open.  

---  

### Conclusions  
The authors present a fully end‑to‑end locomotion policy for humanoid robots that directly consumes raw LiDAR point clouds and outputs joint motor commands, achieving robust, safe, and comfort‑aware navigation.  By formulating safety as a CBF‑inspired cost within a CMDP solved by P3O, and augmenting this with comfort‑oriented rewards, the policy outperforms baseline reward‑shaping and cost‑only variants in both simulated and real‑world tests.  The work bridges a significant gap in RL‑based legged robot navigation, combining lighting‑invariant perception, principled safety, and socially aware motion.

---  

### Key Claims & Contributions  
1. **LiDAR‑direct end‑to‑end policy** for humanoid locomotion.  
2. **Model‑free conversion of Control Barrier Functions to CMDP cost** enabling P3O to enforce safety.  
3. **Comfort‑oriented reward design** encouraging socially acceptable distances and smooth, tangential avoidance.  
4. **Successful sim‑to‑real transfer** on a Unitree G1, achieving agile, safe navigation around static and dynamic obstacles.  

---  

### Definitions & Key Terms  
- **CMDP** – Constrained Markov Decision Process: `(S, A, P, R, {C_j}, {ε_j}, γ_RL)`.  
- **CBF / LDCBF** – Linear Discrete‑time Control Barrier Function; defines safe set via signed distance.  
- **P3O** – Penalised Proximal Policy Optimisation: first‑order constrained RL algorithm handling CMDP.  
- **ICS** – Interactive Comfortable Space (subset of safe states where robot is comfortable w.r.t. human proximity).  
- **Comfort‑oriented reward** – penalties/bonus shaped from proxemics: social distance, safe approach velocity, tangential avoidance.  
- **Cost functions** – hard constraints: distance to obstacles, joint limits, self‑collision.  

---  

### Important Figures & Tables  
- **Fig 1**: Schematic of safe, safe‑comfy, unsafe spaces.  
- **Fig 2**: Training pipeline diagram: LiDAR→GRU→MLP→Actor/Critic.  
- **Fig 3**: Trajectory comparison (P‑RS, P3O, P3O‑CBF).  
- **Fig 4**: Evaluation scenarios: Suspended obstacle, narrow passage, cluttered course, dynamic agents.  
- **Fig 5**: Real‑world cluttered environment test.  
- **Fig 6**: Human approaching; policy avoids.  
- **Table I**: Reward and cost function components with weights.  
- **Table II**: Safety and comfort violation times for three policies.  
- **Table III**: Success rates across scenarios.  

---  

### Limitations & Open Questions  
- Applicability of linear dynamics assumption in LDCBF to highly nonlinear robot dynamics.  
- Scaling of LiDAR embedding dimensionality for more cluttered scenes.  
- Transferability to other robot morphologies.  
- Systematic tuning of comfort‑reward weights.  
- Exploration of dynamic obstacle prediction beyond nearest‑point approach.  

---  

### References to Original Sections  
- **Abstract** – Section “Abstract”.  
- **Introduction & Motivation** – Section I.  
- **Related Work** – Section II.  
- **Definitions** – Section III.  
- **Methods** – Section IV (A‑D).  
- **Experiments** – Section V (A‑D).  
- **Results & Tables** – Tables I‑III in Section V.  
- **Figures** – Figures 1‑6 in Sections III, IV, V.  
- **Conclusion** – Section VI.  

---  

### Executive Summary / Key Takeaways  
1. *LiDAR‑based end‑to‑end locomotion* outperforms blind or 2‑D height-map approaches in complex 3‑D environments.  
2. *CBF‑in‑cost* translation bridges model‑based safety theory with model‑free RL (P3O).  
3. *Comfort‑reward* architecture aligns robot’s motion with human expectations: maximal social distance, tangential avoidance, smooth acceleration.  
4. *Sim‑to‑real transfer* confirmed on a real humanoid, achieving safe navigation among static and dynamic obstacles.  
5. *Performance gains*: 53% reduction in unsafe time, 34% reduction in uncomfortable time; success rates improved from 33% to 60% in narrow passages.  

---  

### Supplementary Material  
- **Project repo**: https://github.com/aCodeDog/SafeHumanoidsPolicy (code and demos).  
- **No additional appendices** were provided.