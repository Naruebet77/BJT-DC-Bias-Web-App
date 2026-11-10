# Transistor Simulator — BJT DC Bias Web App

ENG29 2121 · Computer Programming for Electrical Engineers · Lab 02 (2/2569)

A Flask web application that computes the **DC operating point** of an NPN BJT
Common-Emitter amplifier using **Voltage-Divider Bias** under the Forward-Active
approximation (constant β and V_BE). All results are computed by the Python
backend — nothing is hard-coded in the HTML template.

## Scope

In scope: DC bias only (V_CC, R1, R2, R_C, R_E, β, V_BE → V_B, V_E, V_C, V_CE, I_C).
Out of scope: AC small-signal, Bode plot, transient analysis, signal generator,
interactive schematic editor, FET, SPICE.

## Layout

```
.
├── app.py                  # Flask routes, form parsing, display formatting
├── dc_bias.py              # engineering calculations (no Flask, no HTML)
├── templates/index.html    # input form + DC results (Jinja)
├── static/style.css        # presentation and responsive layout
├── tests/
│   ├── test_dc_bias.py     # engineering math, regions, validation
│   └── test_web.py         # Flask HTTP route tests
├── requirements.txt
├── AGENTS.md               # conventions for AI coding agents
└── docs/
    ├── design-note.md
    ├── validation.md
    └── reflection.md
```

## Setup and run

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Open <http://127.0.0.1:5000/> in a browser, enter the component values and press
**Calculate DC Bias**.

The app must be run through the local Flask server. Opening
`templates/index.html` directly with `file://` does not work, because the
calculation happens in the Python backend.

## Input

| Field | Unit | Notes |
|---|---|---|
| VCC | V | supply voltage, > 0 |
| R1, R2, RC, RE | Ω | enter ohms (`100000`), not `100k` |
| β | – | current gain, > 0 |
| VBE | V | base-emitter voltage (0.4–0.9 V is the usual range) |

Results are also echoed as `100000 Ω (100 kΩ)` so the unit conversion is visible.

## Engineering model

```
VTH = VCC·R2/(R1+R2)          RTH = R1·R2/(R1+R2)
IB  = (VTH − VBE)/(RTH + (β+1)·RE)
IC  = β·IB                    IE = (β+1)·IB
VE  = IE·RE                   VB = VE + VBE
VC  = VCC − IC·RC             VCE = VC − VE
```

Reference case — V_CC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, R_C = 2.2 kΩ,
R_E = 1 kΩ, β = 100, V_BE = 0.70 V:

| Quantity | Expected |
|---|---|
| I_B | 12.30 µA |
| I_C | 1.230 mA |
| I_E | 1.242 mA |
| V_E | 1.242 V |
| V_B | 1.942 V |
| V_C | 9.294 V |
| V_CE | 8.052 V |

## Operating region

The page always shows the region: **Active**, **Cutoff** or **Saturation**.

| Region | Condition | Behaviour |
|---|---|---|
| Active | VTH > VBE and VCE > 0.2 V | Forward-Active values are valid |
| Cutoff | VTH ≤ VBE | currents are clamped to zero; warning shown |
| Saturation | VCE ≤ 0.2 V | Forward-Active equations are reported unclamped (may be negative) with a warning |

Results outside the Forward-Active assumption must not be treated as a simulation.
This is not SPICE.

## Tests

```powershell
python -m unittest discover -s tests -v
```

17 tests: 9 engineering/validation tests and 8 Flask test-client tests.

## Development workflow

Design → plan → approved tasks → tests → review, then commit with **GitHub
Desktop**. AI agents do not commit or push; see `AGENTS.md`.

Design and plan documents: `docs/superpowers/`.
