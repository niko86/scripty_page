
import arrr
import matplotlib.pyplot as plt
from pyscript import document


def translate_english(event):
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = arrr.translate(english)
    plot_div = document.querySelector("#plot")
    plt.plot([1, 2, 3, 4])
    plot_div.innerHTML = plt.show()