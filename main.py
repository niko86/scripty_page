import io

from pyodide.http import open_url
from pyscript import document

url = r"https://gitlab.com/ags-data-format-wg/ags-python-library/-/raw/main/notebooks/East%20West%20Rail%20BGS%20Pre%20October%202018%20upload%20(partial).ags"
# url = r"East West Rail BGS Pre October 2018 upload (partial).ags"


# Fetch the content from the URL
response = open_url(url)

# Read the content into a buffer
buffer = io.StringIO(response.read())

ags_output = document.querySelector("#output")
ags_output.innerHTML = buffer.readlines()
# "https://github.com/pola-rs/polars/"
# https://raw.githubusercontent.com/pola-rs/polars/releases/download/py-1.20.0/polars-1.20.0-cp39-abi3-emscripten_3_1_58_wasm32.whl