## Title & Citation  
**Neural Inverse Rendering from Propagating Light**  
Anagh Malik, Benjamin Attal, Andrew Xie, Matthew O'Toole, David B. Lindell  
University of Toronto & Vector Institute, Carnegie Mellon University.  
[Project webpage](https://anaghmalik.com/InvProp)  

---

## Abstract  
The authors present the **first** system that performs physically‑based, neural inverse rendering from multi‑viewpoint, time‑resolved lidars.  
*Key idea*: a **time‑resolved radiance cache** – a data structure that stores the infinite‑bounce radiance arriving at any point from any direction, eliminating the need for recursive light‑path evaluation.  
The resulting model accounts for both direct and indirect light transport, enabling:  
- state‑of‑the‑art 3‑D reconstruction in the presence of strong indirect light.  
- synthesis of time‑resolved lidar measurements from novel viewpoints.  
- decomposition of captured data into direct and indirect components.  
- novel time‑resolved relighting of captured scenes.  

---

## Introduction & Motivation  

1. **Ultrafast imaging** (LiDAR) measures the time delay of pulsed light backscattered from a scene.  
2. Conventional LiDAR only models **direct** light (single bounce). Indirect light is usually discarded because it is computationally expensive to model via recursive path tracing.  
3. **Indirect light** is a rich source of information on geometry, material, and appearance.  
4. Prior inverse‑rendering from LiDAR results use point‑cloud representations, direct‑only models, or non‑physical formulations, lacking accurate geometry under strong indirect components.  
5. Existing LiDAR or TOF systems underestimate indirect light, resulting in artifacts such as floating features or wrong depth estimates.  
6. *Objective*: to invert **prototypical** time‑resolved measurements from a flash LiDAR while keeping the light transport physically correct, enabling accurate geometry, novel view synthesis, and improved relighting.  

---

## Methods / Approach  

### 1. Physically‑Based Time‑Resolved Rendering  

- **Primary ray**: \(x(t)=o-t\omega_o\).  
- **Objective**: compute outgoing radiance \(L_o(x,\omega_o,\tau)\) along the ray for each time bin \(\tau\).  
- **Rendering equation** (modified for time):

\[
L_o(x,\omega_o,\tau)=\int_{\Omega}f(x,\omega_i,\omega_o)L_i(x,\omega_i,\tau)\,d\omega_i
\]

where \(f\) is the Disney–GGX BRDF.  

- Incident radiance \(L_i\) split into:  

  *Direct component* \(L_{\text{dir},i}\) (simple point‑to‑surface propagation).  
  *Cache component* \(L_{\text{cache},i}\) evaluated via a radiance cache.  

- **Direct light**:

\[
L_{\text{dir},i}(x,\omega_i,\tau)=L_\ell\,\delta(\omega_\ell-\omega_i)\;\frac{1}{\|\!x-x_\ell\!|^2}\;\delta\!\Big(\tau-\,\frac{\|x-x_\ell\|}{c}\Big)
\]

where \(x_\ell\) is the laser position, \(c\) speed of light.

- **Cache evaluation**: secondary rays \(x'(t)=o'-t\omega'_o,\;o'=x,\;\omega'_o=\omega_i\).  
  The cache radiance at \((x,\omega_i,\tau)\) is computed by **time‑resolved volume rendering** of the cached outgoing radiance:

\[
L_{\text{cache},i}(x,\omega_i,\tau)=\int L_{\text{cache},o}\bigl(x',\omega'_o,\tau-\tfrac{t_k}{c}\bigr)\;w_k\,dt_k
\]

\(w_k=\exp\bigl(-\!\int_{t_{k-1}}^{t_k}\sigma(x')\,dt\bigr)\) (transmittance).  

- The **measurement** \(L_{\text{meas},i}\) at the sensor is obtained by rendering the same integral along the primary ray:

\[
L_{\text{meas},i} = \int L_o(x,\omega_o,\tau)\,w_k\,dt_k
\]

### 2. Time‑Resolved Radiance Cache  

- **Geometry network** \(N_{\text{geom}}\) (Zip‑NeRF) outputs density \(\sigma\) and normals \(n\) from position \(x\).  
- **Appearance feature** \(f_{\text{app}}\) produced by a hash‑encoding network \(N_{\text{app}}\).  

- **Direct BRDF** \(f_{\text{dir}}\) decomposed into diffuse \(f_{\text{dir,diff}}(f_{\text{app})\) and specular \(f_{\text{dir,spec}}(f_{\text{app},n,\omega_\ell,\omega'_o)\) components (learned via 2‑layer MLPs).  

- **Indirect caching**: by a split‑sum approximation.  

  *Integrated BRDF* \(f_{\text{indir},\Omega}(f_{\text{app}},n,\omega'_o)\).  
  *Integrated incident radiance* \(L_{\text{indir,i},\Omega}(f_{\text{app}},x_\ell,n,\omega'_o)\).  
  Both are 2‑layer MLPs conditioned on light source position.  

- **Direct cache component** \(L_{\text{cache,dir},o}\) computed directly from \(f_{\text{dir}}\) and geometry.  
- **Indirect cache component** \(L_{\text{cache,indir},o}\) computed via the integrated incident radiance.  

- Finally:

\[
L_{\text{cache},i}(x,\omega_i,\tau)=\!\int\!f_{\text{dir}}(f_{\text{app}},n,\omega_i,\omega'_o)\,L_{\text{cache,dir},o}\,d\omega'_o\\
+\!\int\!f_{\text{indir},\Omega}(f_{\text{app}},n,\omega'_o)\,L_{\text{cache,indir},o}\,d\omega'_o
\]

### 3. Inverse Rendering and Losses  

- **Photometric loss**:

\[
\mathcal{L}_{\text{photo}}=\lambda_{\text{dir}}\!\sum_{\text{dirs}}\!\alpha(L_i)L_i^2
+\lambda_{\text{indir}}\!\sum_{\text{indir}}\!\alpha(L_i)L_i^2
\]

where \(\alpha(L_i)=\frac{1}{\sqrt{1+\beta L_i}}\) (`β`=1–2).  

- Additional regularizers:  

  *Normal loss* \(\mathcal{L}_{\text{norm}}\) to align gradients of density with predicted normals.  
  *Material smoothness* \(\mathcal{L}_{\text{mat}}\).  
  *Proposal, distortion* and mask losses from Zip‑NeRF.  

- **Radiometric prior**: For the cache‑direct and cache‑indirect terms:

\[
\mathcal{L}_{\text{dir/indir}}=\lambda_{\text{dir/indir}}\int g_k(L_i,L_{\text{cache},i}\,dk
\]

where \(g_k\) represent indirect TOF weighting functions; see §B.3 of the paper.  

- **Optimization**: stochastic gradient descent over multi‑resolution hash‑encoded networks, training ~1 day on a single GPU (cf. §5 Discussion).  

---

## Experiments / Data / Results  

| Method  | PSNR  | LPIPS  | SSIM  | MAE  | L1 Depth  | Trans. IOU  |
|----------|-------|---------|--------|-------|------------|--------------|
| T-NeRF | 22.44 | 0.4 | 0.71 | 28.00 | 0.59 | 0.58 |
| FWP++  | 29 | 0.3 | 0.87 | 22.80 | 0.47 | 0.73 |
| **Ours** | 30.99 | 0.31 | 0.89 | 8.45 | 0.21 | 0.76 |

- **Simulated data**: Three small‑scale object sets (Cornell box, pots, peppers) and one room‑scale kitchen scene.  
  - Table 1 (main) contains overall metrics.  
  - Figure 4 shows rendered novel views, recovered normals, per‑frame lidar outputs.  
  - Our method outperforms T‑NeRF (no indirect modeling) and FWP++ (non‑physical modeling).  

- **Captured data**: Four scenes (house, globe, spheres, statue).  
  - Same table as above but with only method columns (no ground‑truth depth/normal).  
  - Figure 5 shows qualitatively better normals for our method versus FWP++ (particularly in walls‑corner and candle‑bottom regions).  
  - Table C‑3 presents per‑scene PSNR, LPIPS, etc.  

- **Relighting** (Fig. 1 & 6): from a captured house scene we flash a 532 nm pulsed laser with a projector‑style pattern.  The time‑resolved cache is conditioned on source position; relighting with new source patterns (C‑V‑P‑R letters) demonstrates physically‑based indirect glow, while novel relights use finely tuned direct/indirect caches.  

- **No LiDAR training data**: We also train on continuous‑wave ToF or simple intensity images (Fig. 7).  The model still recovers detailed direct/indirect patterns, confirming generality.  

### Quantitative Breakdown (Appendix)  

- **Simulated**: Per‑scene scores from Table C‑2 (Pots, Cornell, Peppers, Kitchen).  
- **Captured**: Per‑scene scores from Table C‑3 (House, Globe, Spheres, Statue).  

---

## Discussion & Analysis  

**Limitations**  
- *Physical model over‑constraining*: Compared to FWP++’s flexible caching, our physically‑based formulation sometimes under‑fits captured data where sensor‑model mismatch occurs.  Fine‑tuning on the radiometric loss can reduce but not eliminate gaps.  
- *Training time*: ~1 day per scene on a single GPU due to large time‑resolved vectors, I/O overhead, and memory bandwidth.  Speed‑ups could come from using 3D Gaussian ray tracing or EVER.  
- *Calibration*: Light source and sensor extrinsics are critical; minor mis‑alignment propagates to geometry errors.  

**Open Questions**  
1. Extending to non‑line‑of‑sight imaging (already discussed in related work).  
2. Further improving indirect‑light modeling in more complex scenes (e.g., multiple bounces, specular focusing).  
3. Integrating compressed representations (e.g., learned wavefront spectral sparse representations) to cut training time.  

---

## Conclusions  

The paper presents the **first** physically‑based, neural inverse‑rendering framework that directly exploits time‑resolved lidar measurements to recover accurate geometry, view‑synthesis, and indirect‑lighting relighting.  By coupling time‑resolved radiance caching with a NeRF‑style hash‑encoding, the authors avoid expensive recursive light‑path tracing while keeping a principled physical model.  Experiments on synthetic and real datasets demonstrate state‑of‑the‑art reconstruction error (MAE ≈ 8 mm) and improved handling of indirect light over previous methods.  The approach opens doors for advanced autonomous‑driving, remote sensing, and non‑line‑of‑sight imaging.  

---

## Key Claims & Contributions  

| Claim  | Evidence  |
|--------|------------|
| Time‑resolved radiance caches enable physically‑based inverse rendering of multi‑view LiDAR data.  | Formal derivation (Eq. 5–8) and network implementation (Appendix B). |
| The approach yields **better geometry** (MAE = 8.45 mm) than T‑NeRF and FWP++ on simulated data.  | Table 1, Fig. 4. |
| It accurately **synthesizes time‑resolved lidar frames** from novel viewpoints.  | Fig. 4/5, Table C‑2/3. |
| It can **decompose** captured signals into direct and indirect components and perform time‑resolved relighting.  | Fig. 1, Fig. 6, Table C‑1. |
| It works **without LiDAR supervision** (i.e., by training on continuous‑wave ToF or intensity).  | Fig. 7. |
| It is the **first** system to invert propagation of light in non‑line‑of‑sight contexts using physically‑based models.  | Related‑work discussion (§2). |

---

## Definitions & Key Terms  

- **Flash LiDAR**: Ultrafast pulsed laser illumination + single‑pixel SPAD detector scanning a field of views.  
- **Time‑resolved measurement**: Histogram of photon arrival times (≈ ns‑pulses).  
- **Radiance cache**: A data structure storing incoming radiance per point and direction, avoiding recursive integration.  
- **NeRF**: Neural Radiance Field – MLP that outputs density and view‑dependent color.  
- **Disney‑GGX BRDF**: Disney & GGX micro‑facet shading model (parameters: albedo, roughness, metalness).  
- **Split‑sum approximation**: Integration technique to factor the indirect component into a summed product of integrated BRDF and incident radiance.  
- **Transient intersection‑over‑union (T‑IOU)**: Metric comparing predicted and ground‑truth transient signals.  

---

## Important Figures & Tables  

| Label  | Description  | Significance  |
|--------|---------------|-------------------|
| Fig. 1 |Qualitative preview: view synthesis, relighting, decomposition. |Highlights core contributions.|
| Fig. 2 |Method overview: primary rays, secondary rays (cache), direct/indirect computation. |Visualizes rendering pipeline.|
| Fig. 3 |Hardware acquisition: elevation arm & SPAD scanner, flash LiDAR illumination. |Shows experimental setup.|
| Fig. 4 |Simulated results: novel views, normals, per‑frame lidar. |Shows improved geometry and signal reconstruction.|
| Fig. 5 |Captured results: comparison with FWP++. |Demonstrates better normals under indirect light.|
| Fig. 6 |Relighting with different pulses (letters). |Shows cache’s indirect component handling.|
| Fig. 7 |Training on CW‑ToF and intensity images from only photon data. |Extends applicability beyond LiDAR data.|
| Table 1 |Overall quantitative results (PSNR, LPIPS, etc.). |Direct comparison with baselines.|
| Table C‑1 |Baseline comparison (T‑NeRF, FWP++). |Shows advantage of physically‑based formulation.|
| Table C‑2/C‑3 |Per‑scene results (synthetic/captured). |Detail performance variations.|
| Table D‑1 |Description of captured scenes. |Context for experimental results.|

---

## Limitations & Open Questions  

- **Calibration sensitivity**: Light source placement and SPAD alignment.  
- **Training time**: Computational load from time‑resolved operations.  
- **Model miss‑fit**: Physical simplifications (point light abstraction, limited angular resolution).  
- **Scalability**: Performance on very large scenes or highly reflective environments.  
- **Further usage**: Integration with non‑line‑of‑sight or multi‑bounce handling beyond split‑sum approximation.  

---

## References to Original Sections  

- **Overview**: §2 Overview, Fig. 1.  
- **Physics‑Based Rendering**: §4.1, Eq. 5–8, Fig. 2.  
- **Cache Representation**: §4.2, Fig. 2.  
- **Optimization**: §4.3, Appendix B.  
- **Simulated Results**: §5.1, Table 1, Fig. 4.  
- **Captured Results**: §5.2, Table 1, Fig. 5.  
- **Additional Experiments**: §5.3, Figs. 6–7.  
- **Discussion**: §6, Table C‑2/3.  
- **Limitations**: §6.  

---

## Executive Summary (Key Takeaways)  

- Learned time‑resolved radiance cache integrates global illumination into an inverse‑rendering pipeline without recursive path tracing.  
- Works on a flash LiDAR system with picosecond pulsed laser and scanned SPAD sensor; captures both light source and camera positions.  
- Outperforms Physically‑unconstrained baselines (T‑NeRF, FWP++) on both synthetic and real data.  
- Enables novel view synthesis, indirect‑light decomposition, and time‑resolved relighting.  
- Training takes ~1 day per scene; future work could accelerate with better representations.  

---

## Supplementary Material  

- **Appendix**: Detailed network architecture (Zip‑NeRF proposal, hash‑encoding for appearance and material).  
- **Dataset**: Calibration method (checkerboard intrinsics, COLMAP extrinsics), scene descriptions, light source modeling.  
- **Code & Data**: Available on the project website (https://anaghmalik.com/InvProp).  
- **Additional Figures**: Appendix C (more qualitative results, per‑scene metrics).  

---