import plotly.graph_objects as go


def apply_cadd_plot_theme(fig: go.Figure, legend_title: str | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.82)",
        font=dict(
            family='Inter, "Segoe UI", Arial, sans-serif', size=12, color="#0f172a"
        ),
        margin=dict(l=60, r=150, t=70, b=60),
        hovermode="x unified",
        legend=dict(
            title=legend_title,
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(15, 23, 42, 0.08)",
        zeroline=False,
        linecolor="rgba(15, 23, 42, 0.15)",
        mirror=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(15, 23, 42, 0.08)",
        zeroline=False,
        linecolor="rgba(15, 23, 42, 0.15)",
        mirror=True,
    )
    fig.update_traces(line=dict(width=2.6), selector=dict(type="scatter"))
    fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
    return fig
