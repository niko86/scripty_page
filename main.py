import arrr
import matplotlib.pyplot as plt
from pyscript import document, display


def translate_english(event):
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = arrr.translate(english)
    
    # Create the plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4])
    display(fig, target="plot")
