import panel as pn
import pandas as pd

pn.extension("perspective", design="bootstrap")

pn.template.BootstrapTemplate(
    title="Test App",
    sidebar=[pn.pane.Markdown("Hello World!")],
    main=[pn.pane.Perspective(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}), height_policy="max", width_policy="max", sizing_mode="stretch_width")],
).servable()
