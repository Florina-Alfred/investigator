**Title & Citation**  
*Examining the legibility of humanoid robot arm movements in a pointing task* – Andrej Lúčny et al. (2025)

---

### Abstract  
The authors investigate how well humans can infer the goal of a humanoid robot’s arm movement when only a partial trajectory and social cues (gaze) are available.  Using the 22‑DoF NICO robot, participants watched the robot point to one of seven touchscreen targets.  Robot cues were manipulated in four modes: gaze‑only (G), arm pointing‑only (P), gaze + pointing with congruent direction (GP), and gaze + pointing with incongruent gaze (GPi).  Two trajectory truncations (60 % vs. 80 % of the full reach) were also studied.  Prediction accuracy (bias) and reaction time (RT) were recorded.  The authors tested (i) a *Multimodal Superiority Hypothesis* (H1) that GP yields higher accuracy than unimodal cues and (ii) an *Oculomotor Primacy Hypothesis* (H2) that gaze‑only trials elicit the fastest responses.  Mixed‑effects modelling confirmed both hypotheses: GP reduced bias relative to G or P by about 20–30 mm, and RTs were shortest in G trials.

---

## Introduction & Motivation  
Effective human‑robot interaction (HRI) requires *legible* robot motions—trajectories whose shape and accompanying cues uniquely reveal intent.  Pointing gestures and gaze are two non‑verbal channels that humans naturally use; however, little is known about how observers extrapolate robot intent from *incomplete* movements.  The present study aims to fill this gap by systematically varying the visual (gaze) and motor (arm trajectory) cues available to participants and measuring how accurately and quickly they can predict the robot’s target.

---

## Methods / Approach  

### 3.1 Experimental Environment  
- **Robot**: 22‑DoF NICO (head, shoulders, elbows, wrists, fingers), equipped with eye‑cameras, facial LED arrays, and a speaker.  Arm motions were pre‑computed by a novel gradient‑descent + forward‑kinematics method (Lúčny et al. [8]) to guarantee linear, precise, and repeatable 50‑step trajectories.  
- **Display**: LCD monitor with capacitive touchscreen embedded in a tabletop—seven pre‑defined target points (Fig. 2a).  
- **Monitoring**: Two external USB cameras captured front and side views; a third internal camera recorded the robot’s gaze.  All data and controls were orchestrated by a blackboard‑based software system.  
- **Data availability**: Source code is publicly hosted on GitHub (https://github.com/andylucny/nico2/tree/main/experiment).

### 3.2 Experimental Procedure  
1. Participants received a written/ spoken briefing, then performed the pointing task.  
2. Four cue‑conditions (G, P, GP, GPi) were presented.  
3. For each condition a *trajectory length* was chosen: 60 % or 80 % of the full arm reach.  
4. The order of conditions followed a *batching scheme* to auto‑increase informativeness:  
   - *Batch 1*: G, P60, GP60, GPi60, P80, GP80, GPi80.  
   - *Batch 2*: G, GP60, GPi60, P60, GP80, GPi80, P80.  
5. Each trial consisted of: robot’s cue, a beep cue, and the participant touching the screen with the predicted target within ≤ 2 s.  

### 3.3 Participants  
- N = 28 (11 m/17 f, age 18–35).  All Slovak native speakers; procedure solely in Slovak.  Pilot study (n = 7) verified procedure integrity.

### 3.4 Data Analysis  
- **Bias**: Euclidean distance between participant touch and true target (Equation (1)).  Decomposed into lateral (bias x) and longitudinal (bias y) components.  
- **Reaction Time (RT)**: Interval from cue beep to screen touch.  
- **Statistical Models**: Linear mixed‑effects models (Jamovi 2.6 with GAMLj) with condition as fixed predictor and participant_ID + trajectory as random intercepts.  

#### Equation (1) (Euclidean bias)  
\( \text{bias}_{\text{tot}} = \frac{1}{\sum_{i} \sqrt{(x_{\text{resp},i}-x_{\text{target},i})^2+(y_{\text{resp},i}-y_{\text{target},i})^2}} \)

---

## Experiments / Data / Results  

### Manipulation Check: Trajectory Legibility  
- **paired‑samples t‑test**: 80 % reaches yielded lower total bias (M = 84.8 mm, SD = 21.9) than 60 % reaches (M = 121 mm, SD = 29.2).  
- **t(26)** = 8.78, **p < 0.001**; effect size d = 1.69 (large).  → *Claim 1* (Improved legibility with longer trajectory).

### Multimodal Superiority Hypothesis (H 1)  
- **Mixed‑effects analysis**: Significant condition effect on bias (F(4,5268)=479, p < 0.001).  
- **Post‑hoc (Bonferroni)**:  
  - G vs. P60 t = –13.62, p < 0.001 (G better).  
  - G vs. P80 t = 17.21, p < 0.001 (P80 better).  
  - GP60 vs. P60 t = –23.17, p < 0.001.  
  - GP80 vs. P80 t = –9.26, p < 0.001.  
  - GP60 vs. G t = –9.47, p < 0.001.  
  - GP80 vs. G t = –26.47, p < 0.001.  
> *Claim 2*: Multimodal GP produced a ~20 mm superior accuracy versus each unimodal counterpart.

- **Directional bias**: In G and GP trials, participants exhibited a *lateral* bias opposite the robot arm direction along the x‑axis; this bias was absent in G‑only.  Along y‑axis, a bias toward the robot body indicated under‑estimation of forward reach.

### Oculomotor Primacy Hypothesis (H 2)  
- **RT Mixed‑effects**: Condition effect significant (F(4,5268)=340, p < 0.001).  
- **Post‑hoc**:  
  - G vs. P60 t = –35.27, p < 0.001.  
  - G vs. P80 t = –25.32, p < 0.001.  
  - G vs. GP60 t = –25.38, p < 0.001.  
  - G vs. GP80 t = –21.62, p < 0.001.  
  - P60 vs. GP60 t = 9.90, p < 0.001.  
  - P80 vs. GP80 t = 3.71, p = 0.002.  
> *Claim 3*: RTs were shortest in G conditions; GP trials benefited from the prior gaze priming.

### Figures  
- **Figure 1**: (a) real‑time GUI layout (cameras, robot, touchscreen). (b) Flow diagram of experimental block (sampling, beep, catch‑time).  
- **Figure 2**: (a) schematic of seven target points, with real target (green) and participant touches (red). (b) Mean predictions for G, GP60, GP80. Highlights the bias distance.  
- **Figure 3**: (a) bias bar plot per condition (significant differences indicated). (b) RT bar plot per condition (significant differences indicated).

---

## Discussion & Analysis  

- **Complementary roles of gaze and pointing**: Multimodal superiority shows that observers naturally integrate social (gaze) and spatial (pointing) information to disambiguate intent.  The directional bias analysis suggests that gaze anchors attention horizontally, reducing the lateral over‑reach tendency seen in pointing‑only trials.  

- **Gaze as a rapid cue**: Oculomotor primacy is evidenced by the fastest RTs in gaze‑only trials and the added speed in multimodal ones, implying gaze primes the perceptual system and streamlines the additional processing of pointing.  

- **Trajectory truncation**: Longer trajectories (80 %) allow substantially better prediction, establishing a practical threshold for legible robot motion design.  

- **Future modelling**: The authors propose a Bayesian integrative model to quantify the relative weight gaze and pointing receive during human inference.  This could identify cue‑specific weighting and inform design guidelines for future humanoid robots.

---

## Conclusions  

1. Human observers exploit both gaze and pointing cues to infer robot intent from incomplete arm motions.  
2. Combined (multimodal) cues produce significantly higher accuracy than either cue alone.  
3. Gaze alone is the fastest cue, typifying oculomotor primacy.  
4. Trajectory legibility is markedly improved when 80 % of the full movement is observable.  
5. Spatial bias analysis indicates gaze helps correct lateral over‑reach tendencies of pointing.  

---

## Key Claims & Contributions  

| Claim | Supporting Evidence | Key Implication |
|-------|--------------------|-----------------|
| **Claim 1**: 80 % trajectory reduces bias vs. 60 % | Paired t‑test: t=8.78, p<0.001, Cohen d=1.69 | Robots should extend at least 80 % of a reach for legibility |
| **Claim 2**: Multimodal GP improves accuracy over all unimodal conditions | Mixed‑effects: GP vs. G,GP vs. P60/P80 significant t‑values | In HRI design, simultaneously moving head and arm is more legible |
| **Claim 3**: RT shortest in G; multimodal still faster than P-only | Mixed‑effects: G vs. P60/P80/P60 vs. GP60 etc. | Gaze acts as an attentional prime, reducing processing time |

---

## Definitions & Key Terms  

- **Legibility**: The distinctiveness of a robot’s trajectory that allows observers to unambiguously infer the intended goal.  
- **Bias (x/y)**: Horizontal and vertical components of the Euclidean error between participant touch and true target.  
- **Reaction Time (RT)**: Time from auditory cue to tactile response.  
- **Gaze‑Only (G)**: Robot head directed at target; no arm movement.  
- **Pointing‑Only (P)**: Robot arm moves along trajectory; no head movement.  
- **Multimodal (GP)**: Simultaneous gaze and arm pointing toward target.  
- **Incongruent Gaze (GPi)**: Gaze offset by a small angle from target while arm still points at target.  
- **NICO**: Neuro‑Inspired COmpanion, a 22‑DoF humanoid robot.  
- **Gradient‑Descent Forward‑Kinematics (GDFK)**: Optimization method used to calculate arm joint trajectories.  

---

## Important Figures & Tables  

| Figure | Content & Significance |
|--------|------------------------|
| **Figure 1** | GUI & experimental procedure; helps visualise the experimental setup. |
| **Figure 2a** | Target layout & participant responses; illustrates bias computation. |
| **Figure 2b** | Shows mean predictions by condition; indicates directional bias. |
| **Figure 3a** | Total bias per condition; visual evidence of multimodal superiority. |
| **Figure 3b** | RT per condition; visualizes oculomotor primacy. |

(Refer to the paper for detailed tabulated data; no explicit tables appear in the provided excerpt.)

---

## Limitations & Open Questions  

- **Sample homogeneity**: Only Slovak native speakers aged 18–35; generalizability to other demographics uncertain.  
- **Limited cue set**: Only gaze and pointing were manipulated; other non‑verbal cues (facial expression, body posture) were not studied.  
- **Incongruent condition size**: Only a small gaze offset was used; the robustness across larger offsets remains unknown.  
- **Open problem**: Precise Bayesian weighting of gaze vs. pointing is suggested but not derived; future work will quantify relative cue reliability.  

---

## References to Original Sections  

- **Abstract**: Section* (text prior to §1).  
- **H1/H2 hypotheses**: (§2).  
- **Related Work**: (§2).  
- **Materials & Methods**: (§3).  
- **Experimental Procedure**: (§3.2).  
- **Data Analysis**: (§3.4).  
- **Results**: (§4).  
- **Discussion**: (§5).  
- **References**: §6.

---

## Executive Summary / Key Takeaways (Optional)  

1. Humans predict robot intent from incomplete pointing gestures; legibility improves when 80 % of the reach is visible.  
2. Gaze and pointing cues are complementary: multi‑modal conditions (GP) yield ~20 mm better prediction accuracy than unimodal cues.  
3. Gaze alone is the fastest cue, yielding quickest RTs; it also helps correct lateral bias of pointing.  
4. Trajectory bias analysis indicates gaze anchors horizontal attention and reduces extrapolation beyond the actual target.  
5. Authors propose a future Bayesian model to formalize cue integration and inform robot design guidelines.  

--- 

*All figures, formulas, and numeric results are reproduced verbatim from the source text and anchored to the structures outlined above.*