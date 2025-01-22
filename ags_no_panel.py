import json
import polars as pl

from js import Bokeh, JSON

from bokeh.embed import json_item
from bokeh.plotting import figure
from pyscript import display, document

from models import AgsMap


async def index_ags_file(filename: str, encoding: str) -> dict[str, AgsMap]:
    groups: dict[str, AgsMap] = dict()
    current_group: str = None

    # First Pass: Record byte positions
    with open(filename, "rb") as file:
        line_start_bytes = 0
        for line_counter, line in enumerate(file, start=1):
            if line == b"\r\n":  # Skip empty lines
                continue
            if line.startswith(b'"GROUP"'):
                current_group = line[9:13].decode(
                    encoding
                )  # TODO should i extract group name in a different way?
                groups[current_group] = AgsMap(
                    group_row=line_start_bytes, group_row_num=line_counter
                )
            elif line.startswith(b'"HEADING"'):
                groups[current_group].heading_row = line_start_bytes
                groups[current_group].heading_row_num = line_counter
                groups[current_group].data_row_start = line_start_bytes
            elif line.startswith(b'"TYPE"'):
                groups[current_group].type_row = line_start_bytes
                groups[current_group].type_row_num = line_counter
            elif line.startswith(b'"UNIT"'):
                groups[current_group].unit_row = line_start_bytes
                groups[current_group].unit_row_num = line_counter
            elif line.startswith(b'"DATA"'):
                groups[current_group].data_row_end = file.tell()
                groups[current_group].data_row_end_num = line_counter
                if groups[current_group].data_row_start is None:
                    groups[current_group].data_row_start = line_start_bytes
                    groups[current_group].data_row_start_num = line_counter

            line_start_bytes = file.tell()

    return groups


from pyscript.web import page, div, input_

output_div = document.querySelector("#output")
output_div.innerHTML = ""
page.append(input_(type="file", id="ags_file", name="ags_file", accept=".ags"))
document.querySelector("#ags_file")

# df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
# plot = figure()
# plot.scatter(df["a"], df["b"])
# p_json = json.dumps(json_item(plot, "output"))
# Bokeh.embed.embed_item(JSON.parse(p_json))
# display(df)
