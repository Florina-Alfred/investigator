**Title & Citation**  
*Is Deep Learning Safe for Robot Vision? Adversarial Examples against the iCub Humanoid* – Marco Melis, Ambra Demontis, Battista Biggio, Gavin Brown, Giorgio Fumera, Fabio Roli (PRA Lab, Univ. of Cagliari, Italy; Pluribus One, Univ. of Manchester, UK). Accepted for publication at the ICCV 2017 Workshop on Vision in Practice on Autonomous Robots (ViPAR) – see references [21] and [17].

---

## Abstract
The authors evaluate whether deep‑learning based robot‑vision systems (specifically the iCub humanoid) are vulnerable to adversarial examples (AEs). They propose a **computationally‑efficient counter‑measure** based on rejecting anomalous inputs (the “reject option” from open‑set learning). Experiments confirm that the supervised classification stage is easily fooled by minimally visible perturbations (γ₂‑norm ≤ 10). Empirically, they illustrate that the feature mapping produced by ImageNet’s fc7 layer severely violates the *smoothness assumption* – small input changes can cause large jumps in the deep feature space (average distance 2.38). They discuss limitations (real‑world AE creation) and suggest new directions (robust training, data poisoning, formal verification).

---

## Introduction & Motivation  
- Deep learning brings state‑of‑the‑art performance but suffers from **adversarial vulnerability**.  
- **Embodied agents** (humanoid robots) must cope with *direct*, *physical* interactions with humans; a misclassification can have a tangible impact.  
- The iCub uses a **pre‑trained ImageNet CNN** for feature extraction (fc7 features → 4 096‑dim vector) and a separate multiclass classifier that is retrained online.  
- The goal: *assess* the security of such systems *and* propose a simple defense that does **not** require retraining the whole deep network.

---

## Methods / Approach  

### 1. Visíon System Architecture (iCub)  
- Input image (128 × 128 × 3) → ROI cropped around object.  
- Feature extraction: ImageNet‑based deep network → fc7 features `z ∈ ℝ⁴⁰⁹⁶`.  
- Classification: one‑versus‑all linear SVMs (or RLS) acting on `z`.  
- Predicted class `c* = argmax_k f_k(x)` where `f_k` are discriminant functions per class.

### 2. Adversarial Generation Algorithm  
- Extends Biggio et al. (2013) from binary to multiclass.  
- Two settings:  
  * **Error‑generic**: maximize difference between true class discriminant and the highest of the others (`Ω_generic`).  
  * **Error‑specific**: maximize difference between target class discriminant and the highest of the others (`Ω_specific`).  
- Use a simple **gradient‑descent/ascent** update with projection Π onto feasible set (constraint on `‖x–x0‖₂≤d_max` and optional box constraints).  
- **Algorithm 1** (pseudo‑code provided).  
- Gradient of `Ω` computed as `∇_x Ω = (∂f/∂z)(∂z/∂x)`; `∂z/∂x` is available via automatic differentiation, `∂f/∂z` depends on classifier differentiability.

### 3. Counter‑measure: Reject Option  
- Use SVMs with RBF kernels (`f_i(z) = C Σ_j α_j y_j exp(-γ‖z - z_j‖²) + b`).  
- Because RBF discriminants *abate* with distance, they can decide *“reject”* when all `f_i(z) ≤ 0`.  
- Interpret rejection as **anomaly/indistinguishable** input → *new (unknown) class*.  
- Adjust bias threshold to tune false‑negative rate (see Fig. 3).  

### 4. Experimental Setup  
- Dataset: iCubWorld28 (28 object types, 7 per type) → 20 000 images from 4 sessions.  
- Reduced subset: iCubWorld7 (7 objects, one exemplar per type).  
- Classifiers evaluated:  
  1. Linear SVM (SVM).  
  2. RBF SVM (SVM‑RBF).  
  3. RBF SVM + Reject (SVM‑adv).  

- Hyperparameters: `C ∈ {10⁻³,…,10³}`, `γ∈{10⁻⁶,…,10⁻²}` – tuned via 3‑fold cross‑validation.

---

## Experiments / Data / Results  

| Section | Key Result |
|---------|-------------|
| **Baseline** (Fig. 5) | Accuracy drops as number of classes increases; linear vs RBF similar. |
| **Adversarial Vulnerability** (Fig. 6) | Accuracy vs `d_max` (‖Δx‖₂). *SVM* & *SVM‑RBF* degrade smoothly with no defense. *SVM‑adv* maintains higher accuracy up to ~`d_max=5`. |
| **Reject Option Effect** (Fig. 6) | Raising reject threshold raises security (lower AE success) but increases false‑negative on clean samples by ~5 %. |
| **Real‑world AE** (Fig. 7) | Three example images: (a) full‑image AE, (b) minimal perturbation, (c) AE limited to label region (δ sticker). Perturbations appear imperceptible. |
| **Sensitivity Analysis** (Fig. 8) | Random perturbation (‖Δx‖₂=10) gives `‖Δφ‖₂≈0.022`; AE perturbation gives `‖Δφ‖₂≈2.386`. This shows clearest distance in deep space does not relate to input distance – proof of smoothness violation. |

---

## Discussion & Analysis  

- **Blind‑spot vs Indistinguishable AEs**  
  *Blind‑spot:* AE maps to a region far from training data; detection via reject in SVM‑adv.  
  *Indistinguishable:* AE falls into another class’s training cluster; detection impossible without feature‑space retraining.  

- **Why Deep Nets Fail?**  
  *The fc7 layer is highly non‑linear; adversarial direction *lies* near decision boundaries despite small input norm.*  
  *Adversarial AEs produce large jumps in deep space but similar input distance for random perturbations.*  

- **Effectiveness of Defense**  
  *Reject option mitigates blind‑spot AEs, but cannot counter indistinguishable ones.*  
  *Computation cost negligible – identity of derivative of classifier and network available.*  

- **Practicality of Real‑World AEs**  
  *By restricting modification to a small ROI (e.g., sticker on object label), one can manufacture a physical AE.*  
  *Similar to attack of Sharif et al. (2016) on face recognition.*  

- **Related Work Context**  
  *Prior research on minimal‑perturbation AEs (Szegedy et al. 2014) did not examine max‑perturbation strategy or classification‑only defenses.*  
  *Other defenses (open‑set, adversarial filter statistics, stability‑training [31]) are complementary.*  

- **Limitations & Open Problems**  
  *Feasibility of constructing AEs in *full* physical world still an open question.*  
  *Countermeasures that simultaneously guard against indistinguishable AEs and maintain high classification accuracy remain elusive.*  
  *Need for standardised evaluation framework for *robot‑vision* security.*  

---

## Conclusions  
1. **iCub vision system is indeed vulnerable** to adversarial perturbations as small as ‖Δx‖₂≈10 units (imperceptible).  
2. **One‑versus‑all SVM‑adv with reject improves resilience** against blind‑spot AEs by pushing required perturbations higher, but cannot protect against all AE types.  
3. **The deep feature mapping (fc7)** violates smoothness, making indistinguishable AEs inevitable if only the top‑layer is modified.  
4. **Future Directions**: robust training that enforces small output changes for small input changes (e.g., [31]), exploring data poisoning in robot‑learning pipelines, building comprehensive security benchmarking for embedded robotics.

---

## Key Claims & Contributions  
- **Claim:** Robot‑vision systems using pretrained deep networks **for feature extraction** are susceptible to adversarial examples.  
  *Evidence:* Experiments on iCub showing significant accuracy drop even with `d_max=10`.  
 
- **Claim:** A *computationally efficient* attack that maximises confidence subject to an input‑perturbation bound produces AEs that are *harder* to detect than minimal‑perturbation attacks.  
  *Evidence:* Attack algorithm (Algorithm 1) yields higher misclassification rates under same `‖Δx‖₂`.  

- **Claim:** A *reject option* based on SVM‑RBF discriminants mitigates blind‑spot AEs without altering the deep network.  
  *Evidence:* Fig. 6 middle/right plots – reversal in robustness curve.  

- **Claim:** The fc7 mapping of ImageNet **violates smoothness**; small input perturbations produce large deep‑feature distances.  
  *Evidence:* Fig. 8 – 2.386 vs 0.022 for identical input perturbation.  

- **Claim:** Blind‑spot AE detection is feasible; indistinguishable AE detection is not achievable without changing the deep feature extractor.  
  *Evidence:* Empirical mapping of AEs into deep space vs clean data clusters (Fig. 8).  

---

## Definitions & Key Terms  

| Term | Definition |
|------|-------------|
| **Adversarial Example (AE)** | Input `x'` = `x + Δx`, `‖Δx‖₂ ≤ d_max`, whose predicted class differs from the original. |
| **Error‑generic evasion** | AE misclassifies into *any* incorrect class. |
| **Error‑specific evasion** | AE misclassifies into a *pre‑selected* target class. |
| **Reject option** | Classification algorithm can output *“unknown”* if no discriminant exceeds 0. |
| **RBF SVM** | One‑versus‑all support vector machines with radial‑basis‑function kernels. |
| **Smoothness assumption** | In learning theory, a classifier should assign similar outputs to nearby inputs; violated if deep features change abruptly. |
| **Blind‑spot AE** | AE that falls into a region devoid of training samples, misclassifying with high confidence. |
| **Indistinguishable AE** | AE whose deep features are indistinguishable from those of another class. |

---

## Important Figures & Tables  

1. **Figure 1** – Overview of iCub vision pipeline (ROI → ImageNet fc7 → Linear or RBF SVM).  
2. **Figure 2** – Decision boundaries for error‑specific vs error‑generic attacks; illustrates target class selection and input‑perturbation circle.  
3. **Figure 3** – Conceptual flow of SVM‑adv: without defense, with reject option, with tighter threshold.  
4. **Figure 4** – Sample images from iCubWorld28 and highlighted 7‑class subset.  
5. **Figure 5** – Box plots of baseline accuracies vs number of classes (for linear and RBF SVM).  
6. **Figure 6** – Recognition accuracy curves for SVM, SVM‑RBF, SVM‑adv, across `d_max`, separated by error‑specific and error‑generic. Shows improvement with reject.  
7. **Figure 7** – Visual of real‑world AEs across classification, minimal perturbation, and sticker‑like partial perturbation.  
8. **Figure 8** – Conceptual mapping of random vs adversarial perturbations in input and deep spaces; demonstrates huge jump in feature space.  

---

## Limitations & Open Questions  

| Issue | Note |
|-------|------|
| **Physical Realization** | Demonstrated only on images; physical implementation (print‑and‑photograph) remains to be proven yet literature suggests feasibility. |
| **Generalizability** | Only iCub considered; other robot‑vision architectures may differ. |
| **Defense Scope** | Reject option does not mitigate indistinguishable AEs; full protection may need re‑training of feature extractor or multi‑layer analysis. |
| **Model Complexity vs Resources** | Implementation on a low‑power humanoid may still be heavy for full back‑prop; future work can investigate efficient gradient estimation. |
| **Security Evaluation Framework** | No unified benchmark exists for robot‑vision; paper calls for one. |

---

## References to Original Sections  

- **Methodology**: 2 (iCub), 3 (AE Generation), 4 (Counter‑measure).  
- **Experiments**: 5 (overview), 5.1 (data), 5.2 (results), 5.3 (sensitivity story).  
- **Discussion & Conclusion**: 6 (related work), 7 (future).  

---

## Executive Summary / Key Takeaways  

1. **Deep‑feature‑based vision is vulnerable**: even minimal ℓ₂ perturbations mislead iCub.  
2. **New AE algorithm**: maximised‑confidence subject to a *maximum cost* → stronger attacks than minimal‑perturbation methods.  
3. **Reject option counter**: cheaply implemented on top classifier; protects against blind‑spot AEs but not indistinguishable ones.  
4. **Feature‑mapping non‑smoothness**: random noise → tiny feature shift; adversarial noise → large shift – explains vulnerability.  
5. **Real‑world feasibility**: by focusing on a small ROI (e.g., stickers), AEs can be physically fabricated.  
6. **Future directions**: robust feature training, comprehensive security benchmarks for embodied AI, expansion to data‑poisoning scenarios. 

---