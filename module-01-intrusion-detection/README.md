# Module 1: Network Intrusion Detection with Gaussian Anomaly Detection

An unsupervised intrusion detection system for the **CIC-IDS-2017** dataset (2.83M network flows, 15 classes). It models the density of *benign* traffic only, so it is trained on zero attacks, and it flags flows that fall in low-probability regions.

**Report (PDF):** [`Ruthvik_Nath_Bandari_Module1_Lab_Report.pdf`](Ruthvik_Nath_Bandari_Module1_Lab_Report.pdf)
**Notebook:** [`module1_lab_ids_cicids2017.ipynb`](module1_lab_ids_cicids2017.ipynb)
**Presentation:** [`output/Module1_AI_Threat_Mitigation_Submission.pdf`](output/Module1_AI_Threat_Mitigation_Submission.pdf), with speaker notes in [`Module1_Presentation_SpeakerNotes.md`](Module1_Presentation_SpeakerNotes.md)

## Key results

| Model | ROC-AUC | PR-AUC | False-positive rate |
|---|---|---|---|
| Multivariate Gaussian (from first principles) | 0.921 | 0.787 | 20.9% |
| **Gaussian Mixture Model (k = 10)** | **0.966** | **0.930** | **10.3%** |
| Isolation Forest (benchmark) | 0.848 | n/a | n/a |

- 7 of 14 attack families were detected at >90% recall, including every Heartbleed flow, even though the model never saw an attack.
- At a 1% false-positive budget, the detector reached **95.8% precision at 43.6% recall**.
- It struggles with per-flow-normal attacks (SSH-Patator, Bot) and payload-level web attacks. The report analyses why.

## Pipeline
Data audit → cleaning (infinities, NaNs, duplicates, corrupt labels) → signed `log1p` → correlation pruning (69 → 40 features) → quantile transform → density model → threshold chosen by maximising F1 on validation.

## Data
The dataset is **not included** in this repository (~850 MB). Download `MachineLearningCSV.zip` from the [Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/ids-2017.html). Then either place it next to the notebook or upload it when the notebook prompts in Colab; it unzips to `cicids/MachineLearningCVE/`.

## Stack
Python 3 · NumPy · pandas · SciPy · scikit-learn · matplotlib · seaborn
