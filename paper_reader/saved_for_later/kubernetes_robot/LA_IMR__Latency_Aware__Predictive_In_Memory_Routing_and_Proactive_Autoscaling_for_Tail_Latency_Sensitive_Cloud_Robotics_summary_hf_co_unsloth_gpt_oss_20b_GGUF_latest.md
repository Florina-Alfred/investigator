**Title & Citation**  
- *LA‑IMR: Latency‑Aware, Predictive In‑Memory Routing & Proactive Autoscaling for Tail‑Latency‑Sensitive Cloud Robotics*  
- Authors: Eunil Seo, Chanh Nguyen, Erik Elmroth  
- Department of Computing Science, Umeå University, Sweden  
- e‑mail: {eunil.seo, chanh, elmroth}@cs.umu.se  

---

### Abstract  
Hybrid cloud‑edge systems deliver low latency only when demand remains below the capacity of heterogeneous tiers. Bursty traffic can still trigger long‑tail (P99) spikes that hurt mission‑critical robotics. LA‑IMR introduces a closed‑form, utilization‑driven latency model that decomposes end‑to‑end latency into processing, network, and M/M/c queuing components. The model is calibrated per‑hardware tier and yields two complementary functions: (i) millisecond‑scale routing decisions for traffic offloading and (ii) capacity‑planning that derives replica pool sizes.  LA‑IMR couples this model with: a quality‑differentiated multi‑queue scheduler, a predictive in‑memory router, and a custom‑metric Kubernetes HPA that scales replicas “just‑in‑time” before queues build up. Experiments with YOLOv5m and EfficientDet under bursty traces show up to **20.7 %** reduction in P99 latency relative to latency‑only autoscaling.

---

### Introduction & Motivation  
- *Tail latency* (P99) is critical in autonomous vehicles, surgical robotics, AR/VR, etc.  
- Existing solutions (e.g., C3, hedging) react after spikes or use coarse queue metrics.  
- There is no principled way to *predict* latency and act *before* queues grow.  
- This paper proposes LA‑IMR, an SLO‑aware control layer that sits inside the micro‑service graph, continuously routing, offloading, and autoscaling based on a real‑time analytical model.

---

### Methods / Approach  

| Sub‑section | What was done | Key Algorithms / Formulas |
|-------------|---------------|---------------------------|
| **3.A Latency Components** | Established a closed‑form latency expression `L_t = L_process + D_net + Q_t`.  `L_process` = affine power‑law of per‑instance utilization; `Q_t` derived from M/M/c queuing formula. | `L_{m,i} = L_m / S_{m,i} * (1 + β λ^{γ})` (Eq. 8 in the paper) |
| **Closed‑form Model Calibration** | Per tier (CPU, GPU, TPU) fitted three parameters: reference latency `L_m`, speed‑up `S_{m,i}`, exponent `γ`. Measured using YOLOv5m at different arrival rates & replica counts (Table IV). | Fig. 2 shows‐predicted vs measured latencies |  
| **3.G & 3.H Optimisation** | Two optimisation views: (i) fix replica layout, optimize routing (`x_{t,m,i}`) to satisfy SLO; (ii) fix traffic, optimize replica numbers `N_{m,i}` for cost vs latency. | Formulated `g_{m,i}(λ)` and `G_{m,i}(N)` functions, with Erlang‑C‑derived queueing term. |
| **Algorithm 1** | Event‑driven LA‑IMR controller: updates sliding‑window arrival rates, predicts per‑instance latency, routes or offloads if SLO violated, scales replicas proactively, uses EWMA smoothing. | Pseudocode given in paper. |
| **Custom‑Metric HPA** | Exported desired replica count to Kubernetes HPA which then reconciles every 5 s, enabling “just‑in‑time” scaling and graceful termination. | Equation 39 in the paper (`desired_replicas = G_{m,i}( λ_accum )`). |

**Quality‑Stratified Scheduler** – three QoS queues: \
1. **Low‑Latency** (EfficientDet) – highest priority.  
2. **Balanced** (YOLOv5m).  
3. **Precise** (Faster R‑CNN) – lowest priority.

---

### Experiments / Data / Results  

| Section | Setup | Key Findings |
|---------|-------|--------------|
| **V.A Experiment Environment** | CloudGripper testbed: 5 robots, Raspberry Pi 4 edge cluster (32 nodes), 10 Gbit cloud cluster (19 CPU cores), Prometheus + HPA. | Measurement cadence: <1.8 s startup, network RTT ~36 ms. |
| **V.B Latency Evaluation** | Vary λ (1–6 req/s). | Fig. 7 shows LA‑IMR keeps P99 ≤ 5.4 s while baseline spikes to 6.8 s at λ=6. |
| **V.C Long‑Tail Mitigation** | Box‑plot of SLO‑based latencies. | LA‑IMR reduces inter‑quartile range by 27 % and max outlier by 41 % (Fig. 8). |
| **Table VI** | P95 & P99 latencies for LA‑IMR vs baseline across λ. | LA‑IMR’s P99 improves from 1 % at λ=1 to 20.7 % at λ=6. |
| **Table I, II, IV** | Notation table, model profiles, empirical latency measurements. | Provide calibration parameters. |

---

### Discussion & Analysis  

*Strengths* – Predictive analytic model matches measurements within a few percent; event‑driven routing + proactive autoscaling suppresses queue spikes; microservice decomposition reduces inter‑service interference.  
*Challenges* – Assumes exponential inter‑arrival times; uses a single EWMA smoothing weight α=0.8 and fixed utilization floor ρ_low tuned offline; does not handle correlated bursts across services; global off‑loading & cross‑cluster balancing not optimized.  
*Future Work* – Self‑tuning of control knobs; incorporating memory‑intensive, variable‑batch workloads; dynamic bandwidth/adaptive overhead; combination of fast‑ and slow‑window arrival‑rate estimators to catch sudden spikes without destabilising steady traffic.

---

### Conclusions  

- Introduced a principled closed‑form latency model that decomposes processing, network, and queuing delays.  
- Built LA‑IMR: a predictive in‑memory routing layer with quality‑differentiated queues, proactive autoscaling via custom Kubernetes HPA, and selective off‑loading to upstream tiers.  
- Demonstrated P99 latency reduction up to 20.7 % and variance reduction > 60 % over reactive autoscaling on YOLOv5m/ EfficientDet workloads.  
- Open‑sourced code and Prometheus metrics (not detailed in paper).

---

### Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
| **CLAIM 1 – Closed‑form, dual‑purpose latency model** | Eq. 8, Fig. 2 (measured vs predicted for YOLOv5m). |
| **CLAIM 2 – Millisecond‑scale routing decisions** | Algorithm 1 event‑driven, uses instantaneous λ and predicted `g_inst`. |
| **CLAIM 3 – Proactive autoscaling via custom metric** | Custom metric “desired_replicas” fed to HPA; Table VI shows migration of P99 from 6.85 s (baseline) to 5.44 s (LA‑IMR). |
| **CLAIM 4 – Tail‑latency mitigation in cloud‑robotics** | Box‑plot Fig. 8, 41 % reduction of maximum outliers. |
| **CLAIM 5 – 20.7 % P99 improvement across bursty workloads** | Table VI and Fig. 7. |

---

### Definitions & Key Terms  

- **SLO** – Service Level Objective (latency bound, e.g., P99 ≤ x·L_inf).  
- **M/M/c Queue** – Markovian arrival/service model with `c` parallel servers.  
- **EWMA** – Exponentially Weighted Moving Average (update λ_accum).  
- **Erlang‑C** – Exact formula for steady‑state probability of delay in M/M/c.  
- **CPU‑budget** – `R_m,i` = CPU‑seconds per inference for model m on instance i.  
- **Structural Offloading** – Transfer of invocations to a higher (cloud) tier when local SLO predict breached.  
- **Quality‑Stratified Queue** – Separate dispatch queues for low‑latency, balanced, and precise inference services.  

---

### Important Figures & Tables  

| Label | Description | Significance |
|-------|--------------|--------------|
| **Fig. 1 (LA‑IMR Flow)** | Shows micro‑service tiers, router, and edge‑cloud offloading. | Illustrates architecture. |
| **Fig. 2 (Latency Calibration)** | Plots predicted vs measured latency for YOLOv5m. | Validates closed‑form model. |
| **Fig. 3 (Latency vs λ)** | Average, P95, P99 curves. | Highlights super‑linear tail growth. |
| **Fig. 4 (Micro‑service vs monolithic)** | Comparison of average, P95, P99 as replicas increase. | Shows benefit of microservices. |
| **Fig. 5 (Latency Prediction Trigger)** | Flow of λ → predicted latency → scaling & offload decisions. | Visualizes event‑driven controller. |
| **Fig. 6 (CloudGripper Cells)** | Layout of testbed robots and edge cluster. | Context for experiments. |
| **Fig. 7 (Latency Comparison)** | LA‑IMR vs baseline under load λ=1‑6. | Quantifies improvement. |
| **Fig. 8 (Box‑plot)** | P99 latency across λ with LA‑IMR vs baseline. | Shows variance reduction. |
| **Table I (Notation)** | Variable definitions. | Key for following equations. |
| **Table II (Model Profiles)** | Busy state latencies and CPU demands for EfficientDet / YOLOv5m. | Calibration parameters. |
| **Table IV (Measured Latency)** | YOLOv5m latencies at different λ and replica counts. | Empirical evidence for model. |
| **Table VI (Experimental Results)** | P95 / P99 latencies for LA‑IMR & baseline. | Quantitative performance. |

---

### Limitations & Open Questions  

1. **Assumed Inter‑Arrival Distribution** – The M/M/c queue assumes exponential arrivals; real industrial traffic may deviate.  
2. **Static Control Knobs** – Values for α, ρ_low, γ, and λ_accum were tuned offline per workload; continuous self‑tuning is future work.  
3. **Global Offloading Optimisation** – Only local upstream tier considered; cross‑cluster placement not fully explored.  
4. **Burst Correlation** – Experiments used Poisson/Pareto bursts; correlated spikes across multiple services were not evaluated.  
5. **Hardware Heterogeneity** – Only CPU, GPU, TPU scaling factors used; other accelerators/heterogeneous devices need additional profiling.  

---

### References to Original Sections  

- **System Model & Problem Formulation** – Section III.  
- **LA‑IMR Architecture** – Section IV.  
- **Experimental Evaluation** – Section V, sub‑sections A–D.  
- **Figure & Table Numbers** – as cited in the summary.  

---

### Executive Summary / Key Takeaways  

1. LA‑IMR couples a simple analytic latency model with an event‑driven, in‑memory controller to preemptly route, offload, and scale inference workloads.  
2. Super‑linear utilization exponent (γ≈1.5) captures rapid latency growth under bursty load.  
3. Custom‑metric HPA eliminates the typical 60‑120 s lag of CPU‑based autoscaling.  
4. Experiments on YOLOv5m/ EfficientDet in a cloud‑edge cluster show up to 20.7 % improvement in P99 latency and > 60 % reduction in variance.  
5. Future work lines: adaptive tuning, correlated burst handling, and broader hardware support.

--- 

### Supplementary Material (if present)  

- Code repository and deployment scripts referenced in the paper (not reproduced here).  
- Prometheus dashboards for micro‑service latency metrics.  
- Full parameter values for all benchmarks (see Tables I‑IV).

---