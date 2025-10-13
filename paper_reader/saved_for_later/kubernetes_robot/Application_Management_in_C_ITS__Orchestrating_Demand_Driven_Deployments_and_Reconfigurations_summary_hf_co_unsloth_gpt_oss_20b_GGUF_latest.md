# **Title & Citation**

**Title**  
Application Management in C‑ITS: Orchestrating Demand‑Driven Deployments and Reconfigurations

**Citation**  
L. Zanger, B. Lampe, L. Reiher, and L. Eckstein, *Application Management in C‑ITS: Orchestrating Demand‑Driven Deployments and Reconfigurations*, IEEE 26th International Conference on Intelligent Transportation Systems (ITSC), Madrid, Spain, 2025, pp. 2719‑2725.  
URL: https://ieeexplore.ieee.org/document/10422370

---

## **Abstract**

The paper presents a *demand‑driven application management* approach that leverages the cloud‑native container orchestration platform Kubernetes to automate deployment, reconfiguration, update, upgrade, and scaling of microservices in cooperative intelligent transport systems (C‑ITS).  The method is built atop RobotKube and ROS 2, and aims to reduce computing load and traffic by executing application lifecycle actions only when demanded by C‑ITS entities.  The authors demonstrate the framework in a collective environment perception case, where an object‑detection–fusion application is spawned, reconfigured, and shut down as vehicles approach or leave an intersection.  Source code is published on GitHub.

---

## **Introduction & Motivation**

- **C‑ITS Context**: Vehicles, roadside units, edge/cloud servers, and control centers form a distributed, data‑sharing network that enables new applications (e.g., collective perception, cooperative decision‑making).  
- **Dynamic & Resource‑Constrained**: Demand for computation and communication changes over time, and many nodes have limited power or bandwidth.  
- **Cloud‑Native Opportunity**: Containerization, microservices, and Kubernetes enable loosely‑coupled, resilient systems.  However, Kubernetes lacks C‑ITS‑specific logic (e.g., deploying only when requested, or configuring services depending on data content).  
- **Prior Work**: RobotKube [6] introduced a general orchestration approach; the current paper fills the missing detail of the *application manager* methodology, adding a fully‑demand‑driven reconciliation chain.  

---

## **Methods / Approach**

### 1. Design Principles for Applications

| Element | Description |
|---------|--------------|
| **Application** | Set of one or more microservices, each packaged into a container image. |
| **Microservice** | Independent, may belong to multiple applications; provides clear interfaces allowing dynamic (re)configuration. |
| **Connector** | Pairs of communication client services; enable data transfer between nodes, dynamically enabled/disabled/configured. |

- **Containerization**: Automated via tools like Docker.  
- **Helm Charts**: Bundle Kubernetes resources; allow parameterization.  
- **Registries**: Store images and charts; support continuous integration.  

### 2. Reconciliation Chain

An extension of Kubernetes’ declarative reconciliation loop:

1. **Event Detector (ED)** – Monitors data patterns using analysis rules; emits a *deployment request* (ROSC 2 action interface).  
2. **Application Manager (AM)** – Interprets the request, selects required microservices and connectors, adds system‑specific configuration, and writes **Custom Resources (CRs)** depicting the *current demand* (via Kubernetes API).  
3. **Custom Operators** – One per CRD; read the CR, consult **bookkeeping** (requester lists), decide whether to deploy, reconfigure, or shut down services, and update the desired state. Linear sequence of steps 1‑3 constitutes the *reconciliation chain*.

### 3. Application Manager

- **Input**: Deployment request from the ED (includes: application name, configs, communications, requesters).  
- **Decisions**: Which microservices to launch, where to place them (node selection).  
- **Output**: Kubernetes Custom Resources in the appropriate namespace.  
- **ROS 2 Action Server**: The AM acts as server; the request is sent via ROS 2 action interface.  

### 4. Custom Operators

- **CRDs**: Define the schema of CRs (application name, configuration, list of requester IDs).  
- **Operator Logic**: Watches CR changes; if desired state changed → compute new desired state → instantiate/ modify Kubernetes resources (Pods, Services, ConfigMaps) accordingly.  
- **Bookkeeping**: In‑memory data structure tracking which requesters currently need a service; used to avoid duplicate deployments and to gracefully shut down when no requester remains.  

---

## **Experiments / Data / Results**

### 1. Use‑Case Setup

| Entity | Node | Connections | Data Flow |
|--------|------|------------|------------|
| CV V₀–V₃ | Cluster node | MQTT to Cloud | Ego data, point clouds |
| RISU S | Edge node | MQTT to Cloud | Ego data, point cloud |
| Edge **E** | Edge node | MQTT to Cloud | Egos, point clouds |
| Cloud | Cloud | - | Ego data |

- **Tools**: k3d for mini‑cluster; ROS 2 for message passing; MQTT for inter‑node communication.  
- **Data**: ROS 2 bags simulating live sensor data (lidar point clouds).  

### 2. Application Components (Fig. 2)

| Service | Role | Deployment Location | Inputs |
|---------|------|---------------------|--------|
| Object Detection | Detects objects from lidar | Edge **E** (on demand) | Point cloud |
| Object Fusion | Fuses lists & poses into one object list | Edge **E** (on demand) | Ego data, object lists |
| Communication Clients | Established pairwise connections | V₀–V₃, S, **E** | - |

### 3. Experiment Procedure

1. Vehicles approach intersection.  
2. ED analyses their poses → emits Deployment Request for Object‑Detection–Fusion.  
3. AM creates CRs; Custom Operators reconcile demand → deploy services.  
4. New vehicles trigger new requests; operators update bookkeeping (add to requester list) instead of redeploying same service.  
5. Vehicles leave → ED sends Shutdown request; CR updated → operators remove from list; when list empty → services shut down.  

### 4. Results (Table II)

- **Bookkeeping**: 4th column shows per service the active requester list at each step.  
- **Demonstrated**:
  - *Demand‑driven orchestration*: AM correctly decides when to deploy or reconfigure.  
  - *Bookkeeping*: Avoids duplicates; services remain until last requester leaves.  
  - *Environment‑specific configuration*: Object‑Fusion service reconfigured at runtime to listen to exactly the needed input topics (ego data + object lists).  
  - *Scalability*: Works regardless of number of CVs; edge server handles computational load.  

---

## **Discussion & Analysis**

- **Correctness**: The experimental data confirms the *reconciliation chain* achieves the declared desired state with no resource waste.  
- **Integration with Existing Systems**: Uses established interfaces (Kubernetes, ROS 2, MQTT) and can plug into existing C‑ITS pipelines.  
- **Comparison to Prior Work**: Extends RobotKube by adding a responsible *application manager* and proving its usability under realistic, dynamic demand conditions.  

---

## **Conclusions**

- The proposed *demand‑driven application management* framework allows C‑ITS infrastructure to deploy, reconfigure, update, upgrade, and scale microservice applications *only when demanded* by system entities.  
- The reconciliation chain built‐on operators and CRDs implements this logic in a declarative, Kubernetes‑native way.  
- Experimental validation with a collective perception scenario demonstrates the key capabilities: demand awareness, bookkeeping, environment‑specific configuration, and scalability.  
- Source code and experimental data are publicly available (GitHub), facilitating reproducibility.  

---

## **Key Claims & Contributions**

| Claim | Evidence / Reasoning |
|-------|----------------------|
| **Demand‑driven orchestration** can be achieved in a large‑scale C‑ITS. | AM and operators process ED requests and reconcile deployments only when new or changed demands appear (Sec. III, Table II). |
| **Bookkeeping** prevents duplicate microservice instantiations. | Requester lists in Table II show services stay active until all requesters removed. |
| **Environment‑specific configuration** of services is possible at runtime. | Object‑Fusion service reconfigures input topics without restart (Table II &Fig. 2). |
| **Scalability** across nodes and entities. | Experiments involved 4 vehicles, roadside unit, edge and cloud; same logic applies independent of entity count. |
| **Implementation and open‑source release** to support reproducibility. | Repository: https://github.com/ika-rwth-aachen/application-manager. |
| **Extension of RobotKube** by providing a detailed application manager methodology. | RobotKube previously lacked AM detail; this paper fills that gap (Sec. II). |

---

## **Definitions & Key Terms**

| Term | Definition |
|------|------------|
| **C‑ITS** (Cooperative Intelligent Transport System) | Network of vehicles, roadside units, edge/cloud servers, and control centers exchanging data and computational resources. |
| **Microservice** | Small, independently deployable service focusing on a single functionality. |
| **Containerization** | Packaging software and dependencies into a lightweight, portable image. |
| **Helm Chart** | Packaging of Kubernetes resources (Deployments, Services, ConfigMaps) with parameterization. |
| **Kubernetes** | Open‑source container orchestration system, managing desired vs. observed cluster state. |
| **Custom Resource** (CR) | User‑defined Kubernetes resource describing application demand. |
| **Custom Resource Definition** (CRD) | Schema for a CR, used by operators. |
| **Operator** | Extension of Kubernetes controller that implements domain‑specific logic. |
| **Kopf** | Python framework for writing Kubernetes operators. |
| **Event Detector** | Component that analyses data patterns and emits deployment requests. |
| **Application Manager** | Component that translates deployment requests into CRs. |

---

## **Important Figures & Tables**

| Reference | Content & Significance |
|-----------|-----------------------|
| **Fig. 1** | Depicts the *reconciliation chain*: ED→AM→CR→Operator→Kubernetes API, illustrating data flow and how demands are translated to desired state. |
| **Fig. 2** | Visualizes the experimental setup: nodes, data flow, and Kubernetes cluster layout (V₀‑V₃, S, E, C). |
| **Table I** | Lists C‑ITS participants, their data flow, and transport layers (MQTT). |
| **Table II** | Shows step‑by‑step bookkeeping progression; central to demonstrating correctness of the reconciliation chain. |

---

## **Limitations & Open Questions**

- **Not Discussed**: Scalability limits (e.g., billions of vehicles), potential failure modes (e.g., network partitions), performance overhead of Kubernetes operators.  
- **Open Questions**: Handling of stateful services, security of demand requests, integration with real‑world traffic of millions of requests.  

---

## **References to Original Sections**

| Mapping | Original Section |
|---------|------------------|
| Application Manager description | §III.C |
| Custom Operators explanation | §III.D |
| Reconciliation chain overview | Fig. 1 (Section III) |
| Experimental design | §IV |
| Use‑case description | Fig. 2 |
| Evaluation results | §V |
| Findings in Table II | §V |
| Code release | ⟨GitHub URL⟩ |

---

## **Supplementary Material**

- Source code repository: https://github.com/ika-rwth-aachen/application-manager  
- Experimental setup reproducible (k3d, ROS 2, MQTT, ROS 2 bags) – available at repo.  
- Build scripts and Helm charts included.

---

# End of Summary