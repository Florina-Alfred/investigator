## Enabling 5G QoS configuration capabilities for IoT applications on container orchestration platform  
**Author:** Yu Liu, Ericsson Research Stockholm, Sweden  
**Date:** Not specified (paper version)  

---

### Title & Citation  
- **Title:** *Enabling 5G QoS configuration capabilities for IoT applications on container orchestration platform*  
- **Citation (informal):** Liu, Yu. Ericsson Research Stockholm, Sweden.  

---

## Abstract  
- Modern cloud service platforms use container orchestration (e.g., Kubernetes) and often deploy IoT workloads (robotics, XR, SLAM) across device → edge → cloud.  
- 5G networks provide richer QoS primitives (5QIs, QoS flows) that can be requested via the Network Exposure Function (NEF) or AMF.  
- The paper proposes a **Linux‑fwmark‑based** QoS configuration technique that exposes overlay‑network QoS from containers to the underlay 5G network without packet manipulation.  
- A **Container Networking Interface (CNI)** plugin delivers this functionality by piggy‑backing on the standard Kubernetes CNI chain.  
- Validation is performed on a SLAM application (maplab) showing feasibility and measurable impact on performance.  

**Key benefits:** Kubernetes‑native, non‑intrusive, no packet‑header changes, extends bandwidth limits from node to access network, and fully compatible with existing 5G infrastructures.  

---

## Introduction & Motivation  

1. **Container orchestration** (K8s/K3s) is the backbone of modern cloud and edge deployments.  
2. IoT workloads (robotics, XR, SLAM) increasingly migrate to the **device‑cloud continuum**; 5G brings more compute/latency guarantees.  
3. **QoS in 5G** is expressed through *QFI*, *5QI* values, and per‑flow handling; these are requested via **NEF** or **AMF**.  
4. **Gap:** K8s uses overlay networks (VXLAN / IP‑in‑IP / IPSec), which hide pod‑level QoS marks from the physical interface that configures 5G flows.  
5. Existing CNI‑based QoS plugins (bandwidth, NBWguard, SDN‑related) control **local (node‑level)** traffic only; they do not map pod QoS to the *underlay* 5G access network.  
6. Goal: **Bridge** this gap by exposing pod‑level QoS to 5G without altering packet content and preserving Kubernetes' plug‑and‑play nature.  

---

## Methods / Approach  

### 1. Architecture Overview  
- **Figure 2** illustrates:  
  - *UE* (K8s worker) → *Edge/Cloud* over a **5G network**.  
  - Pod QoS tags are inserted into the K8s control plane (via kube-apiserver).  
  - The **kubelet** triggers container runtime, which in turn invokes a chain of **CNI plugins**.  
  - A new **“traffic‑priority” CNI plugin** creates a dedicated IP flow for the pod, then requests the 5G core to set up a 5G QoS flow (via NEF or AMF).  
  - After successful QoS flow creation, the plugin **marks/filters** the pod’s UDP/TCP traffic onto that flow using **Linux fwmark** + `iptables` + `tc`.  

### 2. Linux `fwmark` visibility & availability  
- **Visibility (Fig 3):** When a pod packet leaves via `eth0 → veth pair → bridge → VXLAN interface`, a PREROUTING iptables rule can set a 32‑bit fwmark **before** VXLAN encapsulation. The mark survives through encapsulation and is visible at the egress interface, enabling downstream `tc` to classify it.  
- **Availability (Table I):**  
  - Bits 0‑12, 16‑31 are used by Cilium,  
  - Bits 7, 13, 14‑15, 16‑31 are used by AWS, Calico, etc.  
  - Generic IPv4. `fwmark` bits for user tags are limited; careful selection is required to avoid conflicts.  

### 3. CNI‑plugin flow (Fig 4)  
- **Standard CNI operations:** `ADD`, `DEL`, `CHECK`, `VERSION`.  
- When `ADD` executed:  
  1. Allocate unique fwmark.  
  2. Add `iptables` rule to tag traffic of the pod’s veth interface.  
  3. Request 5G network (emulated via `tc` REST API) to create QoS flow with corresponding *5QI* (inferred from pod annotation).  
  4. Add `tc` filter on physical interface to redirect marked packets to that flow.  
- `DEL` removes all created rules and flows.  

### 4. 5G emulator integration  
- Emulated 5G network built on Linux TC, exposing REST APIs that mimic NEF/AMF.  
- POD‑level QFI → 5QI mapping → TC class/queue set on physical interface.  

### 5. Limitations & Scope  
- Only **egress (uplink)** traffic is signed.  
- QoS enforcement is limited to the **RAN** (UE ↔ gNB ↔ UPF).  
- Does not guarantee QoS in the public Internet beyond the edge server.  

---

## Experiments / Data / Results  

### 1. Implementation details  
- The plugin is written in Go, using the official CNI specification.  
- Tested on **K3s** (Lightweight K8s) on Raspberry‑Pi‑like nodes.  

### 2. SLAM testbed (Fig 5)  
- **Hardware:** Jetson‑NX (device), Jetson‑AGX (edge), blade servers (cloud).  
- **Software:** K3s, Prometheus + Grafana for metrics.  
- **SLAM application:** `maplab` (visual‑inertial mapping).  

### 3. Test scenarios  
- **QoS‑unlimited:** No QoS requested; pods use default 5QI.  
- **QoS‑limited:** Pods annotated to request a 10 ms delay QoS flow; 5G emulator introduces corresponding delay via `tc`.  

### 4. Metrics & Results (Table II)  
| Category | RMSE (cm) | Mean (cm) |
|----------|-----------|-----------|
| QoS‑unlimited | 9.24 ± 0.14 | 8.13 ± 0.16 |
| QoS‑limited | 10.08 ± 0.12 | 8.85 ± 0.11 |
- The 10 ms delay → ∼1 cm higher RMSE and mean error.  
- Demonstrates plugin’s (and underlying 5G emulation) ability to enforce QoS and measurable effect on an IoT workload.  

---

## Discussion & Analysis  

1. **Non‑intrusive QoS mapping:** By using fwmark, no packet bytes are altered; only kernel metadata is used.  
2. **Transparency to existing overlay mechanisms:** Works with VXLAN, IP‑in‑IP, IPSec; no changes needed in those protocols.  
3. **Compatibility with 5G standards:** No modification to CCAP or NEF; simply uses existing NEF/AMF API calls.  
4. **Scalability considerations:**  
   - fwmark bits may become scarce with multiple concurrent CNI plugins.  
   - May need dynamic allocation or segmentation of fwmark space.  
5. **Performance impact:** Benchmarks not reported; future work suggested to quantify CPU, memory, latency overhead of the plugin and TC/iptables rules.  

---

## Conclusions  

- A **K8s‑native, lightweight** solution has been proposed to expose pod‑level QoS requirements to the 5G access network.  
- **CNI plugin + fwmark + TC** enables mapping of pod Egress traffic to dedicated 5G QoS flows (5QI).  
- Validated on a realistic distributed SLAM workload; observed degradation matches expectations from 5G network theory.  
- Future work: quantitative overhead measurements, supporting ingress traffic, handling multiple QoS tags, and broader application benchmarks.  

---

## Key Claims & Contributions  

| Claim | Supporting evidence |
|-------|---------------------|
| **C1**: Pod QoS can be exposed to 5G network using K8s CNI plugin. | Plugin implementation and Linux `fwmark` + `tc` mapping (Sec III.C). |
| **C2**: No packet header manipulation required. | Fwmark is only metadata; packet unaltered (Sec III.B). |
| **C3**: Works across overlay mechanisms (VXLAN/IP‑in‑IP/IPSec). | Visibility analysis (Fig 3); no API changes required. |
| **C4**: Extends K8s bandwidth plugin scope from node to access network. | Plugin creates flow at physical interface (Sec III.C). |
| **C5**: Fully compatible with existing 5G infrastructure. | Uses only NEF/AMF APIs; no 3GPP changes. |
| **C6**: Validated on real SLAM workload, with measurable impact. | Table II, §IV.B. |

---

## Definitions & Key Terms  

| Term | Definition (Author’s wording) |
|------|-------------------------------|
| **K8s/K3s** | Kubernetes → container orchestration platform; K3s is a lightweight variant. |
| **CNI** | Container Networking Interface – plugin mechanism to set up networking for a container. |
| **QoS** | Quality of Service, referring to latency, priority, packet loss etc., in 5G. |
| **5QI** | 5G QoS Identifier—numeric code representing a set of QoS parameters. |
| **QFI** | QoS Flow Identifier – label for traffic within a UE. |
| **NEF** | Network Exposure Function – API for external applications to create 5G QoS flows. |
| **AMF** | Access & Mobility Management Function – manages RAN/UE. |
| **FW Mark** | 32‑bit field used in Linux iptables to tag packets in the kernel. |
| **TC qdisc** | Traffic Control queueing discipline—Linux native queuing system. |
| **VxLAN** | Virtual Extensible LAN – overlay network method. |
| **SLAM** | Simultaneous Localization and Mapping. |
| **MAPLAB** | Visual‑inertial mapping & localization framework. |

---

## Important Figures & Tables  

| # | Figure/Table | Core Message |
|---|----------------|--------------|
|1 | Figure 1 (VXLAN packet anatomy) | Shows encapsulation boundary for overlay/underlay separation. |
|2 | Figure 2 (Architecture) | Shows plugin chain and API interactions. |
|3 | Figure 3 (fwmark visibility) | Demonstrates mark survives encapsulation. |
|4 | Figure 4 (CNI plugin diagram) | Illustrates plugin call flow. |
|5 | Figure 5 (TC qdisc config example) | Shows how fwmark → TC class → delay is set. |
|Table I| fwmark registry | Highlights bit usage by existing software. |
|Table II| SLAM error comparison | Quantifies impact of QoS-limited test. |

---

## Limitations & Open Questions  

- **Ingress traffic** is not handled; extension needed.  
- **Limited fwmark space** when multiple CNI plugins co‑exist.  
- **Overhead measurement**: CPU usage of plugin/iptables/Tc not studied.  
- **Handling of multiple QoS tags** per pod not explored.  
- **Real 5G network verification**: only emulated via `tc`.  
- **Scalability to large clusters** remains to be evaluated.  

---

## References to Original Sections (if available)  

- *Background* – Sec II  
- *Architecture* – Sec III.A  
- *fwmark details* – Sec III.B  
- *CNI plugin flow* – Sec III.C  
- *Experiments* – Sec IV  
- *Discussion* – Sec V  

---

## Executive Summary (Key Take‑aways)  

1. 5G provides per‑flow QoS that IoT workloads can leverage if exposed from orchestration layer.  
2. The paper proposes a CNI plugin that uses Linux fwmark to tag pod traffic, preserving overlay privacy, then maps Pfmark to 5G QoS flow using NEF/AMF.  
3. Experimental validation on a live SLAM benchmark (maplab) confirms the plugin can enforce QoS with expected performance influence.  
4. The solution is Kubernetes‑native, introduces no packet‑header changes, and stays compatible with existing 5G standards.  
5. Future work required to quantify overhead, handle ingress, and test on real 5G infrastructures.  

---  

*End of Summary*