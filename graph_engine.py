import numpy as np
import plotly.graph_objects as go
import re
from pathlib import Path

OUTPUT_DIR = Path("generated_slides")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_graph_from_spec(graph_spec, slide_index):

    graph_type = graph_spec.get("type")

    if graph_type == "function_plot":
        return generate_function_plot(graph_spec, slide_index)

    raise ValueError("Unsupported graph type")


def generate_function_plot(spec, slide_index):

    equation = spec["equation"]
    x_min, x_max = spec["x_range"]

    # Extract RHS of equation
    match = re.match(r"y\s*=\s*(.*)", equation)
    if not match:
        raise ValueError("Equation must be of form y = ...")

    expression = match.group(1)

    x = np.linspace(x_min, x_max, 400)

    allowed_names = {
        "x": x,
        "np": np,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
    }

    y = eval(expression, {"__builtins__": {}}, allowed_names)

    fig = go.Figure()
    fig.add_scatter(x=x, y=y, mode="lines")

    fig.update_layout(
        template="plotly_dark",
        width=500,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    output_path = OUTPUT_DIR / f"graph_{slide_index}.png"
    fig.write_image(str(output_path))

    return str(output_path)
