#### **About this site**
This app visualizes how ClinVar variants are distributed across CADD PHRED-score thresholds to help choose sensible score cut-offs for specific use cases.

<br>

##### **Quick links**
1.	To explore the **distribution** of ClinVar variants across CADD PHRED-score thresholds you can look <a href="#" onclick="document.querySelector('[data-value=compmetr]').click(); return false;">
    here
</a>.

2.	If you are interested in the **comparison of the different CADD versions and genome releases** you can look <a href="#" onclick="document.querySelector('[data-value=compvergr]').click(); return false;">
    here
</a>.

3.	If you want to investigate **gene-specific distribution** of variants across CADD PHRED-score thresholds you may look <a href="#" onclick="document.querySelector('[data-value=specificgenes]').click(); return false;">
    here
</a>.

4.	If you want to investiagte **panel-specific distribution** of variants across CADD PHRED-score thresholds you may look <a href="#" onclick="document.querySelector('[data-value=genepanels]').click(); return false;">
    here
</a>.

<br>


##### **What is CADD and how to use this application**
CADD (Combined Annotation Dependent Depletion) is a tool that is used for scoring the deleteriousness of single nucleotide variants, multi nucleotide substitutions and insertions/deletions variants in the human genome.
<br>When using CADD there are two scores. The raw and the PHRED-score. For the PHRED-score all potential single nucleotide variants (SNVs) in the genome (~9 billion) are sorted by their pathogenicity in comparison to all others. Each SNV then gets assigned a PHRED score depending on their rank. This means a variant that ranks in the top 10 percent of potentially pathogenic variants receives a PHRED score of 10 or higher. Variants in the top 1 percent receive a score of 20 or higher. PHRED scores are less resolved than Raw scores but are often used as they can be compared better with other scores.
<br> It might seem useful to have a universal cut-off value that clearly seperates pathogenic from benign variants. However, the CADD authors advise against this, as the threshold depends on the specific analysis and use case. Applying a single universal cut-off would risk a considerable loss of valuable information.
<br> Still, it is useful to see how variants are spread across different thresholds and to understand which factors affect what might be a good cut-off. The score distribution of known benign and pathogenic variants has been analysed and made usable on this website to help with finding a good cut-off for specific use cases.
<br>
<br>

##### **Which dataset was used and how?**
- Source: [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) (accessed 2025-02-28). Original file: ~6.8M entries.
- Kept only high-quality reviews (expert panel / practice guideline / multiple submitters, no conflicts). After filtering --> *1,135,635* entries.
- Kept clinical classes: benign, likely benign, pathogenic, likely pathogenic --> *668,455* entries.
- Split by reference genome: GRCh37 (*334,246*) and GRCh38 (*334,209*).
- Scored remaining variants with CADD v1.6 and v1.7. CADD does not score large indels (>50 bp), variants with mismatched reference allele, or mitochondrial variants (*4,085* unscored in GRCh37; *4,196* in GRCh38).
- Duplicated annotations per variant were de-duplicated (one entry per variant used in the "Genes" summary table)

**GRCh37: 252,785 benign / 77,377 pathogenic** <br>
**GRCh38: 252,626 benign / 77,387 pathogenic**

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

<br>
<br>

---
##### **For more information on CADD and reference please refer to the [CADD Website](https://cadd.bihealth.org/).**
##### **You may also look at these publications:**

---
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
