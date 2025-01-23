import micropip

await micropip.install(
    "https://cdn.holoviz.org/panel/1.5.5/dist/wheels/bokeh-3.6.2-py3-none-any.whl"
)
await micropip.install(
    "https://cdn.holoviz.org/panel/1.5.5/dist/wheels/panel-1.5.5-py3-none-any.whl"
)

import io
import warnings

warnings.simplefilter(action="ignore", category=DeprecationWarning)
from pyscript import document
import pandas as pd
import panel as pn
from panel.theme import Bootstrap
from python_ags4 import AGS4
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import Legend, HoverTool, ColumnDataSource
from bokeh.palettes import Category20, Category10, Category20b, Category20c

pn.extension("tabulator")
pn.extension("perspective", design=Bootstrap)

table_selector = pn.widgets.Select(name="Select Table", options=[])
file_upload = pn.widgets.FileInput(accept=".ags", multiple=False)
x_axis_selector = pn.widgets.Select(name="X-Axis", options=[])
y_axis_selector = pn.widgets.Select(name="Y-Axis", options=[])
group_by_selector = pn.widgets.Select(name="Group By", options=[], disabled=True)
marker_size_slider = pn.widgets.IntSlider(name="Marker Size", start=1, end=20, value=5)


def update_html(id: str, content: str):
    document.querySelector(f"#{id}").innerHTML = content


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
        table_selector.options = list(tables.keys())
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
    x_axis_selector.options = numeric_cols
    y_axis_selector.options = numeric_cols

    # Populate string column selectors for grouping
    string_cols = df.select_dtypes(include=["object", "category"]).columns.to_list()
    if string_cols:
        group_by_selector.options = [None] + string_cols
        group_by_selector.disabled = False
        group_by_selector.value = None  # Set default to None
    else:
        group_by_selector.options = [None]
        group_by_selector.disabled = True
        group_by_selector.value = None

    return pn.pane.Perspective(df, columns=list(df.columns), height_policy="max", width_policy="max", sizing_mode="stretch_both")


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
table_bind = pn.bind(display_ags_data, load_ags_bind, table_selector)
plot_bind = pn.bind(
    show_plot,
    load_ags_bind,
    table_selector,
    x_axis_selector,
    y_axis_selector,
    group_by_selector,
    marker_size_slider,
)

widgets = pn.WidgetBox(
    file_upload,
    table_selector,
    x_axis_selector,
    y_axis_selector,
    group_by_selector,
    marker_size_slider,
)

template = pn.FlexBox(
    pn.Row(widgets, table_bind, height_policy="max", width_policy="max", sizing_mode="stretch_both"), #plot_bind
    #pn.Card(table_bind, title="Group Viewer", width_policy="max"),
    height_policy="max", width_policy="max", sizing_mode="stretch_both"
)

template.servable(target="container")
update_html("container", "")