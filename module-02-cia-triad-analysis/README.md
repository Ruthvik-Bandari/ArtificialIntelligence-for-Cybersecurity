# Module 2 Assignment: CIA Triad Analysis of the IDScan.net Breach

A 7-slide threat analysis of a real 2026 incident reported by Krebs on Security. A dark-web service called **Nexus** sold scans of **153M+ U.S. and Canadian driver's licenses**, taken in a year-long, low-and-slow data exfiltration from the ID-verification vendor IDScan.net.

**Slides (PDF):** [`Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pdf`](Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pdf)
**Slides (PowerPoint, with speaker notes):** [`Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pptx`](Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pptx)

## Analysis at a glance

| CIA element | Severity | Why |
|---|---|---|
| Confidentiality | **Severe** | 153M+ license images (front, back, IR, UV) copied and sold; unlike passwords, identity data can't be reset |
| Integrity | High | Forgery-grade scans let criminals pass ID checks, so a "verified" ID no longer proves identity |
| Availability | Low | No reported outage; indirect cost from credit freezes and re-verification |

**Recommended control:** AI-based egress anomaly detection (Parisi, 2019, Ch. 5). The detector learns a per-account baseline of outbound data, scores it with a Gaussian mixture density, and cuts off low-probability activity. This connects to a lesson from [Module 1](../module-01-intrusion-detection/): per-flow models miss slow leaks, so baselines must span days (UEBA).

**Current trend:** mobile driver's licenses (ISO/IEC 18013-5) with selective disclosure. The verifier receives a signed "over 21: yes" instead of an image, so a breach leaks nothing reusable.

## Slides

1. Title
2. Incident: who, what, when, how, impact, plus a timeline
3. CIA triad impact diagram
4. Most severe impact: confidentiality
5. Prevention: AI egress anomaly detection pipeline
6. Current trend: mobile IDs and data minimization
7. Reflection and APA references

## Rebuild

```bash
pip install python-pptx
python build_deck.py
```

The deck is generated from [`build_deck.py`](build_deck.py), and every diagram is a native, editable PowerPoint shape.

## Sources

- Krebs, B. (2026, September 1). [FBI probes service selling 153M+ drivers licenses](https://krebsonsecurity.com/2026/09/fbi-probes-service-selling-153m-drivers-licenses/). *Krebs on Security*.
- Parisi, A. (2019). *Hands-on artificial intelligence for cybersecurity*. Packt Publishing.
- International Organization for Standardization. (2021). *ISO/IEC 18013-5:2021, Mobile driving licence (mDL) application*.
