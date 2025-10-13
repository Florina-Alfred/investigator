# Summary of:  
**A generic approach for reactive stateful mitigation of application failures in distributed robotics systems deployed with Kubernetes**

---

## Title & Citation
**Title:** A generic approach for reactive stateful mitigation of application failures in distributed robotics systems deployed with Kubernetes  
**Authors:** Florian Mirus, Frederik Pasch, Nikhil Singhal, Kay-Ulrich Scholl  
**Affiliation:** Intel Labs, Karlsruhe, Baden-Württemberg, Germany  
**DOI/Reference:** Not provided in the text

---

## Abstract
Offloading computationally expensive algorithms to the edge or cloud is an attractive option to overcome limitations in on-board computational and energy resources of robotic systems. However, complex robotic systems interacting with the physical world pose unique challenges not addressed by existing cloud-native failure mitigation approaches. This paper proposes a novel, application-agnostic, reactive stateful failure mitigation system for distributed robotic systems deployed using Kubernetes (K8s) and ROS2. The system employs Behaviour Trees to enable arbitrary complexity in monitoring and mitigation strategies. It preserves the last healthy state of the robotic system before a failure and allows recovery without disrupting task execution. The approach is validated on two example applications: Autonomous Mobile Robot (AMR) navigation and robotic manipulation in a simulated environment.

---

## Introduction & Motivation
Modern robotics increasingly relies on cloud-native technologies like Kubernetes and ROS2 to manage complex, distributed systems. However, traditional cloud-native failure mitigation approaches are not suitable for robotics due to the real-time interaction with the physical world. The paper addresses the need for stateful, reactive failure mitigation in distributed robotics systems, which can preserve the last healthy state and resume tasks seamlessly after a failure. The key contributions are:
1. A stateful, reactive failure mitigation system based on Behaviour Trees.
2. A robotics-specific workload monitoring system using introspection and external supervision.
3. Recovery strategies balancing system downtime and computational resource usage.

---

## Methods / Approach
The paper proposes a system that combines:
- **Monitoring System:** Uses introspection (monitoring system diagnostics and KPIs) and external supervision (sensor data and behavioral analysis).
- **Failure Mitigation:** Based on Behaviour Trees to encapsulate complex strategies, allowing for arbitrary complexity in recovery.
- **State Recovery:** Preserves the last healthy state of the system and transfers it after recovery.
- **Recovery Strategies:** Four strategies are presented, each with different trade-offs between recovery time and resource usage.

---

## Experiments / Data / Results
### Experimental Setup
The approach is validated on two applications:
1. **AMR Navigation:** Using Turlebot 4 and WidowX-200 robotic arm in Gazebo.
2. **Robotic Manipulation:** Using ROS2 frameworks Nav2 and MoveIt2.

### Recovery Time and Resource Usage
- **Recovery Time (t_recovery):** Composed of detection, cluster-level mitigation, and application-level reinitialization.
- **CPU Usage:** Measured using CAdvisor, with strategies like "restart from scratch" consuming the least resources but being the slowest.
- **Fallback Workloads:** Strategies using initialized fallback workloads offer faster recovery but consume more resources.

### Key Findings
- **Fallback in Execution Mode:** Fastest recovery but highest resource usage.
- **Uninitialized Fallback:** Offers a good balance between downtime and resource usage.
- **Scaling Considerations:** For large fleets, uninitialized fallbacks are more efficient due to lower resource overhead.

---

## Discussion & Analysis
The proposed approach is a significant step towards making distributed robotic systems resilient against application failures. It provides a flexible and scalable solution that can be adapted to various robotic tasks. The use of Behaviour Trees allows for the encoding of complex monitoring and mitigation logic, which is essential for handling the dynamic and unpredictable nature of robotic systems interacting with the physical world.

---

## Conclusions
The paper presents an application-agnostic, reactive stateful failure mitigation system for distributed robotic systems using Kubernetes and ROS2. The system preserves the last healthy state of the system, enabling seamless task resumption after failures. The approach is validated on two applications, demonstrating its effectiveness and flexibility. Future work includes extending the system to handle microservice-oriented architectures and integrating it into larger orchestration solutions.

---

## Key Claims & Contributions
1. **Application-Agnostic Failure Mitigation:** Based on Behaviour Trees, allowing for arbitrary complexity in monitoring and mitigation strategies.
2. **State Preservation:** The system preserves the last healthy state of the robotic system before a failure and resumes tasks seamlessly.
3. **Recovery Strategies:** Four strategies are presented, each with different trade-offs between recovery time and computational resource usage.
4. **Validation on Real-World Applications:** Demonstrated on AMR navigation and robotic manipulation in a simulated environment.

---

## Definitions & Key Terms
- **Kubernetes (K8s):** A container orchestration platform used to manage and scale containerized applications.
- **ROS2 (Robot Operating System 2):** A middleware for robotics software development, providing tools for communication, hardware abstraction, and device drivers.
- **Behaviour Trees:** A decision-making structure used in robotics and AI to represent complex control logic in a structured and readable format.
- **Stateful Failure Mitigation:** A method to preserve the state of a system before a failure and resume operations from that state.
- **Introspection Monitoring:** Monitoring internal system metrics and KPIs to detect failures.
- **External Supervision:** Monitoring the system's behavior using external sensors and comparing it with expected behavior.
- **Fallback Workloads:** Secondary workloads that can take over in case of a failure.

---

## Important Figures & Tables
- **Fig. 1:** High-level overview of the monitoring and failure mitigation system.
- **Fig. 2:** Factors and possible weights for selection of Failure Monitoring and Mitigation Strategy.
- **Fig. 3:** System Architecture.
- **Fig. 4:** Example Behaviour Tree for a mobile manipulator.
- **Fig. 5:** Required steps for the different failure mitigation strategies and their trade-off in terms of failure mitigation time and resource usage.
- **Fig. 6:** Evaluation of failure recovery approaches regarding necessary time for failure mitigation.
- **Fig. 7:** Experimental evaluation of failure recovery approaches regarding CPU load.
- **Fig. 8:** Navigation: Experimental evaluation of failure recovery approaches regarding necessary time for failure mitigation.

---

## Limitations & Open Questions
- **Assumption of Single Container Workloads:** The current approach assumes workloads run in a single container, but real-world systems may involve multiple microservices.
- **Complex Dependencies:** The paper highlights the need to consider interdependencies between microservices in failure mitigation.
- **Future Integration:** The system needs to be integrated into larger orchestration solutions that can also reschedule containers and resources.
- **Scalability for Large Fleets:** While the approach is scalable, further research is needed to optimize resource usage in large fleets.

---

## References to Original Sections
- **Section I:** Introduction and Motivation
- **Section II:** Related Work
- **Section III:** Stateful Failure Mitigation
- **Section IV:** Experiments
- **Section V:** Discussion

---

## Executive Summary / Key Takeaways
- **Problem:** Distributed robotic systems face unique failure mitigation challenges not addressed by cloud-native solutions.
- **Solution:** A stateful, reactive failure mitigation system based on Behaviour Trees, preserving the last healthy state.
- **Approach:** Combines introspection and external supervision for monitoring, and four recovery strategies for mitigation.
- **Validation:** Demonstrated on AMR navigation and robotic manipulation in a simulated environment.
- **Key Findings:** Fallback workloads in execution mode offer the fastest recovery but require more resources; uninitialized fallbacks offer a good balance.
- **Future Work:** Extend to microservice-oriented architectures and integrate into orchestration solutions.

---

## Supplementary Material
- **Scenario Execution for Robotics:** A library for translating Behaviour Tree descriptions into Python-based execution.
- **OpenSCENARIO V2.0:** A standard for describing scenarios used in robotics and autonomous systems.
- **Kubernetes Resources:** Information on deployments, network policies, and stateful sets for container management.

---

## References to Original Sections (if available)
- **Section I:** Introduction and Motivation
- **Section II:** Related Work
- **Section III:** Stateful Failure Mitigation
- **Section IV:** Experiments
- **Section V:** Discussion

---

## Supplementary Material (if present)
- **Scenario Execution for Robotics:** A software library for running reproducible robotics experiments and tests.
- **OpenSCENARIO V2.0:** A standard for describing scenarios used in robotics and autonomous systems.
- **Kubernetes Resources:** Information on deployments, network policies, and stateful sets for container management.