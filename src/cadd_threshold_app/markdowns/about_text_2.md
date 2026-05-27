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
