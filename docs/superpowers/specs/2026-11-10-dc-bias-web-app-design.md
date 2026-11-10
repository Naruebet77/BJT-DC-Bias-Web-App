# Design — BJT DC Bias Web App (ENG29 2121 · Lab 02)

วันที่: 2026-11-10
สถานะ: **อนุมัติแล้ว** (2026-11-10)

## 1. เจตนาและเหตุผล

สร้าง **Flask web application หลายไฟล์** ที่คำนวณ DC operating point ของ NPN BJT
Common-Emitter แบบ **Voltage-Divider Bias** ภายใต้สมมติฐาน Forward-Active
(β คงที่, VBE คงที่) โดยตัวเลขทุกตัวต้องคำนวณจาก Python backend ไม่ใช่ค่าที่ฝังใน HTML

เหตุผล: เป็นชิ้นงานส่งอาจารย์ของ Lab 02 และเป็นบทเรียนเรื่องการแยก
Frontend / Backend / Template / Static / Tests รวมถึงเป็นฐานของ Lab สัปดาห์ถัดไป

ขอบเขตยึดตามเอกสาร Lab 02 §03, §04, §06, §09 อย่างเคร่งครัด — **ไม่เพิ่ม feature ใด ๆ
ที่เอกสารไม่ได้ระบุ**

เอกสารอ้างอิง (ต้นฉบับ ไม่อยู่ใน repo):
`C:\Users\B6821227\Downloads\Lab02_BJT_Simulator_Brainstorm_2-2569.html`
ข้อความในเอกสารนี้สรุปจากต้นฉบับนั้น และใช้ต้นฉบับเป็นตัวตัดสินเมื่อขัดแย้งกัน

## 2. เป้าหมาย (Goals)

| ID | เป้าหมาย | เกณฑ์ที่วัดได้ |
|---|---|---|
| G1 | เปิดหน้าเว็บได้ | `GET /` → 200 และเห็น input form ครบ 7 ช่อง |
| G2 | คำนวณจริงด้วย Python | `POST /calculate` → ตัวเลขใน HTML มาจาก `dc_bias.py` |
| G3 | แสดงผลครบพร้อมหน่วย | VB, VE, VC, VCE [V], IC [mA] + IB [µA], IE [mA], VTH [V], RTH [kΩ] |
| G4 | Validation | ค่าขาด/ไม่ใช่ตัวเลข/R≤0/β≤0/VCC≤0 → ข้อความ error ชัดเจน, ไม่ crash |
| G5 | Region warning | Cutoff (VTH ≤ VBE) และ Saturation (VCE ≤ 0.2 V) ต้องมี warning |
| G6 | Automated tests | ≥3 unit tests ด้านวิศวกรรม + ≥1 test ผ่าน Flask test client |
| G7 | Reproducible | clone → venv → `pip install -r requirements.txt` → รันเว็บ/รันเทสต์ได้ตาม README |

## 3. ไม่ทำ (Non-goals)

- AC small-signal, gain, Bode plot
- Transient analysis, signal generator, amplitude/frequency control
- Interactive schematic editor, DC/AC overlay animation
- Bias type อื่น (Fixed, Emitter), FET
- SPICE / ngspice integration
- ระบบ login, ฐานข้อมูล, การบันทึกประวัติการคำนวณ
- JavaScript framework ใด ๆ

## 4. Anti-goals (ทำแล้วถือว่าล้มเหลว)

- ฮาร์ดโค้ดผลลัพธ์ไว้ใน template
- ต้อง double-click เปิด `templates/index.html` ผ่าน `file://` ถึงจะเห็นผล
- แสดงผลโดยไม่มีหน่วย หรือไม่แปลงหน่วยก่อนคำนวณ
- รายงานว่า "Forward-Active ใช้ได้" ทั้งที่ VTH ≤ VBE หรือ VCE ≤ 0.2 V
- อ้างว่า test ผ่านโดยไม่ได้รันจริง
- `dc_bias.py` import Flask หรือรู้จัก HTML/HTTP

## 5. ข้อจำกัด (Constraints)

- Python 3.14.2, Flask 3.1.3 (ติดตั้งใน `.venv` แล้ว)
- Windows 11, พัฒนา/เดโมผ่าน `http://127.0.0.1:5000/`
- ใช้ `unittest` จาก standard library เท่านั้น (ไม่เพิ่ม pytest/numpy)
- Commit/push ทำโดยเจ้าของโปรเจกต์ผ่าน GitHub Desktop — AI ไม่แตะ git
- เวลาทำงานจริง ~75 นาที

## 6. แนวทางที่พิจารณา

**A. Flask ไฟล์เดียว (`app.py` ทำทุกอย่าง)**
เร็วที่สุด แต่ผิดเจตนารมณ์ §04 ที่บังคับให้แยกความรับผิดชอบ และเทสต์สมการยาก
เพราะปนกับ HTTP → ตกไป

**B. Multi-file ตามโครงในใบแล็บ** (`app.py` / `dc_bias.py` / `templates/` / `static/` / `tests/`)
ตรงกับ §04 ทุกบรรทัด, เทสต์สมการแยกจาก HTTP ได้, ต่อยอด Lab ถัดไปได้ → **เลือก**

**C. เพิ่ม JSON API + fetch จาก JavaScript**
ให้ UX ลื่นกว่า แต่เกินขอบเขตที่เอกสารกำหนด และเพิ่มจุดเสี่ยงในเวลาจำกัด → ตกไป

**สิ่งที่เจ้าของโปรเจกต์เลือก:** ทำตามขอบเขตในเอกสาร HTML ตรง ๆ → แนวทาง B

## 7. สิ่งที่ตกลงแล้ว (ออกแบบไว้)

### 7.1 หน่วยอินพุต
รับค่าตามตาราง §06: `VCC [V]`, `R1, R2, RC, RE [Ω]`, `β` (ไม่มีหน่วย), `VBE [V]`
ผู้ใช้พิมพ์เป็น Ω (เช่น `100000`) และผลลัพธ์แสดงค่าเทียบเป็น kΩ กำกับ
(เช่น `R1 = 100000 Ω (100 kΩ)`) เพื่อให้เห็นว่ามีการแปลงหน่วยจริงตามที่เอกสารต้องการ
ไม่มี dropdown เปลี่ยนหน่วย และไม่รับ suffix อย่าง `100k`

ตรวจสอบกับต้นฉบับแล้ว (§06 ตารางข้อมูลเข้า) ระบุ `R1/R2/RC/RE [Ω]` ชัดเจน จึงยืนยันหน่วย Ω

### 7.1.1 ภาษาบนหน้าจอ
UI เป็น**ภาษาไทย** โดยคงชื่อปริมาณ/ตัวแปรเป็นอังกฤษตามสากล (`VCC`, `VB`, `VCE`, `β`, `DC Bias`)
เช่น ป้าย `แรงดันแหล่งจ่าย VCC (V)`, ป้ายสถานะ `Active / Cutoff / Saturation`
ข้อความ error และ warning เป็นภาษาไทยทั้งหมด (สอดคล้องกับ `ValueError` ใน §7.3)

### 7.2 เส้นทาง HTTP
- `GET /` → ฟอร์ม พร้อมค่าเริ่มต้น = ตัวอย่างในเอกสาร (VCC 12, R1 100000, R2 22000, RC 2200, RE 1000, β 100, VBE 0.7)
- `POST /calculate` → parse → validate → compute → render หน้าเดิมพร้อมผล
- อินพุตผิด → HTTP **400** + แสดง error inline โดยคงค่าที่ผู้ใช้กรอกไว้
- ไม่มี redirect หลัง POST (ผลอยู่ใน response เดียวกัน ตรวจง่ายด้วย test client)

### 7.3 โมดูลวิศวกรรม `dc_bias.py`
```python
@dataclass(frozen=True)
class DcBiasResult:
    vth: float; rth: float
    ib: float; ic: float; ie: float
    ve: float; vb: float; vc: float; vce: float
    region: str          # "active" | "cutoff" | "saturation"
    warnings: list[str]

def compute_dc_bias(vcc, r1, r2, rc, re, beta, vbe) -> DcBiasResult
```
- หน่วยภายในเป็น SI: V, A, Ω (ผลลัพธ์กระแสเป็น A แล้วให้ layer แสดงผลแปลงเป็น mA/µA)
- ค่าผิด → `raise ValueError` พร้อมข้อความภาษาไทยที่อ่านรู้เรื่อง
- VBE นอกช่วง 0.4–0.9 V → ไม่ reject แต่เพิ่ม warning

**ตรรกะ region**
1. ถ้า `VTH <= VBE` → `region="cutoff"`, clamp `IB=IC=IE=0`, `VE=0`, `VB=VTH`, `VC=VCC`,
   `VCE=VCC-VTH` + warning ว่าแบบจำลอง Forward-Active ใช้ไม่ได้
2. ถ้า `VCE <= 0.2` → `region="saturation"` + warning (ค่า 0.2 V เป็น `VCE_SAT` ค่าคงที่ที่ประกาศชัด)
3. มิฉะนั้น → `region="active"` ไม่มี warning

**ค่าที่รายงานในแต่ละ region (ตัดสินแล้ว)**
- `cutoff` clamp ค่าตามข้อ 1 เพราะกระแสจริงเป็นศูนย์ (B-E ไม่ forward bias) — เป็นขีดจำกัดที่ถูกต้องของแบบจำลอง
- `saturation` **รายงานค่าที่คำนวณได้ตามสมการ Forward-Active โดยไม่ clamp** (เช่น VCE = −1.765 V)
  พร้อม warning ว่าแบบจำลองใช้ไม่ได้ เพราะการ clamp เป็น `VCE_SAT` คือการใช้แบบจำลองอีกตัว
  ซึ่งอยู่นอกขอบเขต Lab นี้ — ตัวเลขติดลบคือหลักฐานว่าโจทย์ออกนอกสมมติฐาน
- แสดง**ป้าย region เสมอ** (Active / Cutoff / Saturation) ทั้งกรณีปกติและผิดปกติ เพื่อให้เห็นหลักฐานของ A5

### 7.4 `app.py`
- ฟังก์ชัน `parse_inputs(form) -> dict` แปลง string → float, เก็บ error รวมเป็น list
- เรียก `compute_dc_bias` แล้วส่งผลเข้า template
- จับ `ValueError` จากโมดูล → แปลงเป็น error list
- ไม่มีสมการฟิสิกส์ใน `app.py`

### 7.5 `templates/index.html`
- ฟอร์ม 7 ช่อง + ปุ่ม `Calculate DC Bias`
- ตารางผลลัพธ์ (แสดงเฉพาะเมื่อมีผล) พร้อมหน่วยทุกช่อง
- บล็อก error / warning แยกสี
- ไม่มีสมการฟิสิกส์ใน template

### 7.6 `templates` + CSS
`static/style.css` — layout เรียบ ๆ สองคอลัมน์บนจอกว้าง คอลัมน์เดียวบนจอแคบ
ไม่ต้องเลียนแบบภาพในเอกสารทุกพิกเซล (เอกสารระบุว่าอนุญาตให้ออกแบบเอง)

### 7.7 Tests
`tests/test_dc_bias.py`
1. ค่าอ้างอิง: 12 / 100k / 22k / 2.2k / 1k / 100 / 0.7 → VB 1.942, VE 1.242, VC 9.294, VCE 8.052 V, IC 1.230 mA, region `active`
2. Cutoff: R2 = 4.7 kΩ → VTH 0.5387 ≤ 0.7 → region `cutoff`, IC 0, มี warning
3. Saturation: 12 / 47k / 10k / 4.7k / 470 / 150 / 0.7 → VCE −1.765 V → region `saturation`, มี warning
   (คลาดเคลื่อนจากค่าจริง −1.76549 ตามการปัดเศษ — ใช้ tolerance 0.01 V ในเทสต์กรณีนี้)
4. Validation: R=0, β=0, VCC=0, ค่าไม่ใช่ตัวเลข → `ValueError`
5. VBE นอกช่วง → ได้ warning แต่ยังคำนวณ

`tests/test_web.py` (Flask test client)
1. `GET /` → 200 + มี `name="vcc"` ในฟอร์ม
2. `POST /calculate` ค่าอ้างอิง → 200 + ข้อความผลลัพธ์มี `1.230` และ `8.052`
3. `POST /calculate` ค่าไม่ใช่ตัวเลข → 400 + ข้อความ error และหน้าไม่ล่ม

### 7.8 เอกสาร
`README.md` อัปเดตจากสถานะ scaffold → วิธีติดตั้ง/รัน/ทดสอบจริง
`docs/design-note.md`, `docs/validation.md`, `docs/reflection.md` ตามโครงใน §04

## 8. ข้อมูลทดสอบสำหรับเดโม

| กรณี | VCC | R1 | R2 | RC | RE | β | VBE | ผลที่คาด |
|---|---|---|---|---|---|---|---|---|
| Typical (Active) | 12 | 100k | 22k | 2.2k | 1k | 100 | 0.70 | IC 1.230 mA, VCE 8.052 V |
| Cutoff | 12 | 100k | 4.7k | 2.2k | 1k | 100 | 0.70 | VTH 0.539 V → warning |
| Saturation | 12 | 47k | 10k | 4.7k | 470 | 150 | 0.70 | VCE −1.765 V → warning |
| Invalid | 12 | 0 | 22k | 2.2k | 1k | 100 | 0.70 | error R1 > 0 |

## 9. สิ่งที่เหลือให้ผู้สร้างตัดสินใจ

- โทนสี/รายละเอียดหน้าตา, ระยะห่าง, การจัดวางภายในขอบเขต CSS ข้างต้น
- ถ้อยคำของข้อความ error/warning (ต้องสื่อความหมายและมีหน่วย)
- จำนวนตำแหน่งทศนิยมที่แสดง (แนะนำ V 3 ตำแหน่ง, mA 3 ตำแหน่ง, µA 2 ตำแหน่ง)
- โครงสร้างภายในของ template (block/partial) ตราบใดที่ไม่มีสมการฟิสิกส์
- เนื้อหาของ `docs/design-note.md`, `docs/validation.md`, `docs/reflection.md`
  (ต้นฉบับ §04 ระบุเพียงชื่อไฟล์ ไม่ได้กำหนดหัวข้อภายใน จึงให้ผู้สร้างเลือกโครงเอง
  โดย `validation.md` ต้องมีผลรันเทสต์จริงและค่าอ้างอิงที่ใช้ตรวจ)

## 10. ความสอดคล้องกับเกณฑ์ตรวจรับ

| เกณฑ์ | ครอบคลุมโดย |
|---|---|
| A1 GET / | ข้อ 7.2, test_web #1 |
| A2 POST คำนวณจริง | ข้อ 7.2–7.4, test_web #2 |
| A3 ตรงกับค่าอ้างอิง | ข้อ 7.7 test #1 |
| A4 Validation | ข้อ 7.3–7.4, test_dc_bias #4 |
| A5 Region warning | ข้อ 7.3, test_dc_bias #2–3 |
| A6 Tests | ข้อ 7.7 (8 tests) |
| A7 GitHub reproducibility | ข้อ 7.8 README |
