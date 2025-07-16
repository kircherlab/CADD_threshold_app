from shiny import reactive, render, ui
import starlette.responses
import plotly.graph_objects as go
from data_loader import load_metrics, load_metrics_bar
from shinywidgets import render_widget 
import pandas as pd 
import numpy as np
import re
metrics_dict = load_metrics()
metrics_dict_bar = load_metrics_bar()


from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score,
    f1_score, accuracy_score, balanced_accuracy_score
)


def server(input, output, session):

    @output
    @render.ui
    def out():
        # Register a dynamic route for the client to try to connect to.
        # It does nothing, just the 200 status code is all that the client
        # will care about.
        url = session.dynamic_route(
            "test",
            lambda req: starlette.responses.PlainTextResponse(
                "OK", headers={"Cache-Control": "no-cache"}
            ),
        )

        # Send JS code to the client to repeatedly hit the dynamic route.
        # It will succeed if and only if we reach the correct Python
        # process.
        return ui.tags.script(
            f"""
            const url = "{url}";
            const count_el = document.getElementById("count");
            const status_el = document.getElementById("status");
            let count = 0;
            async function check_url() {{
                count_el.innerHTML = ++count;
                try {{
                    const resp = await fetch(url);
                    if (!resp.ok) {{
                        status_el.innerHTML = "Failure!";
                        return;
                    }} else {{
                        status_el.innerHTML = "In progress";
                    }}
                }} catch(e) {{
                    status_el.innerHTML = "Failure!";
                    return;
                }}

                if (count === 100) {{
                    status_el.innerHTML = "Test complete";
                    return;
                }}

                setTimeout(check_url, 10);
            }}
            check_url();
            """
        )

#---------------------------------------------------------------------------------------------------
# Page 2
#---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select, input.checkbox_group, input.slider)
    def basic_plot():
        df = metrics_dict.get(input.select(), None)
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in input.checkbox_group():
            if metric in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["Threshold"],
                    y=df[metric],
                    mode='lines',
                    name=metric
                ))

        fig.update_layout(
            title='Confusion Matrix Components vs. Thresholds',
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title='Metrics', showgrid=True),
            template='simple_white',
            legend=dict(title='Metrics'),
            width=800,
            height=500
        )

        return fig
    
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

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot():
        data = metrics_dict_bar.get(input.select(), None)
        if data is None:
            return go.Figure()

        # Apply category
        data['category'] = data["ClinicalSignificance"].apply(categorize_label)

        # Create score bins
        bins = range(0, 110, 10)
        labels = [f'{i}-{i+10}' for i in range(0, 100, 10)]
        data['score_bin'] = pd.cut(data["PHRED"], bins=bins, labels=labels, include_lowest=True)

        # Group data
        grouped = data.groupby(['score_bin', 'category']).size().unstack(fill_value=0)

        # Prepare traces
        fig = go.Figure()
        colors = {
            'pathogenic': '#C44E52',
            'likely pathogenic': '#8172B2',
            'benign': '#55A868',
            'likely benign': '#CCB974',
            'unknown': '#4C72B0'
        }

        for category in grouped.columns:
            fig.add_trace(go.Bar(
                x=grouped.index.astype(str),
                y=grouped[category],
                name=category,
                marker_color=colors.get(category, '#333333'),
                text=grouped[category],
                textposition='inside'
            ))

        # Add total labels above bars
        totals = grouped.sum(axis=1)
        for i, total in enumerate(totals):
            fig.add_annotation(
                x=grouped.index[i],
                y=total,
                text=str(total),
                showarrow=False,
                yshift=10,
                font=dict(size=10, color='black', family='Arial Black')
            )

        # Layout adjustments
        fig.update_layout(
            barmode='stack',
            title='Stacked Bar Chart for Thresholds with ClinicalSignificance',
            xaxis_title='Threshold',
            yaxis_title='Count',
            legend_title='Labels',
            height=600,
            width=1000
        )

        return fig
    
    #---------------------------------------------------------------------------------------------------
    # Page 3 - Compare
    #---------------------------------------------------------------------------------------------------
    
    @render_widget
    @reactive.event(input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare)
    def compare_plot():
        metric = input.select_metric()
        fig = go.Figure()

        for version in input.checkbox_group_version_gr():
            df = metrics_dict.get(version, None)
            if df is None:
                continue

            fig.add_trace(go.Scatter(
                    x=df["Threshold"],
                    y=df[metric],
                    mode='lines',
                    name=version
                ))
         
        fig.update_layout(
            title='Confusion Matrix Components vs. Thresholds',
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider_xaxis_compare()),
            yaxis=dict(title='Metrics', showgrid=True),
            template='simple_white',
            legend=dict(title='Metrics'),
            width=800,
            height=500
        )

        return fig
    
    #---------------------------------------------------------------------------------------------------
    # Page 4 - Genes
    #---------------------------------------------------------------------------------------------------
 
    @reactive.calc
    def gene_list():
        if input.list_genes() and input.file_genes():
            raise ValueError("You can either put a list in the text field or upload a file, not both.")
        if not input.list_genes() and not input.file_genes():
            raise ValueError("You must input a gene list or upload a file.")

        if input.list_genes():
            genes = input.list_genes().replace(",", "\n").splitlines()
            return [gene.strip().upper() for gene in genes if gene.strip()]

        elif input.file_genes():
            file_info = input.file_genes()
            file_path = file_info[0]["datapath"]
            filename = file_info[0]["name"].lower()

            if filename.endswith(".tsv") or "\t" in open(file_path).read(1000):
                delimiter = "\t"
            elif ";" in open(file_path).read(1000):
                delimiter = ";"
            elif "\n" in open(file_path).read(1000):
                delimiter = "\n"
            else:
                delimiter = ","

            try:
                df = pd.read_csv(file_path, delimiter=delimiter, header=None)
            except Exception as e:
                raise ValueError(f"Could not read uploaded file: {e}")

            genes = df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()

            return genes

    def has_matching_gene(gene_entry):
        genes = set(gene_list())
        gene_set = set(g.strip() for g in re.split(r"[;,\s]+", gene_entry) if g)
        return not genes.isdisjoint(gene_set)

    @reactive.calc
    def filtered_data():
        data = metrics_dict_bar.get(input.select_version_gr_genes(), None)
        genes = set(gene_list())

        if "GeneSymbol" not in data.columns:
            raise ValueError("The uploaded CSV must contain a 'gene' column.")

        data["GeneSymbol"] = data["GeneSymbol"].astype(str).str.strip()
        mask = data["GeneSymbol"].apply(has_matching_gene)
        df_filtered = data[mask].copy()

        return df_filtered
        
    @render.text
    def missing_genes():
        df = metrics_dict_bar.get(input.select_version_gr_genes(), None)
        genes = set(gene_list())
        df_genes = set(df["GeneSymbol"].astype(str).str.strip().str.upper())

        missing = genes - df_genes
        if missing:
            return f"Genes not found in the CSV: {', '.join(sorted(missing))}"
        else:
            return "All genes were found in the CSV."
        
    @reactive.calc
    def calculate_metrics():
        label_column = "ClinicalSignificance"
        data = filtered_data()

        data["ClinicalSignificance"] = (
            data["ClinicalSignificance"].str.contains("pathogenic", case=False, na=False)
        ).map({True: 'pathogenic', False: 'benign'})

        thresholds = np.arange(1, 100, step=10)
        data = data.sort_values("PHRED")
        #cumulative_benign = pd.Series([False] * len(data), index=data.index)

        rows = []

        for threshold in thresholds:
            current_benign = data["PHRED"] <= threshold

            #cumulative_benign |= current_benign
            data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")
            
            try:
                tn, fp, fn, tp = confusion_matrix(
                    data[label_column], data["binary_prediction"],
                    labels=["benign", "pathogenic"]
                ).ravel()
            except ValueError:
                tn = fp = fn = tp = 0

            precision = precision_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
            recall = recall_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
            f1 = f1_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
            f2 = (5 * precision * recall) / (4 * precision + recall) if (precision + recall) > 0 else 0
            accuracy = accuracy_score(data[label_column], data["binary_prediction"])
            balanced_acc = balanced_accuracy_score(data[label_column], data["binary_prediction"])
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

            rows.append({
                "Threshold": threshold,
                "TrueNegatives": tn,
                "FalsePositives": fp,
                "FalseNegatives": fn,
                "TruePositives": tp,
                "Precision": precision,
                "Recall": recall,
                "F1Score": f1,
                "F2Score": f2,
                "Accuracy": accuracy,
                "BalancedAccuracy": balanced_acc,
                "FalsePositiveRate": fpr,
                "Specificity": specificity
            })

        result_df = pd.DataFrame(rows)
        return result_df
    
    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_plot_genes():
        df = calculate_metrics()
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Threshold"],
                y=df[metric],
                mode='lines',
                name=metric
            ))

        fig.update_layout(
            title='Confusion Matrix Components vs. Thresholds',
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title='Metrics', showgrid=True),
            template='simple_white',
            legend=dict(title='Metrics'),
            width=800,
            height=500
        )

        return fig
    
    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_full():
        return render.DataGrid(filtered_data())
    

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_bar_plot_by_gene():

        data = filtered_data()
        if data is None or data.empty:
            return go.Figure()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = data.groupby([data['GeneSymbol'], 'category']).size().unstack(fill_value=0)
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]

        fig = go.Figure()
        colors = {
            'pathogenic': '#C44E52',
            'likely pathogenic': '#8172B2',
            'benign': '#55A868',
            'likely benign': '#CCB974',
            'unknown': '#4C72B0'
        }

        for category in grouped.columns:
            fig.add_trace(go.Bar(
                x=grouped.index.astype(str),
                y=grouped[category],
                name=category,
                marker_color=colors.get(category, '#333333'),
                text=grouped[category],
                textposition='inside'
            ))

        totals = grouped.sum(axis=1)
        for i, total in enumerate(totals):
            fig.add_annotation(
                x=grouped.index[i],
                y=total,
                text=str(total),
                showarrow=False,
                yshift=10,
                font=dict(size=10, color='black', family='Arial Black')
            )

        fig.update_layout(
            barmode='stack',
            title='Stacked Bar Chart by Gene and Clinical Significance',
            xaxis_title='Gene',
            yaxis_title='Count',
            legend_title='Clinical Significance',
            height=600,
            width=1000,
            xaxis_tickangle=-45
        )

        return fig
    
    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_together():
        data = filtered_data()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = data.groupby([data['GeneSymbol'], 'category']).size().unstack(fill_value=0)
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]
        grouped = grouped.reset_index()

        return render.DataGrid(grouped)







            
        
        
                
