#### Metrics Calculation for gene panels (from PanelApp)
1. Choose your genome release and CADD version.
2. Select a gene panel from the dropdown menu.
3. Click on the “Generate metrics” button.
4. Now all the metrics will load in one line graph. (If you want to see one metric, double click on the name on the legend. If you want to see more than one metrics, deselect all others by clicking once on the name on the legend.)
- If you want to know which variants were used for calculating, together with their annotations, you can look at the table. You may choose if you want to look at the ClinVar or CADD annotations or both.
For ClinVar only these annotations were kept: 'AlleleID', 'Type_x', 'Name', 'GeneID_x', 'GeneSymbol', 'Origin', 'OriginSimple', 'Chromosome', 'ReviewStatus', 'NumberSubmitters', 'VariationID', 'PositionVCF', 'ReferenceAlleleVCF', 'AlternateAlleleVCF', 'ClinicalSignificance'
- To see how many variants were used per gene and if they are pathogenic or benign you can look at the bar chart (it might not be visible if you used a lot of variants, you could still zoom in). Below the bar chart is also a table that summarizes the information from the bar chart.

#### Note:
- The gene panels are retrieved from [PanelApp] (https://panelapp.genomicsengland.co.uk/). The data is updated regularly, but there might be some delay between the latest PanelApp data and the data used in this tool.
- The gene names in the panels are matched against the gene names in the ClinVar and CADD databases. If a gene from the panel is not found in these databases, it will be skipped, and a message will be displayed indicating which genes were not found.
