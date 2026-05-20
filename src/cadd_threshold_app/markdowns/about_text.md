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

