# Cloud-Native Intrusion Detection with Gaussian Anomaly Detection

**AI for Cybersecurity — Module 1 Lab**  
Ruthvik Nath Bandari  
Dataset: CIC-IDS-2017 (Canadian Institute for Cybersecurity, UNB)  
Colab notebook: `module1_lab_ids_cicids2017.ipynb`

## Introduction

This lab implements a network intrusion detection system in Google Colab using the anomaly
detection approach of Parisi (2019, ch. 5). Instead of a supervised classifier, the detector
estimates the probability density of *benign* traffic and flags flows in low-probability regions.
The choice is deliberate: a SOC has unlimited normal traffic but few labelled attacks, and a
density model can flag techniques it has never seen. All eight CIC-IDS-2017 capture files were
used — 2.83 million flows, fifteen classes.

## Methodology

A data-quality audit preceded cleaning; each defect drove one preprocessing step.
Headers carried leading spaces; `Fwd Header Length` appeared twice, byte-identical; `Flow Bytes/s`
and `Flow Packets/s` held 4,376 infinities and 1,358 NaNs from division by zero-duration flows;
eight columns were constant; 329,896 rows were duplicates; and the Web Attack labels contained a
corrupt `U+FFFD` byte preventing those families from grouping. Affected rows (0.101%) were dropped
rather than imputed: inventing a flow rate never observed is worse than losing a thousandth of the
data. Cleaning yielded 2,497,980 flows and 69 features.

Three transformations followed. A signed `log1p` compressed the heavy tails of packet counts
and durations, cutting mean absolute skew from 45.3 to 7.3. Features correlating above
|r| = 0.95 with a retained feature were pruned, reducing 69 to 40 — necessary because the model
inverts the covariance matrix Σ, which collinear features make singular. A quantile transform then
mapped features toward normality. All three were fitted on benign training data alone, preventing leakage.

Training received 60% of benign flows and **zero attacks**; validation and test each took 20% of
benign flows and half the attacks. A multivariate Gaussian was implemented from first
principles, computing log p(x) by Cholesky factorisation for stability, with ridge
regularisation ensuring positive-definiteness. The threshold ε was chosen on validation by
maximising F1, since accuracy is useless here — flagging nothing scores 83%.

## Results

The single Gaussian reached ROC-AUC 0.921 but a 20.9% false-positive rate, because it assumes
benign traffic forms one elliptical cloud. Real traffic is multimodal: DNS lookups, bulk downloads
and keep-alives differ. A Gaussian Mixture Model with k = 10, selected on
validation PR-AUC, lifted ROC-AUC to **0.966** and PR-AUC from 0.787 to **0.930** while halving
the false-positive rate to 10.3%. An Isolation Forest benchmark scored worse (ROC-AUC
0.848), confirming the gain came from modelling, not an easy dataset.

Per-family recall exposed a capability boundary aggregate metrics hide. Seven of fourteen families
exceeded 90% recall, including all eleven Heartbleed flows — caught by a model that never saw one.
But SSH-Patator (9.2%), Bot (26.6%) and all three Web Attack families (≤4.8%) were missed. The
cause is structural: brute-force and bot traffic look like ordinary sessions *per flow*,
suspicious only across many flows, while injection attacks live in HTTP payloads flow statistics
never encode. Tightening ε to a 1% false-positive budget gave 95.8% precision at 43.6% recall —
the configuration a SOC would deploy.

## Current trend: cloud-native IDS

This architecture underpins cloud-native detection. Signature-based IDS assumes a stable
perimeter, but containers live for minutes and serverless functions have no host to enrol; a model
of behaviour survives that churn where a rule naming an IP does not. The economics fit too:
fitting is offline, while scoring is one matrix multiply over kilobytes of state — 2.5 million
flows scored in seconds on a free Colab CPU. Amazon GuardDuty and Microsoft Defender for Cloud
apply comparable analytics to VPC flow logs. Because the detector is just a pipeline, a density
and a threshold, it can be versioned, reviewed and CI-tested — the **detection-as-code** practice
now standard in mature SOCs.

## Conclusion

A model trained without a single labelled attack detected most intrusions in held-out traffic, and
the decisive insight was diagnostic rather than algorithmic: recognising that benign traffic is
multimodal produced a larger gain than any parameter tuning. Equally instructive was learning what
the model cannot do — per-family recall turned a good aggregate score into an honest statement of
where this layer belongs. Interrogating a result until its limits are explicit is the habit I most
want to carry into security engineering work.

*Limitations:* CIC-IDS-2017 is testbed traffic from 2017, cleaner than production; rare families
rest on tiny samples; and the training window is assumed attack-free, which a real deployment must
verify.

## References

Canadian Institute for Cybersecurity (2017) *Intrusion Detection Evaluation Dataset (CIC-IDS2017)*.
University of New Brunswick. Available at: https://www.unb.ca/cic/datasets/ids-2017.html
(Accessed: 20 September 2026).

Parisi, A. (2019) *Hands-On Artificial Intelligence for Cybersecurity*. Birmingham: Packt
Publishing. Chapter 5, 'Network Anomaly Detection with AI'.

Pedregosa, F. et al. (2011) 'Scikit-learn: Machine learning in Python', *Journal of Machine
Learning Research*, 12, pp. 2825–2830.

Sharafaldin, I., Lashkari, A.H. and Ghorbani, A.A. (2018) 'Toward generating a new intrusion
detection dataset and intrusion traffic characterization', in *Proceedings of the 4th
International Conference on Information Systems Security and Privacy (ICISSP)*. Funchal,
Portugal: SCITEPRESS, pp. 108–116. doi:10.5220/0006639801080116.
