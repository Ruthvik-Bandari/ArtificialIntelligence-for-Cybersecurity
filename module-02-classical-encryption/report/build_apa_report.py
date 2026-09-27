"""Build the Module 2 lab report as an APA 7 student paper (HTML -> PDF via headless Chrome).

Usage:  python report/build_apa_report.py
Output: Ruthvik_Nath_Bandari_Module2_Lab_Report.pdf (module folder)

Edit the TITLE PAGE values below, then re-run.
"""
import html
import re
import subprocess
from pathlib import Path

from PIL import Image

# ---- TITLE PAGE (APA 7 student paper) ---------------------------------------------------------
TITLE = "Building and Breaking Classical Ciphers: A Comparison of Caesar and Substitution Encryption"
AUTHOR = "Ruthvik Nath Bandari"
AFFILIATION = "Northeastern University"
COURSE = "[Course Number]: AI for Cybersecurity"
INSTRUCTOR = "[Instructor Name]"
DUE_DATE = "[Due Date]"
# -----------------------------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
FIGS = MODULE / "figures"
OUT_PDF = MODULE / "Ruthvik_Nath_Bandari_Module2_Lab_Report.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def strip_chart_title(src: Path, dst: Path) -> None:
    """APA puts the figure number/title above the image, so remove the title baked into the chart.

    Anchors on the y-axis spine (the longest vertical dark line in the image), crops a little
    above where it starts, and whitens any title remnant to the right of the spine.
    """
    img = Image.open(src).convert("RGB")
    gray = img.convert("L")
    w, h = gray.size
    px = gray.load()
    best_len, spine_top, spine_x = 0, 0, 0
    for x in range(w // 3):                      # the spine sits in the left third
        run, top = 0, None
        for y in range(h):
            if px[x, y] < 80:
                run += 1
                top = y - run + 1
                if run > best_len:
                    best_len, spine_top, spine_x = run, top, x
            else:
                run = 0
    top = max(spine_top - 30, 0)
    out = img.crop((0, top, w, h))
    # Whiten the strip above the axes to the right of the spine: removes any title remnant while
    # keeping the top y-tick label (which sits left of the spine).
    out.paste((255, 255, 255), (spine_x + 3, 0, w, spine_top - top - 2))
    out.save(dst)


def md_inline(text: str) -> str:
    """Tiny inline formatter: *italic*, **bold**; everything else escaped."""
    t = re.sub(r'"(.+?)"', "\u201c\\1\u201d", text)   # curly double quotes
    t = t.replace("'", "\u2019")                            # apostrophes
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t


def paras(block: str) -> str:
    return "\n".join(f"<p>{md_inline(p.strip())}</p>" for p in block.strip().split("\n\n"))


def figure(num: int, title: str, img: str, note: str) -> str:
    return f"""
<div class="figure">
  <p class="label"><b>Figure {num}</b></p>
  <p class="ftitle"><i>{md_inline(title)}</i></p>
  <img src="{img}" alt="{html.escape(title)}">
  <p class="note"><i>Note.</i> {md_inline(note)}</p>
</div>"""


# ---- BODY ---------------------------------------------------------------------------------------
INTRO = """
Encryption converts readable plaintext into ciphertext so that only holders of the key can recover the message. This lab implemented two classical ciphers, the Caesar shift and the simple substitution cipher, and then attacked both. The goal was to measure *why* one cipher is stronger than the other, and why neither is secure.
"""

DATA = """
The attacks compare ciphertext against a statistical model of English, so two inputs were loaded and validated first. The first was Lewand's (2000) letter-frequency table; the code checks that it covers all 26 letters and sums to 100%. The second was an original five-paragraph corpus of 2,304 letters. For analysis only, text was normalized to uppercase A–Z. The ciphers themselves preserve case, spaces, digits, and punctuation, and they reject invalid input such as missing values, non-string types, and substitution keys that are not permutations.
"""

CIPHERS = """
The Caesar cipher shifts each letter by a key *k* (mod 26). The substitution cipher maps A–Z through a randomly shuffled alphabet generated from a fixed seed, and decryption applies the inverse mapping. Assertions verify every required test case, including "Hello World" → "Khoor Zruog".
"""

ATTACK = """
Each candidate decryption was scored with Pearson's chi-squared statistic against English letter frequencies, and the lowest score was selected. I chose chi-squared over the common "most frequent letter is E" heuristic because it uses all 26 letters and heavily penalizes rare letters (Q, X, Z) appearing too often, which is exactly what an incorrect shift produces. For the substitution cipher, the attack combined frequency rank-matching, common-word patterns (*THE*, *AND*), and a known-word "crib" located by its letter pattern.
"""

RESULTS_1 = """
Both ciphers encrypted and decrypted all test cases correctly. Run time scaled linearly with message length, and substitution was about one-third faster on long inputs (0.07 vs. 0.11 µs per character), so speed does not distinguish the two methods.

The automated Caesar breaker recovered a hidden shift from a single sentence: the correct candidate scored χ² = 14.9, compared with 249.5 for the runner-up. Across 300 random trials per message length (see Figure 1), chi-squared recovered the key 93% of the time at 20 letters and 100% of the time from 50 letters onward. The naive E-rule achieved only 34% and 55% at those lengths.
"""

RESULTS_2 = """
Against the substitution cipher, frequency ranking alone decrypted 42.8% of ciphertext letters correctly (see Figure 2). Assuming that the two most common three-letter words were *THE* and *AND* raised this to 51.8%. A single guessed word, "encryption," matched exactly one ciphertext word by shape and raised accuracy to 89.4%, which left the text readable.
"""

SECURITY = """
Table 1 summarizes the comparison. Substitution's key-space advantage of roughly 84 bits is irrelevant in practice, because the attacker never needs to search the keys. Figure 2 shows why: Caesar slides the English histogram sideways and substitution shuffles it, but once sorted, both ciphertext distributions are identical to the plaintext distribution. Repeated words also encrypt identically, and letter patterns such as the double *s* in *password* survive, so a single guessed word can be located by its shape alone.
"""

DISCUSSION = """
Caesar falls to brute force in a fraction of a second. Substitution survives brute force but still falls to statistical analysis, because both ciphers are deterministic and monoalphabetic: they relabel letters without hiding their frequencies or structure. The key lesson is that a large key space is necessary but not sufficient. Secure modern ciphers such as AES-GCM also require diffusion and randomization, so that ciphertext is statistically indistinguishable from random noise (Stallings, 2017).

The breaker is itself a small statistical classifier that scores inputs against a model of "normal," the same principle that underlies the anomaly-based intrusion detector from Module 1. A limitation of this lab is that all results come from a single English corpus; an automated hill-climbing substitution solver would be the natural extension.
"""

TABLE_ROWS = [
    ("Key space", "25 keys (≈4.6 bits)", "26! ≈ 4.0 × 10<sup>26</sup> keys (≈88 bits)"),
    ("Brute force at 10<sup>9</sup> keys/s", "Nanoseconds", "≈1.3 × 10<sup>10</sup> years"),
    ("Known plaintext", "One letter reveals the key", "One word reveals only its letters (36% here)"),
    ("Repeated words and patterns", "Leaked", "Leaked"),
    ("Frequency analysis", "Broken instantly", "Broken with one paragraph"),
]

REFERENCES = [
    "Lewand, R. E. (2000). <i>Cryptological mathematics</i>. Mathematical Association of America.",
    "Stallings, W. (2017). <i>Cryptography and network security: Principles and practice</i> (7th ed.). Pearson.",
]


def body_word_count() -> int:
    text = " ".join([INTRO, DATA, CIPHERS, ATTACK, RESULTS_1, RESULTS_2, SECURITY, DISCUSSION])
    return len(re.findall(r"\S+", re.sub(r"[*]", "", text)))


def build_html() -> str:
    strip_chart_title(FIGS / "fig2_breaker_accuracy.png", HERE / "apa_fig1.png")
    strip_chart_title(FIGS / "fig3_frequency_comparison.png", HERE / "apa_fig2.png")

    table_html = "\n".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in TABLE_ROWS)
    refs_html = "\n".join(f'<p class="ref">{r}</p>' for r in REFERENCES)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title>
<style>
  @page {{ size: letter; margin: 1in;
          @top-right {{ content: counter(page); font: 12pt "Times New Roman", serif; }} }}
  html {{ font: 12pt/2 "Times New Roman", Times, serif; color: #000; }}
  body {{ margin: 0; }}
  p {{ margin: 0; text-indent: 0.5in; text-align: left; }}
  h1, h2 {{ font-size: 12pt; font-weight: bold; margin: 0; line-height: 2; break-after: avoid; }}
  .label, .ftitle {{ break-after: avoid; }}
  h1 {{ text-align: center; }}
  h2 {{ text-align: left; }}
  .title-page {{ text-align: center; page-break-after: always; padding-top: 2in; }}
  .title-page p {{ text-indent: 0; text-align: center; }}
  .title-page .t {{ font-weight: bold; margin-bottom: 2em; }}
  .paper-title {{ text-align: center; font-weight: bold; }}
  .figure, .table {{ break-inside: avoid; margin: 0 0 1em; }}
  .figure p, .table p {{ text-indent: 0; }}
  .figure img {{ width: 100%; display: block; margin: 0.15in 0; }}
  .note {{ line-height: 2; }}
  table {{ width: 100%; border-collapse: collapse; line-height: 1.4; margin: 0.1in 0; }}
  th, td {{ text-align: left; vertical-align: top; padding: 4pt 6pt; }}
  thead th {{ border-top: 1px solid #000; border-bottom: 1px solid #000; font-weight: normal; }}
  tbody tr:last-child td {{ border-bottom: 1px solid #000; }}
  .refs {{ page-break-before: always; }}
  .ref {{ text-indent: -0.5in; padding-left: 0.5in; }}
</style></head><body>

<section class="title-page">
  <p class="t">{html.escape(TITLE)}</p>
  <p>{html.escape(AUTHOR)}</p>
  <p>{html.escape(AFFILIATION)}</p>
  <p>{html.escape(COURSE)}</p>
  <p>{html.escape(INSTRUCTOR)}</p>
  <p>{html.escape(DUE_DATE)}</p>
</section>

<p class="paper-title" style="text-indent:0">{html.escape(TITLE)}</p>
{paras(INTRO)}

<h1>Method</h1>
<h2>Data and Preprocessing</h2>
{paras(DATA)}
<h2>Cipher Implementation</h2>
{paras(CIPHERS)}
<h2>Attack Logic</h2>
{paras(ATTACK)}

<h1>Results</h1>
{paras(RESULTS_1)}
{figure(1, "Caesar Breaker Accuracy by Ciphertext Length", "apa_fig1.png",
        "Each point is the share of 300 random corpus excerpts whose Caesar shift was recovered correctly. "
        "The solid line uses chi-squared scoring across all 26 letters; the dashed line assumes the most "
        "frequent ciphertext letter is E. Corresponds to Figure 2 in the accompanying notebook.")}
{paras(RESULTS_2)}
{figure(2, "Letter Frequency in Standard English Compared With Caesar and Substitution Ciphertext", "apa_fig2.png",
        "English frequencies are from Lewand (2000). Both ciphertexts encrypt the same five-paragraph corpus; "
        "the Caesar key is a shift of 3. Corresponds to Figure 3 in the accompanying notebook.")}

<h1>Security Analysis</h1>
{paras(SECURITY)}
<div class="table">
  <p class="label"><b>Table 1</b></p>
  <p class="ftitle"><i>Security Comparison of the Caesar and Substitution Ciphers</i></p>
  <table>
    <thead><tr><th>Criterion</th><th>Caesar cipher</th><th>Substitution cipher</th></tr></thead>
    <tbody>{table_html}</tbody>
  </table>
  <p class="note"><i>Note.</i> Brute-force times assume one billion key trials per second. The known-plaintext
  figure is the share of message letters revealed by the single known word \u201cFriday.\u201d</p>
</div>

<h1>Discussion</h1>
{paras(DISCUSSION)}

<section class="refs">
  <h1>References</h1>
  {refs_html}
</section>
</body></html>"""


def main() -> None:
    html_path = HERE / "Module2_Lab_Report_APA.html"
    html_path.write_text(build_html(), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", html_path.as_uri()],
                   check=True, capture_output=True)
    print(f"Body word count: {body_word_count()}")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
