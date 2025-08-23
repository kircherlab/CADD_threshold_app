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
<br>When using CADD there are two scores. The raw and the PHRED-score. For the PHRED-score all potential single nucleotide variants (SNVs) in the genome (~9 billion) are sorted by their pathogenicity in comparison to all others. Each SNV then gets assigned a PHRED score depending on their rank. This means a variant that ranks in the top 10 percent of potentially pathogenic variants receives a PHRED score of 10 or higher. Variants in the top 1 percent receive a score of 20 or higher. PHRED scores are less resolved than Raw scores but are often used as they can be compared better with other scores.
<br> It might seem useful to have a universal cut-off value that clearly seperates pathogenic from benign variants. However, the CADD authors advise against this, as the threshold depends on the specific analysis and use case. Applying a single universal cut-off would risk a considerable loss of valuable information.
<br> Still, it is useful to see how variants are spread across different thresholds and to understand which factors affect what might be a good cut-off. The score distribution of known benign and pathogenic variants has been analysed and made usable on this website to help with finding a good cut-off for specific use cases.
<br>

For more information and reference please refer to the [CADD Website] (https://cadd.bihealth.org/).
<br>You may also look at these publications:

The most recent manuscript describes **CADD v1.7**, an extension to the annotations included in the model. Most prominently, this version improves the scoring of coding variants with features derived from the ESM-1v protein language model as well as the scoring of regulatory variants with features derived from a convolutional neural network trained on regions of open chromatin:

Schubach M, Maass T, Nazaretyan L, Röner S, Kircher M.<br>
*CADD v1.7: Using protein language models, regulatory CNNs and other nucleotide-level scores to improve genome-wide variant predictions.*<br>
*Nucleic Acids Res.* 2024 Jan 5. doi: [10.1093/nar/gkad989](https://doi.org/10.1093/nar/gkad989).<br>
PubMed PMID: [38183205](https://pubmed.ncbi.nlm.nih.gov/38183205/).<br>

---
Then there is **CADD-Splice (CADD v1.6)**, which specifically improved the prediction of splicing effects:

Rentzsch P, Schubach M, Shendure J, Kircher M.<br>
*CADD-Splice—improving genome-wide variant effect prediction using deep learning-derived splice scores.*<br>
*Genome Med.* 2021 Feb 22. doi: [10.1186/s13073-021-00835-9](https://doi.org/10.1186/s13073-021-00835-9).<br>
PubMed PMID: [33618777](https://pubmed.ncbi.nlm.nih.gov/33618777/).<br>

---
Our third manuscript describes the updates between the initial publication and **CADD v1.4**, introduces CADD for GRCh38 and explains how we envision the use of CADD. It was published by *Nucleic Acids Research* in 2018:

Rentzsch P, Witten D, Cooper GM, Shendure J, Kircher M.<br>
*CADD: predicting the deleteriousness of variants throughout the human genome.*<br>
*Nucleic Acids Res.* 2018 Oct 29. doi: [10.1093/nar/gky1016](https://doi.org/10.1093/nar/gky1016).<br>
PubMed PMID: [30371827](https://pubmed.ncbi.nlm.nih.gov/30371827/).<br>

---
Finally, the **original manuscript** describing the method was published by *Nature Genetics* in 2014:

Kircher M, Witten DM, Jain P, O'Roak BJ, Cooper GM, Shendure J.<br>
*A general framework for estimating the relative pathogenicity of human genetic variants.*<br>
*Nat Genet.* 2014 Feb 2. doi: [10.1038/ng.2892](https://doi.org/10.1038/ng.2892).<br>
PubMed PMID: [24487276](https://pubmed.ncbi.nlm.nih.gov/24487276/).<br>

<br>

##### **Which dataset was used and how?**
The variants used for the calculations were taken from [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) (accessed February 28, 2025). The original file had 6.806.227 entries. <br> To only use qualitative variants, only variants with the rating of “criteria provided, multiple submitters, no conflicts”, “reviewed by expert panel”, or “practice guideline” were kept. After removing the other entries 1.135.635 entries were left. Also, only variants with the clinical classification “benign”, “likely benign”, “pathogenic”, and “likely pathogenic” are usable so only these were kept. Now 668.455 entries were left. Because ClinVar has both reference genomes GRCh37/hg19 and GRCh38/hg38, these had to be separated too. In the end we were left with 334.246 entries for GRCh37 and 334.209 entries for GRCh38.
<br> All the variants that were left were now scored with CADD version 1.6 and 1.7 including annotations. CADD does not score InDels with more than 50 base pairs, variants where the reference allele does not fit with the reference allele of the reference genome and mitochondrial variants. So, CADD did not score 4.085 variants for GRCh37 and 4.196 variants for GRCh38.
<br> It might be interesting to note that CADD sometimes assigns more than one annotation to one variant. As the score for each annotation stays the same, one entry per variant is enough, so all duplicates were randomly deleted. That means for the table in the bab "Genes" only one annotation is included.
<br> GRCh37 has 252.785 benign and 77.3776 pathogenic variants while GRCh38 has 252.626 benign and 77.387 pathogenic variants.

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
