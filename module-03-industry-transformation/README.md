# Module 3 Assignment: AI Industry Transformation Research

A 10-slide strategic briefing for leadership on how AI is changing cybersecurity operations. It covers a title slide, seven content slides and two APA reference slides.

**Slides (PDF):** [`Bandari_Ruthvik_Nath_Module3_AI_Industry_Transformation.pdf`](Bandari_Ruthvik_Nath_Module3_AI_Industry_Transformation.pdf)
**Slides (PowerPoint, with speaker notes):** [`Bandari_Ruthvik_Nath_Module3_AI_Industry_Transformation.pptx`](Bandari_Ruthvik_Nath_Module3_AI_Industry_Transformation.pptx)

## What it covers

| Slide | Content |
|---|---|
| 2 | Executive summary and recommendation |
| 3 | Step 1: Microsoft (LLM triage), CrowdStrike (behavioral ML), Palo Alto Networks (inline deep learning) |
| 4 | AI vs signature detection, and an ROI chart (IBM 2025: $5.52M vs $3.62M breach cost, 284 vs 204 days) |
| 5 | Most effective techniques and implementation challenges |
| 6 | Step 2: CrowdStrike Charlotte AI, SentinelOne Purple AI, Splunk AI agents in the SIEM |
| 7 | Reactive vs proactive threat intelligence; Google Big Sleep and Darktrace/Ivanti early catches |
| 8 | CIA triad mapping of the AI-assisted FortiGate campaign (Krebs on Security), a NIST-aligned recommendation, and reflection |

Each of the six key questions in the brief is tagged Q1–Q6 on the slide that answers it. Vendor-reported figures are labelled, and IBM's ROI figures are presented as correlational.

## Rebuild

```bash
pip install python-pptx
python build_deck.py
```

The chart and diagrams are native, editable PowerPoint objects. The PDF was exported from PowerPoint.
