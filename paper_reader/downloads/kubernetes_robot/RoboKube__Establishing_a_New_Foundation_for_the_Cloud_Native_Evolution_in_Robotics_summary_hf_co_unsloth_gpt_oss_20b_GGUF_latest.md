**Title & Citation**  
*RoboKube: Establishing a New Foundation for the Cloud Native Evolution in Robotics* – Yu Liu & Aitor Hernandez Herranz, Ericsson Research, Stockholm, Sweden, 2025.

---

## Abstract  
Cloud‑native technologies are expanding beyond the traditional cloud domain into the Internet‑of‑Things (IoT) and cyber‑physical systems (CPS), with robotics being a key application. This paper surveys existing cloud‑robotic practices, then introduces **RoboKube**, an adaptive framework that builds a common cloud‑native platform across the device–edge–cloud continuum. RoboKube is built on top of the Kubernetes (K8s) ecosystem and is focused on deploying cloud‑ified ROS 2 applications. It tackles platform‑level concerns (K8s distribution, networking, overlay, ingress), application‑level issues (containerization, clustering, distribution, offloading, migration), and networking challenges in heterogeneous environments. A teleoperation testbed for a UR5 arm demonstrates the feasibility of the approach.

---

## Introduction & Motivation  
- Cloud‑native evolution [1] is defined by the migration from monoliths to micro‑services, from manual to CI/CD, and from static to dynamic, resilient infrastructure orchestrated by Kubernetes.  
- The robotics community’s ROS 2 brings modular, scalable, QoS‑aware, real‑time, and secure middleware that matches the needs of industrial deployments [2].  
- Despite the progress of ROS 2 and container technology (e.g., Docker), “cloudification” of ROS—i.e., integrating ROS with Kubernetes—has been “relatively slow” [3].  
- There is a clear incentive to build a standardized, production‑ready platform that removes the main barriers (networking, multicast discovery, cross‑cluster communication) and ultimately gears the robotics ecosystem toward true cloud‑native operations.

---

## Methods / Approach  

| Component | Purpose | Key Implementation |
|-----------|---------|---------------------|
| **Orchestration** | Manage ROS workloads, scale, failover. | Any K8s‑compatible distribution; preferred: **K3s** (lightweight, fitting edge) – “single‑binary, minimal dependency, K8s‑compatible” (Fig. 1). |
| **Overlay Network** | Hide underlay heterogeneity, enable DDS/RTPS discovery. | CNI plugins such as **Kube‑ovn** (fast UDP/UDP multicast) and **WeaveNet** (works with UDP multicast); overlay must support multicast for DDS. |
| **Ingress / NodePort** | Expose ROS topics/services to external traffic. | NodePort opens 30000‑32767 on every node; Ingress (Traefik/Haproxy) offers single entry point with flexible routing. |
| **Network Policies** | Prevent broadcast flooding, MTU coordination. | • IGMP snooping to avoid unnecessary multicast flood. <br>• Ensure overlay MTU ≤ physical interface MTU – 100 B. |
| **Device Plugins** | Abstract peripheral hardware into K8s resources. | Example: USB joystick allocated via `squat.joystick: 1` (ensures `joy` node only scheduled on node that owns joystick). |
| **Containerization** | Minimal, reproducible ROS execution environments. | 2‑stage Docker builds → `ldd` to identify dependencies → base **ROS₂** image → `DockerSlim` to prune unused libraries. |
| **Helm** | Declarative application deployment, versioning, CI/CD pipeline. | Publish ROS application charts; Helm chart handles rolling‑updates, rollbacks. |

---

## Experiments / Data / Results  

| Experiment | Setup | Findings |
|------------|-------|----------|
| **Image Size Reduction** | joy node: 486 MB → 83 MB | “82 % reduction” (Fig. 3) |
| **UR5 Driver Image** | Original 2.6 GB → 300 MB | “~88 % reduction” |
| **Teleoperation testbed** | Two K3s nodes, 2 subnets; UR5 driver + joystick container | Showed end‑to‑end operation, ability to offload nodes elsewhere. |
| **Overlay Network Feasibility** | Kube‑ovn vs WeaveNet | Kube‑ovn gives better latency/bandwidth. |
| **Ingress Exposure** | NodePort limitation (30000‑32767) prevented port 50001/50002; Ingress solved. |

---

## Discussion & Analysis  

**Claim 1 – RoboKube removes multicast discovery barriers.**  
Supported by the observation that DDS/RTPS performs broker‑less multicast over UDP. An overlay network (Kube‑ovn or WeaveNet) is required to maintain multicast support across device, edge, and cloud nodes. The paper discusses “multicast is supported by the network backend” and explains that without overlay the nodes cannot discover each other.

**Claim 2 – Single‑container-per‑ROS‑node simplifies scheduling.**  
Because ROS 2 nodes cannot change the RTPS port (7400) and all pods share loopback, “each pod should only run a single ROS 2 container” to avoid port conflict.

**Claim 3 – DockerSlim yields significant size savings.**  
Quantified: 486 MB → 83 MB for joy node; “82 % reduction”. Similarly, driver image 2.6 GB → 300 MB.

**Claim 4 – Ingress enables external ROS traffic.**  
Illustrated by the UR5 driver needing ports 50001/50002, which exceed NodePort range. Ingress (Traefik) is therefore suitable.

**Claim 5 – Device plugin for joystick centralizes hardware binding.**  
Demonstrated via resource definition `squat.joystick: 1`, ensuring the joy node always lands on a hardware‑capable node.

**Limitations & Open Questions**  
- **Performance measurement** – only basic latency/bandwidth compare; no quantitative graphs.  
- **Dynamic offloading/migration** – concept discussed but not evaluated.  
- **Security** – no explicit discussion on authentication/authorization in ROS 2 over K8s.  
- **Multi‑cluster** – only one cluster of two nodes described; cross‑cluster details (e.g., VPN, Istio) still “prototyping”.  
- **Scalability** – claim of “cross‑network deployment in complex network environments” remains to be proven at large scale.

---

## Conclusions  
RoboKube offers a pragmatic, Kubernetes‑native framework that unifies ROS 2 deployment across heterogeneous IoT/edge/cloud environments. It supplies: a flexible orchestration distribution (K3s), overlay networking that preserves DDS multicast, minimal image builds via DockerSlim, Helm for reproducible deployments, and device‑plugin‑based hardware binding. The teleoperation testbed illustrates that robots can be fully cloud‑ified while remaining responsive. The authors view RoboKube as “work‑in‑progress” but believe it can bridge the current gap between cloud‑native practice and industrial robotics.

---

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
| **C1 – Cloud‑native Kubernetes is feasible for ROS 2** | Detailed overlay, networking, and deployment discussion. |
| **C2 – Overlay network must support multicast** | ROS 2 DDS relies on multicast; overlay required. |
| **C3 – DockerSlim + two‑stage builds give dramatic image size reductions** | 486 MB → 83 MB; 2.6 GB → 300 MB. |
| **C4 – Helm charts enable CI/CD, patching, and node migration** | Enabled rolling updates and ability to migrate ROS nodes across K8s nodes. |
| **C5 – Device plugins provide hardware‑aware scheduling** | USB joystick bound via `squat.joystick: 1`. |

---

## Definitions & Key Terms  

| Term | Definition | Source |
|------|-------------|--------|
| **ROS 2** | Open‑Source Robot Operating System 2, uses DDS/RTPS middleware, supports QoS, real‑time, security. | [2] |
| **DDS** | Data Distribution Service; middleware for pub‑sub transport. | [Derived] |
| **RTPS** | Real‑Time Publish‑Subscribe, part of DDS; uses UDP multicast. | [Derived] |
| **QoS** | Quality of Service settings (latency, reliability). | [Derived] |
| **MTU** | Maximum Transmission Unit. | [Derived] |
| **CNI** | Container Network Interface – plugin for container networking. | [Derived] |
| **IGMP** | Internet Group Management Protocol – handles multicast group membership. | [Derived] |
| **K3s** | Lightweight Kubernetes distribution; single binary. | [Section III.A] |
| **Kube‑ovn** | CNI providing OVN integration. | [Section III.B.1] |
| **WeaveNet** | CNI that supports UDP multicast. | [Section III.B.1] |
| **Ingress** | Kubernetes resource controlling external traffic into cluster. | [Section III.B.2] |
| **NodePort** | Opens specific port across all cluster nodes. | [Section III.B.2] |
| **Helm** | Kubernetes package manager, templated charts. | [Section IV.B] |
| **DockerSlim** | Tool that prunes unnecessary libraries in Docker images. | [Section IV.A] |
| **Overlay** | Network layer that hides physical topology. | [Section III.B] |

---

## Important Figures & Tables  

| Figure | Description | Significance |
|--------|-------------|--------------|
| **Fig. 1** | “A common platform across the device‑edge‑cloud continuum” – visualises overlay network over heterogeneous backends. | Shows overlay requirement. |
| **Fig. 2** | Teleoperation testbed architecture (UR5 + joystick). | Illustrates hardware placement and teleoperation flow. |
| **Fig. 3** | ROS 2 architecture diagram (nodes + topics). | Highlights that aside from `joy`, all nodes may be distributed arbitrarily. |

---

## Limitations & Open Questions  

- **Scalability**: Only a two‑node cluster is demonstrated; performance at dozens/hundreds ROS nodes not evaluated.  
- **Security**: No discussion on mutual TLS or arrival of QoS caps for cellular/wifi.  
- **Dynamic Offloading**: Paper discusses trade‑off but not implemented.  
- **Cross‑Cluster VPN**: Paper mentions potential but leaves open integration details.  
- **Reliability under lossy WAN**: No measured end‑to‑end latency under cellular network.  

---

## Executive Summary (Optional)

1. RoboKube turns Kubernetes into a ready‑to‑use ROS 2 deployment platform.  
2. It solves multicast‑based DDS discovery by overlaying Kube‑ovn or WeaveNet.  
3. Uses DockerSlim + two‑stage builds to shrink images 82 % – 88 %.  
4. Helm charts manage deployment, upgrades, and enable migration.  
5. Device plugins enable hardware‑aware scheduling (e.g., joystick).  
6. Teleoperation case study proves end‑to‑end function and cross‑cluster feasibility.  

---