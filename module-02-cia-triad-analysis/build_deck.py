"""Build the Module 2 CIA triad presentation (7 slides, 16:9) with python-pptx.

Usage:  python build_deck.py
Output: Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pptx (next to this script)

All diagrams are native PowerPoint shapes, so the deck stays sharp and editable.
"""
import re
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parent / "Ruthvik_Nath_Bandari_Module2_CIA_Triad_Analysis.pptx"

# ---- palette ----------------------------------------------------------------------------------
NAVY = RGBColor(0x0F, 0x1B, 0x2D)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x5B, 0x64, 0x72)
LIGHT = RGBColor(0xF2, 0xF4, 0xF7)
RULE = RGBColor(0xD5, 0xDA, 0xE1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x1F, 0x5F, 0xAD)
RED = RGBColor(0xC0, 0x39, 0x2B)      # confidentiality: severe
AMBER = RGBColor(0xC7, 0x7C, 0x0E)    # integrity: high
TEAL = RGBColor(0x1E, 0x84, 0x6F)     # availability: low
FONT = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5
MARGIN = 0.6


# ---- helpers ----------------------------------------------------------------------------------
def rich(paragraph, text, size, color, bold=False, italic=False):
    """Add runs to a paragraph; **bold** and *italic* markers inside `text` are honoured."""
    for part in re.split(r"(\*\*.+?\*\*|\*.+?\*)", text):
        if not part:
            continue
        run = paragraph.add_run()
        is_b, is_i = part.startswith("**"), part.startswith("*") and not part.startswith("**")
        run.text = part.strip("*") if (is_b or is_i) else part
        f = run.font
        f.name, f.size, f.color.rgb = FONT, Pt(size), color
        f.bold = bold or is_b
        f.italic = italic or is_i


def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.1, after=6, italic=False):
    """Text box. `paras` is a str or list of str (one paragraph each)."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, p_text in enumerate([paras] if isinstance(paras, str) else paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(after)
        rich(p, p_text, size, color, bold, italic)
    return box


def bullets(slide, x, y, w, h, items, size=16, color=INK, after=10, marker_color=ACCENT):
    """Bulleted list with a coloured square marker drawn as a real bullet character."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.1
        p.space_after = Pt(after)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.28))))
        pPr.set("indent", str(-Emu(Inches(0.28))))
        bu_clr = pPr.makeelement(qn("a:buClr"), {})
        srgb = bu_clr.makeelement(qn("a:srgbClr"), {"val": str(marker_color)})
        bu_clr.append(srgb)
        pPr.append(bu_clr)
        pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "■"}))
        rich(p, item, size, color)
    return box


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.text_frame.text = ""
    return s


def line(slide, x1, y1, x2, y2, color=RULE, width=1.5):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    return c


def header(slide, title, kicker):
    rect(slide, 0, 0, 0.18, SH, ACCENT)
    text(slide, MARGIN, 0.42, SW - 2 * MARGIN, 0.3, kicker.upper(), size=12, color=ACCENT, bold=True)
    text(slide, MARGIN, 0.72, SW - 2 * MARGIN, 0.8, title, size=30, color=NAVY, bold=True, spacing=1.0)


def footer(slide, source, n):
    line(slide, MARGIN, SH - 0.55, SW - MARGIN, SH - 0.55, RULE, 0.75)
    text(slide, MARGIN, SH - 0.45, SW - 2 * MARGIN - 0.6, 0.3, source, size=10, color=MUTED)
    text(slide, SW - MARGIN - 0.5, SH - 0.45, 0.5, 0.3, str(n), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def notes(slide, body):
    slide.notes_slide.notes_text_frame.text = " ".join(body.split())


# ---- slide 1: title ----------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, NAVY)
rect(s, MARGIN, 1.55, 0.9, 0.08, RED)
text(s, MARGIN, 1.8, 11.5, 1.7, ["153 Million Driver’s Licenses", "Advertised for Sale"], size=46, color=WHITE, bold=True, spacing=1.0, after=0)
text(s, MARGIN, 3.55, 12.2, 1.0, "A CIA triad analysis of the Nexus ID-theft service and the confirmed IDScan.net breach",
     size=22, color=RGBColor(0xC9, 0xD3, 0xE0), spacing=1.1)
text(s, MARGIN, 4.85, 8, 1.2, ["**Ruthvik Nath Bandari**",
                                "AAI6680: AI for Cybersecurity · Northeastern University",
                                "Mimoza Dimodugno, PhD · September 2026"],
     size=16, color=RGBColor(0xC9, 0xD3, 0xE0), after=4)
text(s, MARGIN, SH - 0.8, 12, 0.4, "Case source: Krebs, B. (2026, September 1). FBI probes service selling 153M+ drivers licenses. Krebs on Security.",
     size=11, color=RGBColor(0x8A, 0x97, 0xA8), italic=True)
notes(s, """This presentation analyses a breach reported by Brian Krebs on September 1, 2026. A dark-web service
called Nexus advertised scans of more than 153 million U.S. and Canadian driver's licenses. Krebs traced
the samples he could verify to IDScan.net, an identity verification vendor, which later confirmed a breach;
the article does not establish that every advertised record came from that one company. I will summarise the incident, map it to
the CIA triad, explain why confidentiality was hit hardest, and recommend an AI-based control from
Chapter 5 together with a current industry trend that would have reduced the damage.""")

# ---- slide 2: incident ------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "A year-long data drain at an ID-verification vendor", "The incident · threat: data exfiltration for identity fraud")
rows = [
    ("WHO", "Nexus advertised **153M+** licenses. Krebs traced verified samples to **IDScan.net**, an "
            "ID-verification vendor for Hertz, retailers and 1,000+ dispensaries."),
    ("WHAT", "“Nexus,” a dark-web shop selling license scans (front, back, infrared, ultraviolet)."),
    ("WHEN", "Scans from **June 2025** onward; advertised **Aug. 31, 2026**."),
    ("HOW", "“Continuously exfiltrating new data for **over a year**”: ~400K new records in one day."),
    ("IMPACT", "Identity and credit fraud, breach-response costs, and exposure of senior U.S. officials."),
]
y = 1.75
for label, body in rows:
    chip_col = RED if label == "IMPACT" else ACCENT
    rect(s, MARGIN, y + 0.02, 1.0, 0.34, chip_col, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
    text(s, MARGIN, y + 0.02, 1.0, 0.34, label, size=12, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, after=0)
    text(s, MARGIN + 1.25, y, 6.25, 0.9, body, size=14.5, color=INK, after=0)
    y += 0.97

# timeline (right)
tx = 8.55
rect(s, tx - 0.35, 1.65, 4.7, 4.95, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
text(s, tx, 1.85, 4.0, 0.3, "TIMELINE", size=12, color=MUTED, bold=True)
events = [("Jun 2025", "Earliest matched scan timestamps", MUTED),
          ("Aug 31, 2026", "Nexus listed on the Exploit forum", AMBER),
          ("Sep 1, 2026", "FBI opens an investigation", ACCENT),
          ("Sep 8, 2026", "IDScan.net confirms unauthorized access", RED)]
line(s, tx + 0.12, 2.45, tx + 0.12, 6.05, RULE, 2)
ey = 2.35
for date, desc, col in events:
    rect(s, tx, ey, 0.24, 0.24, col, shape=MSO_SHAPE.OVAL)
    text(s, tx + 0.45, ey - 0.06, 3.5, 0.3, date, size=14, color=NAVY, bold=True, after=0)
    text(s, tx + 0.45, ey + 0.26, 3.4, 0.6, desc, size=12.5, color=INK, after=0)
    ey += 1.0
footer(s, "Source: Krebs (2026), including the Sept. 8 update.", 2)
notes(s, """Who: IDScan.net verifies IDs for Hertz, Target, FedEx and more than a thousand cannabis dispensaries,
running over 21 million verifications a month. What: the Nexus service advertised over 153 million driver's
licenses, more than 10 million ID cards, three million travel documents and 579,000 medical cards, often
with infrared and ultraviolet images. When: Krebs matched image timestamps to trips as early as June 2025;
Nexus was advertised on August 31, 2026, the FBI opened an inquiry on September 1, and IDScan confirmed
unauthorized access on September 8. Krebs verified the link to IDScan through nine people whose records
matched their trips; the full 153 million figure is the sellers' own claim. How: the attackers claimed continuous exfiltration for over a year,
and the record count grew by about 400,000 in a single day. The threat is data theft for identity fraud;
the impact includes identity and credit fraud, IDScan's notification and credit-protection costs, an FBI
investigation, and exposure of senior officials such as the U.S. Defense Secretary.""")

# ---- slide 3: CIA diagram ---------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "All three elements were hit, but not equally", "CIA triad impact")
# triangle
cx, top, base_y, half = 4.3, 2.15, 6.1, 2.45
tri = rect(s, cx - half, top, 2 * half, base_y - top, LIGHT, line=RULE, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
text(s, cx - 1.3, 4.35, 2.6, 1.2, ["**Attack vector**", "Long-running, low-and-slow data exfiltration"],
     size=13, color=INK, align=PP_ALIGN.CENTER, after=2)
nodes = [("C", cx, top, RED), ("I", cx - half, base_y, AMBER), ("A", cx + half, base_y, TEAL)]
for letter, nx, ny, col in nodes:
    c = rect(s, nx - 0.42, ny - 0.42, 0.84, 0.84, col, line=WHITE, shape=MSO_SHAPE.OVAL)
    c.line.width = Pt(3)
    text(s, nx - 0.42, ny - 0.42, 0.84, 0.84, letter, size=28, color=WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, after=0)
# callouts (right)
cards = [("CONFIDENTIALITY", "SEVERE", RED,
          "Nexus advertised 153M+ license images; records for sale include the U.S. Defense Secretary’s and an FBI assistant director’s."),
         ("INTEGRITY", "MODERATE", AMBER,
          "No sign IDScan’s records were altered, but forgery-grade IR/UV scans let criminals pass other firms’ ID checks, so a “verified” ID no longer proves identity."),
         ("AVAILABILITY", "LOW", TEAL,
          "No reported outage. Indirect loss: victims freeze credit, and clients must pause or redo verification.")]
cy = 1.75
for name, sev, col, body in cards:
    rect(s, 7.35, cy, 0.1, 1.45, col)
    text(s, 7.65, cy + 0.02, 3.2, 0.3, name, size=14, color=NAVY, bold=True, after=0)
    chip = rect(s, 10.85, cy + 0.02, 1.25, 0.3, col, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, 10.85, cy + 0.02, 1.25, 0.3, sev, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, after=0)
    text(s, 7.65, cy + 0.42, 4.5, 1.0, body, size=13.5, color=INK, after=0)
    cy += 1.65
footer(s, "Diagram: author’s analysis of Krebs (2026). Severity reflects scale, reversibility and downstream harm.", 3)
notes(s, """This diagram maps the attack onto the triad. The attack vector is the long-running exfiltration
in the centre. Confidentiality is severe: Nexus advertised more than 153 million identity images, and Krebs verified
that real, matching records were for sale.
Integrity is moderate: Krebs reports no evidence that IDScan's stored records were altered, so the harm
is downstream. The stolen scans include the infrared and ultraviolet images that verifiers check, so
criminals can make convincing forgeries and open fraudulent accounts elsewhere, which undermines the trust
that a verified ID proves identity. Availability is low: Krebs reports no outage of IDScan's service, but there is
indirect loss, because victims must freeze their credit and business clients may have to pause or repeat
verification while the vendor investigates.""")

# ---- slide 4: most severe ---------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "Confidentiality was hit hardest: identity can’t be reset", "Most severe impact")
for i, (big, small, col) in enumerate([("153M+", "license records advertised; Krebs verified a sample", RED),
                                       ("1+ year", "of exfiltration claimed; scans date to June 2025", NAVY)]):
    yy = 1.85 + i * 2.25
    rect(s, MARGIN, yy, 4.6, 1.95, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    text(s, MARGIN + 0.35, yy + 0.25, 4.0, 0.9, big, size=54, color=col, bold=True, after=0, spacing=1.0)
    text(s, MARGIN + 0.35, yy + 1.2, 4.0, 0.6, small, size=16, color=INK, after=0)
bullets(s, 5.85, 1.95, 6.9, 4.5, [
    "**Irreversible.** A password can be reset; a face, birth date and license number cannot.",
    "**Forgery-grade.** IR and UV scans are exactly what ID verifiers check.",
    "**Harm beyond fraud.** Exposes senior officials, abuse survivors and protected witnesses who cannot change their appearance.",
    "**Root cause.** The integrity and availability damage both flow from this single loss of confidentiality.",
], size=17, after=16, marker_color=RED)
footer(s, "Source: Krebs (2026), citing researcher L. Baldwin on exposure of abuse survivors and protected witnesses.", 4)
notes(s, """Confidentiality is the most severe impact for four reasons. First, it is irreversible: unlike a
password, a person's face, date of birth and license number cannot be rotated. Second, the data is
forgery-grade, because the infrared and ultraviolet scans are the very features that verification systems
inspect. Third, the harm goes beyond financial fraud: a researcher quoted by Krebs warned that the images
expose people fleeing domestic violence and people in witness protection, who cannot meaningfully change
their appearance. Fourth, the integrity and availability harms are downstream of this one confidentiality
failure, so preventing the leak would have prevented the rest.""")

# ---- slide 5: AI control ----------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "Prevention: AI-based egress anomaly detection", "Recommended control · Chapter 5")
steps = [("1  Collect", "Flow and storage-access logs per service account"),
         ("2  Learn normal", "Baseline bytes out, records read, destinations, hour"),
         ("3  Score", "Gaussian / GMM density: low p(x) = anomaly (Parisi, 2019, ch. 5)"),
         ("4  Respond", "Alert, revoke the token, block the destination")]
bw, gap, by = 2.75, 0.33, 1.8
text(s, MARGIN, 3.65, SW - 2 * MARGIN, 0.3,
     "**Current industry practice:** commercial UEBA and network detection and response (NDR) platforms flag exfiltration this way.",
     size=12.5, color=MUTED, after=0)
for i, (head, body) in enumerate(steps):
    bx = MARGIN + i * (bw + gap)
    rect(s, bx, by, bw, 1.75, NAVY if i == 2 else LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    fg = WHITE if i == 2 else NAVY
    text(s, bx + 0.22, by + 0.2, bw - 0.44, 0.35, head, size=16, color=fg, bold=True, after=0)
    text(s, bx + 0.22, by + 0.62, bw - 0.44, 1.1, body, size=13, color=WHITE if i == 2 else INK, after=0)
    if i < 3:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(bx + bw + 0.04), Inches(by + 0.72),
                               Inches(0.25), Inches(0.3))
        a.fill.solid(); a.fill.fore_color.rgb = ACCENT; a.line.fill.background()
panels = [("APPLIED TO THIS BREACH", ACCENT,
           "An account that normally reads few images starts sending ~400K records a day to a new host. "
           "That falls far outside its baseline, so it **could be flagged within hours**, given log coverage, "
           "tuned thresholds and automated response."),
          ("LESSON FROM MY MODULE 1 LAB", RED,
           "My benign-only GMM reached **ROC-AUC 0.966** on CIC-IDS-2017 but missed attacks that look "
           "normal flow by flow. Slow leaks need **per-account baselines over days** (UEBA).")]
for i, (head, col, body) in enumerate(panels):
    px = MARGIN + i * 6.2
    rect(s, px, 4.25, 0.08, 1.45, col)
    text(s, px + 0.3, 4.25, 5.6, 0.3, head, size=12, color=col, bold=True, after=0)
    text(s, px + 0.3, 4.65, 5.6, 2.0, body, size=15, color=INK, after=0)
footer(s, "Sources: Parisi (2019), Ch. 5, network anomaly detection with AI; Krebs (2026); author’s Module 1 lab results.", 5)
notes(s, """My recommended control is AI-based egress anomaly detection, which applies Chapter 5 of Parisi
directly. The detector learns what normal outbound activity looks like for each service account, using
features such as bytes sent, records read, destination and time of day, and fits a Gaussian or Gaussian
mixture density. Activity with very low probability is flagged, and a SOAR playbook can revoke the token
and block the destination. In this breach, an account suddenly moving hundreds of thousands of license
images a day would likely stand out. Whether it is stopped within hours depends on having logs for the
image store, well-tuned thresholds and an automated response, so I present that as a plausible outcome
rather than a guarantee. My Module 1 lab adds a caveat: my benign-only
mixture model scored ROC-AUC 0.966, but it missed attacks that look normal one flow at a time. So the
detector must aggregate per account over days, which is how commercial UEBA and network detection
platforms work today. This makes the control realistic for current industry practice.""")

# ---- slide 6: current trend -------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "Trend: mobile IDs can shrink what there is to steal", "Current trend · data minimization")
cols = [("TODAY: SCAN AND STORE", RED, ["Physical license scanned", "Vendor keeps the full image: front, back, IR, UV",
                                        "A breach leaks a reusable identity"]),
        ("MOBILE ID (ISO/IEC 18013-5)", TEAL, ["Phone shares a state-signed credential", "Verifier asks only “age over 21?” and gets yes/no",
                                                "Less to leak, if the verifier does not retain data"])]
for i, (head, col, items) in enumerate(cols):
    px = MARGIN + i * 3.45
    rect(s, px, 1.8, 3.2, 4.05, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    rect(s, px, 1.8, 3.2, 0.12, col)
    text(s, px + 0.25, 2.1, 2.8, 0.6, head, size=13, color=col, bold=True, after=0)
    iy = 2.85
    for j, it in enumerate(items):
        text(s, px + 0.25, iy, 2.75, 0.9, it, size=14, color=INK, after=0)
        if j < len(items) - 1:
            d = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(px + 1.45), Inches(iy + 0.82), Inches(0.26), Inches(0.28))
            d.fill.solid(); d.fill.fore_color.rgb = col; d.line.fill.background()
        iy += 1.15
bullets(s, 7.75, 1.9, 5.0, 3.2, [
    "**The trend:** mobile driver’s licenses (ISO/IEC 18013-5). TSA accepts digital IDs at 250+ airports and “sees only the necessary information.”",
    "**Mitigation link:** verifiers can receive only what they need. The benefit depends on retention: ISO/IEC 18013-5 leaves storage rules out of scope.",
    "**With the AI control:** minimize what is stored, then monitor what remains.",
], size=16, after=14, marker_color=TEAL)
text(s, 7.75, 5.35, 5.0, 1.0, "“We don’t have nearly the oversight to ensure they are safe.”  Z. Edwards, privacy researcher, in Krebs (2026)",
     size=13, color=MUTED, italic=True)
footer(s, "Sources: International Organization for Standardization (2021); Krebs (2026); Transportation Security Administration (n.d.).", 6)
notes(s, """The current trend I connect to mitigation is the shift to mobile driver's licenses and selective
disclosure, standardised in ISO/IEC 18013-5. TSA already accepts digital IDs at more than 250 airports and says it
sees only the information it needs. Instead of photocopying a physical card, the verifier asks the
phone a narrow question, such as whether the holder is over 21, and receives a cryptographically signed
yes or no from the issuing state. That reduces what the verifier receives, but the benefit depends on
implementation: ISO/IEC 18013-5 leaves requirements for storing mDL data out of scope, so verifiers still
need retention limits for a breach to yield less. This is data minimization in practice, and it answers the oversight gap the privacy
researcher Zach Edwards raised in the article. It pairs with the AI control: minimization shrinks what can
be stolen, and anomaly detection shrinks how long a thief has to steal what remains.""")

# ---- slide 7: reflection + references ---------------------------------------------------------
s = prs.slides.add_slide(BLANK)
header(s, "Reflection and references", "Takeaways")
rect(s, MARGIN, 1.8, 5.6, 3.85, LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
text(s, MARGIN + 0.3, 2.0, 5.0, 0.3, "WHAT I LEARNED", size=12, color=ACCENT, bold=True, after=0)
text(s, MARGIN + 0.3, 2.4, 5.0, 3.9, [
    "My Module 1 detector scored well, but this breach exposes its blind spot: a patient attacker who "
    "looks normal one flow at a time. **A model’s limits matter as much as its score.**",
    "The cipher lab showed me that patterns leak. Here, stored data leaked. Sometimes the strongest "
    "control is keeping less.",
    "As a future security engineer, I want to build detectors that track **behavior over time**, with a "
    "named analyst approving high-impact responses.",
], size=15, color=INK, after=12)
refs = [
    "Krebs, B. (2026, September 1). FBI probes service selling 153M+ drivers licenses. *Krebs on Security*. "
    "https://krebsonsecurity.com/2026/09/fbi-probes-service-selling-153m-drivers-licenses/",
    "International Organization for Standardization. (2021). *Personal identification: ISO-compliant driving "
    "licence. Part 5: Mobile driving licence (mDL) application* (ISO/IEC Standard No. 18013-5:2021). "
    "https://www.iso.org/standard/69084.html",
    "Parisi, A. (2019). *Hands-on artificial intelligence for cybersecurity: Implement smart AI systems for "
    "preventing cyber attacks and detecting threats and network anomalies*. Packt Publishing.",
    "Transportation Security Administration. (n.d.). *Digital identity and facial comparison technology*. "
    "Retrieved September 27, 2026, from https://www.tsa.gov/digital-id",
]
text(s, 6.65, 1.85, 6.1, 0.3, "REFERENCES", size=12, color=ACCENT, bold=True, after=0)
box = text(s, 6.65, 2.25, 6.1, 4.2, refs, size=11.5, color=INK, after=8, spacing=1.05)
for p in box.text_frame.paragraphs:        # APA hanging indent
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(Emu(Inches(0.4))))
    pPr.set("indent", str(-Emu(Inches(0.4))))
footer(s, "References formatted in APA 7th edition.", 7)
notes(s, """This case exposed a blind spot in my own Module 1 detector. It scored well overall, but it
judged single flows, and this attacker was patient enough to blend in flow by flow for over a year. The
habit I most want to carry forward is interrogating a model until its limits are explicit, because a
strong score does not prove broad protection. The cipher lab in this module taught me that structure
leaks through encryption; this breach showed that stored data leaks too, so sometimes the best control
is simply keeping less of it. In my future security engineering work, I want to build detectors that
model behavior over time, and keep a named analyst accountable for high-impact automated responses. The
references are listed in APA format: the Krebs on Security article, the ISO standard for mobile driving
licences, Chapter 5 of Parisi's Hands-On Artificial Intelligence for Cybersecurity, and TSA's page on
digital IDs.""")


prs.save(OUT)
print("wrote", OUT, len(prs.slides), "slides")
