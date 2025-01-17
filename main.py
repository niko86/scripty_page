import io
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)

import panel as pn
from python_ags4 import AGS4

pn.extension('tabulator')

def uploaded_ags(uploaded_data) -> None:
    if uploaded_data is not None:
        io_buffer = io.BytesIO(uploaded_data)
        tables, _ = AGS4.AGS4_to_dataframe(io_buffer)
        df = AGS4.convert_to_numeric(tables['SAMP'])
        table = pn.widgets.Tabulator(df)
        
        filename, button = table.download_menu(
            text_kwargs={'name': 'Enter filename', 'value': 'default.csv'},
            button_kwargs={'name': 'Download table'}
        )
        
        pn.Row(pn.Column(filename, button),table).servable(target="output")

file_upload = pn.widgets.FileInput(accept='.ags', multiple=False)
#select_box = pn.widgets.Select(name='Select')
load_ags_bind = pn.bind(uploaded_ags, file_upload)
# selection_bind = pn.bind(display_ags_data, load_ags_bind, select_box)

(
    pn.Row(
        file_upload,
        #select_box,
        load_ags_bind,
    ).servable(target="url")
)
