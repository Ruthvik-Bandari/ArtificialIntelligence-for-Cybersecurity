"""Build the Module 3 lab report as an APA 7 student paper (HTML -> PDF via headless Chrome).

Usage:  python report/build_apa_report.py
Output: Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf (module folder)

Edit the TITLE PAGE values below, then re-run.
"""
import html
import re
import subprocess
from pathlib import Path

# ---- TITLE PAGE (APA 7 student paper) ---------------------------------------------------------
TITLE = "Detecting Network Intrusions With an Autoencoder: Unsupervised Anomaly Detection on NSL-KDD"
AUTHOR = "Ruthvik Nath Bandari"
AFFILIATION = "Northeastern University"
COURSE = "AAI6680: AI for Cybersecurity"
INSTRUCTOR = "Mimoza Dimodugno, PhD"
DUE_DATE = "September 29, 2026"
# -----------------------------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
FIGS = MODULE / "figures"
OUT_PDF = MODULE / "Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


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


def figure(num: int, title: str, img: Path, note: str, width: str = "100%") -> str:
    return f"""
<div class="figure">
  <p class="label"><b>Figure {num}</b></p>
  <p class="ftitle"><i>{md_inline(title)}</i></p>
  <img src="{img.as_uri()}" alt="{html.escape(title)}" style="width:{width}; margin-left:auto; margin-right:auto">
  <p class="note"><i>Note.</i> {md_inline(note)}</p>
</div>"""


# ---- BODY ---------------------------------------------------------------------------------------
INTRO = """
Signature-based intrusion detection only catches attacks someone has already described. This lab tested an alternative: an autoencoder trained on normal network connections only, which flags any connection it cannot reconstruct. The official NSL-KDD test set contains 17 attack types that never appear in training, so it also measures whether the detector generalizes to attacks it has never seen.
"""

METHOD = """
NSL-KDD (Tavallaee et al., 2009) provides 125,973 training and 22,544 test connections, each described by 41 features. Following the brief, I kept numerical features only. I dropped the three categorical fields and the constant *num_outbound_cmds*, which left 37 inputs. The 67,343 normal training records were split 80/20 into training and validation sets. Heavy-tailed count and byte features were log-transformed, and a StandardScaler was then fitted on the training portion only, to prevent leakage.

The autoencoder (37–20–10–20–37, ReLU hidden layers, linear output) was trained with Adam and mean squared error for 50 epochs with early stopping. The anomaly threshold was the 95th percentile of training reconstruction errors. An Isolation Forest (Liu et al., 2008) received identical inputs and the same threshold rule.
"""

RESULTS_1 = """
Training loss fell from 0.786 to 0.135, and validation loss followed it with no widening gap (Figure 1). The threshold flagged 5.05% of unseen normal validation records. On the test set, the autoencoder achieved a precision of 0.958, recall of 0.737, F1 of 0.833, and ROC-AUC of 0.958, with a 4.3% false-positive rate (Figure 2).

The autoencoder outperformed the Isolation Forest overall (Table 1), but not everywhere. At a 1% false-positive budget, the Isolation Forest caught 56% of attacks, compared with 48% for the autoencoder. The larger difference was which attacks each model caught: the autoencoder detected far more remote-to-local (R2L) and user-to-root (U2R) attacks, while the Isolation Forest was better on scans. The autoencoder also detected 66.5% of attack records belonging to the 17 test-only attack types.
"""

RESULTS_2 = """
The per-attack analysis (Figure 3) shows where detection fails. Floods and scans such as *neptune*, *nmap*, and *satan* exceeded 90% recall. R2L was the hardest category, at 35%, although published category mappings differ for a few test-only attacks. The model never detected *snmpgetattack* or *snmpguess*. In fact, 30% of *snmpgetattack* records are numerically identical to normal records, so these features cannot separate them. *guess_passwd* reached only 18%: only 38% of its records show a failed login, so each guess looks like an ordinary short session.

Two misses trace back to design choices. *smurf* (2%) connections carry a median of 1,008 source bytes, compared with 30 for normal ICMP echo connections, but with the protocol and service fields removed that volume looks ordinary. *pod* (27%) connections carry a non-zero wrong-fragment count never seen in normal traffic, yet averaging the error over 37 features probably diluted that single signal below the threshold. An ablation showed that the log transform raised ROC-AUC from 0.936 to 0.958, so preprocessing is itself a detection decision.
"""

REFLECTION = """
In Module 1, my Gaussian mixture detector missed SSH brute force and botnet traffic because each individual flow looked normal. The autoencoder is far more flexible, yet it failed on *guess_passwd* for the same reason. That repetition was the most useful lesson of this lab: model capacity cannot recover information the features do not contain. I did not test a deeper network, but the evidence points to features rather than capacity: a feature that counts failed logins per source over ten minutes would expose a password-guessing campaign directly. The *pod* result suggested a related lesson: even when the right signal is present, the way the error is scored can hide it.

The lab also reinforced that the threshold is a security decision, not a technical detail. Moving from the 95th to the 99th percentile cuts false alarms from 4.3% to under 1%, but drops recall from 74% to 47%. That trade-off belongs to the team answering the alerts. The work I want to do is build detectors that model behavior over time, per user and per host, and pair them with analysts who can act on ranked, explained alerts. This lab showed me that an autoencoder is a useful part of that system, but not the whole system.
"""

TABLE_ROWS = [
    ("Precision", "0.958", "0.972"),
    ("Recall", "<b>0.737</b>", "0.660"),
    ("F1-score", "<b>0.833</b>", "0.786"),
    ("False-positive rate", "0.043", "<b>0.025</b>"),
    ("ROC-AUC", "<b>0.958</b>", "0.939"),
    ("Recall at 1% false-positive rate", "0.481", "<b>0.561</b>"),
    ("Recall: DoS / Probe", "<b>0.856</b> / 0.814", "0.801 / <b>0.914</b>"),
    ("Recall: R2L / U2R", "<b>0.352 / 0.690</b>", "0.067 / 0.500"),
]

REFERENCES = [
    "Liu, F. T., Ting, K. M., &amp; Zhou, Z.-H. (2008). Isolation forest. In <i>Proceedings of the 2008 Eighth IEEE "
    "International Conference on Data Mining</i> (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17",
    "Tavallaee, M., Bagheri, E., Lu, W., &amp; Ghorbani, A. A. (2009). A detailed analysis of the KDD CUP 99 data set. "
    "In <i>Proceedings of the 2009 IEEE Symposium on Computational Intelligence for Security and Defense "
    "Applications</i> (pp. 1–6). IEEE. https://doi.org/10.1109/CISDA.2009.5356528",
]


def body_word_count() -> int:
    text = " ".join([INTRO, METHOD, RESULTS_1, RESULTS_2, REFLECTION])
    return len(re.findall(r"\S+", re.sub(r"[*]", "", text)))


def build_html() -> str:
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
{paras(RESULTS_1)}

<h1>Attack Type Analysis</h1>
{paras(RESULTS_2)}

<h1>Reflection</h1>
{paras(REFLECTION)}

<section class="refs">
  <h1>References</h1>
  {refs_html}
</section>

<section class="float-page">
<div class="table">
  <p class="label"><b>Table 1</b></p>
  <p class="ftitle"><i>Autoencoder Compared With Isolation Forest on the NSL-KDD Test Set</i></p>
  <table>
    <thead><tr><th>Metric</th><th>Autoencoder</th><th>Isolation Forest</th></tr></thead>
    <tbody>{table_html}</tbody>
  </table>
  <p class="note"><i>Note.</i> Both models were trained on the same normal-only records and thresholded at the
  95th percentile of their own training scores. The better value in each row is in bold.</p>
</div>
</section>
<section class="float-page">
{figure(1, "Autoencoder Training and Validation Loss on Normal Traffic", FIGS / "fig1_loss_curve.png",
        "Mean squared reconstruction error per epoch on a logarithmic scale. Both sets contain normal records only; "
        "validation loss was still improving at epoch 50, so early stopping did not end training.")}
</section>
<section class="float-page">
{figure(2, "Autoencoder Confusion Matrix and ROC Curve on the NSL-KDD Test Set", FIGS / "fig3_confusion_roc.png",
        "Threshold = 95th percentile of training reconstruction error. The black dot marks this operating "
        "point on the ROC curve. Test set: 9,711 normal and 12,833 attack connections.")}
</section>
<section class="float-page">
{figure(3, "Reconstruction Error by Category and Detection Rate by Attack Type", FIGS / "fig5_attack_type_recall.png",
        "Left: error distributions on a log scale; the dashed line is the detection threshold. Right: autoencoder "
        "recall for attack types with at least 20 test records; an asterisk marks types absent from training.")}
</section>
</body></html>"""


def main() -> None:
    html_path = HERE / "Module3_Lab_Report_APA.html"
    html_path.write_text(build_html(), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files",
                    f"--print-to-pdf={OUT_PDF}", html_path.as_uri()],
                   check=True, capture_output=True)
    print(f"Body word count: {body_word_count()}")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
