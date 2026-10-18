"""Build the Module 5 lab report as an APA 7 student paper (HTML -> PDF via headless Chrome).

Every number and figure is read from an executed notebook: the cell tagged "summary" prints a JSON summary,
and cells tagged "fig_*" hold the figures. Pointing the script at the Colab-executed notebook therefore produces
a report that matches that run exactly.

Usage:  python report/build_apa_report.py [path/to/executed_notebook.ipynb]
Output: Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf (module folder)
"""
import base64
import html
import json
import math
import re
import subprocess
import sys
from pathlib import Path

# ---- TITLE PAGE (APA 7 student paper) ---------------------------------------------------------
TITLE = "Detecting Phishing Emails With NLP: An Explainable Ensemble Trained on Enron and Synthetic Phishing"
AUTHOR = "Ruthvik Nath Bandari"
AFFILIATION = "Northeastern University"
COURSE = "AAI6680: AI for Cybersecurity"
INSTRUCTOR = "Mimoza Dimodugno, PhD"
DUE_DATE = "October 18, 2026"
# -----------------------------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
NOTEBOOK = Path(sys.argv[1]) if len(sys.argv) > 1 else MODULE / "Bandari_Ruthvik_Nath_AI_IDS_lab3.ipynb"
OUT_PDF = MODULE / "Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def load_notebook(path: Path):
    """Return the JSON summary and write each tagged figure to report/<tag>.png."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    summary, figs = None, {}
    for cell in nb["cells"]:
        tags = cell.get("metadata", {}).get("tags", [])
        if cell["cell_type"] != "code" or not tags:
            continue
        for out in cell.get("outputs", []):
            if tags[0] == "summary" and out.get("output_type") == "stream" and out.get("name") == "stdout":
                text = "".join(out["text"])
                if "{" in text:
                    summary = json.loads(text[text.index("{"):text.rindex("}") + 1])
            png = out.get("data", {}).get("image/png")
            if tags[0].startswith("fig_") and png:
                dst = HERE / f"{tags[0]}.png"
                dst.write_bytes(base64.b64decode(png))
                figs[tags[0]] = dst
    if summary is None:
        sys.exit("No summary output found: run the notebook to the end first.")
    return summary, figs


S, FIGS = load_notebook(NOTEBOOK)
T, R = S["test"], S["real"]
ENS = T["Stacked ensemble @ high-recall threshold"]
NB_REAL = R["Naive Bayes (baseline)"]["real phishing caught"]
PROF = S["profile"]
NER = S["ner_sensitive"]
W = S["weights"]
pct = lambda v, d=1: f"{v * 100:.{d}f}%"
prauc_min = min(m["PR-AUC"] for m in T.values())
PRAUC_TEXT = (f"every classifier reached a PR-AUC of {prauc_min:.3f}" if f"{prauc_min:.3f}" == "1.000" else f"every classifier reached a PR-AUC of at least {prauc_min:.3f}")
_w = sorted(S["weights"].items(), key=lambda kv: -kv[1])
WEIGHT_TEXT = (f"The combiner gave the most weight to the {_w[0][0].replace(' model', '').lower()} and "
               f"{_w[1][0].replace(' model', '').lower()} specialists ({_w[0][1]:.2f} and {_w[1][1]:.2f}) and less to the "
               f"{_w[2][0].replace(' model', '').lower()} specialist ({_w[2][1]:.2f}).")
WEIGHT_TEXT = WEIGHT_TEXT.replace("url specialist", "URL specialist").replace("url and", "URL and").replace("and url", "and URL")
_terms = [f'"{t}"' if " " in t else f"*{t}*" for t in list(S["top_terms"])[:4]]
top_terms = ", ".join(_terms[:-1]) + ", and " + _terms[-1]
_rf = [f"*{f}*" for f in list(S["top_rf"])[:3]]
top_rf = ", ".join(_rf[:-1]) + ", and " + _rf[-1]
_b = list(S["brands"])[:3]
BRAND_SENT = (f" The most impersonated named brands were {', '.join(_b[:-1])}, and {_b[-1]}." if len(_b) >= 2 else "")
TACTIC_NOTE = ("Every synthetic tactic was detected in the test set."
               if S["worst_tactic_rate"] >= 1.0 else
               f"Among synthetic tactics, {min(S['tactic_detection'], key=S['tactic_detection'].get).lower()} was detected least often "
               f"({S['worst_tactic_rate']:.1%}).")


def md_inline(text: str) -> str:
    """Tiny inline formatter: *italic*, **bold**; everything else escaped."""
    t = re.sub(r'"(.+?)"', "“\\1”", text)   # curly double quotes
    t = t.replace("'", "’")                            # apostrophes
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t


def paras(block: str) -> str:
    return "\n".join(f"<p>{md_inline(p.strip())}</p>" for p in block.strip().split("\n\n"))


def figure(num: int, title: str, img: Path, note: str) -> str:
    return f"""
<div class="figure">
  <p class="label"><b>Figure {num}</b></p>
  <p class="ftitle"><i>{md_inline(title)}</i></p>
  <img src="{img.as_uri()}" alt="{html.escape(title)}">
  <p class="note"><i>Note.</i> {md_inline(note)}</p>
</div>"""


# ---- BODY ---------------------------------------------------------------------------------------
INTRO = f"""
Phishing succeeds through language: urgency, authority, and a believable brand. This lab built a natural language processing (NLP) phishing detector from legitimate Enron corporate email (Klimt & Yang, 2004) and synthetic phishing built around verified PhishTank URLs (Cisco Talos Intelligence Group, 2026), and then tested it on real-world phishing.
"""

METHOD = f"""
I sampled {S['n_legit']:,} unique emails from the {S['n_enron_files']:,} files in the Enron archive (Cohen, 2015) and generated the same number of synthetic phishing emails from eight documented tactics, such as credential harvesting, invoice fraud, and CEO wire fraud. Each used a real PhishTank URL and the brand it impersonated. For the real-world test, I used 1,000 real phishing emails from a public dataset (Cyber Cop, 2023), never used in training.

Text was preprocessed with NLTK (Bird et al., 2009): tokenization, stop-word removal, Porter stemming, and TF-IDF unigrams and bigrams. I engineered {S['n_eng']} phishing-specific features: urgency and call-to-action phrases, out-of-vocabulary rate as a grammar proxy, VADER sentiment (Hutto & Gilbert, 2014), URL patterns from regular expressions, subject-line and sender-domain metadata, and named-entity recognition (NER). A NER flag for a person or organization named next to a credential, account, or payment term fired on {pct(NER['1'])} of synthetic phishing against {pct(NER['0'])} of Enron mail. Company names, email addresses, and quoted reply headers were deleted so that no model could learn "mentions Enron means safe."

Naive Bayes, a linear support vector machine (SVM), and a random forest were tuned with stratified five-fold cross-validation on PR-AUC. A stacked ensemble combined text, URL, and metadata specialists, and its threshold was set on out-of-fold predictions to catch at least 99% of phishing.
"""

RESULTS = f"""
On the held-out synthetic test set, {PRAUC_TEXT}, and at its high-recall threshold the ensemble reached a precision of {ENS['precision']:.3f} and a recall of {ENS['recall']:.3f} (Table 1; Figure 1).

The real-world test told a different story. The same ensemble caught {pct(S['real_recall'])} of the 1,000 real phishing emails, and Naive Bayes caught {pct(NB_REAL)} (Table 2). The feature profiles explain why. Real phishing averaged {PROF['Real-world phishing']['body_words']:.0f} words against {PROF['Synthetic phishing']['body_words']:.0f} for synthetic phishing, carried no subject or sender headers, and used fewer urgency phrases ({PROF['Real-world phishing']['urgency_words']:.2f} against {PROF['Synthetic phishing']['urgency_words']:.2f}); the missed examples show that much of it was bulk spam. The models had learned the synthetic templates, not phishing.
"""

ANALYSIS = f"""
The notebook's dashboard scores each email and explains the verdict from the model itself: the specialist with the largest contribution and the words that pushed the score up. Figure 2 summarizes the scores by source and tactic. {WEIGHT_TEXT} The strongest phishing n-grams included {top_terms}, and the random forest relied most on {top_rf} (Figure 3). {TACTIC_NOTE}

PhishTank data show that {pct(S['https_share'], 0)} of live phishing links use HTTPS (Cisco Talos Intelligence Group, 2026), so a padlock says nothing about legitimacy.{BRAND_SENT} I recommend quarantining above the high-recall threshold, sandboxing links, call-back verification for payment requests, and validating any model on real, recent phishing before deployment.
"""

REFLECTION = f"""
The real-world test taught me the most. Near-perfect scores on synthetic phishing looked like success, but the model caught almost none of the real phishing. That is the distribution-shift problem this course keeps returning to: a model is only as good as the data it learned from. I want to build email defenses that are trained and validated on fresh, real attacks and that explain every verdict, because an employee will only act on a warning they understand.
"""

TABLE1 = [(n.replace(" @ high-recall threshold", ", high-recall threshold"), f"{m['precision']:.3f}", f"{m['recall']:.3f}",
           f"{m['F1']:.3f}", f"{m['PR-AUC']:.3f}", f"{int(m['false alarms'])}")
          for n, m in T.items()]
TABLE2 = [(n.replace(" @ high-recall threshold", ", high-recall threshold"), pct(m["real phishing caught"]),
           f"{m['median risk score']:.3f}") for n, m in R.items()]

REFERENCES = [
    "Bird, S., Klein, E., &amp; Loper, E. (2009). <i>Natural language processing with Python</i>. O’Reilly Media.",
    "Cisco Talos Intelligence Group. (2026). <i>PhishTank: Online, valid phishing URLs</i> [Data set]. Retrieved October 18, 2026, "
    "from https://phishtank.org/developer_info.php",
    "Cohen, W. W. (2015). <i>Enron email dataset</i> [Data set]. Carnegie Mellon University. https://www.cs.cmu.edu/~enron/",
    "Cyber Cop. (2023). <i>Phishing email detection</i> [Data set]. Kaggle. https://www.kaggle.com/datasets/subhajournal/phishingemails",
    "Hutto, C. J., &amp; Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. "
    "<i>Proceedings of the International AAAI Conference on Web and Social Media, 8</i>(1), 216–225. https://doi.org/10.1609/icwsm.v8i1.14550",
    "Klimt, B., &amp; Yang, Y. (2004). The Enron corpus: A new dataset for email classification research. In J.-F. Boulicaut, F. Esposito, "
    "F. Giannotti, &amp; D. Pedreschi (Eds.), <i>Machine learning: ECML 2004</i> (pp. 217–226). Springer. https://doi.org/10.1007/978-3-540-30115-8_22",
]


def body_word_count() -> int:
    text = " ".join([INTRO, METHOD, RESULTS, ANALYSIS, REFLECTION])
    return len(re.findall(r"\S+", re.sub(r"[*]", "", text)))


def table(num, title, head, rows, note):
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"""
<div class="table">
  <p class="label"><b>Table {num}</b></p>
  <p class="ftitle"><i>{md_inline(title)}</i></p>
  <table><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}</tr></thead><tbody>{body}</tbody></table>
  <p class="note"><i>Note.</i> {md_inline(note)}</p>
</div>"""


def build_html() -> str:
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
  .title-page {{ text-align: center; page-break-after: always; padding-top: 2in; }}
  .title-page p {{ text-indent: 0; text-align: center; }}
  .title-page .t {{ font-weight: bold; margin-bottom: 2em; }}
  .paper-title {{ text-align: center; font-weight: bold; }}
  .figure, .table {{ break-inside: avoid; margin: 0 0 1em; }}
  .figure p, .table p {{ text-indent: 0; }}
  .figure img {{ width: 100%; display: block; margin: 0.15in 0; }}
  .note {{ line-height: 2; }}
  table {{ width: 100%; border-collapse: collapse; line-height: 1.5; margin: 0.1in 0; font-size: 11pt; }}
  th, td {{ text-align: left; vertical-align: top; padding: 4pt 6pt; }}
  thead th {{ border-top: 1px solid #000; border-bottom: 1px solid #000; font-weight: normal; }}
  tbody tr:last-child td {{ border-bottom: 1px solid #000; }}
  .refs {{ page-break-before: always; }}
  .float-page {{ page-break-before: always; }}
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
{paras(METHOD)}

<h1>Results</h1>
{paras(RESULTS)}

<h2>Phishing Patterns and Threat Intelligence</h2>
{paras(ANALYSIS)}

<h1>Reflection</h1>
{paras(REFLECTION)}

<section class="refs">
  <h1>References</h1>
  {refs_html}
</section>

<section class="float-page">
{table(1, "Test-Set Performance by Classifier (Enron vs Synthetic Phishing)",
       ["Model", "Precision", "Recall", "F1", "PR-AUC", "False alarms"], TABLE1,
       f"Held-out test set of {S['n_test']:,} emails (Enron and synthetic phishing). Rows use a 0.5 threshold except the last, which "
       f"uses the ensemble's high-recall threshold of {S['threshold']:.3f}. SVM = support vector machine.")}
</section>
<section class="float-page">
{table(2, "Real-World Test: Share of 1,000 Real Phishing Emails Caught",
       ["Model", "Real phishing caught", "Median risk score"], TABLE2,
       "Real phishing emails from a public dataset, never used in training. Rows use a 0.5 threshold except the last, which uses "
       "the ensemble's high-recall threshold.")}
</section>
<section class="float-page">
{figure(1, "Precision-Recall Curves and Confusion Matrix on the Test Set", FIGS["fig_eval"],
        "Left: precision-recall curves on the held-out test set (AP = average precision). Right: the stacked ensemble at its high-recall threshold.")}
</section>
<section class="float-page">
{figure(2, "Phishing Detection Dashboard", FIGS["fig_dashboard"],
        "Left: ensemble risk scores by email source, with the high-recall threshold dashed. Middle: share of each phishing tactic detected, including real-world phishing. "
        "Right: brands most often named as targets in the PhishTank feed.")}
</section>
<section class="float-page">
{figure(3, "Top Phishing Indicators", FIGS["fig_indicators"],
        "Left: random forest importance of engineered features. Middle: stemmed n-grams with the largest SVM weights toward phishing. "
        "Right: logistic-regression weights the ensemble gives each specialist.")}
</section>
</body></html>"""


def main() -> None:
    html_path = HERE / "Module5_Lab_Report_APA.html"
    html_path.write_text(build_html(), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={OUT_PDF}", html_path.as_uri()],
                   check=True, capture_output=True)
    print(f"Source notebook: {NOTEBOOK.name}")
    print(f"Body word count: {body_word_count()}")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
