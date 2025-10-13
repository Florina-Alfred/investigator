# Title & Citation
**Title:**  
*A generic approach for reactive stateful mitigation of application failures in distributed robotics systems deployed with Kubernetes*  

**Authors:** Florian Mirus, Frederik Pasch, Nikhil Singhal, & Kay-Ulrich Scholl (Intel Labs, Karlsruhe, Germany)  

**Citation:** Mirus, F.; Pasch, F.; Singhal, N.; Scholl, K.-U. (2024). “A generic approach for reactive stateful mitigation of application failures in distributed robotics systems deployed with Kubernetes.” *IEEE 41st International Conference on Robotics and Automation (ICRA)*, 2024, pp. 6791‑6797.  

---  

## Abstract  
The authors present an application‑agnostic, reactive mitigation framework for distributed ROS2‑based robotic workloads running on Kubernetes (K8s).  Using Behavior Trees (BTs) they monitor introspectively (topic frequencies, diagnostics) and externally (camera‑based pose tracking) to detect failures of application containers.  Four recovery strategies are defined (re‑start from scratch, fallback pod in various initialization states), all of which preserve the *last healthy state* of the failed workload via coordinated state transfer.  The framework is evaluated on two distinct workloads – autonomous mobile robot navigation (Nav2) and robotic arm manipulation (MoveIt2) – running on a Turtlebot 4 and WidowX‑200 over the Gazebo simulator.  Experiments quantify recovery time, CPU overhead, and down‑time trade‑offs, demonstrating the method’s effectiveness and generic applicability to arbitrary ROS2 applications.  

---  

## Introduction & Motivation  

- **Research Gap:** While cloud edge‑offloading is common for resource‑intensive robotics tasks (e.g., perception, grasp planning), failure‑m mitigation in *cloud‑native* robotic systems remains under‑explored. Existing works [1]–[2] address network failures but not application‑level faults in distributed ROS2 workloads.  

- **Key Challenges:**  
  1. Robots interact with a *physical* real‑time environment; stateful failure recovery must preserve dynamic robot state (positions, sensor data).  
  2. Failures can occur at *compute node*, *network*, or *container* levels.  
  3. Existing cloud‑native mitigation (e.g., patching, re‑start) lacks “last healthy state” preservation.  

- **Goal:** Build a *reactive* failure mitigation system that:  
  * is agnostic to application type,  
  * uses introspection + external supervision for failure detection,  
  * preserves the last healthy state, and  
  * is implemented with pure Kubernetes & ROS2 primitives (no code changes).  

---  

## Methods / Approach  

### 1. Overview (Fig. 1)

- **Monitoring Component** – observes ROS2 topics and external sensors, reports a *critical failure*.  
- **Failure Mitigation Component** – executes a user‑defined *BT* that dictates:  
  * how to restart / patch the application,  
  * how to transfer state,  
  * when to resume the task (task‑proxy).  

Both components form a *monitor‑mitigation loop* that runs alongside the application.  

### 2. Decision Taxonomy (Fig. 2)

- **Factors** used to weight the choice of monitoring & mitigation strategy: safety, availability, resource usage, task criticality, etc.  
- This taxonomy allows a *customizable* “trade‑off” per deployment.  

### 3. Monitoring System  

**A. Introspective Monitoring**  
- Implements the *topic‑frequency* monitors from Jiang et al. [20].  
- Uses a *hierarchical* tree of monitors (BT) that depends on *current task* (e.g., mobile base velocity vs. joint‑state).  
- Example BT visualised in *Fig. 4*.  

**B. External Supervision**  
- Unique to *Cyber‑Physical Systems*: sensor (cameras, LIDAR) → pose detection → predicted base velocity; compare against actual velocity.   
- If discrepancy > predefined threshold → “critical failure”.  

### 4. Failure Mitigation Strategies (Fig. 5)

| Strategy | Cluster‑level Actions | Application‑level Actions | Time / Resource Trade‑off |
|----------|-----------------------|---------------------------|---------------------------|
| **Restart‑from‑scratch** | Restart K8s pod | Re‑start application | Long `t_cluster` (≈ 32 × slower) ; lowest CPU |
| **Fallback‑uninitialized** | Patch NetworkPolicies to route to fallback pod | Start fallback pod (no pre‑init) | Shorter `t_cluster` (`≈ 2.9 s`); moderate CPU |
| **Fallback‑partial‑init** | – | Start fallback pod; load pre‑init state | Intermediate time |
| **Fallback‑full‑init** | – | Run fallback pod in *execution mode* | Zero start‑up, fastest recovery; highest CPU (≈ +100 % of main pod) |

> **Claim**: *Restart‑from‑scratch* has the shortest cluster‑restart time, but highest down‑time and lower resource usage.  
> **Evidence**: Fig. 6 (green bars) show 32× longer `t_cluster` for restart‑from‑scratch vs. 0.1 s for fallback.

### 5. State Recovery  

- State transfer is encoded inside the mitigation BT.  
- Supports *complex dependencies*: if the failing workload depends on another healthy pod, it may also need recovery.  
- Implementation relies on off‑the‑shelf Kubernetes primitives (Deployments, NetworkPolicies).  

### 6. Implementation Details  

- **BT Execution** via *Scenario Execution for Robotics* (ScenarioExec, ScenarioExec 2024).  
- **OpenSCENARIO 2** (ASAM) used for BT description.  
- **Py‑trees** library translates OpenSCENARIO BTs to Python BTs that run at runtime.  
- A *task‑proxy* keeps the original task request active across re‑initialisations.  

---  

## Experiments / Data / Results  

### 1. Experimental Setup  

| Item | Description |
|------|-------------|
| **Hardware** | Turtlebot 4, WidowX‑200 |
| **Simulation** | Gazebo 27/28 |
| **Workloads** | Nav2 31/32 (mobile navigation), MoveIt2 33/34 (arm manipulation) |
| **Failure Injection** | Delete the pod of the main workload after user‑def. `t_failure` |
| **Monitors** | Topic frequency (base velocity, joint states) |
| **External** | Camera + ArUco markers (for Nav2) |
| **Metrics** | `t_recovery` (sum of 4 components per Eq. 1), CPU usage `γ(c,t)` (CAdvisor), average CPU `σ(CPU)` (Eq. 2) |

**Equation 1**: `t_recovery = t_detection + t_cluster + t_startup + t_reinitialization`  
**Equation 2**: `σ(CPU) = Σ_c σ(c)`  

### 2. Recovery Strategies Evaluation (Fig. 6, 7, 8)  

#### A. AMR Navigation  

- **Results** (Fig. 6)  
  * `t_detection` set to 500 ms for all strategies.  
  * **Restart‑from‑scratch**: `t_cluster ≈ 32 ×` longer than fallback (approx 2.9 s vs. 0.1 s).  
  * **Full‑init fallback**: `t_startup = 0` (already running).  
  * `t_reinitialization` decreases linearly with greater fallback init level.  

- **CPU Usage** (Fig. 7)  
  * Restart‑from‑scratch consumes ~10 % CPU (main pod only).  
  * Fallback-uninitialized adds ~60 % of main pod’s CPU.  
  * Full‑init fallback duplicates CPU of main pod (≈ +100 % extra).  

#### B. Manipulation  

- Similar trend; only restart‑from‑scratch, partial‑init, and full‑init used (no “uninitialized” because fully built).  
- Relative timings in Fig. 8 match navigation results (restart fastest → full‑init fastest).  

### 3. Scaling Considerations (Sec. IV‑C)  

- Modeled expected down‑time `t_S` for a fleet of `N` robots.  
- Probability of more failures than fallback instances within a window of length `t_S` derived as a binomial sum.  
- **Example**: `N=1000`, `failure rate=1/h = 1000/h`.  
  * In 30‑s window, ~8.3 failures expected.  
  * With 4 fallback instances (full‑init), remaining ~5 failures in a 6‑s window → down‑time probability of 1.2 %.  
  * Adding a 10× fallback for all robots doubles CPU but halves down‑time probability.  

- **Claim:** “An uninitialized fallback workload in parallel provides a good balance between down‑time and resource usage.”  
  * **Evidence:** CPU numbers in Fig. 7 and probability calculation above.  

---  

## Discussion & Analysis  

- **State Preservation**: The approach reliably restores “last healthy state,” enabling tasks to resume where the failure occurred – critical for real‑time robotics.  
- **BT Flexibility**: By encoding monitoring and mitigation as BTs, arbitrary application behaviors can be modeled without source modifications.  
- **Trade‑off**: Four strategies allow users to choose between *down‑time* (restart‑from‑scratch) and *resource* (full‑init) according to fleet requirements.  
- **Limitations**:  
  1. Current implementation assumes workload runs in a single container – micro‑service–level workloads (e.g., Nav2 has multiple nodes) need extra dependency modeling.  
  2. Only *predetermined* monitoring vectors considered – safety‑centric monitoring not yet implemented.  
  3. The framework is untested on real robots with network jitter/packet loss.  

---  

## Conclusions  

The paper proposes a *generic, reactive, stateful failure mitigation* framework for distributed ROS2 applications running on Kubernetes.  The main novelty lies in preserving the last healthy state, integrating introspective and external supervision, and delivering a Behavior‑Tree based, application‑agnostic mitigation policy that trades off downtime against computational overhead.  Experiments on Nav2 and MoveIt2 confirm the framework’s effectiveness and genericness.  

---  

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
| 1. **Stateful recovery** is possible without application code changes. | End‑to‑end transfer of state via BT defined in Sec. III‑C; experiments show tasks resume exactly after failures. |
| 2. **Four recovery strategies** provide a clear trade‑off. | Fig. 5 visualizes steps; Fig. 6, 7, 8 quantify time and CPU. |
| 3. **Behavior Trees** enable arbitrary monitoring/mitigation logic. | Fig. 4 demonstrates a BT; BTs are used in all four components. |
| 4. **External supervision** complements introspection. | Monitoring via ArUco trajectories; discrepancy triggers failure in Nav2 example. |
| 5. **Generic to any ROS2 workload**. | Same framework applied to Nav2 (navigation) and MoveIt2 (manipulation). |

---  

## Definitions & Key Terms  

| Term | Definition |
|------|-------------|
| **Robot Operating System (ROS2)** | Next‑generation robotics middleware providing publish/subscribe, services, actions, and real‑time capabilities. |
| **Kubernetes (K8s)** | Open‑source container orchestration system used to deploy, scale, and manage ROS2 nodes. |
| **Nav2** | ROS2 navigation stack (localisation, global planner, local planner, controller). |
| **MoveIt2** | ROS2 robotic manipulation motion‑planning framework (kinematics, collision‑checking). |
| **Behavior Tree (BT)** | Hierarchical decision logic (selector, sequence, condition, action nodes). |
| **Fallback pod** | Secondary pod that can be swapped in when main pod fails. |
| **External supervision** | Monitoring by observing robot behavior from external sensors (camera, LIDAR). |
| **\(t_\text{recovery}\)** | Sum of detection, cluster, startup, and re‑initialisation times (Eq. 1). |
| **\(σ(\mathrm{CPU})\)** | Mean CPU consumption across all pods (Eq. 2). |
| **\(N\)** | Number of robots in the fleet. |
| **\(t_S\)** | Downtime per failure for selected strategy. |

---  

## Important Figures & Tables  

- **Fig. 1** – System overview (monitor → failure mitigation → BT).  
- **Fig. 2** – Weight matrix for selecting monitoring/mitigation strategy.  
- **Fig. 3** – Detailed system architecture (pods, services, tasks).  
- **Fig. 4** – Example BT for basic failure mitigation.  
- **Fig. 5** – Flow for the four strategies, trade‑off illustration.  
- **Fig. 6** – Recovery time breakdown per strategy (Nav2).  
- **Fig. 7** – CPU usage per strategy (Nav2).  
- **Fig. 8** – Performance summary (Nav2).  

---  

## Limitations & Open Questions  

1. **Micro‑service Splitting** – Each ROS2-Process (e.g., `tf2_ros`, `nav2_planner`) could run in its own pod; current approach works on single-pod workloads.  
2. **Safety‑centric Monitoring** – Extending to handle safety‑threshold violations (e.g., collision risk).  
3. **Real‑world Testing** – Only simulation; unknown performance with network jitter on edge devices.  
4. **State Transfer Granularity** – Currently only last‑known “state” (e.g., poses) is passed; complex nested states need further work.  

---  

## References to Original Sections (if available)  

- **Introduction** – Sec. I  
- **Stateful Failure Mitigation** – Sec. III  
- **Monitoring System** – Sec. III‑A  
- **Failure Mitigation** – Sec. III‑B  
- **State Recovery** – Sec. III‑C  
- **Implementation Details** – Sec. III‑D  
- **Experiments** – Sec. IV‑A  
- **Evaluation of Recovery Strategies** – Sec. IV‑B  
- **Scaling Considerations** – Sec. IV‑C  
- **Discussion** – Sec. V  

---  

## Executive Summary (Optional)  

- Proposes a Behavior‑Tree based, reactive, stateful failure mitigation framework for ROS2 workloads on Kubernetes.  
- Introduces *introspective* (topic frequency) + *external* (pose monitoring) detection.  
- Four recovery strategies trade‑off downtime vs. CPU.  
- Preserves last healthy state, enabling task resumption.  
- Evaluated on Nav2 (navigation) and MoveIt2 (manipulation) in Gazebo; demonstrates generic applicability.  
- Future work: support multi‑pod workloads, safety‑centric monitoring, real‑world deployments.  

---  

*End of summary.*