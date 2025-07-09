from shiny import reactive
from data_loader import load_metrics_bar
import pandas as pd 
metrics_dict_bar = load_metrics_bar()

def register_data_processing(input, output, session):

    #---------------------------------------------------------------------------------------------------
    # Labels for Bar Plots
    #---------------------------------------------------------------------------------------------------

    def categorize_label(label):
        label_lower = str(label).lower()
        if ('pathogenic' in label_lower and 'likely' not in label_lower) or 'pathogenic/likely risk allele' in label_lower:
            return 'pathogenic'
        elif 'likely pathogenic' in label_lower:
            return 'likely pathogenic'
        elif 'benign' in label_lower and 'likely' not in label_lower:
            return 'benign'
        elif 'likely benign' in label_lower:
            return 'likely benign'
        else:
            return 'unknown'
        
    #---------------------------------------------------------------------------------------------------
    # Page 4 - Genes | Take Genes from File or List | Filter Data for the Gene Input
    #---------------------------------------------------------------------------------------------------
    
        
    @reactive.calc
    def gene_list():
        if input.list_genes() and input.file_genes():
            raise ValueError("You can either put a list in the text field or upload a file, not both.")
        if not input.list_genes() and not input.file_genes():
            raise ValueError("You must input a gene list or upload a file.")

        if input.list_genes():
            genes = input.list_genes().replace(",", "\n").splitlines()
            return [gene.strip() for gene in genes if gene.strip()]

        elif input.file_genes():
            file_info = input.file_genes()
            df = pd.read_csv(file_info[0]["datapath"], header=None)
            return df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        
    @reactive.calc
    def filtered_data():
        data = metrics_dict_bar.get(input.select_version_gr_genes(), None)

        genes = set(gene_list())
        if "GeneSymbol" not in data.columns:
            raise ValueError("The uploaded CSV must contain a 'gene' column.")

        data["GeneSymbol"] = data["GeneSymbol"].astype(str).str.strip()
        df_filtered = data[data["GeneSymbol"].isin(genes)].copy()

        return df_filtered

