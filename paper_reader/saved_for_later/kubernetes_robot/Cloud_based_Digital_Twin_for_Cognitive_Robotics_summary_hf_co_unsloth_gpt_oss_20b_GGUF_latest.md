**Title & Citation**  
**Title**: *Cloud-based Digital Twin for Cognitive Robotics*  
**Authors**: Arthur Niedzwiecki, Michaela Kümpel, Sascha Jongebloed, Jörn Syrbe, Yanxiang Zhan, Michael Beetz  
**Institution**: Institute for Artificial Intelligence, University of Bremen, Germany  
**Published**: Not formally published; manuscript available through a private repository (see references).  

---

## Abstract  
The authors present a **cloud‑based digital twin learning platform** that enables students and researchers to train and teach concepts of **cognitive robotics** without installing bulky, fragile software locally. By using **Docker** and **Kubernetes** the platform deploys containerised ROS‑based simulation and AI software, coupled with a web‑based **JupyterLab** (note spelling in the paper) integrated with **RvizWeb** and **XPRA**.  Real‑time visualisation of sensor data and robot behaviour is provided in a user‑friendly environment for interacting with ROS applications.  The paper evaluates the platform’s use in teaching Knowledge Representation & Reasoning (KRR), Knowledge Acquisition & Retrieval, and Task‑Executives, and reports successful deployment in several academic courses and a 2023 Fall School.  The authors conclude that the platform is a valuable, **open‑source** tool that promises to **democratise** education and research in cognitive robotics.

---

## Introduction & Motivation  
- **Cognitive robotics** combines engineering, CS, and psychology to make a robot perceive, reason, and act.  
- Complex behaviour is usually divided into perception, motion planning, reasoning, navigation, trajectory calculation, etc.  
- **Barriers**: high hardware/software cost, expert‑only access, steep setup requirements.  
- **Goal**: Build an accessible, cloud‑based **digital twin** (virtual laboratory that mirrors a physical robot environment) to lower the barrier to entry and increase collaboration.  
- **Key benefit**: A digital twin provides a *visual, intuitive* way to see robot–environment interaction, using 3‑D rendering and sensor streams.  

---

## Methods / Approach  
### 1. Containerisation  
- **Docker** is used to package ROS, AI‑applications (CRAM, KnowRob), JupyterLab, RvizWeb, XPRA, and Gazebo into a single image.  
- Each container is an isolated Linux environment → consistent behaviour across diverse hardware. (See Figure 3).  

### 2. Cloud Deployment  
- **BinderHub** (open‑source “reproducible, interactive, sharable” service) builds the image from a “Dockerfile” added to a Git‑repository.  
- Built images are served via **Kubernetes** (the de‑facto standard for container orchestration).  
- The infrastructure can run on major public clouds or a self‑hosted Linux server.  
- Multiple concurrent user sessions are handled by Kubernetes (number of pods can be scaled).  

### 3. Web‑based Development Environment  
- **JupyterLab** (spelled Jupyter in the paper) offers a notebook UI accessible directly from the browser.  
- Inside the notebook users launch ROS nodes (commands, AI‑models, CRAM) and run Python code.  
- Input/Output to ROS is possible from the terminal within the notebook.  

### 4. Real‑time Visualization  
- **RVizWeb** re‑implements ROS’ RViz in a browser‑compatible way.  
- **ROSBoard** is a Jupyter plugin visualising standard ROS data types (laser scans, camera feeds, maps).  
- **XPRA** delivers a lightweight VNC session, enabling Gazebo (3‑D physics simulation) to appear in the browser (Figure 4).  

### 5. Memory & Compute  
- 8 GB RAM is provisioned per user session (≥ ≥ require 8 GB, can be increased for heavier twins, e.g., Unreal Engine).  

---

## Experiments / Data / Results  
- **Deployment**:  
  - Fall School 2021‑2023, IROS 2023, university courses “KI basierte Robotersteuerung” and “Robot Programming with ROS”.  
  - Platform hosted on BinderHub; students opened the URL and received an isolated container instantly.  
- **Effectiveness**:  
  - High participation: Fall School 2023 recorded the *highest ratio of attendance* compared to previous years. (Section V.e).  
  - Students interacted with KRR (KnowRob), KRA (Web Acq./Retrival), and Task‑Executives via CRAM.  
  - Automatic updating: BinderHub rebuilds the container on repository updates, so tutorials stay current.  

---

## Discussion & Analysis  
- **Previous Approach**: VirtualBox VMs with full desktop + ROS; too large to download quickly, limited participation.  
- **Current Approach**: Browser‑based Jupyter notebooks → no heavy local install, immediate access.  
- **Visualization**: Combining RvizWeb, ROSBoard, XPRA achieves near‑real‑time rendering without requiring a full desktop.  
- **Scalability**: Kubernetes scales compute; 8 GB per client is adequate for typical ROS simulations.  
- **Limitations**:  
  - Requires servers to provide GPU/CPU (non‑trivial for heavier physics simulation).  
  - Google Colab blocks WebSocket protocol → visualization fails; GitHub Codespaces resource limits are too small.  
- **Future Work**: Build courses for secondary education; explore other cloud pre‑providers (Codespaces, Colab).  

---

## Conclusion  
- Containerised, cloud‑based digital twin environments remove the hardware barriers for cognitive robotics education.  
- Real‑time 3‑D visualisation in the browser is the key innovation enabling platform‑independent teaching.  
- The open‑source stack (ROS, CRAM, KnowRob, Gazebo, Rviz, XPRA, BinderHub, Kubernetes) produces a reproducible **PaaS** for education and research.  
- While big cloud providers (Amazon, NVIDIA) offer similar services, the focus here is on *free, open‑source* solutions specifically tailored to academic contexts, encouraging broader adoption.  

---

## Key Claims & Contributions  

| Claim | Supporting Evidence |
|-------|---------------------|
| **Claim 1**: The platform eliminates local installation and hardware constraints. | Containerised ROS + JupyterLab in a web URL (Section IV.c; Fig. 3) → users launch with a browser; 8 GB RAM pre‑allocated (Section V.e). |
| **Claim 2**: Real‑time 3‑D simulation can be visualised in the browser. | RvizWeb + ROSBoard + XPRA + Gazebo → visualised in browser (Fig. 4, Section IV.d). |
| **Claim 3**: The platform supports complete cognitive robotics stack (KRR, KRA, Task‑Executives). | Demonstrated in courses (KnowRob, CRAM, KRR tutorials; Section V.a-c). |
| **Claim 4**: Usefulness confirmed by increased participation in Fall School 2023. | Highest attendance ratio compared to previous years (Section V.e). |
| **Claim 5**: The platform is open‑source, enabling widespread adoption. | All software components (ROS, CRAM, Gazebo, Rviz, JupyterLab, BinderHub) are open‑source; container image available via GitHub (References [17], [21]). |

---

## Definitions & Key Terms  

- **Digital Twin** – a running virtual representation of a physical robot/environment.  
- **Semantic Digital Twin (semDT)** – a digital twin enhanced with semantic annotations, allowing autonomous creation of virtual reps; used in examples (pick&place lesson, Fig. 1).  
- **Cognitive Robotics** – robotics where knowledge drives selection, execution, and understanding (Sandini et al. [18]).  
- **ROS** – Robot Operating System, the open‑source middleware for robotic software.  
- **JupyterLab** – web‑based interactive development environment (spelled Jupyter in the paper).  
- **RVizWeb** – web‑integrated version of ROS’ RViz for visualising sensor streams.  
- **ROSBoard** – plugin for visualising ROS data types in Jupyter.  
- **XPRA** – lightweight VNC/remote‑display system enabling Gazebo to appear in the browser.  
- **CRAM** (Cognitive Robot Abstract Machine) – high‑level task‑executive architecture (Doelitzscher et al. [26]).  
- **BinderHub** – open‑source platform that builds Docker images from Git repositories and serves them as self‑contained web services.  
- **Kubernetes** – orchestrator for Docker containers.  

---

## Important Figures & Tables  

| Figure | Content & Significance |
|--------|------------------------|
| **Fig. 1** – Assignment screenshot. Shows pick&place task on left (list of robots) and physics simulation on right (Robot’s believed world state). Illustrates “real‑world vs. simulation” difference. |
| **Fig. 2** – BinderHub architecture. Demonstrates how a user’s request triggers a new Docker container and Kubernetes pod. |
| **Fig. 3** – Containerised application inside Kubernetes. Depicts ROS → AI, JupyterLab, RVizWeb, XPRA; shows board of nodes and used GUI (e.g., `Spawn`, `CRAM` nodes). |
| **Fig. 4** – ROSBoard widget in Jupyter: 3 panes – laser scan, front camera, map; Grafana bottom part shows Gazebo in XPRA VNC overlay. Signifies real‑time combined visualisation. |

---

## Limitations & Open Questions  

1. **Compute Resources** – 8 GB RAM is minimal; heavier twins (Unreal Engine) may require more; GPU provisioning is not discussed.  
2. **WebSocket Restrictions** – Google Colab blocks websockets → visualization fails; other platforms may have similar limitations.  
3. **Widget Compatibility** – RvizWeb and XPRA rely on specific versions of ROS (e.g., ROS1 or ROS2); migration to ROS2 may cause incompatibilities.  
4. **Scalability Across Institutions** – Potential bottleneck in Kubernetes cluster if many simultaneous students; self‑hosted servers need sufficient nodes.  
5. **Long‑term Maintenance** – Continuous updates of ROS packages, CRAM, KnowRob are required; slow or stale dependencies may degrade learning experience.  

---

## References to Original Sections  

- **Section I** – Motivation and vision.  
- **Section II** – Related webs and twin platforms.  
- **Section III** – Background terminology.  
- **Section IV** – Architecture details (containerisation, cloud deployment, Jupyter, RvizWeb, XPRA).  
- **Section V** – Application in courses, KRR tutorials, CRAM.  
- **Section VI** – Challenges and future directions.  

---

## Supplementary Material (if present)  
- Figure 1–4 are the only supplied figures.  
- No tables or additional appendices are available in the manuscript.

---