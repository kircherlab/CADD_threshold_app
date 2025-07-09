from shiny import reactive, render
import plotly.graph_objects as go
from data_loader import load_metrics, load_metrics_bar
from shinywidgets import render_widget 
import pandas as pd
metrics_dict = load_metrics()
metrics_dict_bar = load_metrics_bar()

from .data_processing import categorize_label, gene_list, filtered_data
from .metrics import calculate_metrics

def register_plots(input, output, session):

    #---------------------------------------------------------------------------------------------------
    # Page 1 - Basic Plot for Metrics
    #---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select, input.checkbox_group, input.slider, input.slider2)
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

    #---------------------------------------------------------------------------------------------------
    # Page 2 - Bar Plot to show number of labels per threshold
    #---------------------------------------------------------------------------------------------------


    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot():
        data = metrics_dict_bar.get(input.select(), None)
        if data is None:
            return go.Figure()

        data['category'] = data["ClinicalSignificance"].apply(categorize_label)

        bins = range(0, 110, 10)
        labels = [f'{i}-{i+10}' for i in range(0, 100, 10)]
        data['score_bin'] = pd.cut(data["PHRED"], bins=bins, labels=labels, include_lowest=True)

        grouped = data.groupby(['score_bin', 'category']).size().unstack(fill_value=0)

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
            title='Stacked Bar Chart for Thresholds with ClinicalSignificance',
            xaxis_title='Threshold',
            yaxis_title='Count',
            legend_title='Labels',
            height=600,
            width=1000
        )

        return fig

    #---------------------------------------------------------------------------------------------------
    # Page 3 - Compare a metric for all 4 Versions + Genome Releases
    #---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare, input.slider_yaxis_compare)
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
    # Page 4 - Genes | Text for missing genes in database | Basic Plot gene specific 
    #                | Table with all used entries | Bar Plot for number of labels per gene
    #                | Table for number of labels per gene 
    #---------------------------------------------------------------------------------------------------

    @render.text
    def missing_genes():
        df = metrics_dict_bar.get(input.select_version_gr_genes(), None)
        genes = set(gene_list())
        df_genes = set(df["GeneSymbol"].astype(str).str.strip())

        missing = genes - df_genes
        if missing:
            return f"Genes not found in the used database: {', '.join(sorted(missing))}"
        else:
            return "All genes were found in the used database."
        
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




