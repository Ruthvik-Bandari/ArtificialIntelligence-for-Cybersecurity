# Module 4 Assignment: AI Threat Detection System

A Random Forest (ensemble) classifier that separates normal network connections from attacks in NSL-KDD, and a 9-slide deck built around one threat: denial-of-service attacks.

**Slides (PDF):** [`Bandari_Ruthvik_Nath_Module4_AI_Threat_Detection.pdf`](Bandari_Ruthvik_Nath_Module4_AI_Threat_Detection.pdf)
**Slides (PowerPoint, with speaker notes):** [`Bandari_Ruthvik_Nath_Module4_AI_Threat_Detection.pptx`](Bandari_Ruthvik_Nath_Module4_AI_Threat_Detection.pptx)
**Notebook (Colab):** [`Ruthvik_Nath_Bandari_AI_Threat_Detection.ipynb`](Ruthvik_Nath_Bandari_AI_Threat_Detection.ipynb)

## Key results

| Test | Result |
|---|---|
| Held-out 20% of the training file | **99.90%** accuracy, 7 false alarms in 13,469 normal connections |
| Official NSL-KDD test set (17 unseen attack types) | **76.7%** accuracy; new attack types caught 23% of the time vs 77% for known ones |
| Best-detected threat | DoS: 78.9% on the official test set (floods have a median of 172 connections to one host in 2 s, against 4 for normal traffic) |
| Worst | R2L: 5.6% (password guessing is the most-missed attack) |

**Takeaway:** a supervised ensemble is excellent on attacks it has seen and weak on new ones. Pair it with anomaly detection (Parisi, 2019, Chapter 5). Use autonomous mitigation only for high-confidence floods, and send uncertain alerts to analysts.

## Rebuild

```bash
python build_notebook.py && jupyter nbconvert --to notebook --execute --inplace Ruthvik_Nath_Bandari_AI_Threat_Detection.ipynb
python build_deck.py            # reads its numbers from the executed notebook
```
