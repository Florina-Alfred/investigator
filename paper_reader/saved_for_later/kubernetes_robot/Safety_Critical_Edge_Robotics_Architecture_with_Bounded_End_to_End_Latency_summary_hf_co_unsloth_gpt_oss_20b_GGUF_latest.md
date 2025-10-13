# Safety‑Critical Edge Robotics Architecture with Bounded End‑to‑End Latency  
**Gautam Gala, Luiz Maia, Isser Kadusale, Mohammad Ibrahim Alkoudsi, Gerhard Fohler**  
Chair of Real‑Time Systems, Technical University of Kaiserslautern‑Landau (RPTU) – {gala,maia,kadusale,alkoudsi,fohler}@eit.uni‑kl.de  

---

## 1. Abstract
This work proposes a complete edge‑robotic architecture that allows a safety‑critical robotics use‑case (Monte‑Carlo range‑finder‑based localisation) to be fully virtualized and executed on an edge node, replacing an on‑board dedicated hardware solution.  The design combines **Linux** with **Zephyr RT‑OS** on the robot, **Docker containers** for isolation, **Kubernetes** for container orchestration, and a local wireless network based on the **TTWiFi** time‑triggered modification of IEEE 802.11n.  A new **Resource Management & Orchestration (RMO)** layer keeps all shared resources (CPU, cache, memory bandwidth, network bandwidth) bounded and coordinated across the edge nodes.  Experimental results on the MCL‑+Path‑Finder container show that, without the additional RMO orchestration and TTWiFi, bounded end‑to‑end latency cannot be guaranteed; with the extensions it can be achieved.  The paper further discusses fault‑tolerance, security, and scaling aspects required for safety‑critical robotics on the edge.

---

## 2. Introduction & Motivation
- **Safety and SWaP constraints**: mobile robots cannot increase power or weight to gain computing power; thus, on‑board compute is limited.
- **Edge computing** offers high computational density close to the robot, reducing worst‑case network delay versus cloud.
- **Existing effort**: Prior work (e.g. [1–5]) show feasibility but omit strict timing guarantees, fault‑tolerance and security needed for safety‑critical robotics.
- **Goal**: Offload the resource‑intensive part (Monte‑Carlo localisation) to edge while keeping the robot small, battery‐efficient, and guaranteeing bounded E2E latency, safety, security, and full fault‑tolerance.

---

## 3. Methods / Approach

| Layer | Technology | Motivating decisions |
|-------|------------|-----------------------|
| **Robot runtime** | *Zephyr RT‑OS* (Linux‑like, 100% preemptable) | Provides tight WCET guarantees for real‑time tasks. |
| **Hardware abstraction** | Microcontroller with single core; UART via static ISR | Simplifies Worst‑case execution and isolation of driver code. |
| **Container stack** | Docker | Isolate robot’s safety‑critical applications from other best‑effort edge workloads. |
| **Container orchestration** | *Kubernetes* (modified for edge) | Deploy, scale, and re‑deploy containers across edge nodes. |
| **Resource manager** | RMO (LRM + MON + LRS) | Monitors CPU cache/mem bandwidth; enforces minute “critical” core isolation (`isolcpus`) and full dynticks (`nohz_full`) such that housekeeping processes do not run on critical cores. |
| **Wireless network** | IEEE 802.11n + TTWiFi.  Modifications (via ModWifi) – disable CSMA‑CA, set minimum IFS, 0 back‑off, use UDP | Provides deterministic TDMA slots with bounded transmission time; reduces jitter. |
| **Security / Fault tolerance** | Replicate MCL containers across nodes; RMO‑driven rejuvenation; cryptographic key‑delayed release (article [30]); address‑space randomisation, obfuscation | Guarantees integrity/authenticity, privacy, and recovery from crash/BYBE faults. |

### 3.1 Edge Node Partitioning
- *M core* = number of physical cores on edge node.  
- *Critical cores* (e.g. C2..CM) reserved for safety‑critical containers.  
- *Best‑effort cores* (C0, C1, C(M+1)..C(N‑1)) carry Kubernetes + Docker housekeeping.  
- Isolation parameters used:  
  - `isolcpus=C2..CM`, `nohz_full=C(M+1)..C(N‑1)`, `rcu_nocb_poll`, `irqaffinity=C0..C(M+1)`.

### 3.2 RMO Internals
- **Local Resource Manager (LRM)** per node:  
  - **Monitors (MON)** – hardware counters, OS plan tracing, network bandwidth measurement.  
  - **Local Resource Schedulers (LRS)** – performs run‑time binding of containers to critical cores, LLC slices, memory bandwidth partitions, and network slot allocation.  
- **Coordination** – LRM communicates with others via Kubernetes CRDs (custom resource definitions) to migrate containers on demand.

---

## 4. Experiments / Data / Results

| Experiment | Setup | Observed WCET | Comment |
|------------|-------|---------------|---------|
| **MCL + Path Finder container alone** | 1 core cactus | 2.3 ms (mean), 3.2 ms (max) | Baseline for later comparisons. |
| **Using 1–4 cores (critical)** | 1* vs 2/3/4 cores | ⬕ (max) decreases from 4.0 ms → 2.1 ms | More cores improve speed but limited by memory bandwidth. |
| **Replication: 4 MCL containers in parallel** | 4 pods on same node | WCET increased to 5.8 ms | Demonstrates contention on shared resources. |
| **End‑to‑end (sensor data + transmission + execution)** | TTWiFi (400 Mbit/s, 5888 B data, 1 µs IFS) | Upper bound 122.16 µs to transmit data | *Claim:* With TTWiFi modifications, transmission bound < 125 µs. |
| **Combined E2E bound** | Robot → Edge (TTWiFi) + container WCET + feedback slot (= 50 ms) | Total guarantee < 650 µs (dominated by 122 µs TX + 500 µs processing) | *Claim:* System‑wide bounded E2E latency achieved. |

*Figures referenced:*  
- **Figure 5a** – WCET vs core count.  
- **Figure 5b** – WCET vs number of parallel instances.  
- **Figure 3** – MCL workflow on edge device.  
- **Figure 4** – Overall architecture diagram.  

---

## 5. Discussion & Analysis

### 5.1 Achieved Goals
- **Bounded E2E latency**: TTWiFi + RMO deliver deterministic < 128 µs transmission; container execution bounded by 3–5 ms; overall E2E < 650 µs.  
- **Fault‑tolerant**: Replication of containers + RMO‑driven rejuvenation prevent single container failure from stalling whole node.  
- **Security**: Network-level authentication and integrity protection (delayed key release). Real‑time constraints not affected because cryptographic overhead is negligible at our data rate.

### 5.2 Observed Bottlenecks
- **Shared cache contention** between multiple containers on best‑effort cores.  
- **Network bandwidth**: with many robots at once, UDP overhead may grow; still deterministic thanks to QoS token supply.  
- **Clock drift**: Even with guard‑time, drift observed if network very busy; mitigated using fault‑tolerant averaging ([24]).

### 5.3 Trade‑offs
- **CPU isolation** (isolcpus) vs. **Kernel preemption**: critical cores preempt freely, best‑effort cores run Docker housekeeping.  
- **UDP vs. TCP**: UDP eliminates retransmits but needs application‑level loss detection; negligible since all nodes visible.  

---

## 6. Conclusions

The paper presents a complete, safety‑critical, edge‑robotic architecture that combines well‑understood Linux‑based RT OS, container isolation, Kubernetes orchestration, and active resource management.  With the TTWiFi modifications and the RMO, the authors demonstrate bounded end‑to‑end latency of the Monte‑Carlo localisation/trajectory planning use case.  Fault‑tolerance and a lightweight security scheme are further integrated.  The next stage (future work) involves a real‑time deployment with several robots and a complete E2E latency test on a live TTWiFi network.

---

## 7. Key Claims & Contributions

| Claim | Supporting evidence |
|-------|----------------------|
| **C1** – A safety‑critical robotic application can be fully virtualized on edge nodes with bounded E2E latency. | WCET measurements (Fig 5a), TTWiFi upper bound (< 125 µs) → total < 650 µs. |
| **C2** – Linux + Docker + RMO + TTWiFi ensure deterministic node‑critical behaviour. | Experimented MTBF for container migrations; deterministic scheduling of critical cores. |
| **C3** – Security does not degrade real‑time performance. | Key delay authentication algorithm ([30]) adds < 1 µs overhead at 400 Mbit/s. |
| **C4** – Replicated containers (on multiple nodes) provide fault‑tolerance with negligible performance penalty. | Replicated MCL containers experiment: same WCET (~3 ms) with/without replication. |
| **C5** – Critical resources must be simultaneously managed across all edge nodes. | RMO specification: LRM, MON, LRS coordinate across nodes via Kubernetes; necessary for 4‑robot deployment. |

---

## 8. Definitions & Key Terms

- **Zephyr RT‑OS** – A lightweight, preemptable RT kernel based on Linux architecture, used on the robot’s MCU.  
- **TTWiFi** – Time‑Triggered wireless networking built upon IEEE 802.11n, using a static TDMA schedule and disabling carrier‑sense to close jitter.  
- **RMO (Resource Management & Orchestration)** – Layer that includes a **Local Resource Manager (LRM)**, **Monitors (MON)**, and **Local Resource Schedulers (LRS)** for controlling CPU affinity, cache slices, and memory/ network bandwidth.  
- **Kernel Flags** – `isolcpus`, `nohz_full`, `rcu_nocb_poll`, `irqaffinity`: all used to ensure critical cores run only the safety‑critical containers.  
- **Monte‑Carlo Localization (MCL)** – Probabilistic localisation algorithm that samples a large number of particles (≥10,000).  
- **UDP** – Connectionless transport chosen to keep jitter minimal and avoid TCP re‑transmission.  

---

## 9. Important Figures & Tables

| # | Title | Content | Significance |
|---|------|----------|--------------|
| 1 | Figure 1 | Magni robot with custom LIDAR attachment | Illustrates hardware baseline. |
| 2 | Figure 3 | MCL workflow on edge device | Shows off‑load partitioning. |
| 3 | Figure 4 | Architecture overview | Highlights layers & interactions. |
| 4 | Figure 5a | WCET vs core usage | Demonstrates benefit of critical core isolation. |
| 5 | Figure 5b | WCET vs parallel instances | Illustrates resource contention when multiple containers run. |
| 6 | Table I | Baseline task set | Baseline periodic tasks on MCUs. |

---

## 10. Limitations & Open Questions

| Limitation | Comment |
|------------|---------|
| **Network assumptions** – All nodes visible and no hidden nodes; may not hold in larger deployments. |
| **Security** – No confidentiality required; real‑time encryption may become heavier if needed. |
| **Fault model** – Only crash and Byzantine faults considered for containers; hardware faults not fully covered. |
| **Scalability** – Experiments limited to 1‑4 MCL containers; full 10+ robot scaling future. |
| **Energy metrics** – Impact on robot battery life measured only qualitatively; detailed consumption analysis pending. |

---

## 11. References to Original Sections

| Reference | Section |
|-----------|---------|
| [1] | Related Work (Sec II) – & RT‑cloud background |
| [23] | Wireless design details (Sec V) – TTWiFi |
| Fig. 5 | Methods & Results (Sec IV‑C and V) |
| Table I | Methodology (Sec III‑b) |
| Fig. 4 | Architecture overview (Sec IV‑D) |
| Eq. (transmission bound) | V‑a |

---

## 12. Executive Summary (Optional)

1. **Safe, low‑SWaP robot**—Magni plus RPLIDAR.  
2. **Zephyr RT‑OS** ensures critical timing on the MCU.  
3. **Docker + Kubernetes + RMO** isolate safety‑critical containers, enforce critical core bindings, and manage cross‑node resources.  
4. **TTWiFi** schedules deterministic wireless slots, removes CSMA‑CA and IFS jitter.  
5. **Experiments** show < 650 µs end‑to‑end latency for MCL+Path‑Finder; replication does not hurt WCET.  
6. **Security**: authentication with key‑delayed release; crash/Byzantine removal via rejuvenation.   
7. **Future**: deploy full‑scale 10‑robot testbed, measure battery improvements, and strengthen network fault model.

---

**End of Summary**