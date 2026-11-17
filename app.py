"""Flask application for the BJT DC Bias calculator.

This module only parses HTTP input and renders templates; the engineering
math lives in dc_bias.py.
"""

from flask import Flask, render_template, request

from dc_bias import compute_dc_bias, compute_emitter_bias, compute_fixed_bias

app = Flask(__name__)

MODE_FIELDS = {
    "divider": ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"),
    "fixed": ("vcc", "rb", "rc", "beta", "vbe"),
    "emitter": ("vcc", "rb", "rc", "re", "beta", "vbe"),
}
MODES = tuple(MODE_FIELDS)
MODE_LABELS = {
    "divider": "Voltage Divider Bias",
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
}

FIELDS = MODE_FIELDS["divider"]  # kept for compatibility with Lab 2 callers
RESISTORS = ("r1", "r2", "rb", "rc", "re")

DEFAULTS = {
    "vcc": "12",
    "r1": "100000",
    "r2": "22000",
    "rb": "1000000",
    "rc": "2200",
    "re": "1000",
    "beta": "100",
    "vbe": "0.70",
}


def parse_form(form, fields=FIELDS) -> tuple[dict[str, float], list[str]]:
    """Convert only this mode's raw form strings into floats.

    Values arrive in the form's units (V, ohm) and are already SI at this
    boundary, so no scaling is needed before the engineering functions.
    """
    values: dict[str, float] = {}
    errors: list[str] = []
    for name in fields:
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
        "vth": f"{result.vth:.3f} V" if result.vth is not None else "—",
        "rth": f"{result.rth / 1e3:.3f} kΩ" if result.rth is not None else "—",
    }


def format_inputs(values: dict[str, float], fields=FIELDS) -> dict[str, str]:
    """Echo only this mode's inputs, showing the ohm/kilohm equivalence."""
    summary = {"vcc": f"{values['vcc']:g} V", "beta": f"{values['beta']:g}",
               "vbe": f"{values['vbe']:g} V"}
    for name in RESISTORS:
        if name in fields:
            ohms = values[name]
            summary[name] = f"{ohms:.0f} Ω ({ohms / 1e3:g} kΩ)"
    return summary


def _render(mode, inputs, errors, view=None, result=None, input_summary=None):
    """Render with a consistent context so a failed round never shows old results."""
    fields = MODE_FIELDS.get(mode, ())
    return render_template(
        "index.html",
        mode=mode,
        mode_label=MODE_LABELS.get(mode, mode),
        active_fields=fields,
        inputs=inputs,
        errors=errors,
        view=view,
        result=result,
        input_summary=input_summary,
    )


@app.get("/")
def index():
    mode = request.args.get("mode", "divider")
    if mode not in MODES:
        return _render(mode, {}, [f"ไม่รู้จักโหมด '{mode}' — เลือก Divider, Fixed หรือ Emitter"]), 400
    return _render(mode, DEFAULTS, [])


@app.post("/calculate")
def calculate():
    # A Lab 2 form has no "mode" field at all: keep that client working as
    # Divider. An explicitly supplied but unrecognised mode is an error.
    mode = "divider" if "mode" not in request.form else request.form.get("mode", "")
    if mode not in MODES:
        return _render(mode, {}, [f"ไม่รู้จักโหมด '{mode}' — เลือก Divider, Fixed หรือ Emitter"]), 400

    fields = MODE_FIELDS[mode]
    raw = {name: (request.form.get(name) or "") for name in fields}
    parsed, errors = parse_form(request.form, fields)

    if not errors:
        try:
            # Explicit dispatch: an unknown mode is rejected above, never
            # silently treated as the divider circuit.
            if mode == "fixed":
                result = compute_fixed_bias(
                    vcc=parsed["vcc"], rb=parsed["rb"], rc=parsed["rc"],
                    beta=parsed["beta"], vbe=parsed["vbe"],
                )
            elif mode == "emitter":
                result = compute_emitter_bias(
                    vcc=parsed["vcc"], rb=parsed["rb"], rc=parsed["rc"],
                    re=parsed["re"], beta=parsed["beta"], vbe=parsed["vbe"],
                )
            else:  # divider — same call and same results as Lab 2
                result = compute_dc_bias(**parsed)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            return _render(mode, raw, [], view=format_result(result),
                           result=result, input_summary=format_inputs(parsed, fields))

    return _render(mode, raw, errors), 400
