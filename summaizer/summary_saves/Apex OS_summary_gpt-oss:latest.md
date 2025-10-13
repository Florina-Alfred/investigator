# Summary (gpt-oss:latest)

- **Webinar Overview**
  - Presenter: Thomas Vamperev, VP Business Development at XAI
  - Co‑hosts: Laura (Europe business) and Laya Johnson (engineering, Palo Alto) – Q&A moderators
  - Purpose: Accelerate software development for high‑performance computing (HPC) systems with AI, emphasizing reusability, architecture decisions, calibration, testing, and domain‑specific safety regulations
  - Target industries: Agriculture, medical, robotics, industrial, mobility‑as‑a‑service, marine

- **Agenda Recap**
  - Brief company background
  - Architecture opportunities in HPC systems
  - Customer use‑case demonstrations
  - Q&A session

- **Company History & Philosophy**
  - Founded 2017; roots in 25‑year legacy from Germany
  - Founders: Jan Becker (autonomous driving pioneer, ROS/Willow Garage, SAE level‑5 contributor) & Diane Pagbacic
  - Transition from open‑source to *source‑available* model
    - Transparent source code, commercial license, no GPL/Apache obligations
    - Combines open‑source benefits with commercial support and certification
  - Mission: Deliver safety‑certified, high‑performance software across diverse domains

- **Core Product Suite**
  - **Epic OS**
    - Platform‑independent framework abstracting OS details
    - Supports RTOS (QNX, VxWorks, Linux RT) and SoC platforms
    - Enables safety‑critical applications without vendor lock‑in
  - **Epic Grace (SDK)**
    - Libraries, tools, and safety certification options
    - C++, C++17, 1721, Rust interfaces
    - Safety element out‑of‑context (IEC 61508, ISO 26262, IEC 60601, etc.)
    - Provides deterministic record/replay for AI validation
  - **Epic IDAR (Data Transport)**
    - High‑performance, zero‑copy communication across ECUs, hypervisors, OS, domains
    - Handles protocol translation, bus systems, and mixed‑criticality
    - Throughput ~100 Gbps, low latency; suitable for system‑of‑systems
  - **EPICS Allen (CI/CD)**
    - Automated pipeline: integration, testing, deployment
    - Cloud‑agnostic (Azure, GCP, AWS)
    - Reduces feedback time from months to hours; supports monorepo and model‑build environments

- **Key Technical Highlights**
  - SDK abstracts hardware, focuses on user‑facing functions
  - Deterministic communication and data transport enable safety certification
  - Zero‑copy mechanism reduces CPU load, saves energy, improves latency
  - Record & replay supports reproducible AI training and validation
  - Compatibility with ROS Humble (100 % wire‑level), enabling rapid migration

- **Use‑Case Highlights**
  - **Mobility‑as‑a‑Service** (e.g., Volkswagen Moira)
    - Middleware bridges vehicle, backend, and multiple suppliers
  - **Marine** (Brunswick)
    - Auto‑docking features, real‑time control, safety‑critical messaging
  - **Agriculture**
    - Compute distribution between tractor and implement
    - Legacy protocol support, vendor‑neutral architecture
  - **Medical & Robotics**
    - Safety‑critical control loops, deterministic communication
  - Benefits: Reduced vendor lock‑in, long product life cycles, improved scalability

- **Safety & Certification**
  - Epic Grace and Epic OS provide safety element out‑of‑context
  - Supports IEC 61508 base; ISO 26262, IEC 60601, marine and agricultural safety norms
  - Validation tools: deterministic record/replay, AI safety case generation
  - End‑customer must still adhere to OS safety manuals (e.g., RTOS safety directives)

- **Performance & Efficiency**
  - Benchmark throughput ~100 Gbps, ultra‑low latency
  - Zero‑copy reduces energy consumption on battery‑powered devices
  - Hardware cost savings by distributing compute across multiple SoCs
  - Fast migration: days to weeks for small projects; months for large codebases

- **Global Footprint & Investment**
  - Headquarters: Palo Alto, California; Germany (Stuttgart, Munich)
  - Additional offices: Sweden, Japan, Korea
  - Recent investor: IG (announced last month)

- **Q&A Highlights**
  - **Determinism vs. ROS**: Epic OS offers deterministic, safety‑case ready ROS variant with support and feature customization
  - **Industry‑specific standards**: Uses IEC 61508 as foundation; derives ISO 26262, IEC 60601, etc.; safety element out‑of‑context certification
  - **Timeline impact**: Prototype‑to‑production gap narrowed; hardware & energy savings; reduced feedback cycles
  - **Android integration**: Epic IDAR abstracts communication, handling data formats between Apex OS and Android
  - **ROS Humble support**: Added in 2025 release; 100 % wire compatibility; migration effort minimal
  - **Native OS support**: Develop on Linux; deploy on various RTOS/SoC combos; support matrix provided
  - **Agriculture use‑case**: Compute distribution, vendor neutrality, long life cycles
  - **Build system modularity**: Supports CMake, Bazel, Make, etc.; no mandatory build system
  - **Safety coverage**: Epic OS is a safety element out‑of‑context; end‑customers still must meet OS safety directives
  - **Adoption time**: Weeks for small teams, up to months for large codebases; migration includes architecture review

- **Closing & Next Steps**
  - Thank you from Thomas, Laura, and Laya
  - Future industry‑specific sessions, deep‑dive technical webinars
  - Contact: email, white paper, demo request
  - Feedback encouraged; LinkedIn channel for updates