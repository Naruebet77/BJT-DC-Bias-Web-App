# AGENTS.md — Working agreements for AI coding agents

## Project
BJT Common-Emitter **DC Bias** web app (ENG29 2121 Lab 02).
Flask + Python backend, multi-file layout, automated tests.

## Scope guard
In scope: DC operating point for **Voltage-Divider Bias** only.
Out of scope for this lab: AC small-signal, Bode plot, transient, signal generator,
interactive schematic editor, FET, and any SPICE integration.

If a request implies out-of-scope work, say so and propose the smallest in-scope step.

## File responsibilities
| File | Responsibility |
|---|---|
| `app.py` | Flask app, HTTP GET/POST routes, input parsing, error handling |
| `dc_bias.py` | Pure engineering calculations. Must not import Flask or know about HTML/HTTP |
| `templates/` | Jinja templates: form + results rendering. No physics equations here |
| `static/` | CSS and static assets |
| `tests/` | `test_dc_bias.py` (engineering math), `test_web.py` (Flask test client) |
| `docs/` | design-note, validation, reflection |

## Engineering model (Forward-Active, constant beta and VBE)
```
VTH = VCC * R2 / (R1 + R2)
RTH = R1 * R2 / (R1 + R2)
IB  = (VTH - VBE) / (RTH + (beta + 1) * RE)
IC  = beta * IB
IE  = (beta + 1) * IB
VE  = IE * RE
VB  = VE + VBE
VC  = VCC - IC * RC
VCE = VC - VE
```
Rules:
- Accept values in SI units (V, A); convert kΩ/mA at the boundary and state units.
- Report units in every displayed value (V, mA, µA).
- Never hard-code a result in the template; every displayed number must come from Python.
- Warn (do not silently report "valid") when `VTH <= VBE` (cutoff) or `VCE` is near/below
  saturation. State the model's limitations explicitly.

## Validation rules
Reject with a readable error, never a crash:
- missing or non-numeric input
- `R1, R2, RC, RE <= 0`
- `beta <= 0`
- `VCC <= 0`
- `VBE` outside 0.4–0.9 V (warn rather than reject)

## Testing
- At least 3 unit tests on the engineering math, including the reference case
  (VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, beta=100, VBE=0.70 V
  → VB≈1.942 V, VE≈1.242 V, VC≈9.294 V, VCE≈8.052 V, IC≈1.230 mA).
- At least 1 test through the Flask test client (GET form + POST calculation).
- Run `python -m unittest discover -s tests -v` and report the real output.

## Git rules
- NEVER run `git commit`, `git push`, `git add`, `git reset`, or `git checkout` of history.
- The human reviews and commits using **GitHub Desktop**.
- Leave finished work as uncommitted changes and list the changed files when a task is done.
- Keep one task = one reviewable change set.

## Verification
Do not claim a task is complete without showing the actual command output
(server start, test run, or HTTP response) that proves it.
