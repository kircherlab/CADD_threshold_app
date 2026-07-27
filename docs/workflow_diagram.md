# CADD Threshold App Workflow Diagram

Use this schematic as a manuscript figure to complement UI screenshots.

```mermaid
flowchart LR
    subgraph OFFLINE_DATA_GENERATION
        CV[ClinVar release]
        CADD[CADD score tables\nversion and genome release]
        PP[PanelApp API snapshot]
        WK[Preprocessing workflow\nnormalization, consequence labels, joins]
        PM[Panel metrics generation\nall panels for available datasets]
        DS[(Packaged data directory\nmetrics, annotations, panel summaries)]

        CV --> WK
        CADD --> WK
        PP --> PM
        WK --> DS
        PM --> DS
    end

    subgraph WEB_APP_RUNTIME
        APP[CADD Threshold App]

        TAB1[Compare metrics across thresholds]
        TAB2[Compare versions and genome releases]
        TAB3[Specific genes analysis\nfilter plus recompute metrics]
        TAB4[Gene panel analysis\nselect panel plus compute or load panel metrics]
        OUT[Interactive plots plus tables plus CSV export\nwith support indicator]

        APP --> TAB1
        APP --> TAB2
        APP --> TAB3
        APP --> TAB4
        TAB1 --> OUT
        TAB2 --> OUT
        TAB3 --> OUT
        TAB4 --> OUT
    end

    subgraph USER_PROVIDED_INPUTS
        GL[User gene list\npaste or upload]
        GP[User panel choice\nfrom PanelApp derived list]
        UD[Custom prepared dataset path\n--data or env var]
    end

    DS --> APP
    GL --> TAB3
    GP --> TAB4
    UD -. replaces packaged data source .-> DS
```

## Suggested caption (manuscript)

Figure X. End-to-end workflow of the CADD Threshold App. ClinVar and CADD releases are combined in an offline preprocessing workflow that generates the precomputed tables used by the application. PanelApp snapshots are processed in parallel to generate panel-level summaries and metrics. At runtime, users explore precomputed analyses (global threshold and version/genome comparisons) and can run user-driven analyses via custom gene lists or selected PanelApp panels. Optionally, users can provide a custom prepared dataset directory, which replaces the packaged data source. All analysis paths converge in interactive visualizations, tables, exportable summaries, and the support indicator.
