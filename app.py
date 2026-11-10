"""Flask application for the BJT DC Bias calculator.

This module only parses HTTP input and renders templates; the engineering
math lives in dc_bias.py.
"""

from flask import Flask, render_template, request

from dc_bias import compute_dc_bias

app = Flask(__name__)

FIELDS = ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")
RESISTORS = ("r1", "r2", "rc", "re")

DEFAULTS = {
    "vcc": "12",
    "r1": "100000",
    "r2": "22000",
    "rc": "2200",
    "re": "1000",
    "beta": "100",
    "vbe": "0.70",
}


def parse_form(form) -> tuple[dict[str, float], list[str]]:
    """Convert the raw form strings into floats, collecting readable errors."""
    values: dict[str, float] = {}
    errors: list[str] = []
    for name in FIELDS:
        raw = (form.get(name) or "").strip()
        if not raw:
            errors.append(f"{name.upper()} ต้องเป็นตัวเลข")
            continue
        try:
            values[name] = float(raw)
        except ValueError:
            errors.append(f"{name.upper()} ต้องเป็นตัวเลข")
    return values, errors


def format_result(result) -> dict[str, str]:
    """Format the engineering result with units for display."""
    return {
        "vb": f"{result.vb:.3f} V",
        "ve": f"{result.ve:.3f} V",
        "vc": f"{result.vc:.3f} V",
        "vce": f"{result.vce:.3f} V",
        "ic": f"{result.ic * 1e3:.3f} mA",
        "ib": f"{result.ib * 1e6:.2f} µA",
        "ie": f"{result.ie * 1e3:.3f} mA",
        "vth": f"{result.vth:.3f} V",
        "rth": f"{result.rth / 1e3:.3f} kΩ",
    }


def format_inputs(values: dict[str, float]) -> dict[str, str]:
    """Echo the entered values, showing the ohm/kilohm equivalence."""
    summary = {"vcc": f"{values['vcc']:g} V", "beta": f"{values['beta']:g}",
               "vbe": f"{values['vbe']:g} V"}
    for name in RESISTORS:
        ohms = values[name]
        summary[name] = f"{ohms:.0f} Ω ({ohms / 1e3:g} kΩ)"
    return summary


@app.get("/")
def index():
    return render_template("index.html", inputs=DEFAULTS, errors=[], view=None,
                           result=None, input_summary=None)


@app.post("/calculate")
def calculate():
    raw = {name: (request.form.get(name) or "") for name in FIELDS}
    parsed, errors = parse_form(request.form)

    if not errors:
        try:
            result = compute_dc_bias(**parsed)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            return render_template(
                "index.html",
                inputs=raw,
                errors=[],
                view=format_result(result),
                result=result,
                input_summary=format_inputs(parsed),
            )

    return render_template("index.html", inputs=raw, errors=errors, view=None,
                           result=None, input_summary=None), 400
