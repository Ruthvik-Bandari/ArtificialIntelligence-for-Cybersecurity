# Module 4: Credit Card Fraud Detection with Threat Intelligence

A supervised fraud detector on the Kaggle **Credit Card Fraud Detection** dataset (284,807 transactions, 0.17% fraud), plus the phishing-email exploration the brief's Step 1 asks for.

**Notebook:** [`Bandari_Ruthvik_Nath_AI_IDS_lab3.ipynb`](Bandari_Ruthvik_Nath_AI_IDS_lab3.ipynb). The filename is the one the assignment brief specifies.
**Report (PDF, APA 7):** [`Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf`](Bandari_Ruthvik_Nath_AI_IDS_lab3_Report.pdf)

## Pipeline

1. **Data:** both datasets download automatically with `kagglehub`; duplicates are removed before a stratified 80/20 split.
2. **Imbalance:** SMOTE to a 1:10 ratio, applied inside each cross-validation training fold only.
3. **Models:** logistic regression, random forest and XGBoost, each tuned with GridSearchCV over stratified 3-fold CV (F1 and AUC-ROC).
4. **Ensemble:** a soft-voting ensemble of the two strongest models, plus feature importance from four methods.
5. **Step 3:** test metrics with ROC and PR curves, a 6-panel dashboard, false positive/negative analysis, a generated threat intelligence report with thresholds chosen on training folds, and real-time scoring with an uncertainty band and approve/review/block decisions.

## Run it

**Google Colab:** upload the notebook and choose *Runtime → Run all*. It takes about 25 minutes on a free CPU and needs no Kaggle login.

**Rebuild the report** from any executed copy of the notebook, for example the one run on Colab:
```bash
python report/build_apa_report.py path/to/executed_notebook.ipynb
```
Every number and figure in the PDF comes from that notebook's outputs.
