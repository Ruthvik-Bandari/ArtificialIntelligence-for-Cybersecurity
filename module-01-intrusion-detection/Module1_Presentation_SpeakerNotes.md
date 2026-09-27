# Slide 1: Title

**Title:** Detecting Ransomware Before Encryption: AI-Based Network Anomaly Detection  
**Subtitle:** Balancing Automated Detection with AI Governance  
**Presenter:** Ruthvik Nath Bandari  
**Course:** AI for Cybersecurity, Module 1 Assignment  
**Date:** September 2026

# Slide 2: Introduction

**Heading:** Introduction: Why Ransomware Needs Earlier Detection

- Ransomware appeared in 44% of data breaches in the 2025 DBIR, up 37% year over year (Verizon, 2025).
- The median ransom payment was US$115,000, while 64% of victims refused to pay (Verizon, 2025).
- When attackers disclosed the incident, the average extortion or ransomware breach cost reached $5.08 million (IBM, 2025).
- Question: can AI flag suspicious network behavior before encryption starts?

**Speaker notes:** The 2025 DBIR shows why earlier detection matters: ransomware is common, costly, and still rising. This presentation asks whether network anomaly detection can reveal suspicious behavior before encryption begins.

# Slide 3: Threat overview

**Heading:** Threat Overview: Impact and Pre-Encryption Signals

- Ransomware appeared in 44% of breaches overall and 88% of SMB breaches; attacks rose 37% year over year (Verizon, 2025).
- The median payment was US$115,000. An extortion or ransomware breach disclosed by the attacker averaged $5.08 million (Verizon, 2025; IBM, 2025).
- Ransomware deployment is often preceded by command-and-control activity and lateral movement, creating a window for network detection (CISA et al., 2023).

**Visual:** Bar chart comparing ransomware presence in all breaches and SMB breaches, victim payment and recovery outcomes, and incident costs. Data sources: Verizon (2025), IBM (2025), and Sophos (2025).

**Speaker notes:** The impact is especially severe for smaller organizations. The defensive opportunity appears before encryption, when command-and-control traffic and lateral movement may depart from a network's normal baseline.

# Slide 4: AI solution

**Heading:** AI Solution: Network Anomaly Detection

- Chapter 5 models normal network traffic with Gaussian density and flags low-probability flows as anomalies (Parisi, 2019).
- A benign-only Gaussian Mixture Model (k = 10) reached ROC-AUC 0.9655 on 627,314 held-out flows.
- Recall reached 99.75% for DDoS and 99.60% for PortScan, but only 26.59% for Bot and 9.20% for SSH-Patator.
- The evidence supports an early-warning layer, not a stand-alone ransomware control.

**Visual:** Per-family recall chart from `module1_lab_ids_cicids2017.ipynb`.

**Speaker notes:** My CIC-IDS-2017 lab reproduced the Chapter 5 concept with a benign-only Gaussian Mixture Model. It detected loud, structural attacks almost perfectly, but attacks resembling ordinary sessions remained hard to separate. That limitation is why the model should support, not replace, other controls.

# Slide 5: Current trend

**Heading:** Current Trend: AI Governance for Automated Response

- Threshold choice determines how many threats the system misses and how many benign flows it blocks.
- At a 1% false-positive budget, my GMM delivered 95.8% precision but only 43.6% recall.
- 63% of breached organizations lacked an AI governance policy or were still developing one; one in five reported a shadow-AI breach (IBM, 2025).
- NIST AI RMF provides a structure for documenting risk, monitoring performance, and assigning human oversight (NIST, 2023).

**Visual:** Precision-recall comparison between the maximum-F1 threshold and a 1% false-positive budget.

**Speaker notes:** Thresholds translate model scores into operational consequences. A lower false-positive budget reduced alert burden and increased precision, but missed more than half of attack flows. Governance must document this tradeoff, monitor performance, and keep a person accountable for consequential actions.

# Slide 6: Conclusion

**Heading:** Conclusion: Early Warning with Human Oversight

- Anomaly detection can expose network behavior that precedes ransomware encryption, but coverage varies sharply by attack family.
- My lab showed that model choice and threshold selection are security decisions, not just technical tuning.
- In practice, I would document the threshold, retain an audit trail, and require a named analyst to authorize high-impact actions.

**Speaker notes:** This work changed how I think about security models. A strong aggregate score does not prove broad protection. In my future security engineering work, I want to pair measurable operating limits with human review so automation remains useful, explainable, and accountable.

# Slide 7: References

- Cybersecurity and Infrastructure Security Agency, National Security Agency, Federal Bureau of Investigation, & Multi-State Information Sharing and Analysis Center. (2023). *#StopRansomware guide* (Version 3.0). Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/sites/default/files/2025-03/StopRansomware-Guide%20508.pdf
- IBM. (2025, July 30). *IBM report: 13% of organizations reported breaches of AI models or applications, 97% of which reported lacking proper AI access controls* [Press release]. https://newsroom.ibm.com/2025-07-30-ibm-report-13-of-organizations-reported-breaches-of-ai-models-or-applications,-97-of-which-reported-lacking-proper-ai-access-controls
- Parisi, A. (2019). *Hands-on artificial intelligence for cybersecurity*. Packt Publishing.
- Sophos. (2025). *The state of ransomware 2025*. https://www.sophos.com/en-us/content/state-of-ransomware
- Tabassi, E. (2023). *Artificial intelligence risk management framework (AI RMF 1.0)* (NIST AI 100-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-1
- Verizon. (2025). *2025 data breach investigations report*. https://www.verizon.com/business/resources/reports/2025-dbir-data-breach-investigations-report.pdf
