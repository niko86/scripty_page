import polars as pl
from python_ags4 import AGS4
from pyodide.http import open_url
from pyscript import document, display

url = r"https://gitlab.com/ags-data-format-wg/ags-python-library/-/raw/main/notebooks/East%20West%20Rail%20BGS%20Pre%20October%202018%20upload%20(partial).ags"
# url = r"East West Rail BGS Pre October 2018 upload (partial).ags"

ags_output = document.querySelector("#output")

tables, headings = AGS4.AGS4_to_dataframe(open_url(url))
ags_output.innerHTML = str(tables["PROJ"].head())
