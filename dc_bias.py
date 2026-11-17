"""DC Bias calculations for an NPN BJT.

Voltage-Divider Bias (Lab 2), Fixed Bias and single-supply Emitter Bias (Lab 3).
Forward-Active approximation: constant beta and constant VBE.
Pure Python: this module must not import Flask or know about HTML/HTTP.
"""

import math
from dataclasses import dataclass

VCE_SAT = 0.2  # [V] collector-emitter saturation threshold used for region checks

VBE_MIN = 0.4
VBE_MAX = 0.9


@dataclass(frozen=True)
class DcBiasResult:
    ib: float    # [A]
    ic: float    # [A]
    ie: float    # [A]
    ve: float    # [V]
    vb: float    # [V]
    vc: float    # [V]
    vce: float   # [V]
    region: str  # "active" | "cutoff" | "saturation"
    warnings: tuple[str, ...]
    # Thevenin equivalent exists only for Voltage-Divider Bias.
    vth: float | None = None  # [V]
    rth: float | None = None  # [ohm]


def _require_positive(name: str, value: float, unit: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
    if value <= 0:
        raise ValueError(f"{name} ต้องมากกว่า 0 {unit}")


def compute_dc_bias(vcc: float, r1: float, r2: float, rc: float, re: float,
                    beta: float, vbe: float) -> DcBiasResult:
    """Compute the DC operating point of a voltage-divider biased BJT.

    All arguments are in SI units: volts, ohms (beta is dimensionless).
    Raises ValueError for inputs that make the model meaningless.
    """
    _require_positive("VCC", vcc, "โวลต์")
    _require_positive("R1", r1, "โอห์ม")
    _require_positive("R2", r2, "โอห์ม")
    _require_positive("RC", rc, "โอห์ม")
    _require_positive("RE", re, "โอห์ม")
    _require_positive("beta", beta, "")

    # Thevenin equivalent of the base divider
    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    ib = (vth - vbe) / (rth + (beta + 1.0) * re)
    ic = beta * ib
    ie = (beta + 1.0) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    warnings: list[str] = []

    if vth <= vbe:
        # Base-emitter junction is not forward biased: no collector current flows.
        ib = ic = ie = 0.0
        ve = 0.0
        vb = vth
        vc = vcc
        vce = vcc - vth
        region = "cutoff"
        warnings.append(
            "วงจรอยู่ในช่วง Cutoff (VTH ≤ VBE): แบบจำลอง Forward-Active ใช้ไม่ได้ "
            "กระแสทุกตัวจึงถูกปรับเป็นศูนย์"
        )
    elif vce <= VCE_SAT:
        region = "saturation"
        warnings.append(
            f"วงจรอยู่ในช่วง Saturation (VCE ≤ {VCE_SAT} V): แบบจำลอง Forward-Active "
            "ใช้ไม่ได้ ค่าที่แสดงคือผลจากสมการ Forward-Active โดยตรง (ไม่ได้ clamp)"
        )
    else:
        region = "active"

    if not (VBE_MIN <= vbe <= VBE_MAX):
        warnings.append(
            f"VBE = {vbe:g} V อยู่นอกช่วงปกติ {VBE_MIN}–{VBE_MAX} V "
            "ผลลัพธ์อาจไม่สมจริง"
        )

    return DcBiasResult(
        vth=vth,
        rth=rth,
        ib=ib,
        ic=ic,
        ie=ie,
        ve=ve,
        vb=vb,
        vc=vc,
        vce=vce,
        region=region,
        warnings=tuple(warnings),
    )


def _assemble_result(*, vcc: float, rc: float, beta: float, vbe: float,
                     ib: float, ve: float, base_ok: bool) -> DcBiasResult:
    """Shared tail for Fixed/Emitter: derive IC..VCE plus region and warnings.

    Unlike compute_dc_bias (Lab 2), Lab 3 does not clamp values in cutoff —
    it only warns when the Forward-Active model may not apply.
    """
    ic = beta * ib
    ie = (beta + 1.0) * ib
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    warnings: list[str] = []
    if not base_ok:
        region = "cutoff"
        warnings.append(
            "IB ≤ 0: แบบจำลอง Forward-Active อาจใช้ไม่ได้ "
            "(Lab 3 ไม่ได้หาค่าจริงในช่วง Cutoff ค่าที่แสดงเป็นผลจากสมการโดยตรง)"
        )
    elif vce <= VCE_SAT:
        region = "saturation"
        warnings.append(
            f"VCE ≤ {VCE_SAT} V: แบบจำลอง Forward-Active อาจใช้ไม่ได้ "
            "ค่าที่แสดงเป็นผลจากสมการโดยตรง (ไม่ได้ clamp)"
        )
    else:
        region = "active"

    if not (VBE_MIN <= vbe <= VBE_MAX):
        warnings.append(
            f"VBE = {vbe:g} V อยู่นอกช่วงปกติ {VBE_MIN}–{VBE_MAX} V "
            "ผลลัพธ์อาจไม่สมจริง"
        )

    return DcBiasResult(
        ib=ib, ic=ic, ie=ie, ve=ve, vb=vb, vc=vc, vce=vce,
        region=region, warnings=tuple(warnings),
    )


def compute_fixed_bias(vcc: float, rb: float, rc: float,
                       beta: float, vbe: float) -> DcBiasResult:
    """Fixed Bias: RB from VCC to base, emitter connected directly to ground.

    IB = (VCC - VBE) / RB ; VE = 0 V ; VB = VBE.
    All arguments are SI units (V, ohm); beta is dimensionless.
    """
    _require_positive("VCC", vcc, "โวลต์")
    _require_positive("RB", rb, "โอห์ม")
    _require_positive("RC", rc, "โอห์ม")
    _require_positive("beta", beta, "")

    ib = (vcc - vbe) / rb
    return _assemble_result(vcc=vcc, rc=rc, beta=beta, vbe=vbe,
                            ib=ib, ve=0.0, base_ok=ib > 0.0)


def compute_emitter_bias(vcc: float, rb: float, rc: float, re: float,
                         beta: float, vbe: float) -> DcBiasResult:
    """Emitter Bias (single supply): RB from VCC to base, RE from emitter to ground.

    IB = (VCC - VBE) / [RB + (beta + 1) * RE] ; VE = IE * RE.
    All arguments are SI units (V, ohm); beta is dimensionless.
    """
    _require_positive("VCC", vcc, "โวลต์")
    _require_positive("RB", rb, "โอห์ม")
    _require_positive("RC", rc, "โอห์ม")
    _require_positive("RE", re, "โอห์ม")
    _require_positive("beta", beta, "")

    ib = (vcc - vbe) / (rb + (beta + 1.0) * re)
    return _assemble_result(vcc=vcc, rc=rc, beta=beta, vbe=vbe,
                            ib=ib, ve=(beta + 1.0) * ib * re,
                            base_ok=ib > 0.0)
