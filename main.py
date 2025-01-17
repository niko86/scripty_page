import io
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import pandas as pd
import panel as pn

pn.extension()

def uploaded_ags(uploaded_data) -> None:
    if uploaded_data is not None:
        io_buffer = io.BytesIO(uploaded_data)
        df = pd.read_csv(io_buffer, skiprows=1, nrows=3)
        pn.Row(pn.pane.DataFrame(df, width=400)).servable(target="output")

file_upload = pn.widgets.FileInput(accept='.ags', multiple=False)
load_ags_bind = pn.bind(uploaded_ags, file_upload)

(
    pn.Row(
        file_upload,
        load_ags_bind,
    ).servable(target="url")
)
