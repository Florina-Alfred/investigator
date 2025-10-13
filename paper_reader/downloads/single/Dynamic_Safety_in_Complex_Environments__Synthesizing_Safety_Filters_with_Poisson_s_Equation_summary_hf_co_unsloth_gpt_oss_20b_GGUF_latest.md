**Title & Citation**  
*Dynamic Safety in Complex Environments: Synthesizing Safety Filters with Poisson's Equation* – Gilbert Bahati, Ryan M. Bena, and Aaron D. Ames, Dept. of Mechanical & Civil Engineering, California Institute of Technology, Pasadena, CA, USA. 2025.  

---

## Abstract  
The paper proposes an algorithm that constructs **safety functions** for robotic systems operating in dynamically changing, complex environments.  By solving Poisson’s equation on a local occupancy map with Dirichlet boundary conditions and a specially designed forcing term, the resulting function is shown to be a smooth *Control Barrier Function* (CBF).  The authors prove that this safety function yields a forward‑invariant safe set, and demonstrate how the same function can be used within a CBF‑based safety filter to guarantee safe control actions.  Real‑time hardware tests on a Go2 quadruped and a G1 humanoid confirm collision‑avoidance in both static and dynamic obstacle fields.

---

## I. Introduction & Motivation  
- Safe autonomous operation requires a **quantifiable functional description of safety** that can be matched to the system dynamics.  
- Existing popular approaches (Hamilton–Jacobi reachability, MPC, artificial potential fields, CBFs) each have limitations when environments become highly non‑convex or objects have arbitrary shapes.  
- Signed‑distance functions (SDFs) are widely used for safety but suffer from **gradient discontinuities**.  
- The paper’s aim: *synthesize a smooth safety descriptor directly from perception data and the same descriptor can be used for CBF‑based safety filters*.  

---

## II. Methods / Approach  
| Item | Description |
|------|--------------|
| **System model** | Non‑linear control‑affine dynamics: 𝑥̇ = f(x) + g(x) u. |
| **Safety set** | 0–superlevel set of a scalar *safety function* h(x). |
| **Poisson Dirichlet problem** | Δh = f(y),   h |∂Ω = 0. |
| **Forcing function f** | Designed to be **negative** everywhere in Ω, ensuring h ≥ 0 inside Ω. Several constructions discussed: distance‑metric, constant value, average‑flux, and *guidance field* (via Laplace’s equation). |
| **Guidance field method** | Introduce a smooth vector field v that satisfies ∇·v = f. Minimizer of J[h] = ½∫‖∇h−v‖² gives h; boundary flux b(y) ˆn(y) parameterizes desired gradient magnitude on obstacles. |
| **Regularity** | Theorems 4 & 5 guarantee that if f ∈ Ck,α with α∈(0,1) then h ∈ C2+k,α. |
| **CBF proof** | Theorem 1: solution h is a Control Barrier Function; forward invariance follows from Nagumo because Dh=0 on ∂C. |
| **High‑order control** | For outputs of relative degree r≥2, backstepping/CBF‑backstepping is used to construct auxiliary controllers k_i and a composite safety function h_B. Theorem 6 proves forward invariance of a re‑shrunken set C_B. |

---

## III. Experiments / Data / Results  
### 1. Simulations – Double Integrator (2 D)  
- **Domain** Ω: open, bounded, piecewise‑smooth.  
- **Forcing functions** compared: (29) (guidance field) vs traditional SDF.  
- **Outcome**: Trajectories from the safety filter avoid obstacles; the SDF results in undesirable equilibria/excessive “dead‑locks” due to discontinuous gradients.  
- *Figure 4* shows the safe trajectories (middle/right) against the SDF trajectory (left).  

### 2. Hardware – Go2 Quadruped  
- **Perception**: RGB camera → Meta SAM2 segmentation.  
- **Occupancy map**: 2‑D grid, buffer for robot size.  
- **PDE solver**: Successive Over‑Relaxation (SOR) on GPU (GeForce RTX 4070), 120×120 grid, 0.2 – 0.3 ms solve time.  
- **Real‑time Updates**: Poisson safety function h updated at ~10 Hz.  
- **Static obstacle experiment**: Three start‑points → goal, nominal controller versus CBF filter. *Figure 5* shows time‑lapse, safety function, safe paths, and filtered velocity commands. “h” remained > 0 throughout.  

### 3. Hardware – Quadruped & G1 Humanoid in Dynamic Environments  
- **Dynamic obstacles**: moving chair/box, moving dynamic obstacle for humanoid.  
- **Dynamic “h”**: time‑derivative approximated by replacing f(y) with β‖∇h‖^(p−2)∇h.  
- *Figure 6* – Quadruped: true avoidance, “h” > 0.  
- Humanoid: minor safety violations, brief “h” < 0 (see figure).  Indicates less accurate ROM for humanoid compared to quadruped, causing velocity tracking lag.  

---

## IV. Discussion & Analysis  
- **Key Advantage**: Poisson safety functions are **smooth everywhere**, avoiding the sharp ridges of SDFs and thus eliminating chattering in safety filters.  
- **Flexibility**: Guidance field allows assignment of arbitrary boundary flux b(∂Ω), giving differentiated repulsive gradients per obstacle.  
- **Scalability**: Solving Poisson/ Laplace on a grid with SOR + GPU parallelism yields real‑time performance.  
- **Limitations** (Section VII):  
  1. **Unwanted equilibria**: safety filters can dead‑lock if nominal controller steers toward obstacles; remedied by adding a navigation layer.  
  2. **Boundary‑to‑unsafe extension**: h defined only on Ω; extension into obstacle interiors may not preserve Lipschitz continuity of gradient across ∂Ω. Use mollifiers suggested.  
  3. **High‑order systems**: require h ∈ C2+k,α with k≥r−1 (Lemma 1); if not satisfied, may need extra technical assumptions.  

---

## V. Conclusions  
- Introduced a *constructive* algorithm that synthesizes safe sets via Poisson’s equation.  
- The resulting safety function is a CBF, enabling a safety filter for any system obeying a reduced‑order model with known relative degree.  
- Demonstrated real‑time performance on quadruped and humanoid robots in challenging dynamic scenes.  

---

## Key Claims & Contributions  
1. **Construction of safety functions from perception**: given any occupancy map, solve Poisson’s equation with Dirichlet BCs → safe set characterised by 0‑superlevel.  
2. **Safety function is a unique minimizer of a variational problem** – ensures smoothness and lowest‑energy gradient field.  
3. **Theorem 1 & 6**: Prove forward invariance for first‑order and high‑order systems.  
4. **Real‑time implementation**: GPU‑accelerated SOR solver yields 10 Hz updates, outperforming offline methods.  
5. **Hardware demonstrations**: Collision‑avoidance on Go2 quadruped and G1 humanoid in dynamic and static obstacle fields.  

---

## Definitions & Key Terms  
| Term | Formalisation |
|------|---------------|
| *Safety set* C := {x ∈ ℝⁿ | h(x) ≥ 0}. |
| *Control Barrier Function* (CBF) h:ℝⁿ→ℝ satisfying Dh(x)=0 when h(x)=0, and ∃γ∈K∞:  ⟨∂h/∂x, f(x)+g(x)u⟩+γ(h(x))≥0. |
| *Relative degree* r: smallest integer with L_g L_f^{r-1}h ≠ 0 for affine system. |
| *Poisson’s equation* Δh = f(y) on Ω. |
| *Guidance field* v:ℝ³→ℝ³ with ∇·v=f, boundary condition v= b(y) n̂ on ∂Ω. |
| *Dirichlet BC* h|∂Ω = 0. |
| *Hopf’s Lemma* – sign of normal derivative on boundary for super‑harmonic h. |
| *Spherical interior condition* – existence of an interior ball touching boundary at exactly one point. |

---

## Important Figures & Tables  
- **Fig. 1**: Montage of safe‐set synthesis from perception data; video link.  
- **Fig. 2**: Visual comparison of Poisson solutions for various forcing terms (distance‑metric, constant, average‑flux, guidance field).  
- **Fig. 3**: Guidance field generation via Laplace’s equation; shows boundary flux term.  
- **Fig. 4**: Trajectories for double‑integrator simulation; left (SDF), middle/right (Poisson).  
- **Fig. 5**: Quadruped experiment: (a) video, (b) safety function, (c) safe paths, (d/e) nominal vs filtered velocities, (f) safety function evolution (always > 0).  
- **Fig. 6**: Dynamic obstacle experiments: (a/b) quadruped, (c/d) humanoid; marked that “h” remained > 0 for quadruped, brief negative for humanoid.  

---

## Limitations & Open Questions  
- **Equilibria**: proximity to obstacle may trap system; requires supplementary navigation heuristics.  
- **Gradient continuity across safe/unsafe boundary**: no guarantee for magnitude; could be improved by mollifier or smooth extension.  
- **High‑order requirement**: need H¨ older continuity of f up to k to ensure h ∈ C2+k. If f is only Lipschitz, existence still but must verify additional regularity.  
- **Scalability**: While solved efficiently in 2‑D for 120×120 grid, extension to 3‑D (N×N×N grid) would increase ∼N³ complexity; GPU scaling roughly √N, still to be investigated for real‑time on embedded hardware.  
- **Dynamic environments**: currently approximate time derivative via β‖∇h‖^{p-2}∇h; more rigorous dynamic PDE treatment remains an open direction.  

---

## References to Original Sections  
| Section | Content |
|---------|---------|
| I | Introduction & Motivation |
| III | Safety‑set synthesis via Poisson’s equation (definition 4, theorem 1) |
| IV | Forcing function construction (distance‑metric, guidance field) |
| V | Safety‑critical control via Poisson safety functions (Proposition 1, Theorem 6) |
| VI | Experiments: simulations, quadruped, humanoid |
| VII | Limitations |
| VIII | Conclusion |

---

## Supplementary Material  
- **Appendix A**: Detailed theorems on Poisson’s equation (Dirichlet, Gauss, Maximum/Minimum, Regularity, Variational equivalence).  
- **Appendix B**: Formal statement of backstepping for high‑order systems (Theorem 6) and HOCBF variant theory.  

---