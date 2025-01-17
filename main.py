import io
import warnings
warnings.simplefilter(action="ignore", category=DeprecationWarning)

import pandas as pl
import panel as pn
from panel.theme import Bootstrap
from python_ags4 import AGS4

pn.extension("tabulator", design=Bootstrap)

select_box = pn.widgets.Select(name="Select Table", options=[])
file_upload = pn.widgets.FileInput(accept=".ags", multiple=False)

def uploaded_ags(uploaded_data) -> dict:
    """Load AGS file and update the select widget."""
    if uploaded_data is not None:
        io_buffer = io.BytesIO(uploaded_data)
        tables, _ = AGS4.AGS4_to_dataframe(io_buffer)
        # Populate select_box with the table keys
        select_box.options = list(tables.keys())
        # Return the tables dict so it can be passed to other functions
        return tables
    return {}

def display_ags_data(tables: dict[str, pl.DataFrame], table_name):
    """Return a Tabulator widget for the chosen table."""
    if not tables or table_name not in tables:
        return pn.pane.Markdown("No table selected")
    df = AGS4.convert_to_numeric(tables[table_name].drop("HEADING", axis=1))
    tabulator = pn.widgets.Tabulator(df, show_index=False, pagination="remote", page_size=15)
    return tabulator

# Bind the file upload and selection to display the correct DataFrame
load_ags_bind = pn.bind(uploaded_ags, file_upload)
selection_bind = pn.bind(display_ags_data, load_ags_bind, select_box)

pn.Column(
    pn.Row(file_upload),
    pn.Row(select_box),
    pn.Row(selection_bind), 
    width_policy="max",
).servable(target="output")