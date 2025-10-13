**Title & Citation**  
**RobotKube: Orchestrating Large-Scale Cooperative Multi‑Robot Systems with Kubernetes and ROS**  
Lampe, B.; Reiher, L.; Zanger, L.; Woopen, T.; van Kempen, R.; Eckstein, L. (2023) IEEE conference proceedings.  

---

**Abstract**  
Modern cyber‑physical systems (CPS), especially Cooperative Intelligent Transport Systems (C‑ITS), are increasingly defined by the software that runs on them. Micro‑service architectures, where each function is containerised and loosely coupled, are common. However, orchestrating such containers efficiently over the changing, distributed landscape of robots and supporting infrastructure remains difficult.  
RobotKube is an approach that automatically orchestrates containerised ROS‑based services over a Kubernetes cluster. It introduces two plug‑inable components: an **event detector**, which analyses incoming data and triggers high‑level tasks (e.g. application deployment, re‑configuration, or data recording); and an **application manager**, which translates these tasks into concrete Kubernetes workloads. The paper demonstrates an end‑to‑end use‑case in which a cloud‑based operator detects when two automated vehicles approach each other, deploys communication modules, launches a recording application that streams data to a MongoDB, and then shuts everything down when the vehicles separate. The entire setup is publicly available on GitHub.  

---

### 1. Introduction & Motivation  
- CPS such as C‑ITS consist of heterogeneous nodes: vehicles, roadside units, control centres, edge/cloud servers.  
- Software must be **co‑operated** across these nodes and evolve continuously → DevOps necessity.  
- Micro‑service architecture decomposes CPS functionality into fine‑grained, isolated services that communicate via well‑defined protocols.  
- **Containerisation** enables rapid deployment, OTA updates, and isolation; the common choice is **Docker**.  
- **Orchestration** automates deployment, scaling, and lifecycle; **Kubernetes** is the state‑of‑the‑art solution.  
- Kubernetes already offers many features needed in C‑ITS (self‑healing, rolling updates, horizontal autoscaling), but lacks **domain‑specific orchestration rules** (e.g. deploy application *on‑demand* when two vehicles approach).  
- RobotKube extends Kubernetes with containerised components that endow it with knowledge of CPS data and domain‑specific policies.  

---

### 2. Methods / Approach  

#### 2.1 System Architecture (Fig. 1)  
- **Initial cluster configuration**: A set of C‑ITS applications is deployed manually by operators.  
- **Application**: One or several ROS micro‑services with a single purpose.  
- **Operator**: A person or software that manages deployments, configuration, and other cluster‑level tasks.  
- Components undergo **Verification & Validation (V&V)** before being added to an **application registry**.  
- **Operator applications** can react to **developer‑defined events** detected from data flowing in the cluster.  
- **Event detector** → detects events → **application manager** issues Kubernetes workloads → new services are brought up or down.  

#### 2.2 Event Detector (B)  
- **Buffer**: Ring buffer storing recent ROS messages (configurable sliding window).  
- **Analysis**: Periodic scan of the buffer using developer‑supplied rules (e.g. “two vehicles within X m”).  
- **Action plugin**: Executes the consequence of the detected event:
  * *Operator plugin* → requests deployment or re‑configuration via the application manager.  
  * *Recording plugin* → requests data‑recording configuration.  
- Implemented in **C++ ROS node** for high performance.  

#### 2.3 Application Manager (C)  
- Receives a **task description** from the event detector’s operator plugin.  
- **Translates** it into a specific Kubernetes workload (deploy, destroy, re‑configure).  
- Handles **composition of requested applications** from available micro‑services.  
- Can also **re‑configure** or **shut down** existing applications.  
- Acts *optionally*: if resources are insufficient, it resolves conflicts.  
- Implemented in **Python ROS node** via the Kubernetes Python API.  

#### 2.4 Design Principles (Table I)  
1. *Connected agents expose compute nodes to Kubernetes* → nodes may reside in cloud, edge, roadside, or vehicle.  
2. *Application = one or several micro‑services* (e.g. object detection + tracking).  
3. *Operator = person or software* that manages deployments, life‑cycles, configuration.  
4. *Different operator applications manage different application types* (e.g. cloud‑based vs vehicle‑based).  
5. *Each micro‑service packaged into its own container* → independent rollout.  
6. *Applications are node‑agnostic* → deployment migrates to any available node.  
7. *Application updates = update individual container images* → incremental changes.  
8. *Operator applications can deploy other operator applications* → operator application chains.  
9. *Operator applications select appropriate applications from the registry* via task description + guarantees.  
10. *Operator applications resolve conflicts* automatically (e.g. insufficient compute).  

---

### 3. Experiments / Data / Results  

#### 3.1 Use‑case Description (Fig. 2)  
- **Scenario**:  
  - N = 15 vehicles (N≥M).  
  - M = 2 vehicles equipped with lidar generating point clouds.  
  - All vehicles publish pose messages at 100 Hz to a cloud server C via MQTT‑bridged ROS nodes.  
- **Event**: Cloud‑based event detector continuously analyses poses and detects when any two lidar‑equipped vehicles Vᵢ, Vⱼ are within **d_start = 400 m**.  
- **Task**:  
  - Launch a recording application that records poses + point clouds of Vᵢ & Vⱼ.  
  - Cloud‑based application manager:
    - Creates communication modules (ROS‑to‑MQTT bridges).  
    - Spawns recording application in the cloud.  
  - *Recording plugin* stores every frame into a MongoDB without further analysis.  
- **Termination**: When vehicles separate past **d_stop = 500 m**, recording application shuts down automatically.  

#### 3.2 Experimental Setup (Table II)  
| Parameter | Value |  
|-----------|--------|  
| N         | 15     |  
| M         | 2      |  
| f_p (pose) | 100 Hz |  
| f_pc (point cloud) | 10 Hz |  
| d_start | 400 m |  
| d_stop | 500 m |  

- **Cluster**: Kubernetes‑in‑Docker (KinD) producing a virtual multi‑node cluster on a single physical machine, enabling reproducibility.  
- **Communication model**: MQTT broker bridging ROS messages and vice‑versa (cf. Ref. [34]).  
- **Data storage**: MongoDB hosted in the cloud.  

#### 3.3 Quantitative Results & Latencies  
| Stage | Approx. Latency (ms–s) | Key Observations |  
|-------|------------------------|------------------|  
| 1. Communication | Negligible in simulation | Real‑world systems may add 5G / ITS‑G5 delays |  
| 2. Event detection | A few ms (distance check) | Straightforward calculation |  
| 3. Translation to Kubernetes workload | ~100 ms | Composition of application, configuration, etc. |  
| 4. Cluster reconciliation (K8s control plane) | ~5 s | Creation of four MQTT clients + event detector + recording plugin | Dominant latency component |  
| 5. Data storage | 0.5 s for 10 s worth of poses+point clouds | Asynchronous write |  

- **Total time from event to data stored** ≈ **5 s + 0.5 s ≈ 5.5 s**.  
- *Interpretation*: While acceptable for many C‑ITS use‑cases, it limits applicability for latency‑critical functions (e.g. collision avoidance).  

#### 3.4 Observed Behaviour  
- Event detector triggers precisely at 400 m separation.  
- Application manager successfully selects appropriate micro‑services and deploys them on available cloud nodes.  
- MongoDB shows continuous stream of pose & point cloud data during the 100 s recording window.  

---

### 4. Discussion & Analysis  

- **Event‑driven orchestration** decouples data analysis from deployment rules, enabling flexible domain‑specific policies.  
- **Latency profile** indicates that **cluster reconciliation** dominates overhead. Strategies such as *pre‑launching idle containers* or *hot‑starting* could reduce this further.  
- **Scalability**: With only 15 vehicles but 7 nodes in the cluster, the approach scales comfortably; in real deployment, vehicles and roadside units would become more nodes.  
- **Fault tolerance**: Kubernetes’ self‑healing ensures that if a node dies, the event detector/application manager will re‑schedule workloads on healthy nodes.  
- **Verification & Validation**: By requiring registry placement after V&V, the system guarantees that only compliant services are orchestrated.  
- **Observability**: The system leaves all data in the Kubernetes cluster as POD logs and Fluent‑d logs, making inspection and debugging straightforward.  

---

### 5. Conclusions  

RobotKube demonstrates that large‑scale cooperative multi‑robot CPS can be automatically orchestrated using Kubernetes together with ROS. The **event detector** and **application manager** decouple domain‑specific policy from underlying infrastructure. The experimental use‑case illustrates the ability to deploy communication modules and a recording application on demand, capture rich data, and shut down after the event horizon. Latency measurements show that the major delay originates from cluster reconciliation; while acceptable for many C‑ITS scenarios, it imposes limits for ultra‑low‑latency use‑cases. Future enhancements (pre‑launch, stateless communication) are expected to widen applicability.

---

### 6. Key Claims & Contributions  

**Claim 1:** *RobotKube extends Kubernetes with containerised ROS components to orchestrate containerised micro‑services in large‑scale C‑ITS.*  
_Support:_ System architecture (Fig. 1), event detector + application manager components detailed in Sections 2.2–2.3.  

**Claim 2:** *The event detector can detect developer‑defined data patterns and trigger high‑level tasks such as application deployment or re‑configuration.*  
_Support:_ Explanation of buffer, analysis, and action plugin (Section 2.2).  

**Claim 3:** *The application manager translates tasks into Kubernetes workloads, compositions from micro‑services, and manages their lifecycle.*  
_Support:_ Section 2.3 content, translation description.  

**Claim 4:** *RobotKube was successfully evaluated in an example where cloud‑based detection of vehicle proximity triggers deployment of recording and communication modules.*  
_Support:_ Setup (Section 3.1, Table II) and results depiction in Fig. 2.  

**Claim 5:** *The largest latency observed was 5 s due to cluster reconciliation, limiting applicability to non‑critical‑latency scenarios yet acceptable for many C‑ITS processes.*  
_Support:_ Latency table in Section 3.3.  

**Claim 6:** *All code, Docker images, and configuration are publicly available, allowing reproducibility and reuse.*  
_Support:_ Supplementary Material, GitHub repo mention.  

---

### 7. Definitions & Key Terms  

- **Cyber‑Physical System (CPS)** – interconnected hardware and software capable of sensing and actuation (e.g. autonomous vehicles).  
- **Co‑operative Intelligent Transport System (C‑ITS)** – a CPS focusing on automated and connected transport.  
- **Micro‑service architecture** – software divided into fine‑grained, isolated services communicating via defined protocols.  
- **Containerisation** – encapsulation of an application and its dependencies into a lightweight, isolated unit (Docker).  
- **Orchestration** – automated deployment, scaling, and management of containerised services.  
- **Kubernetes (pronounced “kubernetes”)** – open‑source orchestration platform widely used in industry.  
- **Robot Operating System (ROS)** – open‑source middleware for robot software, providing messaging, parameter handling, and tools.  
- **Event detector** – component that buffers, analyzes incoming data, identifies events, and triggers action plugins.  
- **Action plugin** – part of an event detector that implements the outcome of an event (e.g. request to application manager).  
- **Application manager** – translates application‑level tasks into specific K8s workload definitions and manages deployment.  
- **Operator application** – a software application that uses RobotKube components to orchestrate cluster operations automatically (e.g. event detection + application management).  
- **Recording application** – application that stores ROS messages into a database (MongoDB in the experiment).  
- **Event** – developer‑defined data pattern that must trigger a cluster‑level action.  
- **Pod** – K8s unit that runs one or more containers; corresponds to a ROS monolith in RobotKube.  
- **Verification & Validation (V&V)** – tests ensuring an application functions as intended before registry insertion.  

---

### 8. Important Figures & Tables  

- **Figure 1** – System architecture diagram: cluster nodes, applications, operators, registries, data flows.  
- **Figure 2** – Experimental setup illustration: ROS messages, event detector, task description, application manager, spawned workloads, and data storage schematic.  
- **Table I** – Design principles of RobotKube: 10 bullet points (see Section 2.4).  
- **Table II** – Experimental parameter values used in the demonstration (N, M, f_p, f_pc, d_start, d_stop).  

---

### 9. Limitations & Open Questions  

- **Latency bottleneck**: 5 s cluster reconciliation limits use‑cases requiring sub‑second response.  
- **Communication realism**: Current simulation uses KinD with negligible network delays; real deployments would add wireless latencies.  
- **Scalability to high‑vehicle counts**: Demonstrated with only 15 vehicles; future research needed for larger fleets.  
- **Pre‑deployment strategy**: Assess effectiveness of keeping “hot” containers idle to shorten start‑up times.  
- **Security & isolation**: Field‑tests required to evaluate container isolation in safety‑critical applications.  

---

### 10. References to Original Sections  

| Claim / Item | Original Section | Figure / Table |  
|--------------|------------------|----------------|  
| Abstract | Abstract | – |  
| Design principles | III.A | Table I |  
| Event detector functionality | III.B | – |  
| Application manager functionality | III.C | – |  
| Use‑case logic | IV | Fig. 2 |  
| Latency measurements | V | Table II |  

---

### 11. Executive Summary (Optional)  

1. RobotKube marries Kubernetes and ROS for large‑scale C‑ITS orchestration.  
2. Introduces event detector & application manager to translate data patterns into workload changes.  
3. Demonstrated via a cloud detector that deploys communication, recording, and MongoDB persistence when two vehicles approach.  
4. Latency dominated by K8s reconciliation (~5 s).  
5. Full source (Docker images, Kubernetes configs) released on GitHub for reproducibility.  

---

### 12. Supplementary Material (if present)  

- **GitHub repository**: https://github.com/ika-rwth-aachen/robotkube  
  - Contains Dockerfiles, Kubernetes manifests, ROS nodes, experiment replay scripts, and README.  
- **Reproducible experiment**: Docker images for vehicles, operator, recording, and database; all run on a single machine using KinD.  

---