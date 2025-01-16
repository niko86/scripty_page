import io
import base64

import arrr
import matplotlib.pyplot as plt
from pyscript import document


def translate_english(event):
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = arrr.translate(english)
    
    # Create the plot
    plt.plot([1, 2, 3, 4])
    
    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert the buffer to a base64 string
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    # Set the src attribute of the img element
    plot_div = document.querySelector("#plot")
    plot_div.innerHTML = f'<img src="data:image/png;base64,{img_base64}" />'