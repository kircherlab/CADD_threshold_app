##### **Which dataset was used and how?**
- Source: [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) (accessed 2026-04-22). Original file: *~8.9M* entries.
- Kept only high-quality reviews (expert panel / practice guideline / multiple submitters, no conflicts)
- Kept clinical classes: benign, likely benign, pathogenic, likely pathogenic
- After filtering -> *758.130* entries
- Split by reference genome: GRCh37 (*379.015*) and GRCh38 (*378.983*).
- Scored remaining variants with CADD v1.6 and v1.7. CADD does not score large indels (>50 bp), variants with mismatched reference allele, or mitochondrial variants 
- remaining variants -> GRCh37 & CADD v1.6: *377.966*;  GRCh37 & CADD v1.7: *377.965*; GRCh38 & CADD v1.7: *377.834*; GRCh38 & CADD v1.6: *377.835*
- Duplicated annotations per variant were de-duplicated (one entry per variant used in the "Genes" summary table)

**GRCh37: 284.194 benign / 93.772 (-1 for CADD v1.7) pathogenic** <br>
**GRCh38: 284.049 benign / 93.786 (-1 for CADD v1.7) pathogenic**

<br>