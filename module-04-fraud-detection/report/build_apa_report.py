"""Build the Module 4 lab report as an APA 7 student paper (HTML -> PDF via headless Chrome).

Every number and figure is read from an executed notebook: the cell tagged "summary" prints a JSON summary,
and cells tagged "fig_*" hold the figures. Pointing the script at the Colab-executed notebook therefore produces
a report that matches that run exactly.

Usage:  python report/build_apa_report.py [path/to/executed_notebook.ipynb]
Output: Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf (module folder)
"""
import base64
import html
import json
import re
import subprocess
import sys
from pathlib import Path

# ---- TITLE PAGE (APA 7 student paper) ---------------------------------------------------------
TITLE = "Detecting Credit Card Fraud With a Voting Ensemble: Imbalanced Learning and Threat Intelligence"
AUTHOR = "Ruthvik Nath Bandari"
AFFILIATION = "Northeastern University"
COURSE = "AAI6680: AI for Cybersecurity"
INSTRUCTOR = "Mimoza Dimodugno, PhD"
DUE_DATE = "October 11, 2026"
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
T = S["test"]
ENS = f"Ensemble ({S['ensemble_label']})"
LR, RF, XGB = T["Logistic Regression"], T["Random Forest"], T["XGBoost"]
E = T[ENS]
TH = S["thresholds"]
BAL = TH["Balanced (max F1 in training)"]
HR = TH["High recall (≥ 90% recall in training)"]
BUD = TH["Alert budget (≤ 100 alerts per 100k in training)"]
REF = TH["Reference: default 0.5"]
P = S["params"]
nice = lambda name: name.replace("Random Forest", "random forest").replace("Logistic Regression", "logistic regression")
aucs = [m["AUC-ROC"] for m in T.values()]
prs = [m["PR-AUC"] for m in T.values()]
f1, f2, f3 = S["top_features"][:3]
ens_name = S["ensemble_label"].replace("Random Forest", "random forest").replace("Logistic Regression", "logistic regression")


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
Card fraud is a needle-in-a-haystack problem. In the Credit Card Fraud Detection dataset (Dal Pozzolo et al., 2015; Machine Learning Group - ULB, 2018), only {S['fraud_rate']:.2%} of transactions are fraudulent. This lab compared three supervised models and a voting ensemble and turned their output into threat intelligence for a bank's fraud team. As the brief requested, it also briefly analyzes phishing emails (Cyber Cop, 2023).
"""

METHOD = f"""
After {S['n_dupes']:,} duplicate rows were removed, {S['n']:,} transactions remained, {S['n_fraud']} of them fraudulent. A stratified 80/20 split kept the real fraud rate in the test set. *Amount* was scaled with a robust scaler; the other 28 features are anonymized principal components. *Time* was excluded because it counts seconds from the start of the recording and would mean nothing for a live transaction. To counter the imbalance, SMOTE (Chawla et al., 2002) generated synthetic frauds up to a 1:10 ratio, only inside each cross-validation training fold, so no synthetic data reached validation or test scores.

Logistic regression, random forest, and XGBoost (Chen & Guestrin, 2016) were tuned with grid search over stratified three-fold cross-validation, selecting on F1 and reporting AUC-ROC. The best settings were C = {P['Logistic Regression']['C']} for logistic regression, a maximum depth of {P['XGBoost']['max_depth']} and learning rate of {P['XGBoost']['learning_rate']} for XGBoost, and fully grown trees for the random forest. The two strongest models were combined in a soft-voting ensemble. Detection thresholds were chosen from out-of-fold training predictions, never from the test set.
"""

same_tp = len({m["TP"] for m in T.values()}) == 1
ref_name = S["ens_fp_ref"]
test_sentence = (
    f"On the test set (Table 1), every model found {int(E['TP'])} of {S['test_fraud']} frauds at the default threshold, but the "
    f"ensemble raised only {int(E['FP'])} false alarms, against {int(XGB['FP'])} for XGBoost and {int(LR['FP'])} for logistic "
    f"regression. That gave the ensemble a precision of {E['precision']:.3f} and an F1 of {E['F1']:.3f}."
    if same_tp else
    f"On the test set (Table 1), the ensemble found {int(E['TP'])} of {S['test_fraud']} frauds with {int(E['FP'])} false alarms "
    f"(precision {E['precision']:.3f}, F1 {E['F1']:.3f}), against {int(T[ref_name]['TP'])} and {int(T[ref_name]['FP'])} for "
    f"{nice(ref_name)}; with only {S['test_fraud']} test frauds, that difference is small."
)
cv = S["cv"]
RESULTS = f"""
In cross-validation, XGBoost (F1 = {cv['XGBoost']['f1']:.3f}) and random forest ({cv['Random Forest']['f1']:.3f}) outperformed logistic regression ({cv['Logistic Regression']['f1']:.3f}). The {ens_name} ensemble scored highest ({S['ens_cv']['CV f1']:.3f}), although the gain was within one fold-to-fold standard deviation. {test_sentence} AUC-ROC barely separated the models ({min(aucs):.3f}–{max(aucs):.3f}), whereas PR-AUC did ({min(prs):.3f}–{max(prs):.3f}; Figure 1). PR-AUC is therefore the more informative summary.
"""

INTEL = f"""
In the full dataset, the median fraudulent transaction was small (€{S['fraud_amount']:.2f} against €{S['legit_amount']:.2f}; see also the dashboard in Figure 2), although a tail of larger frauds pushed the fraud mean above the legitimate mean. The fraud rate peaked at {S['peak_rate']:.1%} in hour {S['peak_hour']} counted from the first transaction (both days pooled), one of the lowest-volume hours. Ranked by mean position across four importance methods (Figure 3), *{f1}*, *{f2}*, and *{f3}* were the strongest fraud indicators.

Table 2 gives the recommended thresholds. The balanced threshold ({BAL['threshold']:.3f}) caught {BAL['caught']} test frauds with a precision of {BAL['precision']:.2f}. The high-recall threshold caught {HR['caught']}, but alerts rose from {BAL['alerts_per_100k']:,.0f} to {HR['alerts_per_100k']:,.0f} per 100,000 transactions. The default 0.5 caught {REF['caught']}, so thresholds need recalibration after deployment. The {S['fn']} missed frauds had a median value of €{S['fn_amount']:.2f} and looked close to legitimate traffic on the top predictor, *{f1}*, suggesting that per-card behavioral features, not a more complex model, are the next step. In a simulated real-time stream, scoring took {S['latency_ms']:.1f} ms per transaction ({S['decision_ms']:.0f} ms with the uncertainty band), and uncertain transactions went to manual review.

The phishing classifier reached an AUC-ROC of {S['phish_auc']:.3f}, an easier task because phishing vocabulary is distinctive. With two days of 2013 data and a random split, production results would likely be weaker.
"""

REFLECTION = """
My Module 1 and Module 3 detectors learned only from normal traffic. This lab gave me labels, and they did not make the problem easy. With roughly one fraud in every 600 transactions, accuracy is meaningless, and SMOTE had to stay inside the cross-validation folds; applying it before splitting would have produced better-looking numbers and a worse model.

The missed frauds looked close to legitimate traffic on the strongest components, which echoes my Module 3 autoencoder: a stronger model cannot find a signal the data does not contain. I want to build detection systems whose thresholds are set together with the analysts who handle the alerts, and which, like the review band in my real-time scorer, know when they are unsure and hand those cases to a person.
"""


def fmt_row(name, m):
    return (name, f"{m['precision']:.3f}", f"{m['recall']:.3f}", f"{m['F1']:.3f}", f"{m['AUC-ROC']:.3f}",
            f"{m['PR-AUC']:.3f}", f"{int(m['FP'])}")


TABLE1 = [fmt_row("Logistic regression", LR), fmt_row("Random forest", RF), fmt_row("XGBoost", XGB),
          fmt_row(f"Ensemble ({nice(S['ensemble_label'])})", E)]
TABLE2 = [(label, f"{v['threshold']:.3f}", v["caught"], f"{v['precision']:.2f}", f"{v['alerts_per_100k']:,.0f}")
          for label, v in [("Balanced (maximum F1 in training), recommended", BAL),
                           ("High recall (at least 90% recall in training)", HR),
                           ("Alert budget (at most 100 alerts per 100,000 in training)", BUD),
                           ("Reference: default threshold", REF)]]

REFERENCES = [
    "Chawla, N. V., Bowyer, K. W., Hall, L. O., &amp; Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling "
    "technique. <i>Journal of Artificial Intelligence Research, 16</i>, 321–357. https://doi.org/10.1613/jair.953",
    "Chen, T., &amp; Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In <i>Proceedings of the 22nd ACM SIGKDD "
    "International Conference on Knowledge Discovery and Data Mining</i> (pp. 785–794). Association for Computing Machinery. "
    "https://doi.org/10.1145/2939672.2939785",
    "Cyber Cop. (2023). <i>Phishing email detection</i> [Data set]. Kaggle. https://www.kaggle.com/datasets/subhajournal/phishingemails",
    "Dal Pozzolo, A., Caelen, O., Johnson, R. A., &amp; Bontempi, G. (2015). Calibrating probability with undersampling for "
    "unbalanced classification. In <i>2015 IEEE Symposium Series on Computational Intelligence</i> (pp. 159–166). IEEE. "
    "https://doi.org/10.1109/SSCI.2015.33",
    "Machine Learning Group - ULB. (2018). <i>Credit card fraud detection</i> (Version 3) [Data set]. Kaggle. "
    "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
]


def body_word_count() -> int:
    text = " ".join([INTRO, METHOD, RESULTS, INTEL, REFLECTION])
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
  table {{ width: 100%; border-collapse: collapse; line-height: 1.5; margin: 0.1in 0; }}
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

<h2>Threat Intelligence</h2>
{paras(INTEL)}

<h1>Reflection</h1>
{paras(REFLECTION)}

<section class="refs">
  <h1>References</h1>
  {refs_html}
</section>

<section class="float-page">
{table(1, "Test-Set Performance of the Three Models and the Voting Ensemble",
       ["Model", "Precision", "Recall", "F1", "AUC-ROC", "PR-AUC", "False alarms"], TABLE1,
       f"Test set of {S['n_test']:,} transactions, {S['test_fraud']} of them fraud, at a probability threshold of 0.5. "
       "PR-AUC = area under the precision-recall curve.")}
</section>
<section class="float-page">
{table(2, "Recommended Detection Thresholds for the Ensemble",
       ["Operating point", "Threshold", "Frauds caught", "Precision", "Alerts per 100,000"], TABLE2,
       f"Thresholds were chosen from out-of-fold predictions on the training set and evaluated on the {S['n_test']:,}-transaction "
       f"test set ({S['test_fraud']} frauds). The default threshold is shown for comparison only.")}
</section>
<section class="float-page">
{figure(1, "ROC and Precision-Recall Curves on the Test Set", FIGS["fig_roc"],
        "The middle panel zooms into false-positive rates of 1% or less. AP = average precision (PR-AUC).")}
</section>
<section class="float-page">
{figure(2, "Fraud Detection Dashboard", FIGS["fig_dashboard"],
        f"Test-set transactions scored by the ensemble at the balanced threshold of {BAL['threshold']:.3f}. Hours are counted "
        "from the dataset's first transaction because clock time is not provided. The 48-hour timeline uses the full dataset.")}
</section>
<section class="float-page">
{figure(3, "Top Fraud Predictors by Four Importance Methods", FIGS["fig_importance"],
        "Logistic regression coefficients are scaled by each feature's standard deviation. Permutation importance measures "
        "the drop in the ensemble's PR-AUC on the test set when a feature is shuffled.")}
</section>
</body></html>"""


def main() -> None:
    html_path = HERE / "Module4_Lab_Report_APA.html"
    html_path.write_text(build_html(), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={OUT_PDF}", html_path.as_uri()],
                   check=True, capture_output=True)
    print(f"Source notebook: {NOTEBOOK.name}")
    print(f"Body word count: {body_word_count()}")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
