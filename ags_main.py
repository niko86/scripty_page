import io
import warnings

warnings.simplefilter(action="ignore", category=DeprecationWarning)

import pandas as pd
import panel as pn
from panel.theme import Bootstrap
from python_ags4 import AGS4
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import Legend, HoverTool, ColumnDataSource
from bokeh.palettes import Category20, Category10, Category20b, Category20c

pn.extension("tabulator")  # , design=Bootstrap)

select_box = pn.widgets.Select(name="Select Table", options=[])
file_upload = pn.widgets.FileInput(accept=".ags", multiple=False)
x_select = pn.widgets.Select(name="X-Axis", options=[])
y_select = pn.widgets.Select(name="Y-Axis", options=[])
group_select = pn.widgets.Select(name="Group By", options=[], disabled=True)
marker_size_slider = pn.widgets.IntSlider(name="Marker Size", start=1, end=20, value=5)


def get_selected_table(
    tables: dict[str, pd.DataFrame], table_name: str
) -> pd.DataFrame | None:
    """Retrieve and convert the selected table to a numeric DataFrame."""
    if not tables or table_name not in tables:
        return None
    return tables[table_name]


def uploaded_ags(uploaded_data) -> dict:
    """Load AGS file and update the table-select widget."""
    if uploaded_data:
        io_buffer = io.BytesIO(uploaded_data)
        tables, _ = AGS4.AGS4_to_dataframe(io_buffer)
        select_box.options = list(tables.keys())
        tables = {
            key: AGS4.convert_to_numeric(value.drop("HEADING", axis=1))
            for key, value in tables.items()
        }
        return tables
    return {}


def display_ags_data(tables: dict[str, pd.DataFrame], table_name: str):
    """Show the selected table as a Tabulator widget."""
    df = get_selected_table(tables, table_name)
    if df is None:
        return pn.pane.Markdown("No table selected")

    tabulator = pn.widgets.Tabulator(
        df, show_index=False, pagination="local", page_size=10, width_policy="max"
    )

    # Populate numeric column selectors
    numeric_cols = df.select_dtypes(include=["number"]).columns.to_list()
    x_select.options = numeric_cols
    y_select.options = numeric_cols

    # Populate string column selectors for grouping
    string_cols = df.select_dtypes(include=["object", "category"]).columns.to_list()
    if string_cols:
        group_select.options = [None] + string_cols
        group_select.disabled = False
        group_select.value = None  # Set default to None
    else:
        group_select.options = [None]
        group_select.disabled = True
        group_select.value = None

    return tabulator


def show_plot(
    tables: dict[str, pd.DataFrame],
    table_name: str,
    x_col: str,
    y_col: str,
    group_col: str,
    marker_size: int,
):
    """Generate a Bokeh plot of the chosen numeric columns."""
    df = get_selected_table(tables, table_name)
    if df is None:
        return pn.pane.Markdown("Select a table first.")
    if x_col not in df.columns or y_col not in df.columns:
        return pn.pane.Markdown("Select valid numeric columns for X and Y.")

    p = figure(
        title=f"{table_name}: {x_col} vs {y_col}",
        x_axis_label=x_col,
        y_axis_label=y_col,
    )

    if group_col and group_col in df.columns:
        groups = df[group_col].unique().tolist()
        # Combine multiple palettes to handle more groups
        palette = Category20[20] + Category10[10] + Category20b[20] + Category20c[20]

        renderers = []
        for i, group in enumerate(groups):
            group_df = df[df[group_col] == group].copy()
            group_df["group"] = group  # Add 'group' column

            source = ColumnDataSource(
                data=dict(x=group_df[x_col], y=group_df[y_col], group=group_df["group"])
            )

            renderer = p.scatter(
                "x",
                "y",
                source=source,
                size=marker_size,
                alpha=0.7,
                color=palette[i % len(palette)],
                name=str(group),
            )
            renderers.append((str(group), [renderer]))

        # Configure HoverTool
        # colors = brewer['YlGnBu'][len(categories)]
        hover = HoverTool(tooltips=[("X", "@x"), ("Y", "@y"), ("Group", "@group")])
        p.add_tools(hover)

        # Configure Legend
        legend = Legend(items=renderers, location="center", orientation="vertical")
        p.add_layout(legend, "right")
        p.legend.click_policy = "mute"

    else:
        source = ColumnDataSource(data=dict(x=df[x_col], y=df[y_col]))
        p.scatter("x", "y", source=source, size=marker_size, alpha=0.7)
        # Configure HoverTool without 'Group'
        hover = HoverTool(tooltips=[("X", "@x"), ("Y", "@y")])
        p.add_tools(hover)

    return pn.pane.Bokeh(
        column(
            p,
            min_height=500,
            width_policy="max",
            height_policy="max",
            sizing_mode="stretch_both",
        )
    )


load_ags_bind = pn.bind(uploaded_ags, file_upload)
table_bind = pn.bind(display_ags_data, load_ags_bind, select_box)
plot_bind = pn.bind(
    show_plot,
    load_ags_bind,
    select_box,
    x_select,
    y_select,
    group_select,
    marker_size_slider,
)

widgets = pn.WidgetBox(
    file_upload, select_box, x_select, y_select, group_select, marker_size_slider
)

# Layout
# pn.FlexBox(
#     pn.Row(widgets, plot_bind, width_policy="max"),
#     pn.Card(table_bind, title="Group Viewer", width_policy="max"),
# ).servable(target="app")

pn.template.BootstrapTemplate(
    title="AGS Viewer", main=[widgets, plot_bind, table_bind]
).servable(target="app")
