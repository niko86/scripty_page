import io

import polars as pl
from pyodide.http import open_url
from pyodide.ffi import JsProxy
from pyscript import document

url = r"https://raw.githubusercontent.com/niko86/scripty_page/refs/heads/master/East%20West%20Rail%20BGS%20Pre%20October%202018%20upload%20(partial).ags"
#url = r"https://gitlab.com/ags-data-format-wg/ags-python-library/-/raw/main/notebooks/East%20West%20Rail%20BGS%20Pre%20October%202018%20upload%20(partial).ags"
url_output = document.querySelector("#url")
url_output.innerHTML = f"Ready to load AGS from: \n{url}"

def load_ags(event: JsProxy) -> None:
    # Fetch the content from the URL
    response = open_url(url)
    # Read the content into a buffer
    buffer = io.StringIO(response.read())

    ags_output = document.querySelector("#output")
    # Print the first line of the buffer
    url_output.innerHTML = f"File loaded"
    ags_output.innerHTML = buffer.readlines()
    
