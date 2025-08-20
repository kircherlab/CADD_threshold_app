from shiny import reactive, render, ui
import starlette.responses
import plotly.graph_objects as go
import plotly.express as px
from data_loader import load_metrics, load_metrics_bar
from shinywidgets import render_widget
import pandas as pd
import numpy as np
import re
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score, balanced_accuracy_score
#metrics_dict = load_metrics()
#metrics_dict_bar = load_metrics_bar()





def server(input, output, session):

    @output
    @render.ui
    def out():
        # Register a dynamic route for the client to try to connect to.
        # It does nothing, just the 200 status code is all that the client
        # will care about.
        url = session.dynamic_route(
            "test",
            lambda req: starlette.responses.PlainTextResponse("OK", headers={"Cache-Control": "no-cache"}),
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

    # ---------------------------------------------------------------------------------------------------
    # Page 2
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select, input.checkbox_group, input.slider)
    def basic_plot():
        df = load_metrics(input.select())
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in input.checkbox_group():
            if metric in df.columns:
                fig.add_trace(go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=metric))

        fig.update_layout(
            title="Metrics at different thresholds",
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title="Metrics (Number of variants or percent)", showgrid=True),
            template="simple_white",
            legend=dict(title="Metrics"),
            width=800,
            height=500,
        )

        return fig

    def categorize_label(label):
        label_lower = str(label).lower()
        if ("pathogenic" in label_lower and "likely" not in label_lower) or "pathogenic/likely risk allele" in label_lower:
            return "pathogenic"
        elif "likely pathogenic" in label_lower:
            return "likely pathogenic"
        elif "benign" in label_lower and "likely" not in label_lower:
            return "benign"
        elif "likely benign" in label_lower:
            return "likely benign"
        else:
            return "unknown"

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot():
        df = load_metrics_bar(input.select())
        if df is None:
            return go.Figure()

        data = df.copy()
        data['category'] = data["ClinicalSignificance"].apply(categorize_label)

        bins = range(0, 110, 10)
        labels = [f"{i}-{i+10}" for i in range(0, 100, 10)]
        data["score_bin"] = pd.cut(data["PHRED"], bins=bins, labels=labels, include_lowest=True)

        grouped = data.groupby(['score_bin', 'category'], observed=True).size().unstack(fill_value=0)

        fig = go.Figure()
        colors = {
            "pathogenic": "#C44E52",
            "likely pathogenic": "#8172B2",
            "benign": "#55A868",
            "likely benign": "#CCB974",
            "unknown": "#4C72B0",
        }

        for category in grouped.columns:
            fig.add_trace(
                go.Bar(
                    x=grouped.index.astype(str),
                    y=grouped[category],
                    name=category,
                    marker_color=colors.get(category, "#333333"),
                    text=grouped[category],
                    textposition="inside",
                )
            )

        totals = grouped.sum(axis=1)
        for i, total in enumerate(totals):
            fig.add_annotation(
                x=grouped.index[i],
                y=total,
                text=str(total),
                showarrow=False,
                yshift=10,
                font=dict(size=10, color="black", family="Arial Black"),
            )

        fig.update_layout(
            barmode="stack",
            title="Distribution of ClinVar variants from threshold 0 to 100 in steps of 10",
            xaxis_title="PHRED Score",
            yaxis_title="Number of variants",
            legend_title="Clinical Classification from ClinVar",
            height=600,
            width=1000,
        )

        return fig

    @render_widget
    @reactive.event(input.select, input.slider_bar_small)
    def basic_bar_plot_smaller():
        df = load_metrics_bar(input.select())
        if df is None:
            return go.Figure()

        min_val, max_val = input.slider_bar_small()
        df = df[(df["PHRED"] >= min_val) & (df["PHRED"] < max_val)]

        data = df.copy()
        data['category'] = data["ClinicalSignificance"].apply(categorize_label)

        bins = range(0, 101, 1)
        labels = [f"{i}-{i+1}" for i in range(0, 100)]
        data["score_bin"] = pd.cut(data["PHRED"], bins=bins, labels=labels, include_lowest=True, right=False)

        grouped = data.groupby(['score_bin', 'category'], observed=True).size().unstack(fill_value=0)
        grouped.index = grouped.index.astype(str)

        fig = go.Figure()
        colors = {
            "pathogenic": "#C44E52",
            "likely pathogenic": "#8172B2",
            "benign": "#55A868",
            "likely benign": "#CCB974",
            "unknown": "#4C72B0",
        }

        for category in grouped.columns:
            fig.add_trace(
                go.Bar(
                    x=grouped.index,
                    y=grouped[category],
                    name=category,
                    marker_color=colors.get(category, "#333333"),
                    text=grouped[category],
                    textposition="inside",
                )
            )

        totals = grouped.sum(axis=1)
        for i, total in enumerate(totals):
            fig.add_annotation(
                x=grouped.index[i],
                y=total,
                text=str(total),
                showarrow=False,
                yshift=10,
                font=dict(size=10, color="black", family="Arial Black"),
            )

        fig.update_layout(
            barmode="stack",
            title="Distribution of ClinVar variants in steps of 1",
            xaxis_title="PHRED Score",
            yaxis_title="Nummber of variants",
            legend_title="Clinical Classification from ClinVar",
            height=600,
            width=1000,
            xaxis=dict(type='category')
        )

        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot_consequence_pathogenic():
        df = load_metrics_bar(input.select())
        if df is None:
            return go.Figure()

        data = df.copy()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)
        data_filtered = data[data['category'].isin(['pathogenic', 'likely pathogenic'])]

        # Bins
        bins = list(range(0, 101))
        labels = [f"{i}-{i+1}" for i in range(0, 100)]
        data_filtered["score_bin"] = pd.cut(data_filtered["PHRED"], bins=bins, labels=labels, include_lowest=True, right=False)

        # Group by score_bin, category, and consequence
        grouped = (
            data_filtered
            .groupby(['score_bin', 'category', 'Consequence'])
            .size()
            .reset_index(name='count')
        )

        fig = go.Figure()
        categories = ['pathogenic', 'likely pathogenic']
        consequences = grouped['Consequence'].unique()

        palette = px.colors.qualitative.Light24  # 26 colors, enough for most cases
        color_map = {cons: palette[i % len(palette)] for i, cons in enumerate(consequences)}

        # For grouped bars, offset by category
        for cons in consequences:
            for cat in categories:
                df_cons = grouped[(grouped['Consequence'] == cons) & (grouped['category'] == cat)]
                if not df_cons.empty:
                    fig.add_trace(go.Bar(
                        x=df_cons['score_bin'],
                        y=df_cons['count'],
                        name=cons,  # legend shows only consequences
                        offsetgroup=cat,  # separate pathogenic vs likely pathogenic
                        legendgroup=cons,  # ensures one legend entry per consequence
                        showlegend=(cat == 'pathogenic'),  # only show legend once
                        marker_color=color_map[cons],
                        opacity=0.6 if cat == 'likely pathogenic' else 1.0,
                        hovertemplate=f"%{{x}}<br>{cat}<br>{cons}: %{{y}}<extra></extra>"
                    ))

        fig.update_layout(
            barmode="stack",  # stack only consequences within each category bar
            xaxis=dict(type='category'),
            title="Distribution of variant consequences across thresholds for pathogenic/likely pathogenic variants",
            xaxis_title="PHRED Score",
            yaxis_title="Number of variants",
        )
        return fig


    # ---------------------------------------------------------------------------------------------------
    # Page 4 - Genes
    #---------------------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------------------
    # Read Genes from File or List
    #---------------------------------------------------------------------------------------------------

    @reactive.calc
    def gene_list():
        try:
            if input.list_genes() and input.file_genes():
                return None
            if not input.list_genes() and not input.file_genes():
                return None

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
                    return None

                genes = df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
                return genes

        except Exception as e:
            print(f"Unexpected Error in gene_list: {e}")
            return None

    #---------------------------------------------------------------------------------------------------
    # Print Errors or Genes not available
    #---------------------------------------------------------------------------------------------------

    @render.text
    def missing_genes():
        data = load_metrics_bar(input.select_version_gr_genes())
        df = data.copy()
        genes = gene_list()

        if genes == None:
            if input.list_genes() and input.file_genes():
                return "You can either put a list in the text field or upload a file, not both."
            elif not input.list_genes() and not input.file_genes():
                return "You must input a gene list or upload a file."
            else:
                return "Something went wrong while processing your input."

        if df is None or df.empty:
            return "No dataset loaded for the selected version."

        df_genes = set(df["GeneName"].astype(str).str.strip().str.upper())
        missing = set(genes) - df_genes

        if missing:
            return f"Genes not found in the CSV: {', '.join(sorted(missing))}"
        else:
            return "All genes were found in the CSV."

    #---------------------------------------------------------------------------------------------------
    # Find the matching entries and Filter the CSV (Copy)
    #---------------------------------------------------------------------------------------------------

    def has_matching_gene(gene_entry):
        genes = set(gene_list())
        gene_set = set(g.strip() for g in re.split(r"[;,\s]+", gene_entry) if g)
        return not genes.isdisjoint(gene_set)

    @reactive.calc
    def filtered_data():
        data = load_metrics_bar(input.select_version_gr_genes())
        if "GeneName" not in data.columns:
            raise ValueError("The uploaded CSV must contain a 'gene' column.")

        data["GeneName"] = data["GeneName"].astype(str).str.strip()
        mask = data["GeneName"].apply(has_matching_gene)
        df_filtered = data[mask].copy()

        return df_filtered

    #---------------------------------------------------------------------------------------------------
    # Calculate the new metrics
    #---------------------------------------------------------------------------------------------------

    @reactive.calc
    def calculate_metrics():
        label_column = "ClinicalSignificance"
        data = filtered_data()

        data["ClinicalSignificance"] = (data["ClinicalSignificance"].str.contains("pathogenic", case=False, na=False)).map(
            {True: "pathogenic", False: "benign"}
        )

        thresholds = np.arange(1, 100, step=10)
        data = data.sort_values("PHRED")

        rows = []

        for threshold in thresholds:
            current_benign = data["PHRED"] <= threshold

            data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")

            try:
                tn, fp, fn, tp = confusion_matrix(
                    data[label_column], data["binary_prediction"], labels=["benign", "pathogenic"]
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

            rows.append(
                {
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
                    "Specificity": specificity,
                }
            )

        result_df = pd.DataFrame(rows)
        return result_df

    #----------------------------------------------------------------------------------------------------------------------------------
    # Page 4 - Plots: Linear Plot with all metrics | the whole dataframe | Barplot for number of entries | Table for number of entries
    #----------------------------------------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_plot_genes():
        df = calculate_metrics()
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in df.columns:
            fig.add_trace(go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=metric))

        fig.update_layout(
            title="Confusion Matrix Components vs. Thresholds",
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title="Metrics", showgrid=True),
            template="simple_white",
            legend=dict(title="Metrics"),
            width=800,
            height=500,
        )

        return fig

    @render.data_frame
    @reactive.event(input.action_button_genes, input.radio_buttons_table)
    def data_frame_full():
        df = filtered_data()
        genes = gene_list()

        if genes == None:
             return render.text("No Genes were given (yet)")
        elif input.radio_buttons_table() == "ClinVar":
            return render.DataGrid(df[['AlleleID', 'Type_x', 'Name', 'GeneID_x', 'GeneSymbol', 'Origin', 'OriginSimple', 'Chromosome', 'ReviewStatus', 'NumberSubmitters', 'VariationID', 'PositionVCF', 'ReferenceAlleleVCF', 'AlternateAlleleVCF', 'ClinicalSignificance']])
        elif input.radio_buttons_table() == "CADD":
            return render.DataGrid(df.drop(columns=['AlleleID', 'Type_x', 'Name', 'GeneID_x', 'GeneSymbol', 'Origin', 'OriginSimple', 'ReviewStatus', 'NumberSubmitters', 'VariationID', 'ClinicalSignificance']))
        else:
            return render.DataGrid(df)

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_bar_plot_by_gene():

        data = filtered_data()
        if data is None or data.empty:
            return go.Figure()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = data.groupby([data['GeneName'], 'category'], observed=True).size().unstack(fill_value=0)
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]

        fig = go.Figure()
        colors = {
            "pathogenic": "#C44E52",
            "likely pathogenic": "#8172B2",
            "benign": "#55A868",
            "likely benign": "#CCB974",
            "unknown": "#4C72B0",
        }

        for category in grouped.columns:
            fig.add_trace(
                go.Bar(
                    x=grouped.index.astype(str),
                    y=grouped[category],
                    name=category,
                    marker_color=colors.get(category, "#333333"),
                    text=grouped[category],
                    textposition="inside",
                )
            )

        totals = grouped.sum(axis=1)
        for i, total in enumerate(totals):
            fig.add_annotation(
                x=grouped.index[i],
                y=total,
                text=str(total),
                showarrow=False,
                yshift=10,
                font=dict(size=10, color="black", family="Arial Black"),
            )

        fig.update_layout(
            barmode="stack",
            title="Stacked Bar Chart by Gene and Clinical Significance",
            xaxis_title="Gene",
            yaxis_title="Count",
            legend_title="Clinical Significance",
            height=600,
            width=1000,
            xaxis_tickangle=-45,
        )

        return fig

    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_together():
        data = filtered_data()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = data.groupby([data['GeneName'], 'category'], observed=True).size().unstack(fill_value=0)
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]
        grouped = grouped.reset_index()

        return render.DataGrid(grouped)
