# Transistor Simulator — BJT DC Bias Web App

ENG29 2121 · Computer Programming for Electrical Engineers · Lab 02 + Lab 03 (2/2569)

A Flask web application that computes the **DC operating point** of an NPN BJT
Common-Emitter amplifier under the Forward-Active approximation (constant β and
V_BE). Three circuits can be selected from the form: **Voltage-Divider Bias**
(Lab 2, unchanged), **Fixed Bias** and single-supply **Emitter Bias** (Lab 3).
All results are computed by the Python backend — nothing is hard-coded in the
HTML template.

**Status:** Lab 03 implemented (ready for review and commit via GitHub Desktop).

## Scope

In scope: DC operating point only. Per circuit the backend takes V_CC, R_C, β,
V_BE plus the circuit-specific resistors (R1/R2/R_E for Divider, R_B for Fixed,
R_B/R_E for Emitter) and returns V_B, V_E, V_C, V_CE, I_C, I_B, I_E.

Out of scope: AC small-signal, Bode plot, transient analysis, signal generator,
interactive schematic editor, FET, SPICE, DC load line and bypass capacitors.
Lab 3 does not add new unit tests; verification is done in a real browser.

Selecting a circuit uses a plain GET reload of the form (no JavaScript). An
unknown mode is rejected with an error and is never guessed as Divider.

## Layout

```
.
├── app.py                  # Flask routes, form parsing, display formatting
├── dc_bias.py              # compute_dc_bias / compute_fixed_bias / compute_emitter_bias
                            #   (pure engineering math: no Flask, no HTML)
├── templates/index.html    # input form + DC results (Jinja)
├── static/style.css        # presentation and responsive layout
├── tests/
│   ├── test_dc_bias.py     # engineering math, regions, validation
│   └── test_web.py         # Flask HTTP route tests
├── requirements.txt        # Flask 3.1.3
├── AGENTS.md               # conventions for AI coding agents
├── .gitignore
├── README.md
└── docs/
    ├── design-note.md
    ├── validation.md       # test evidence + acceptance criteria A1–A7
    └── reflection.md
    └── superpowers/
        ├── specs/          # approved design doc
        └── plans/          # implementation plan (5 tasks)
```

## Setup and run (Windows PowerShell)

```powershell
# create virtual environment (run once)
.venv\Scripts\python.exe -m venv .venv

# install dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt

# run the Flask development server
.venv\Scripts\python.exe -m flask --app app run --debug
```

Then open **http://127.0.0.1:5000/** in a browser.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

The app must be run through the local Flask server. Opening
`templates/index.html` directly with `file://` does not work, because the
calculation happens in the Python backend.

## Input

| Field | Unit | Used by | Notes |
|---|---|---|---|
| VCC | V | all | supply voltage, > 0 |
| R1, R2 | Ω | Divider | base divider resistors |
| RB | Ω | Fixed, Emitter | VCC → base resistor |
| RC | Ω | all | collector resistor |
| RE | Ω | Divider, Emitter | emitter resistor (Fixed has VE = 0 V) |
| β | – | all | current gain, > 0 |
| VBE | V | all | base-emitter voltage (0.4–0.9 V is the usual range) |

Enter ohms (`1000000`), not `1M` or `100k`. Values arrive in SI units already
(V, Ω) and are converted to kΩ only for the echoed summary. Missing,
non-numeric, non-finite or non-positive required values produce a readable
error instead of a crash. Results are echoed as `1000000 Ω (1000 kΩ)` so the
unit conversion is visible.

## Engineering model

```
Shared                        IC = β·IB        IE = (β+1)·IB
                              VB = VE + VBE    VC = VCC − IC·RC
                              VCE = VC − VE

Fixed      IB = (VCC − VBE)/RB                  VE = 0 V
Emitter    IB = (VCC − VBE)/(RB + (β+1)·RE)     VE = IE·RE
Divider    IB = (VTH − VBE)/(RTH + (β+1)·RE)    VE = IE·RE
           VTH = VCC·R2/(R1+R2)  RTH = R1·R2/(R1+R2)
```

`compute_dc_bias` (Divider) keeps the Lab 2 equations and cutoff clamping
unchanged, so the reference case below and all 17 original tests still hold.

Reference case (Divider) — V_CC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, R_C = 2.2 kΩ,
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
| Active | base forward-biased and VCE > 0.2 V | Forward-Active values are valid |
| Cutoff | Divider: VTH ≤ VBE · Fixed/Emitter: IB ≤ 0 | Divider clamps currents to zero; Lab 3 circuits only warn and report the raw equation values |
| Saturation | VCE ≤ 0.2 V | Forward-Active equations are reported unclamped (may be negative) with a warning |

VBE outside 0.4–0.9 V always adds a warning but does not reject the input.
None of the displayed values comes from a SPICE simulation.

Results outside the Forward-Active assumption must not be treated as a simulation.
This is not SPICE.

## Tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

17 tests: 9 engineering/validation tests and 8 Flask test-client tests.
Full evidence and acceptance criteria: `docs/validation.md`

## Development workflow

Design → plan → approved tasks → tests → review, then commit with **GitHub
Desktop**. AI agents do not commit or push; see `AGENTS.md`.

Design and plan documents: `docs/superpowers/`.
