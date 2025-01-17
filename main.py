import io
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import pandas as pl
import panel as pn
from panel.theme import Bootstrap
from python_ags4 import AGS4
from bokeh.plotting import figure

pn.extension("tabulator", design=Bootstrap)

select_box = pn.widgets.Select(name="Select Table", options=[])
file_upload = pn.widgets.FileInput(accept=".ags", multiple=False)
x_select = pn.widgets.Select(name="X-Axis", options=[])
y_select = pn.widgets.Select(name="Y-Axis", options=[])

def get_selected_table(tables: dict[str, pl.DataFrame], table_name: str) -> pl.DataFrame | None:
    """Retrieve and convert the selected table to a numeric DataFrame."""
    if not tables or table_name not in tables:
        return None
    return AGS4.convert_to_numeric(tables[table_name].drop("HEADING", axis=1))

def uploaded_ags(uploaded_data) -> dict:
    """Load AGS file and update the table-select widget."""
    if uploaded_data:
        io_buffer = io.BytesIO(uploaded_data)
        tables, _ = AGS4.AGS4_to_dataframe(io_buffer)
        select_box.options = list(tables.keys())
        return tables
    return {}

def display_ags_data(tables: dict[str, pl.DataFrame], table_name: str):
    """Show the selected table as a Tabulator widget."""
    df = get_selected_table(tables, table_name)
    if df is None:
        return pn.pane.Markdown("No table selected")

    tabulator = pn.widgets.Tabulator(
        df,
        show_index=False,
        pagination="remote",
        page_size=15,
    )
    numeric_cols = df.select_dtypes(include="number").columns.to_list()
    x_select.options = numeric_cols
    y_select.options = numeric_cols
    return tabulator

def show_plot(tables: dict[str, pl.DataFrame], table_name: str, x_col: str, y_col: str):
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
        height=300
    )
    p.scatter(df[x_col].to_list(), df[y_col].to_list(), size=5, alpha=0.7)
    return pn.pane.Bokeh(p)

load_ags_bind = pn.bind(uploaded_ags, file_upload)
selection_bind = pn.bind(display_ags_data, load_ags_bind, select_box)
plot_bind = pn.bind(show_plot, load_ags_bind, select_box, x_select, y_select)

pn.Column(
    pn.Row(file_upload),
    pn.Row(select_box),
    pn.Row(selection_bind),
    pn.Row(x_select, y_select),
    pn.Row(plot_bind),
    width_policy="max"
).servable(target="output")