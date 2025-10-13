**Title & Citation**  
*Cloud-Based Scheduling Mechanism for Scalable and Resource‑Efficient Centralized Controllers* – Achilleas Santi Seisa, Sumeet Gajanan Satpute, George Nikolakopoulos (2024, conference/journal not specified).

---

## Abstract  
The paper proposes a Kubernetes‑based scheduling framework that monitors and triggers updates for Centralized Non‑Linear Model Predictive Controllers (CNMPCs) in multi‑UAV systems. By creating CNMPC deployments on worker nodes that match the controllers’ CPU‑memory demands, the framework off‑loads the heavy computation of NMPC from the robots themselves. Experiments conducted in Ericsson’s real‑time cloud show that the mechanism keeps resource utilisation bounded as the number of agents grows, and that timing delays for the closed‑loop controller remain within acceptable limits when the number of robots varies. The work is positioned as the first cloud architecture that allows robots to join or leave a mission without pre‑defining the total number of agents, thus alleviating the well‑known scalability bottleneck of centralized NMPC.

---

## Introduction & Motivation  
*Background:* Cloud robotics has gained traction mainly for vision, learning, and SLAM. Classical trajectory‑tracking with embedded collision avoidance (NMPC) remains computationally demanding and has not been widely deployed on the cloud.  

*Gap:* Existing cloud‑robotic platforms (e.g., KubeROS [10]) require all robots to be inside the cluster; they have no policy to dynamically launch new CNMPC instances when the agent count changes.  

*Objective:* Provide a fully dynamic scheduler that can detect changes in `agent_d_num` (the desired number of cloud‑controlled agents), automatically calculate the necessary number of CNMPC instances (`CNMPC_num`), and launch / delete Kubernetes pods accordingly. The goal is to keep each CNMPC’s resource consumption within a narrow CPU‑memory band while leaving the robots able to join or leave a mission on‑the‑fly.

---

## Methods / Approach  

### Mission Planner  
Publishes the desired agent count and high‑level mission commands (take‑off, safety‑land). Also sends the reference trajectories `x_ref_i` for every UAV.  

### Scheduler (Core component)  
*Receives* `agent_d_num`, `CNMPC_args`.  
*Creates* deployments and services for each CNMPC, ensuring load balancing and redundancy (replicas).  
*Algorithm 1* (pseudo‑code supplied) – determines `CNMPC_num = ceil((agent_d_num‑1)/agent_max+1)` (where `agent_max` is the empirically determined maximum UAVs a single CNMPC can manage).  
If `agent_d_num` decreases, it deletes unused deployments/services.  
If it increases, it computes how many agents each new CNMPC must control (`agent_CNMPC`, `agent_float_CNMPC`) and updates the deployments accordingly.  

### Resource Allocation  
Unlike generic rule‑based schedulers, the authors derived formulas (Eq. (1) & (2)) that map `N` (prediction horizon), `N_a` (number of agents), and `CNMPC_args` to expected CPU and memory usage.  
For each CNMPC the scheduler sets CPU and memory limits `[CPU_d_min, CPU_d_max]`, `[M_d_min, M_d_max]`.  
It also defines absolute min/max usage per pod `CPU_n_min,…`.  
These bounds are based on empirical measurements of execution time for different MPC configurations.  

### ROS / Proxy Tunnel  
All pods join the same Kubernetes network; a dedicated ROS master pod runs on the cluster.  
Communication to the physical or simulated UAVs goes through a UDP‑proxy server. Each UAV runs a client that converts ROS messages into byte arrays; the proxy server interpolates them back into ROS messages for the cluster.  
Because CNMPCs are stateful, this design ensures all pods share the same ROS topic namespace.

### Centralized Non‑Linear MPC  
1. **UAV Model:** 6‑DOF fixed‑body; state variables `[p,q]`, mass `m`, rotation `R_i`, gravity `g`, drag `A`.  
Control vector `u_i = [roll, pitch, thrust]` appears as `F_i(t‑τ)`.  
Latency `τ = d₁+d₂` is explicitly modelled in the prediction.  
2. **State Estimator:** Estimating `[p, v]` at time `t‑τ`.  
3. **MPC Problem:** Minimize cost  
```
J = Σ_n (x_n⁻¹ Q_x x_n + Δu_n⁻¹ Q_δu Δu_n + u_n⁻¹ Q_u u_n)
```  
subject to system dynamics and collision‑avoidance constraints  
`dist(p_i,p_j) ≥ r_safe`.  
4. **Solver:** PANOC (Proximal Averaged Newton‑type) with N iterations (“Eq. (8)”). Performance guarantees from [21].  

---

## Experiments / Data / Results  

### Setup  
*Cloud:* Ericsson Research real‑time cloud (OpenStack).  
*Kubernetes cluster:* 1 master, 3 workers.  
- Master: 3‑core CPU, 2 GB RAM.  
- Worker 1: 32‑core, 460 GB.  
- Worker 2: 16‑core, 32 GB.  
- Worker 3: 4‑core, 8 GB.  
*Simulator:* One external VM (32‑core, 480 GB) runs a ROS/Gazebo simulation of multiple quadrotors (ROS package [24]).

| Node | CPU | RAM | OS |
|------|-----|-----|----|
| Master | 3 | 2 GB | Ubuntu 20.04.6 |
| Worker 1 | 32 | 460 GB | Ubuntu 20.04.6 |
| Worker 2 | 16 | 32 GB | Ubuntu 20.04.6 |
| Worker 3 | 4 | 8 GB | Ubuntu 20.04.6 |
| Simulator | 32 | 480 GB | Ubuntu 20.04.6 |

`Fig. 4` shows the cluster snapshot. CNMPC pods are created at demand and placed on workers 1 and 2; Worker 3 hosts Mission Planner, Scheduler, and the UDP tunnel.

### Resource Utilisation Test  
- 50 trials with varying `agent_d_num` between 1 and 25.  
- **Fig. 5 (left):** Without scheduler – CPU utilisation explodes as more agents are added (10 agents require 5 on CNMPC 1 + 5 on CNMPC 2).  
- **Fig. 5 (right):** With scheduler – utilisation remains within a narrow band; pods are migrated when a new CNMPC is launched, preventing any single pod from overloading.  

### Tracking Error & Agent Migrations  
- **Fig. 6** depicts ten UAVs.  
  * At t = 0 a CNMPC 1 manages 4 UAVs.  
  * t = 65 s: 3 new UAVs join → Scheduler launches CNMPC 1′ (new pod) → all 7 UAVs migrate.  
  * t = 125 s: 3 further UAVs join → Scheduler creates CNMPC 1′′ and CNMPC 2. UAV 6 & 7 shift to CNMPC 2; a brief increase in tracking error is observable due to their new set‑point far from current position.  

### Delay & Processing Time  
- Round‑trip time `τ_rrt = τ_u + τ_d + τ_p`.  
- `τ_p` (processing time) is averaged over a sliding window [25].  
- **Fig. 7** shows CPU utilization vs `τ_p`.  
  * CPU < blue band → `τ_p` stays below 10 ms.  
  * Exceeding band → `τ_p` rises sharply.  

The scheduler’s dynamic pod creation keeps CPU below the threshold, thus guaranteeing `τ_rrt` remains within bounds independent of agent count.

---

## Discussion & Analysis  

- **Scalability:** By deriving `CNMPC_num` on‑the‑fly from `agent_d_num`, the design breaks the “pre‑defined number of agents” limitation seen in [14] and [10].  
- **Dynamic Resource Mapping:** The empirically derived formulas (Eqs. 1–2) allow the scheduler to give each CNMPC the exact CPU & memory range needed. This is more precise than typical rule‑based schedulers (e.g., [26]) that only use static thresholds.  
- **High‑throughput Communication:** A UDP proxy removes the ROS network bottleneck on the edge while the cluster’s shared network guarantees synchronous ROS topics across pods.  
- **Robustness:** Replicas of CNMPC pods ensure controllers stay online if a pod crashes.  
- **Cost‑effectiveness:** All heavy computations stay on the cluster; UAVs only run lightweight odometry and actuator commands.  
- **Limitations Discussed:** Experiments were purely simulated; real‐world wireless latency, environmental disturbances, and hardware limits were not tested.

---

## Conclusions & Future Work  

The authors presented an end‑to‑end scheduler that, using Kubernetes, automatically scales CNMPC deployments as the number of UAVs changes. Experiments prove that the mechanism keeps CPU utilisation, processing time, and communication delays within acceptable limits even as the agent count grows.  
Future directions include:  
- Deploying the framework on civil UAVs in real environments.  
- Extending the scheduler to distributed NMPC settings or other robot types.  
- Investigating more advanced optimisation (e.g., learning‑based prediction of resource use).

---

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
|1. A scheduling algorithm (Algorithm 1) can dynamically compute the number of CNMPCs needed for any `agent_d_num`. | Algorithm pseudo‑code & explanation. |
|2. Empirical formulas (Eqs. (1)–(2)) map MPC configuration to CPU/memory bounds, enabling precise pod sizing. | Figures 5 & 7 showing bounded utilisation. |
|3. The framework leaves robots in the field; they can join/leave missions without re‑configuring the cluster. | Fig. 6: UAVs migrating to new CNMPC pods. |
|4. Communication delays (uplink/downlink) remain bounded regardless of agent count. | Fig. 5 & 7; mention τ_rrt. |
|5. The system outperforms a baseline without scheduling for resource utilisation. | Fig. 5 (left vs right). |

---

## Definitions & Key Terms  

- **CNMPC** – Centralized Non‑Linear Model Predictive Controller.  
- **Kubernetes** – Container orchestration system used to deploy and manage CNMPC pods.  
- **KubeROS** – Earlier platform for deploying ROS2 on Kubernetes.  
- **Proxy Server** – UDP tunnel that translates between ROS messages and byte arrays for communication between VMs and cluster.  
- **Agent_d_num** – Desired number of cloud‑controlled robots.  
- **agent_max** – Empirically determined maximum number of agents a single CNMPC can manage.  
- **τ₁, τ₂** – Uplink and downlink delays.  
- **PANOC** – Proximal Averaged Newton‑type optimisation method used to solve the MPC.  
- **r_safe** – Minimum separation distance enforced by collision‑avoidance constraints.  

---

## Important Figures & Tables  

- **Fig. 1** – High‑level overview of the cloud framework.  
- **Fig. 2** – Block diagram (Mission Planner → Scheduler → CNMPCs ↔ UDP Proxy ↔ Robots).  
- **Fig. 3** – System diagram showing the real‑time cloud and simulator VM.  
- **Fig. 4** – Cluster snapshot (k8s nodes + simulator).  
- **Fig. 5** – CPU utilisation with/without scheduler.  
- **Fig. 6** – Tracking error during CNMPC migrations.  
- **Fig. 7** – CPU vs Processing time (τ_p).  
- **Table I** – Cluster & simulator specifications.  

---

## Limitations & Open Questions  

1. **Simulation‑only** – No physical UAV experiments were performed; real Wi‑Fi/5G latencies, packet loss, or UAV dynamics might affect results.  
2. **Single Platform** – Only Ericsson’s OpenStack‑based real‑time cloud was used; performance on other cloud providers (AWS, GCP) remains unproven.  
3. **MPC Configuration Sensitivity** – The formulas for resource mapping were derived empirically for a particular NMPC (prediction horizon, solver iterations); generalising to other NMPC variants may need re‑calibration.  
4. **UDP Proxy Overheads** – UDP is unordered; potential message loss is not addressed; future work might integrate ACK or use ROS 2 over DDS.  
5. **Security & Isolation** – Pods share the same network; the paper does not discuss isolation of sensitive control data.

---

## References to Original Sections  

- *Details of Fig. 1* – Section I (Introduction).  
- *Algorithm 1 description* – Section II‑B.  
- *Resource allocation formulas* – Section II‑C.  
- *Data flow description* – Section II‑D.  
- *CNMPC UAV model* – Section II‑D1.  
- *Solver choice* – Section II‑D1.  
- *Experimental setup* – Section III.  
- *Table I* – Section III (paragraph after Fig. 4).  
- *Figures 5, 6, 7* – Section III.  

---

## Executive Summary (Key Takeaways)  

1. A Kubernetes scheduler can **dynamically deploy/terminate** CNMPC pods based on the real‑time number of UAVs.  
2. Using **empirical CPU/memory bounds** (Eqs. (1–2)) the scheduler gives each CNMPC exactly the resources it needs, keeping CPU utilisation within a tight band.  
3. A **UDP‑proxy server** keeps ROS messages flowing between VMs and cluster with low, bounded delay.  
4. Experiments show that despite adding up to 25 UAVs, processing time remains stable (≤ 10 ms) and tracking error is acceptable even when UAVs migrate between CNMPCs.  
5. The approach eliminates the requirement to pre‑define the total number of agents and thus offers a practical solution for large‑scale cloud‑controlled robotic fleets.

---