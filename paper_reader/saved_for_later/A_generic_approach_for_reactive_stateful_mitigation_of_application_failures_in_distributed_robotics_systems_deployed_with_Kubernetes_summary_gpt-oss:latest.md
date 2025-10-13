**Title & Citation**  
*A generic approach for reactive stateful mitigation of application failures in distributed robotics systems deployed with Kubernetes*  
Florian Mirus, Frederik Pasch, Nikhil Singhal, Kay‑Ulrich Scholl – Intel Labs, Karlsruhe, Germany – 2024 (ICRA 2024, to appear).

---

## Abstract  
Offloading computationally expensive robotic algorithms to the edge or cloud mitigates on‑board resource limits but introduces new failure‑resilience challenges.  Existing cloud‑native failure‑mitigation schemes are unsuitable because robotic systems interact with the physical world in real‑time and often require stateful recovery.  This work presents an application‑agnostic, reactive mitigation framework for distributed robotics deployed with Kubernetes (K8s) and ROS 2.  The system combines introspective monitoring of ROS 2 diagnostics and key‑performance indicators (KPIs) with external supervision of observable robot behaviour.  Behaviour Trees (BTs) encode arbitrary monitoring and mitigation logic, enabling preservation of the last healthy state and selection of mitigation strategies that trade off downtime against computational overhead.  Evaluation on two simulated workloads – AMR navigation (Nav2) and robotic manipulation (MoveIt2) – demonstrates the effectiveness and generality of the approach.

---

## Introduction & Motivation  
*Key points*  
1. Modern robotics increasingly relies on AI‑driven algorithms that are computationally heavy and energy‑intensive.  
2. Mobile robots are often resource‑constrained; thus, offloading computation to edge or cloud is attractive.  
3. Distributed robotic fleets (e.g., industrial automation) run on container‑managed infrastructures such as K8s, which introduces failure modes: node crashes, network partitions, pod crashes, etc.  
4. Cloud‑native resilience strategies (reactive vs. proactive) focus on isolated micro‑services and do not consider state preservation or physical‑world interaction.  
5. Existing work (e.g., FogROS2, KubeROS, the authors’ own previous study on AMR communication failure) addresses limited failure classes but not stateful, application‑agnostic recovery.  
*Motivation* – To develop a generic, stateful, reactive mitigation scheme that can be applied to any ROS 2 workload on K8s, preserving the last good state, while respecting the constraints of real‑time robotics.

---

## Methods / Approach  
The proposed system has two tightly coupled components, both expressed as Behaviour Trees (BTs).

### 1. Monitoring System  
| Monitoring type | Description | Implementation |
|-----------------|-------------|----------------|
| **Introspective** | Observe ROS 2 topic frequencies (e.g., velocity command, joint state). Adapt thresholds based on robot’s current task (e.g., navigation vs. manipulation). | BT nodes that poll topic frequencies; hierarchical task‑dependent monitoring. |
| **External Supervision** | Compare expected robot behaviour (from introspection) against observations from external sensors (cameras, LIDAR). Detect discrepancies indicating hidden failures. | BT nodes that ingest external perception data (e.g., ArUco pose estimates) and perform sanity checks. |

*Figure 1* (system overview) shows how the monitoring BT feeds a *failure‑flag* to the mitigation module.  
*Figure 4* presents a sample BT that monitors an AMR’s velocity command and restarts the Nav2 stack when the command stream stops.

### 2. Failure Mitigation System  
Four recovery strategies are defined, each represented by a BT that encapsulates the necessary Kubernetes and application steps.

| Strategy | Core idea | Trade‑offs | Typical BT actions |
|----------|-----------|------------|---------------------|
| **Restart‑from‑scratch** | Delete failing pod; let K8s respawn it. | Longest downtime; minimal extra compute. | `DeletePod` → `CreatePod` → `Initialize` |
| **Fallback (uninitialized)** | Run a standby pod in parallel; after failure, switch network traffic to it. | Moderate downtime; extra compute for standby. | `CreateFallbackPod` → `PatchNetworkPolicies` → `Initialize` |
| **Fallback (partially initialized)** | Standby pod already started but not executing critical nodes. | Lower downtime than uninitialized; still extra compute. | `CreateFallbackPod` → `StartCriticalNodes` → `PatchNetworkPolicies` |
| **Fallback (fully initialized + running)** | Standby pod fully running the stack and awaiting switch. | Fastest recovery; highest compute overhead. | `CreateFallbackPod` → `FullStartup` → `PatchNetworkPolicies` |

*Figure 5* illustrates the required Kubernetes steps and their time components:  
- `t_detection` – time to detect failure (user‑specified).  
- `t_cluster` – time for K8s to perform pod deletion/recreation or network policy patch.  
- `t_startup` – time to bring a new pod to a running state (depends on fallback init level).  
- `t_reinitialization` – time to restore the last healthy state (state transfer, parameter loading).  

#### State Recovery  
The failing workload serialises its last healthy state (e.g., map, localisation pose, motion planner state) and hands it to the fallback or restarted instance.  BTs can encode complex dependencies (e.g., if localisation fails, also restart the path planner).  

#### Implementation Details  
- **Kubernetes primitives**: `Deployment` for pod lifecycle, `NetworkPolicy` for traffic rerouting.  
- **BT runtime**: Scenario Execution for Robotics (SER) library, OpenSCENARIO 2 for BT definition, `pytrees` for execution.  
- **Task proxy**: Maintains high‑level task state across restarts (e.g., goal list).

---

## Experiments / Data / Results  

### Experimental Setup  
| Application | Robot | ROS 2 Framework | Task | Failure Injection | Monitoring | External Supervision |
|-------------|-------|-----------------|------|--------------------|------------|----------------------|
| AMR Navigation | Turtlebot 4 | Nav2 | Move to series of goals | Delete Nav2 pod at `t_failure` | Topic frequency (velocity) | Camera with ArUco markers (expected vs. observed velocity) |
| Manipulation | WidowX‑200 arm | MoveIt2 | Reach sequence of poses | Delete MoveIt2 pod at `t_failure` | Topic frequency (joint states) | – |

- All workloads containerised; executed in Gazebo 3 simulation.  
- One monitor per application; BTs run in parallel to the main workload.  
- Monitoring checks run at 10 Hz; failure detected within 500 ms.

#### Metrics  
1. **Recovery time**  
   ```
   t_recovery = t_detection + t_cluster + t_startup + t_reinitialization
   ```
   (Eq. 1 – derived from experimental logs).  
2. **CPU usage** – per‑container `γ_c,t_i` measured by CAdvisor; average per container `σ(c)`; overall cluster average `σ(CPU)=∑_c σ(c)`.  

### Results – AMR Navigation  
*Figure 6* (AMR) shows breakdown of `t_recovery` for each strategy.  

- **Restart‑from‑scratch**: `t_cluster` ≈ 32× longer than network patch; total recovery ≈ 6 s.  
- **Fallback (uninitialized)**: `t_cluster` ≈ 0.1 s; `t_startup` ≈ 2.5 s; `t_reinitialization` ≈ 1 s.  
- **Fallback (partially initialized)**: reduced `t_startup` and `t_reinitialization` proportionally.  
- **Fallback (fully initialized)**: `t_startup = 0`; overall recovery ≈ 1.2 s.  

*Figure 7* (CPU load) shows:  
- **Restart‑from‑scratch** consumes ≈ 30 % of cluster CPU.  
- **Uninitialized fallback** adds ≈ 60 % of the main workload’s CPU.  
- **Fully initialized fallback** doubles the main workload’s resource use (≈ 60 % extra).  

### Results – Manipulation  
*Figure 8* (Manipulation) illustrates that only strategies 1, 2, and 4 are applicable.  
Recovery times follow the same trend: full fallback fastest; restart slowest.  
CPU usage pattern similar to navigation; omitted for brevity.

### Scaling Considerations  
- Consider fleet of `N` robots, each with a monitored workload.  
- Failure of workload causes downtime `t_S` (depends on strategy).  
- For a fleet, the probability that more than `k` failures happen within a window of length `t_S` can be bounded analytically (see Section IV‑C).  
- Example: `N=1000`, 1 failure/hr per robot → ≈ 8.3 failures every 30 s.  
  - 4 uninitialized fallbacks yield 1.2 % chance that >4 failures hit within a 6 s window (downtime).  
  - Fully initialized fallback for all 1000 robots would double CPU usage but reduce downtime by factor 10.  
- Recommendation: use *uninitialized fallback* as a sweet spot for large fleets with moderate resource budgets.

---

## Discussion & Analysis  
- **Effectiveness**: The framework successfully restores any ROS 2 workload to a healthy state while preserving the last known good state, thus maintaining task continuity.  
- **Generality**: Tested on two distinct workloads (navigation, manipulation); same BTs can be reused with minimal adaptation.  
- **Trade‑off**: Clear mapping between strategy, downtime, and resource overhead; allows deployment‑specific tuning.  
- **Limitations**: Current implementation assumes each monitored workload runs in a single container; real‑world stacks often split into multiple micro‑services (localisation, planning, execution).  Dependencies between services are not yet fully handled.  
- **Open Questions**:  
  - How to automatically generate introspective monitors for arbitrary ROS 2 topics?  
  - How to integrate safety‑critical monitoring (e.g., collision risk) into the BT framework?  
  - Can the mitigation be combined with proactive predictive failure detection (e.g., LSTM forecasts)?  

---

## Conclusions  
The paper presents a *generic, reactive, stateful failure‑mitigation framework* for distributed robotic systems deployed on Kubernetes and ROS 2.  Using Behaviour Trees, the system provides:  
1. An application‑agnostic monitoring layer (introspective + external).  
2. Multiple mitigation strategies that trade off recovery time against resource usage while preserving the last healthy state.  
3. Empirical validation on AMR navigation and manipulation workloads.  The results confirm the feasibility and scalability of the approach for large robot fleets.

---

## Key Claims & Contributions  
- **Claim 1**: *The system can preserve the last healthy state across a pod restart or switch to a fallback.*  
  **Evidence**: State transfer logic described in Section III‑C; experimental logs show tasks resume from the same position after recovery.  

- **Claim 2**: *Behaviour Trees enable arbitrary, application‑agnostic monitoring and mitigation logic.*  
  **Evidence**: Figure 4 demonstrates a BT for AMR; Section III‑A and III‑B show BT structure; SER library provides reusable runtime.  

- **Claim 3**: *Four mitigation strategies yield predictable trade‑offs between downtime and CPU usage.*  
  **Evidence**: Figures 6–8; Section IV‑B.  

- **Claim 4**: *The framework scales to large fleets with modest additional resource overhead.*  
  **Evidence**: Scaling analysis in Section IV‑C; probability calculations for 1000‑robot fleet.

---

## Definitions & Key Terms  

| Term | Definition |
|------|------------|
| **ROS 2** | Robot Operating System version 2, a middleware for robotic software. |
| **Kubernetes (K8s)** | Container orchestration system managing deployments, scaling, networking. |
| **Behaviour Tree (BT)** | Tree‑structured control flow model (nodes: Sequence, Selector, Decorator, Action). |
| **Fallback workload** | A standby instance (pod) that can take over after a failure. |
| **Stateful mitigation** | Recovery that preserves the last consistent application state. |
| **Introspective monitoring** | Observing internal metrics (e.g., topic frequency, diagnostics). |
| **External supervision** | Observing the robot’s external behaviour (camera, LIDAR). |
| **Network Policy** | K8s resource that controls pod communication. |
| **Deployment** | K8s resource that manages pod replicas, rollout, scaling. |
| **Nav2** | ROS 2 navigation stack. |
| **MoveIt2** | ROS 2 manipulation framework. |
| **t_recovery** | Total time to recover after failure. |
| **γ_c,t_i** | CPU usage of container *c* at time *t_i*. |
| **σ(c)** | Mean CPU usage of container *c* over the experiment. |
| **σ(CPU)** | Sum of mean CPU usage of all containers in the cluster. |

---

## Important Figures & Tables  

| Figure | Caption & Relevance |
|--------|----------------------|
| **Fig. 1** | High‑level overview of monitoring and mitigation architecture (inputs, BTs, outputs). |
| **Fig. 2** | Taxonomy of monitoring/mitigation strategies with factor weights (safety, availability, resources). |
| **Fig. 3** | Detailed system architecture: containers, BTs, SER library, K8s components. |
| **Fig. 4** | Sample BT for basic failure mitigation (AMR navigation). |
| **Fig. 5** | Flow of steps and trade‑offs for each mitigation strategy (cluster vs. application time). |
| **Fig. 6** | Breakdown of recovery time components for AMR navigation strategies. |
| **Fig. 7** | CPU load comparison among strategies (stacked bars per container). |
| **Fig. 8** | Recovery time for manipulation use‑case (only applicable strategies). |

---

## Limitations & Open Questions  

1. **Single‑container assumption** – Real robotic stacks often split across multiple pods (e.g., localisation, planning).  Current BTs can express dependencies, but practical evaluation is pending.  
2. **Safety‑critical monitoring** – The taxonomy (Fig. 2) outlines safety as a factor, but concrete safety monitors (e.g., collision risk) are not yet integrated.  
3. **State transfer overhead** – The paper does not quantify serialization/deserialization time or network bandwidth for state transfer.  
4. **No baseline comparison** – Other frameworks (FogROS2, KubeROS) lack the same functionality; no direct benchmark.  
5. **Scalability to thousands of robots** – The scaling analysis is theoretical; real deployments may face network and K8s cluster limits.  
6. **Proactive failure prediction** – Not addressed; could be integrated via machine‑learning predictors.  

---

## References to Original Sections  

- **Monitoring system** – Section III‑A, Fig. 4, Fig. 1.  
- **Failure mitigation strategies** – Section III‑B, Fig. 5, Section IV‑B.  
- **State recovery** – Section III‑C, Fig. 5.  
- **Implementation** – Section III‑D.  
- **Experimental evaluation** – Section IV, Figures 6‑8.  
- **Scaling analysis** – Section IV‑C.  
- **Discussion & conclusion** – Section V‑A, V‑B.

---

## Executive Summary / Key Takeaways  

1. **Generic, reactive, stateful failure mitigation** for ROS 2 workloads on K8s is feasible using Behaviour Trees.  
2. **Dual monitoring** (introspective + external) provides robust failure detection without altering application code.  
3. **Four recovery strategies** allow tuning between downtime (≈ 1 s–6 s) and resource overhead (≈ +30 % to +200 % CPU).  
4. **State preservation** ensures tasks resume from the last healthy point, critical for continuous operations.  
5. **Scalable**: with a fleet of 1000 robots, an *uninitialized fallback* gives a good balance (≈ 1 % probability of extended downtime) with modest CPU overhead.  
6. **Future work**: multi‑pod dependencies, safety‑aware monitoring, proactive prediction, deeper integration with K8s scheduler.

---

## Supplementary Material  
- **Scenario Execution for Robotics (SER)** library – open‑source implementation of BT runtime for robotics experiments.  
- **OpenSCENARIO 2** files – human‑readable BT definitions used in experiments (not included in the paper).  
- **CAdvisor** metrics – used for CPU profiling.  

---