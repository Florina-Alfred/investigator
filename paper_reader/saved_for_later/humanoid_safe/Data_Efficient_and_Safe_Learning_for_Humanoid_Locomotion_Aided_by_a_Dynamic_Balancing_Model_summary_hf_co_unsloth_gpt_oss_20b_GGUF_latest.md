# Title & Citation  

**“Data‑Efficient and Safe Learning for Humanoid Locomotion Aided by a Dynamic Balancing Model”**  
Junhyeok Ahn, Jaemin Lee, Luis Sentis  
*IEEE Robotics & Automation Letters*, 2020 (accepted 5 Apr 2020).  

---

## Abstract  

The authors propose a novel Markov Decision Process (MDP) that blends an analytical walking‑pattern generator (WPG) with a residual neural footstep policy and a safety controller.  The policy maps a reduced‑order Linear Inverted Pendulum Model (LIPM) state to a desired next‑stance location; a proximal policy optimizer (PPO) learns the residual controller while a Gaussian‑process (GP) learns the dynamics residual, and a control‑barrier function projects each action onto a safe set defined by the capture‑region of the LIPM.  Experiments on a 10–DoF DRACO biped and a 23–DoF ATLAS (DART) show that the hybrid approach learns safe, efficient walking faster than pure end‑to‑end RL or the TVR WPG alone, and generalizes to turning, irregular terrain, and disturbance rejection.

---

## Introduction & Motivation  

*Technical problem*: Traditional analytic WPGs decompose the high‑order humanoid dynamics into a 2–DoF LIPM, enabling efficient pattern generation (e.g., TVR planner) and a whole‑body controller (WBC) for torques.  However, the low‑order model introduces model mismatch that degrades footstep tracking and requires aggressive tuning.  Pure data‑driven RL learns joint torques directly from sensors, but it is sample‑inefficient, often produces jerky motions, and may visit unstable states.  

*Goal*: Combine the model‑useful structure of analytic planners with the expressive power of neural networks, while guaranteeing safety through a learned GP model and a control‑barrier safety projection.  

*Key contribution*: A **structured footstep policy** comprising three components – (i) a TVR analytic guidance, (ii) a stochastic neural layer, (iii) a safety projection – that is trained by PPO under a rigorously defined reward and safety set.

---

## Methods / Approach  

### 1. Analytical Foundations  

- **LIPM Dynamics**:  
  \[
  \dot{x}=A\,x,\quad
  A=
  \begin{bmatrix}
   0 & 0 & 1 & 0 \\
   0 & 0 & 0 & 1 \\
   g/h & 0 & 0 & 0 \\
   0 & g/h & 0 & 0
  \end{bmatrix}
  \]  
  with constant CoM height \(h\) and gravity \(g\).  
- **Time‑to‑Velocity‑Reversal (TVR) Planner**: Computes next‑stance \(a_k\) such that the sagittal and lateral CoM velocity are driven to zero after specified times \(T_{x'},T_{y'}\).  The solution uses hyperbolic cosine/sine functions \(C_1(t)=\cosh(\omega t),\; C_2(t)=\sinh(\omega t)/\omega\) with \(\omega=\sqrt{g/h}\).  
- **Whole‑Body Controller (WBC)**: A sensor‑based feedback controller that produces joint torques to track the CoM trajectory produced by the WPG and the desired next‑stance.

### 2. MDP Formulation  

| Sym. | Meaning | Formula |
|-------|---------|----------|
| \(S_k\) | State at Apex moment \(k\) | \((x_{k,a},p_{k,a},\phi_{bs,k,a},w_{bs,k,a},\phi_{pv,k,a})\) |
| \(A_k\) | Action (desired next‑stance) | \(a_k \in \mathbb R^2\) |
| \(T(S_k,A_k)=S_{k+1}\) | Deterministic state transition (control‑affine: \(S_{k+1}=f(S_k)+g(S_k)A_k+ d(S_k)\)) |
| \(r(S_k,A_k)\) | Reward: a sum of living bonus, uprightness penalty, CoM‑position, velocity, and actuation penalty. |

The unknown function \(d(S_k)\) captures the gap between the LIPM prediction and the true dynamics – it is learned online by a GP.

### 3. Structured Policy  

The final action is composed as  

\[
a_k = a_{\text{TVR},k}+ a_{\theta,k} + a_{\text{SF},k} \tag{16}
\]

* **\(a_{\text{TVR},k}\)** – analytic guidance from the TVR planner (substituted in Eq. (5) to produce the footstep that would bring the CoM velocity to zero).  
* **\(a_{\theta,k}\)** – residual feed‑forward action sampled from a neural network \(\mathcal N_{\theta}\) parameterised by weight vector \(\theta\).  \(\theta\) is updated by PPO.  
* **\(a_{\text{SF},k}\)** – safety compensation; a quadratic‑program (QP) that projects the combined action onto the safe set \(C\) derived from the *capture‑region* of the LIPM (Eq. 13/14).  

### 4. Safety Projection  

- **Capture‑Region**: one‑step and two‑step capture regions derived from the LIPM state:
  \[
  \kappa^\pm(u,p)=\pm h\left(\frac{T_{\text{LF}}}{\tanh(T_{\text{LF}}\omega) -\frac{T_{k,a}^{\prime}}{\tanh(T_{k,a}^{\prime}\omega)}\right)
  \]  
  (Eq. 13).  
- **Safe Set \(C\)**: All pairs \((x,p)\) lying inside the approximated polytope of the capture‑region.  
- **QP**: Minimises \(\|a_{\text{SF},k}\|^2\) subject to the safety constraint (18) and control limits (Eq. 16). The solution is quadratic thanks to linear safety constraints in state‑space.  

### 5. Reinforcement‑Learning Loop  

1.  Initialise policy network \(\pi_{\theta}\).  
2.  For each Episode:  
   *   For each Sample:  
     - Sample \(a_{\theta,k}\sim \pi_{\theta}\).  
     - Compute \(a_{\text{TVR},k}\).  
     - Solve QP to get \(a_{\text{SF},k}\).  
     - Feed combined action \(a_k\) to the WBC to achieve next Apex moment.  
     - Store transition \((S_k,a_k,S_{k+1},r_k)\).  
3.  Update policy using PPO loss (Eq. 15).  
4.  Update GP with all collected samples.  

This corresponds to Algorithm 1 in the paper.

---

## Experiments / Data / Results  

| Platform | Robot | Simulation | MDP Variants | Baselines | Evaluation Metrics |
|----------|-------|------------|--------------|------------|--------------------|
| DRACO | 10–DoF | DART | (8 MDPs over 10 FPS) |  End‑to‑end (joint state), End‑to‑end (LIPM), DeepLoco, TVR only, Our MDP (conservative vs relaxed capture sets, with/without TVR) | Average return, episode terminations, stride, speed, 2‑norm ZMP |

### Forward Walking (Main Result)  

- The *conservative one‑step capture* MDP achieved higher returns than baselines early on but suffered slower walking due to tight strides.  
- The *relaxed two‑step capture* MDP (orange curve) eventually reached the best average return, matching or exceeding the DeepLoco (purple) curves while using **five times** less data.  
- Removing the TVR guidance (pink curve) yielded negligible improvement, confirming the necessity of analytic guidance.  
- The safety projection that does not use TVR (red curve) performed poorly, highlighting the need for a composed “lift‑plus‑offset” exploration (Section IV‑C).  

**Claim 1**: *Structured footstep policy with TVR and safety projection outperforms pure end‑to‑end RL or TVR alone, achieving higher returns with far fewer samples.*   (Fig. 6, Table I).

### Generalization Tests  

Three extended scenarios: turning, irregular terrain, and random disturbances.  

- Policies trained on the same MDP but with high‑variance disturbances (± 600 N) still walked successfully.  The CoM velocity returned to near zero after disturbances in symmetric scans.  
- Turning demonstrated that the gait planner could handle non‑zero base yaw without extra reward terms.  
- Irregular terrain (± 10°) produced slightly longer strides but the agent maintained uprightness by adjusting footstep locations.

**Claim 2**: *The learned policy generalizes to non‑standard configurations (turning, slopes, jitters) without retraining, because of the physics‑based guidance.*  (Fig. 7a‑b).

### Robustness against Unexpected Disturbances  

Specific tests measured CoM velocity under three disturbance patterns (see Section V‑B).  The WBC combined with the policy corrected the speed quickly after a `+600 N` swing‑phase disturbance but could not recover from a `+600 N` landing‑phase disturbance (resulting in a fall).  

**Limitations Highlighted**:  
- The LIPM model fails to capture high-frequency dynamics, limiting disturbance rejection when it occurs after the Apex.  
- No real‑world validation yet; all results are in DART simulation.  

---

## Discussion & Analysis  

- **Model versus data**: The analytic TVR component drastically reduces exploration space, while the GP step ensures safety with low sample overhead.  The synergy between model guidance (TVR) and data‑driven residual (NN) results in stable, efficient learning.  
- **Safety projection**: The QP guarantees that any step is chosen within the *capture set*, thus preventing falls.  This rigoury avoids the typical “curriculum learning” fallback of RL.  
- **Training Efficiency**: Because actions are states of a 10‑dimensional LIPM, the policy space is far smaller than joint‑torque space; hence PPO converges 5× faster than baseline RL methods.  
- **Scalability**: Experiments on two distinct robots (DRACO vs ATLAS) demonstrate that the same MDP formulation can be scaled by only changing numeric constants (e.g., \(h,\;T_{x′}\)).  

---

## Conclusions  

The paper presents a *structured, data‑efficient, and safe* method for humanoid walking that stitches analytical planning (TVR) and whole‑body control (WBC) with residual neural learning and GP‑based safety.  Empirical results demonstrate:  
1. Fast convergence to stable walking.  
2. Superior performance over end‑to‑end and pure analytic baselines.  
3. Generalization to turning, irregular terrains, and force disturbances.  

The authors plan to transfer the method to a real DRACO biped in future work.

---

## Key Claims & Contributions  

| # | Claim | Evidence |
|---|--------|----------|
| 1 | Structured policy architecture (TVR+NN+Safety) yields higher returns than pure RL or TVR alone | Fig. 6, Table I |
| 2 | GP‑based safety projection guarantees staying inside capture set while allowing exploration | Alg. 1, QP (18) |
| 3 | System scales to multiple humanoids (DRACO, ATLAS) with only parameter changes | Section V, simulations |
| 4 | Policy generalizes to turning, irregular terrain, and disturbances | Fig. 7a‑b |
| 5 | Learning requires five times fewer samples than DeepLoco while learning faster | Fig. 6 |

---

## Definitions & Key Terms  

- **LIPM (Linear Inverted Pendulum Model)** – 2‑DoF model describing CoM dynamics at constant height.  
- **TVR Planner** – Time‑To‑Velocity‑Reversal; analytic footstep planner that zeros CoM velocity after predetermined times.  
- **WBC (Whole‑Body Controller)** – low‑level feedback controller that maps desired trajectories to joint torques.  
- **WPG (Walking Pattern Generator)** – high‑level footstep planner (e.g., TVR).  
- **MDP (Markov Decision Process)** – formal model of states, actions, transition, and reward for RL.  
- **PPO (Proximal Policy Optimization)** – policy gradient algorithm that keeps updates within a trust‑region.  
- **GP (Gaussian Process)** – non‑parametric model for unknown dynamics residuals and its uncertainty estimate.  
- **Control‑Barrier Function** – safety constraint that keeps state inside safe set \(C\).  
- **Capturability** – property that the robot can stop its CoM using a finite number of steps; used to compute capture regions.  

---

## Important Figures & Tables  

| Fig. | Title | Content |
|-------|-------|----------|
| 1 | Controller structure | (a) analytic WPG+WBC, (b) end‑to‑end NN, (c) proposed WPG+NN+Safety |
| 2 | State machine + LIPM abstraction | Shows apex/switching moments; mapping to LIPM state |
| 3 | (a) Safety‑guaranteeing policy schematic | (b) Projection of capture regions onto x‑ẋ plane |
| 4 | Safety compensation illustration | Demonstrates why TVR guidance keeps additional exploration volume |
| 5 | MDP variations | Eight configurations of state/action layout for forward walking |
| 6 | Learning curves | Average return, terminations, stride, speed, ZMP |
| 7 | Generalisation results | (a) return curves, (b) CoM velocities under disturbances |
| Table I | Simulation parameters | Values for LIPM, SM, a_TVR, safety limits, rewards for DRACO & ATLAS |

---

## Limitations & Open Questions  

1. **Model fidelity** – LIPM neglects limb dynamics and angular momentum, leading to residual errors that GP must capture with sufficient data.  
2. **Disturbance Sensing** – Disturbances after the Apex (landing or swing‑phase) are not fully recoverable; future work suggested adding a disturbance observer.  
3. **Real‑world Dev** – Only simulations are present; transfer to hardware may reveal sensor noise or actuator limits.  
4. **Scalability to more complex tasks** – Such as uneven terrain height or multi‑contact shifts require further extensions of the capture region.  

---

## References to Original Sections (if available)  

- Methodology: § II‑B (TVR equations), § III (MDP formalization), § IV (policy representation & safety).  
- Experiments: § V (forward walking); Fig. 5 (MDP variants).  
- Generalization: § V‑B, Fig. 7.  
- Conclusion: § VI.  

---

**Executive Summary (optional)**  

- Combine LIPM‑based TVR planner and whole‑body control with a residual neural policy.  
- Enforce safety via GP‑learned safety projection onto capture‑region.  
- Learn with PPO, obtaining stable walking 5× faster than end‑to‑end baselines.  
- Works on two distinct humanoids, generalises to turning, slopes, and disturbances.  

---