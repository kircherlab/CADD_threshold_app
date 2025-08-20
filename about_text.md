#### This website shows the results of analysing the distribution of ClinVar variants at certain CADD-Score Thresholds.

<br>

##### **What to do here?**
1.	You can look at the results of the calculations with the whole dataset <a href="#" onclick="document.querySelector('[data-value=compmetr]').click(); return false;">
    here
</a>.

2.	If you are interested in the comparison of the different CADD versions and genome releases you can look <a href="#" onclick="document.querySelector('[data-value=compvergr]').click(); return false;">
    here
</a>.

3.	If you have a specific use case and know the genes for the variants, you are looking at you can look <a href="#" onclick="document.querySelector('[data-value=specificgenes]').click(); return false;">
    here
</a>.

<br>

##### **What is CADD?**
CADD (Combined Annotation Dependent Depletion) is a tool that is used for scoring the deleteriousness of single nucleotide variants, multi nucleotide substitutions and insertions/deletions variants in the human genome.
<br> When using CADD there are two scores. The Raw and the PHRED Score. “The “PHRED-scaled” scores are normalized to all potential ~9 billion SNVs”. This means “a scaled score of 10 or greater indicates a raw score in the top 10% of all possible reference genome SNVs, and a score of 20 or greater indicates a raw score in the top 1%”. PHRED scores are less resolved than Raw scores but are often used as they can be compared better with other scores.
<br> It would also be nice to have a universal cut-off value for the score from where variants can be “declared as pathogenic as opposed to benign”. However, the developers of CADD do not recommend it as the choice of a cut-off depends on many “analysis-specific factors” and is individual to the use-case. If there was a universal cut-off value, the developers fear that there would be a “substantial loss of information”.
<br> Now the score distribution of known benign and pathogenic variants has been analysed and made usable on this website to help with finding a good cut-off for specific use cases.
<br> For more information on CADD:
PAPERS

<br>

##### **Which dataset was used and how?**
The variants used for the calculations were taken from ClinVar (DATUM). The original file had 6.806.227 entries. <br> To only use qualitative variants, only variants with the rating of “criteria provided, multiple submitters, no conflicts”, “reviewed by expert panel”, or “practice guideline” were kept. After removing the other entries 1.135.635 entries were left. Also, only variants with the clinical classification “benign”, “likely benign”, “pathogenic”, and “likely pathogenic” are usable so only these were kept. Now 668.455 entries were left. Because ClinVar has both reference genomes GRCh37/hg19 and GRCh38/hg38, these had to be separated too. In the end we were left with 334.246 entries for GRCh37 and 334.209 entries for GRCh38.
<br> All the variants that were left were now scored with CADD version 1.6 and 1.7 including annotations. CADD does not score InDels with more than 50 base pairs, variants where the reference allele does not fit with the reference allele of the reference genome and mitochondrial variants. So, CADD did not score 4.085 variants for GRCh37 and 4.196 variants for GRCh38.
<br> It might be interesting to note that CADD sometimes assigns more than one annotation to one variant. As the score for each annotation stays the same, one entry per variant is enough, so all duplicates were randomly deleted. That means for the table in the bab "Genes" only one annotation is included.
<br> GRCh37 has 252.785 benign and 77.3776 pathogenic variants while GRCh38 has 252.626 benign and 77.387 pathogenic variants.

<br>

##### **Normalized Calculation ???**
As some genes are represented more than others

<br>

##### **Used Metrics**

 Metric               | Meaning |
|----------------------|---------|
| **True Negatives (TN)** | Negative values were correctly identified as negative |
| **True Positives (TP)** | Positive values were correctly identified as positive |
| **False Negatives (FN)** | Positive values were incorrectly identified as negative |
| **False Positives (FP)** | Negative values were incorrectly identified as positive |
| **Precision** | `TP / (TP + FP)`: proportion of correctly positive predictions among all predicted positives |
| **Recall (Sensitivity)** | `TP / (TP + FN)`: proportion of correctly positive predictions among all actual positives |
| **False Positive Rate (FPR)** | `FP / (FP + TN)`: proportion of false positive predictions among all actual negatives |
| **Specificity** | `TN / (TN + FP)`: proportion of correct negative predictions among all actual negatives |
| **F1 Score** | `2 * (Precision * Recall) / (Precision + Recall)`: harmonic mean of precision and recall |
| **F2 Score** | Same as F1 Score but recall is weighted more heavily: `5 * (Precision * Recall) / (4 * Precision + Recall)` |
| **Accuracy** | `(TP + TN) / (TP + FP + FN + TN)`: proportion of correct predictions |
| **Balanced Accuracy** | `(Recall + Specificity) / 2`: useful for unbalanced classes |
