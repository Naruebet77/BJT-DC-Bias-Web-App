"""DC Bias calculations for an NPN BJT in Voltage-Divider Bias.

Forward-Active approximation: constant beta and constant VBE.
Pure Python: this module must not import Flask or know about HTML/HTTP.
"""

from dataclasses import dataclass

VCE_SAT = 0.2  # [V] collector-emitter saturation threshold used for region checks

VBE_MIN = 0.4
VBE_MAX = 0.9


@dataclass(frozen=True)
class DcBiasResult:
    vth: float   # [V]  Thevenin base voltage
    rth: float   # [ohm] Thevenin base resistance
    ib: float    # [A]
    ic: float    # [A]
    ie: float    # [A]
    ve: float    # [V]
    vb: float    # [V]
    vc: float    # [V]
    vce: float   # [V]
    region: str  # "active" | "cutoff" | "saturation"
    warnings: tuple[str, ...]


def _require_positive(name: str, value: float, unit: str) -> None:
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
