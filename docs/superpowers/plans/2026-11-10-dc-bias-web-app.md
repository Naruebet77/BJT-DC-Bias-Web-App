# BJT DC Bias Web App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flask web app หลายไฟล์ที่รับ `VCC, R1, R2, RC, RE, β, VBE` แล้วคำนวณ DC operating point ของ BJT Voltage-Divider Bias ด้วย Python backend พร้อม validation, region warning และ automated tests

**Architecture:** แยกสมการวิศวกรรมไว้ใน `dc_bias.py` (pure Python, ไม่รู้จัก Flask) ส่วน `app.py` ทำหน้าที่ parse/validate/Render เท่านั้น เทมเพลต Jinja แสดงผลโดยไม่มีสมการฟิสิกส์

**Tech Stack:** Python 3.14.2 · Flask 3.1.3 · Jinja2 · `unittest` (standard library) · HTML/CSS ไม่มี JavaScript

**Spec:** `docs/superpowers/specs/2026-11-10-dc-bias-web-app-design.md`

## Global Constraints

- รันทุกคำสั่งด้วย `.venv\Scripts\python.exe` (Windows) — เช่น `.venv\Scripts\python.exe -m unittest discover -s tests -v`
- ใช้ `unittest` เท่านั้น ห้ามเพิ่ม pytest / numpy / ไลบรารี외부อื่น
- อินพุตตัวต้านทานเป็น **Ω** (`100000`) ไม่รับ suffix `100k`; แสดงผลเทียบเป็น kΩ ด้วย
- หน่วยภายใน `dc_bias.py` เป็น SI (V, A, Ω) — การแปลงเป็น mA/µA เกิดที่ชั้นแสดงผลใน `app.py`
- UI ภาษาไทย + ชื่อปริมาณอังกฤษ (`VCC`, `VB`, `VCE`, `β`, `DC Bias`); `region` เป็น `active` / `cutoff` / `saturation`
- แสดงหลัก 3 ตำแหน่งสำหรับ V และ mA, 2 ตำแหน่งสำหรับ µA, 3 ตำแหน่งสำหรับ kΩ
- ห้ามฮาร์ดโค้ดผลลัพธ์ใน `templates/index.html`; ตัวเลขทุกตัวมาจาก Python
- `dc_bias.py` ห้าม import Flask; `app.py` ห้ามมีสมการฟิสิกส์
- **AI ห้ามรัน `git add` / `git commit` / `git push`** — เจ้าของโปรเจกต์ commit ผ่าน GitHub Desktop (ดู `AGENTS.md`)
- Flask debug server ใช้เฉพาะเครื่องตัวเองที่ `http://127.0.0.1:5000/`

## Review Focus

ปัจจัยที่ spec ไม่ได้เขียนไว้แต่มีโอกาสทำให้ผู้ใช้เจอปัญหา — แต่ละข้อมีเทสต์ผูกไว้ใน task ที่รับผิดชอบ

1. **ตัวต้านทานเป็น 0 หรือติดลบ** → ต้องได้ข้อความ error ที่อ่านรู้เรื่อง ไม่ใช่ `ZeroDivisionError` หรือหน้า 500 (Task 1)
2. **กรอกค่าไม่ใช่ตัวเลข / ช่องว่าง / มี comma เช่น `1,000` / ใส่ `100k`** → ต้องแจ้ง error ภาษาไทยและคงค่าที่กรอกไว้ ไม่ล่ม (Task 4)
3. **ค่าที่ทำให้ VTH ≤ VBE (cutoff)** → ต้องไม่แสดงกระแสติดลบ และต้องขึ้น warning ชัดเจน (Task 2)
4. **ค่าที่ทำให้ VCE ติดลบ (saturation)** → ต้องรายงานค่าตามสมการพร้อม warning ไม่ clamp และไม่ crash (Task 2)
5. **ค่าขนาดสุดขั้ว (R = 1e12, β = 1e9) หรือค่าที่ทำให้ตัวหารเป็นศูนย์** → ต้องไม่ hang/overflow และหน้าเว็บยัง render ได้ (Task 1)

---

## File Structure

| ไฟล์ | ความรับผิดชอบ |
|---|---|
| `dc_bias.py` | dataclass ผลลัพธ์, `VCE_SAT`, `compute_dc_bias()` + validation — pure Python |
| `app.py` | Flask app, `parse_form()`, `format_result()`, routes `GET /` และ `POST /calculate` |
| `templates/index.html` | ฟอร์ม 7 ช่อง, ตารางผล, ป้าย region, error/warning block |
| `static/style.css` | layout สองคอลัมน์ / คอลัมน์เดียวบนจอแคบ |
| `tests/test_dc_bias.py` | เทสต์สมการ, region, validation |
| `tests/test_web.py` | เทสต์ HTTP ผ่าน Flask test client |
| `docs/design-note.md` | เหตุผลการออกแบบและโครงสร้าง |
| `docs/validation.md` | ค่าอ้างอิง, ผลรันเทสต์จริง, ตารางเดโม |
| `docs/reflection.md` | สิ่งที่เรียนรู้/ข้อจำกัดของแบบจำลอง |
| `README.md` | วิธีติดตั้ง/รัน/ทดสอบ (แก้จากสถานะ scaffold) |

---

### Task 1: Engineering module — สมการ DC Bias และ validation

**Files:**
- Create: `dc_bias.py`
- Test: `tests/test_dc_bias.py`

**Interfaces:**
- Produces:
  - `VCE_SAT: float = 0.2`
  - `@dataclass(frozen=True) class DcBiasResult` มีฟิลด์ `vth, rth, ib, ic, ie, ve, vb, vc, vce` (`float`), `region` (`str`), `warnings` (`tuple[str, ...]`)
  - `compute_dc_bias(vcc: float, r1: float, r2: float, rc: float, re: float, beta: float, vbe: float) -> DcBiasResult` — raise `ValueError` เมื่ออินพุตผิด

- [ ] **Step 1: เขียนเทสต์ที่ยังไม่ผ่าน**

สร้าง `tests/test_dc_bias.py`:

```python
import unittest

from dc_bias import compute_dc_bias

REF = dict(vcc=12.0, r1=100_000.0, r2=22_000.0, rc=2_200.0, re=1_000.0,
           beta=100.0, vbe=0.70)


class ReferenceCaseTest(unittest.TestCase):
    def test_reference_operating_point(self):
        r = compute_dc_bias(**REF)
        self.assertAlmostEqual(r.vth, 2.163934, places=5)
        self.assertAlmostEqual(r.rth, 18_032.787, places=2)
        self.assertAlmostEqual(r.ib, 12.2986e-6, delta=1e-9)
        self.assertAlmostEqual(r.ic, 1.229858e-3, delta=1e-8)
        self.assertAlmostEqual(r.ie, 1.242157e-3, delta=1e-8)
        self.assertAlmostEqual(r.ve, 1.242157, places=5)
        self.assertAlmostEqual(r.vb, 1.942157, places=5)
        self.assertAlmostEqual(r.vc, 9.294312, places=5)
        self.assertAlmostEqual(r.vce, 8.052155, places=5)
        self.assertEqual(r.region, "active")
        self.assertEqual(r.warnings, ())


class ValidationTest(unittest.TestCase):
    def test_zero_resistor_rejected(self):
        for key in ("r1", "r2", "rc", "re"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                compute_dc_bias(**{**REF, key: 0.0})

    def test_negative_resistor_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "rc": -2_200.0})

    def test_zero_beta_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "beta": 0.0})

    def test_zero_vcc_rejected(self):
        with self.assertRaises(ValueError):
            compute_dc_bias(**{**REF, "vcc": 0.0})

    def test_extreme_values_still_compute(self):
        r = compute_dc_bias(**{**REF, "r1": 1e12, "beta": 1e9})
        self.assertTrue(all(isinstance(v, float) for v in (r.vb, r.vce, r.ic)))
```

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run: `.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dc_bias'`

- [ ] **Step 3: เขียน `dc_bias.py`**

สร้างไฟล์พร้อม `VCE_SAT = 0.2`, dataclass `DcBiasResult` ตาม Interfaces และฟังก์ชัน `compute_dc_bias` ที่:
1. ตรวจ `vcc <= 0`, `r1 <= 0`, `r2 <= 0`, `rc <= 0`, `re <= 0`, `beta <= 0` → `raise ValueError` ข้อความภาษาไทยระบุชื่อพารามิเตอร์ เช่น `"R1 ต้องมากกว่า 0 โอห์ม"`
2. คำนวณ `vth`, `rth`, `ib`, `ic`, `ie`, `ve`, `vb`, `vc`, `vce` ตามสมการใน spec §7.3
3. ตั้ง `region="active"` และ `warnings=()` (การแยก region เป็นงานของ Task 2)

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run: `.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
Expected: PASS 6 tests

- [ ] **Step 5: ส่งงานให้เจ้าของ commit**

รายงานไฟล์ที่เปลี่ยน (`dc_bias.py`, `tests/test_dc_bias.py`) — เจ้าของ commit ผ่าน GitHub Desktop ด้วยข้อความ `feat: add dc bias engineering module`

---

### Task 2: Region classification และ warnings

**Files:**
- Modify: `dc_bias.py`
- Test: `tests/test_dc_bias.py` (เพิ่มคลาสใหม่)

**Interfaces:**
- Consumes: `compute_dc_bias`, `DcBiasResult`, `VCE_SAT` จาก Task 1
- Produces: `region` เป็น `"cutoff"` / `"saturation"` / `"active"` และ `warnings` ที่มีข้อความภาษาไทยตามเงื่อนไขใน spec §7.3

- [ ] **Step 1: เขียนเทสต์ที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_dc_bias.py`:

```python
class RegionTest(unittest.TestCase):
    def test_cutoff_when_vth_not_above_vbe(self):
        r = compute_dc_bias(**{**REF, "r2": 4_700.0})
        self.assertAlmostEqual(r.vth, 0.5387, places=4)
        self.assertEqual(r.region, "cutoff")
        self.assertEqual(r.ib, 0.0)
        self.assertEqual(r.ic, 0.0)
        self.assertEqual(r.ie, 0.0)
        self.assertAlmostEqual(r.vb, r.vth, places=9)
        self.assertAlmostEqual(r.vce, 12.0 - r.vth, places=9)
        self.assertTrue(r.warnings)

    def test_saturation_reports_unclamped_values(self):
        r = compute_dc_bias(vcc=12.0, r1=47_000.0, r2=10_000.0, rc=4_700.0,
                            re=470.0, beta=150.0, vbe=0.70)
        self.assertEqual(r.region, "saturation")
        self.assertAlmostEqual(r.vce, -1.76549, delta=0.01)
        self.assertLess(r.vce, 0.2)
        self.assertTrue(r.warnings)

    def test_vbe_outside_normal_range_warns_but_computes(self):
        r = compute_dc_bias(**{**REF, "vbe": 0.30})
        self.assertEqual(r.region, "active")
        self.assertTrue(any("VBE" in w for w in r.warnings))
```

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run: `.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
Expected: FAIL — `test_cutoff_...` ได้ `region == "active"` และ/หรือ `ic` ติดลบ

- [ ] **Step 3: เพิ่มตรรกะ region ใน `compute_dc_bias`**

ตามลำดับ:
1. ถ้า `vth <= vbe` → clamp `ib = ic = ie = 0.0`, `ve = 0.0`, `vb = vth`, `vc = vcc`, `vce = vcc - vth`, `region = "cutoff"`, warning ว่าแบบจำลอง Forward-Active ใช้ไม่ได้ (วงจรอยู่ใน cutoff)
2. elif `vce <= VCE_SAT` → `region = "saturation"` + warning (คงค่าที่คำนวณได้ ไม่ clamp)
3. else → `region = "active"`
4. ถ้า `vbe` ไม่อยู่ในช่วง 0.4–0.9 V → เพิ่ม warning ที่มีคำว่า `VBE` (ทุก region)

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run: `.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
Expected: PASS 9 tests

- [ ] **Step 5: ส่งงานให้เจ้าของ commit**

รายงานไฟล์ที่เปลี่ยน — commit ด้วย `feat: classify operating region and warn outside forward active`

---

### Task 3: Flask app + ฟอร์ม (GET /)

**Files:**
- Create: `app.py`, `templates/index.html`, `static/style.css`
- Test: `tests/test_web.py`

**Interfaces:**
- Consumes: `compute_dc_bias`, `DcBiasResult` จาก Task 1–2
- Produces:
  - `app: flask.Flask` (import ได้ด้วย `from app import app`)
  - `DEFAULTS: dict[str, str]` ค่าเริ่มต้น = `{"vcc": "12", "r1": "100000", "r2": "22000", "rc": "2200", "re": "1000", "beta": "100", "vbe": "0.70"}`
  - route `GET /` → 200 พร้อมฟอร์ม

- [ ] **Step 1: เขียนเทสต์ที่ยังไม่ผ่าน**

สร้าง `tests/test_web.py`:

```python
import unittest

from app import app


class GetFormTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_index_returns_form(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', body)

    def test_get_index_prefills_reference_values(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('value="100000"', body)
        self.assertIn("Calculate DC Bias", body)
```

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run: `.venv\Scripts\python.exe -m unittest tests.test_web -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: สร้าง `app.py`, `templates/index.html`, `static/style.css`**

`app.py` ประกอบด้วย `app = Flask(__name__)`, `DEFAULTS`, และ route `GET /` ที่ `render_template("index.html", inputs=DEFAULTS, errors=[], view=None)` — ยังไม่มี route POST
`templates/index.html`: `<form method="post" action="{{ url_for('calculate') }}">` พร้อม input 7 ช่อง (`name="vcc"` … `name="vbe"`, `inputmode="decimal"`), ปุ่ม `Calculate DC Bias`, บล็อก error (ว่างเมื่อไม่มี) และ `<link>` ไป `static/style.css`
`static/style.css`: grid 2 คอลัมน์เมื่อกว้าง ≥ 720px, คอลัมน์เดียวเมื่อแคบกว่านั้น

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run: `.venv\Scripts\python.exe -m unittest tests.test_web -v`
Expected: PASS 2 tests

- [ ] **Step 5: ตรวจด้วยตาว่ารันได้จริง**

Run: `.venv\Scripts\python.exe -m flask --app app run --debug`
Expected: ขึ้น `Running on http://127.0.0.1:5000` และเปิดเบราว์เซอร์เห็นฟอร์ม (หยุดด้วย Ctrl+C)

- [ ] **Step 6: ส่งงานให้เจ้าของ commit**

commit ด้วย `feat: add Flask app and DC bias input form`

---

### Task 4: POST /calculate — คำนวณ, แสดงผล, จัดการ error

**Files:**
- Modify: `app.py`, `templates/index.html`
- Test: `tests/test_web.py` (เพิ่มคลาสใหม่)

**Interfaces:**
- Consumes: `compute_dc_bias`, `DcBiasResult`, `DEFAULTS`
- Produces:
  - `parse_form(form: Mapping[str, str]) -> tuple[dict[str, float], list[str]]` — คืนค่า float 7 ตัว และ list ข้อความ error ภาษาไทย
  - `format_result(result: DcBiasResult) -> dict[str, str]` — คีย์ `vb, ve, vc, vce, ic, ib, ie, vth, rth` พร้อมหน่วยในสตริง
  - `format_inputs(values: Mapping[str, float]) -> dict[str, str]` — คีย์ `vcc, r1, r2, rc, re, beta, vbe` โดยตัวต้านทานได้รูปแบบ `100000 Ω (100 kΩ)`
  - route `POST /calculate` → 200 เมื่อสำเร็จ, 400 เมื่ออินพุตผิด

- [ ] **Step 1: เขียนเทสต์ที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_web.py`:

```python
class CalculateTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def post(self, **overrides):
        data = {"vcc": "12", "r1": "100000", "r2": "22000", "rc": "2200",
                "re": "1000", "beta": "100", "vbe": "0.70"}
        data.update(overrides)
        return self.client.post("/calculate", data=data)

    def test_reference_case_renders_results(self):
        resp = self.post()
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        for expected in ("1.942", "1.242", "9.294", "8.052", "1.230", "Active"):
            self.assertIn(expected, body)

    def test_zero_resistor_shows_error(self):
        resp = self.post(r1="0")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("R1", resp.get_data(as_text=True))

    def test_non_numeric_shows_error_not_crash(self):
        resp = self.post(rc="abc")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ตัวเลข", resp.get_data(as_text=True))

    def test_comma_and_suffix_rejected(self):
        for bad in ("1,000", "100k"):
            with self.subTest(value=bad):
                resp = self.post(r1=bad)
                self.assertEqual(resp.status_code, 400)

    def test_cutoff_warning_shown(self):
        resp = self.post(r2="4700")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_data(as_text=True)
        self.assertIn("Cutoff", body)
        self.assertIn("Forward-Active", body)
        self.assertIn("0.000", body)  # IC ถูก clamp เป็น 0 mA

    def test_saturation_warning_shown(self):
        resp = self.client.post("/calculate", data={
            "vcc": "12", "r1": "47000", "r2": "10000", "rc": "4700",
            "re": "470", "beta": "150", "vbe": "0.70"})
        body = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Saturation", body)
```

> หมายเหตุสำหรับผู้ทำแผน: warning ภาษาไทยต้องมีคำว่า `Forward-Active` เพื่อให้
> เทสต์ `test_cutoff_warning_shown` ตรวจได้ และค่า IC ที่ clamp เป็น 0 ต้องแสดง
> เป็น `0.000 mA` ตาม Global Constraints

- [ ] **Step 2: รันเทสต์ให้เห็นว่า fail**

Run: `.venv\Scripts\python.exe -m unittest tests.test_web -v`
Expected: FAIL — `POST /calculate` ตอบ 404

- [ ] **Step 3: เพิ่ม `parse_form`, `format_result` และ route `POST /calculate`**

- `parse_form`: สำหรับแต่ละฟิลด์ใน `DEFAULTS` แปลงด้วย `float(raw.strip())`; ถ้า `ValueError` เพิ่ม error `"<ชื่อฟิลด์> ต้องเป็นตัวเลข"`; ตรวจ `<= 0` ตาม Task 1 แล้วปล่อยให้ `compute_dc_bias` raise `ValueError` เพื่อรวมข้อความ
- `format_result`: จัดรูปด้วย f-string ตาม Global Constraints เช่น `f"{result.vce:.3f} V"`, `f"{result.ic*1e3:.3f} mA"`, `f"{result.ib*1e6:.2f} µA"`, `f"{result.rth/1000:.3f} kΩ"`
- `format_inputs`: ตัวต้านทาน → `f"{v:.0f} Ω ({v/1000:g} kΩ)"`, แรงดัน → `f"{v:g} V"`, `β` → `f"{v:g}"`
- route: เรียก `parse_form` → ถ้ามี error `render_template(..., errors=errors, inputs=raw_form)` พร้อม `status=400`; ถ้าไม่มี เรียก `compute_dc_bias(**parsed)` แล้ว `render_template(..., view=format_result(result), inputs=format_inputs(parsed), result=result)`
- `templates/index.html`: เพิ่มตารางผลจาก `view`, ป้าย region จาก `result.region` (แสดงเสมอ), บล็อก warning จาก `result.warnings`, และ `value="{{ inputs[...] }}"` เพื่อคงค่าที่กรอก

- [ ] **Step 4: รันเทสต์ทั้งหมดให้ผ่าน**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: PASS 17 tests (9 จาก `test_dc_bias` + 8 จาก `test_web`)

- [ ] **Step 5: ตรวจด้วยมือในเบราว์เซอร์**

Run: `.venv\Scripts\python.exe -m flask --app app run --debug`
ตรวจ: (1) ค่าเริ่มต้น → Active และ IC 1.230 mA (2) `R2=4700` → Cutoff + warning (3) ชุด saturation → Saturation + VCE ติดลบ (4) `R1=0` → error ภาษาไทยและค่าที่กรอกยังอยู่

- [ ] **Step 6: ส่งงานให้เจ้าของ commit**

commit ด้วย `feat: calculate DC bias from form input with validation and warnings`

---

### Task 5: เอกสาร, README และการตรวจรับ

**Files:**
- Create: `docs/design-note.md`, `docs/validation.md`, `docs/reflection.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: ผลรันเทสต์จริงจาก Task 4, ค่าอ้างอิงจาก spec §8

- [ ] **Step 1: รันเทสต์เก็บหลักฐาน**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: PASS ทั้งหมด — คัดลอกข้อความจริงไปใส่ `docs/validation.md`

- [ ] **Step 2: เขียน `docs/validation.md`**

ตาราง 4 กรณีจาก spec §8 (Active / Cutoff / Saturation / Invalid) เทียบผลที่เว็บแสดงกับค่าที่คำนวณมือ พร้อมผลรันเทสต์จริง (วาง output ที่คัดลอกมา) และระบุข้อจำกัดของแบบจำลอง (Forward-Active, β คงที่, ไม่ใช่ SPICE)

- [ ] **Step 3: เขียน `docs/design-note.md` และ `docs/reflection.md`**

`design-note.md`: เหตุผลที่แยก `dc_bias.py` ออกจาก `app.py`, เหตุผลที่อินพุตเป็น Ω, เหตุผลที่ไม่ clamp ค่า saturation
`reflection.md`: สิ่งที่เรียนรู้เรื่อง HTTP/template/backend และข้อจำกัดที่พบระหว่างทำ

- [ ] **Step 4: อัปเดต `README.md`**

เปลี่ยนสถานะจาก scaffold → implemented, ใส่คำสั่งรันจริงที่ทดสอบแล้ว (venv, pip install, flask run, unittest) และตารางค่าอ้างอิง

- [ ] **Step 5: ตรวจเกณฑ์ A1–A7 ด้วยตัวเอง**

ไล่ทีละข้อตาม spec §10 และจดผลไว้ใน `docs/validation.md` (A1–A6 พิสูจน์ได้จากเทสต์/เบราว์เซอร์, A7 ตรวจว่า clone แล้วทำตาม README ได้)

- [ ] **Step 6: ส่งงานให้เจ้าของ commit**

commit ด้วย `docs: add design note, validation evidence and reflection`

---

## Self-Review

- **Spec coverage:** §7.1 หน่วย → Task 3/4 · §7.1.1 ภาษา → Task 3/4 · §7.2 routes → Task 3/4 · §7.3 โมดูล+region → Task 1/2 · §7.4 app.py → Task 3/4 · §7.5 template → Task 3/4 · §7.6 CSS → Task 3 · §7.7 tests → Task 1/2/3/4 · §7.8 docs → Task 5 · §10 A1–A7 → Task 5 Step 5
- **Types:** `compute_dc_bias` / `DcBiasResult` / `VCE_SAT` / `parse_form` / `format_result` ใช้ชื่อเดิมทุก task
- **Review Focus:** ครบ 5 ข้อ ผูกกับ Task 1 (ข้อ 1, 5), Task 2 (ข้อ 3, 4), Task 4 (ข้อ 2)
