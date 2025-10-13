**Title & Citation**  
*QBIT: Quality‑Aware Cloud‑Based Benchmarking for Robotic Insertion Tasks*  
Constantin Schempp, Yongzhou Zhang, Christian Friedrich, Björn Hein. 2025.

---

## Abstract  
Insertion tasks are core to assembly yet notoriously difficult because of continuous contact and perception error.  Existing benchmarks report only success rates, missing essential quality dimensions such as contact forces and smoothness.  QBIT augments benchmarking with two additional metrics—force energy and force smoothness—alongside success rate and completion time.  To reduce the sim‑to‑real gap, QBIT randomizes contact physical parameters, models pose uncertainty, and supplies a large‑scale Kubernetes‑based execution pipeline.  All components are containerised in a micro‑service architecture, enabling easy extension to new robots, tasks and datasets.  Three classic strategies (geometric‑, force‑, and learning‑based control) are compared on simulations and a real UR5e, showing that the added metrics expose qualitative differences invisible to success‑rate alone.  Sphere‑based mesh decomposition and contact‑parameter randomisation further reduce the sim‑to‑real discrepancy.  Source code is public on GitHub.

---

## Introduction & Motivation  
*Insertion* (e.g., peg‑in‑hole) is ubiquitous in manufacturing, but performance evaluation is still dominated by binary success, neglecting contact forces, repeatability and industry‑often‑required tolerances.  
*Motivation*  
1. **Quality assessment** – industrial assembly demands minimal forces and smooth insertion to prevent surface damage.  
2. **Reproducibility** – current datasets/benchmarks (REASSEMBLE, RLBench) lack quality‑related metrics.  
3. **Sim‑to‑real transfer** – continuous contact makes real‑world failures costly; thus a better sim‑to‑real bridge is needed.  

*QBIT* addresses these by (i) adding force‑based metrics, (ii) modeling pose/perceptual uncertainty, (iii) randomising contact parameters in MuJoCo, and (iv) running many experiments on a Kubernetes cloud to reach statistical significance.  

*Key contributions* listed in the introduction are:  
- a cloud‑based quality‑aware benchmark,  
- the proposed force energy and smoothness metrics,  
- a sphere‑based mesh decomposition,  
- a stochastic contact‑parameter randomisation,  
- a scalable microservice pipeline, and  
- its open‑source joint‑container design.

---

## Methods / Approach  

### 1. Insertion Task Formulation  
- Initial pose \(H_s \in \mathbb{R}^6\) (position & Euler angles).  
- Contact wrench \((\mathbf{F}, \mathbf{T})\in \mathbb{R}^6\) recorded at each timestep.  
- For a trial \(i\) the discrete timeline is \(\mathbf{w}_i(n)=(\mathbf{F}(n),\mathbf{T}(n))\).  

### 2. Statistical Uncertainty Model  
- Pose error \(H_s^\Delta \sim \mathcal{N}(H_s,\Sigma_H)\).  
- Sensor noise: Gaussian white noise added to wrench data in MuJoCo.  
- Repeats \(K\) to obtain statistically robust metrics.  

### 3. Quality‑Aware Metrics  
| Metric | Definition | Observed Significance |
|--------|------------|----------------------|
| **Force Energy** \(E_z\), \(E_{xy}\) | \(E_z = \sum \|F_z(n)\| \cdot dt,\; E_{xy} = \sum \|F_{xy}(n)\| \cdot dt\) | Tracks cumulative force—high values indicate abrupt, undesirable contact. |
| **Force Smoothness** \(S_z\), \(S_{xy}\) | Standard deviation of \(\dot{F}_z,\dot{F}_{xy}\) after low‑pass filter  | Low values imply smooth force profile. |
| **Success Rate** \(R=\frac{\sum b_i}{K}\) (binary \(b_i\)) | Indicates whether functionally insertion succeeded. |
| **Completion Time** \(\bar{t} = \frac{1}{K}\sum t_i\) | Measures overall speed of the approach. |

### 4. Framework Architecture  
- **Micro‑service‑oriented**: each logical component (algorithm, simulator, hardware interface) is a stand‑alone container.  
- **Simulation Path**: MuJoCo as physics engine, supports solving 6‑DOF inverse dynamics; uses convex decomposition methods — VHACD, COACD, and a newly proposed **sphere‑based** decomposition.  
- **Randomised Parameters**: Contact stiffness (solref), compliance (solimp), friction slider computed per run within given ranges (e.g. solref ∈[0.01,0.5], friction ∈[0.1,0.7]).  
- **Batch Scheduler**: YAML file lists algorithm image, simulator image, randomisation spec, and uncertainty; the QBIT batch calls the Kubernetes API to spawn special simulation instances and shuffles the trial queue.  
- **Client‑Server Interaction**: Simulation instance calls algorithm server via gRPC; this reduces overhead compared to embedding the inference in the simulation loop.  
- **Hardware Adapter**: ROS2 + MoveIt2 + ros2_control used to interface with real robots (UR5e, UR10 etc.). All hardware clients are containerised so that only the interface container needs to be adapted for new robots.  

### 5. Experimental Setup  
- **Real Robot**: UR5e arm, peg fixed to end‑effector, 6‑axis FTN‑AXIA80 force‑torque sensor.  
- **Simulation**: Peg‑in‑hole with tolerances 1 mm, 0.1 mm, and small objects (USB plugs).  
- **Metrics & Repeats**: 100 successful runs per approach, with random pose error \(H_s^\Delta\).

### 6. Test Algorithms  
- **Position‑controlled**: Pure Cartesian motion, no force feedback. Baseline.  
- **Force‑controlled**: Classical equation  
  \[
  \tau=\tau_d + M\vect{W}_a + D\dot{\vect{W}}_a + C\tilde{\vect{W}}_a
  \]  
  with desired wrench \(W^d=(F_z=F_{desired},0,0)\).  
- **Learning‑based (InsertionNet)**: Multi‑modal network mapping RGB image + wrench to residual pose correction \(a\). Proposed architecture: CNN encoder -> LSTM → fully connected → output 6D pose correction. Trained offline on collected data.  

---

## Experiments / Data / Results  

| Approach | t (s) | \(E_z\) | \(E_{xy}\) | \(S_z\) | \(S_{xy}\) | Comments |
|----------|--------|---------|------------|---------|-----------|-------------------------------------------------|
| **Force‑controlled** | **0.8375** | **0.9972** | **0.9999** | 0.9259 | 0.9534 | Lowest forces, longest time |
| **Position‑controlled** | 0.8395 | 0.0279 | 0.0002 | 0.8183 | 0.8016 | Fastest, but high forces |
| **InsertionNet** | 0.1178 | 0.6173 | 0.7481 | 0.7406 | 0.4652 | Moderate duration, lower forces |

*Table I* (PEG‑IN‑HOLE, Physical Robot).  
**Claim:** Force‑controlled approach achieves minimal contact forces at cost of time; Position‑controlled fastest but with high forces (highlighted by \(E_z,E_{xy}\)).  
**Proof:** Table I and Fig. 7 show normalized metrics; 100 runs each.  

**Simulation Comparison**:  
- Randomised MuJoCo contact parameters + sphere‑based mesh decomposition reproduce force statistics observed on real robot (Fig. 9).  
- For fixed hold‑over (0.1 mm tolerance, roughness Ra 50 µm–100 µm), sphere‑based decomposition yields mean/max forces close to real values (Fig. 11) whereas VHACD/COACD overshoot the maximum by 20%–35%.  
- **Claim:** Sphere‑based decomposition improves sim‑to‑real fidelity.  
- **Proof:** Fig.9, Fig.11.  

Execution times (Fig. 10):  
- Fine mesh (2000 spheres, 1 mm radius) increases per‑time‑step cost factor ~1.7–2.0 relative to coarse VHACD.  

**Cloud‑Accelerated Scaling** (Table II):  
- Sequential: 14.9 h for Large Net + Simple Sim.  
- 1 node parallel: 0.69 h.  
- 3 nodes: 0.18 h.  
- **Claim:** Kubernetes cluster drastically reduces simulation time.  
- **Proof:** Table II.  

---

## Discussion & Analysis  

1. **Quality‑Aware Metrics**:  
   - Figures 7 & Table I demonstrate that only success‑rate would hide distinctions; e.g., all approaches succeed (~100%) but comparative force energy and smoothness heavily differ.  
2. **Randomized Contact Parameters**:  
   - The param ranges (solref, solimp, friction) produce a distribution of maximum forces that aligns with real measurements (Fig. 9).  
3. **Mesh Decomposition**:  
   - Sphere‑based method increases contact points, enabling smoothed contact surface; VHACD/COACD have high sensitivity to down‑scale; small deviations affect the maximal force due to a coarse discretisation.  
4. **Learning‑Based Approach**:  
   - InsertionNet handles multi‑modal input but uses indirect force‑control; hence lower force smoothness than force‑controlled.  
5. **Scalability**:  
   - Micro‑service containers plus Kubernetes cluster demonstrate the system can run thousands of trials in parallel with minimal serial overhead.  
6. **Reproducibility**:  
   - All containers share same code base; ROS2 interface standardises real‑robot communication.  

---

## Conclusions  

QBIT offers a **quality‑enriched** benchmark for insertion tasks, capturing force‑based metrics and smoothness, thereby enabling industrial‑level evaluation.  Its **cloud‑native** design (micro‑service, Kubernetes, ROS2) removes research entry barriers.  Sphere‑based mesh decomposition and contact‑parameter randomisation effectively narrow the sim‑to‑real gap, confirmed by close alignment of simulated and real forces.  Extensive simulation can be executed at scale thanks to the batch pipeline.  Future work will target **router‑agnostic** support, **bundle** wider contact‑rich manipulation tasks, and an improved rendering backend.

---

## Key Claims & Contributions  

| Claim | Substantiation |
|-------|-----------------|
| *Quality metrics expose performance differences beyond success rate.* | Table I, Fig. 7 |
| *Sphere‑based mesh decomposition yields more realistic contact forces.* | Fig. 9, Fig. 11 |
| *Randomising contact parameters reduces sim‑to‑real discrepancy.* | Fig. 9 |
| *Micro‑service architecture supports extensibility & reproducibility.* | Fig. 3, Fig. 4 |
| *Kubernetes‑based cloud acceleration lowers simulation time from 14 h to under 0.2 h.* | Table II |
| *Force‑controlled approach minimizes forces; position‑controlled minimizes time.* | Table I |
| *Learning‑based approach balances low forces and moderate time.* | Table I |

---

## Definitions & Key Terms  

- **Insertion Task**: Robot repeatedly moves an object into a hole or cavity.  
- **MuJoCo**: Physics engine used for contact modeling.  
- **VHACD / COACD**: Standard convex‑decomposition algorithms for mesh contact.  
- **Sphere‑based Decomposition**: Novel method where mesh is replaced by thousands of spheres (radius = 1 mm) that approximate the object surface.  
- **Force Energy (Ez, Exy)**: Cumulative integrated normal/orthogonal force over trial.  
- **Force Smoothness (Sz, Sxy)**: Standard deviation of derivative of force signals.  

---

## Important Figures & Tables  

| # | Figure / Table | Description | Significance |
|---|-----------------|-------------|--------------|
|1|Fig.1|QBIT architecture overview|Shows cloud, quality metrics, containerisation.|
|2|Fig.2|Insertion task formulation, metric arrows|Illustrates variables and force components.|
|3|Fig.3|Software architecture|Containerisation of simulations & real robots.|
|4|Fig.4|Batch scheduling logic|Demonstrates YAML‑driven Kubernetes launching.|
|5|Fig.5|Experimental setups|Real robot, simulation and object diagram.|
|6|Fig.6|Peg‑in‑hole UR5e demo|Visual of actual insertion in real world.|
|7|Fig.7|Metrics heat‑map (simulation & real)|Shows comparisons across approaches.|
|8|Fig.8|Mesh decompositions: VHACD, COACD, sphere|Shows geometry of sphere method.|
|9|Fig.9|Force distributions for param randomization|Sphere yields smaller variance.|
|10|Fig.10|Simulation time vs mesh size|Higher resolution drains more CPU time.|
|11|Fig.11|Avg/Max force & average contacts|Sphere matches real forces.|
|12|Table I|Metrics of peg‑in‑hole on real robot|Quantifies relative performance.|
|13|Table II|CPU/Cluster time for 1000 runs|Demonstrates scaling benefit.|

---

## Limitations & Open Questions  

1. **Robot Portability** – Current implementation supports only the lab robots (UR5e; UR10). Extending to more families (e.g., Kinova, ABB) requires new containerised interfaces.  
2. **Sim‑to‑Real Coverage** – Randomised parameters cover a wide range but cannot guarantee absolute convergence; further statistical validation is needed.  
3. **Rendering** – MuJoCo’s built‑in rendering is limited; future work will integrate external visualization libraries for 3D cameras.  
4. **Real‑World Noise** – Only Gaussian sensor/pose noise considered; additional systematic biases were not modelled.  
5. **Coverage of Complex Geometries** – Only regular shapes (cylinder, USB plug) used; further tests on irregular or compliant objects are planned.  

---

## References to Original Sections (if available)  

- *Figure 1* – Sec. II (“Framework overview”).  
- *Fig. 2,* *Sec. III.A* – Task formulation.  
- *Fig. 3,* *Sec. IV* – Architecture.  
- *Fig. 4,* *Sec. IV.B* – Batching.  
- *Fig. 5,* *Sec. V.A* – Setup.  
- *Fig. 6,* *Sec. V.B* – UR5e demo.  
- *Fig. 7,* *Sec. V.C* – Metric results.  
- *Fig. 8,* *Sec. V.D* – Mesh decompositions.  
- *Fig. 9,* *Sec. V.D* – Force distribution.  
- *Fig. 10,* *Sec. V.D* – Execution time vs mesh.  
- *Fig. 11,* *Sec. V.E* – Real vs sim force.  
- *Table I,* *Sec. V.C* – Peg‑in‑hole metrics.  
- *Table II,* *Sec. V.F* – Cloud scaling.  

---

## Executive Summary / Key Takeaways  

- QBIT’s **quality‑aware metrics** (force energy + smoothness) reveal perceptual differences that success rate alone masks.  
- **Sphere‑based mesh decomposition** combined with **parameter randomisation** achieves closer contact‑force statistics to reality than VHACD/COACD.  
- **Micro‑service + Kubernetes** allows >11× speed‑up for 1000 simulation steps, enabling statistically significant benchmarks.  
- **Learning‑based approaches** yield comparable low forces but longer completion times; deterministic force‑control achieves the lowest forces at expense of time.  
- The framework is **extensible**; new robots or tasks merely require a new container.  

--- 

## Supplementary Material  

- GitHub repository: <https://github.com/djumpstre/Qbit> (contains Dockerfiles, YAML definitions, and benchmarking scripts).  
- No additional appendices.