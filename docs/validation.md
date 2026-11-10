# Validation — BJT DC Bias Web App

## 1. ค่าอ้างอิงที่คำนวณด้วยมือ

แบบจำลอง Forward-Active (β คงที่, VBE คงที่):
`VTH = VCC·R2/(R1+R2)`, `RTH = R1·R2/(R1+R2)`, `IB = (VTH−VBE)/(RTH+(β+1)RE)`

กรณีทดสอบหลัก: VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ,
β = 100, VBE = 0.70 V

| ปริมาณ | คำนวณมือ | เว็บแสดง |
|---|---|---|
| VTH | 2.163934 V | 2.164 V |
| RTH | 18.032787 kΩ | 18.033 kΩ |
| IB | 12.2986 µA | 12.30 µA |
| IC | 1.229858 mA | 1.230 mA |
| IE | 1.242157 mA | 1.242 mA |
| VE | 1.242157 V | 1.242 V |
| VB | 1.942157 V | 1.942 V |
| VC | 9.294312 V | 9.294 V |
| VCE | 8.052155 V | 8.052 V |
| Region | Active (VTH > VBE, VCE > 0.2 V) | Active |

## 2. ตารางทดสอบบนเบราว์เซอร์ (รันจริงผ่าน `http://127.0.0.1:50xx/calculate`)

| กรณี | อินพุต | ผลที่ได้ | สถานะ |
|---|---|---|---|
| Active | ค่าเริ่มต้น (ตามตารางข้อ 1) | `region-active`, IC = 1.230 mA, VCE = 8.052 V | ✅ ตรงกับมือ |
| Cutoff | R2 = 4 700 Ω | `region-cutoff`, VTH = 0.539 V, IC = 0.000 mA, มี warning | ✅ |
| Saturation | VCC 12, R1 47k, R2 10k, RC 4.7k, RE 470, β 150, VBE 0.7 | `region-saturation`, VCE = −1.765 V, มี warning | ✅ |
| Invalid | R1 = 0 | HTTP 400, ข้อความ "R1 ต้องมากกว่า 0 โอห์ม", ค่าที่กรอกยังอยู่, ไม่มี traceback | ✅ |
| Non-numeric | RC = `abc` | HTTP 400, ข้อความ "RC ต้องเป็นตัวเลข" | ✅ |
| Unit suffix | R1 = `100k` หรือ `1,000` | HTTP 400 (ไม่รับ suffix/comma) | ✅ |

## 3. ผลรัน automated tests

คำสั่ง: `.venv\Scripts\python.exe -m unittest discover -s tests -v`

```
test_extreme_values_still_compute (test_dc_bias.ValidationTest.test_extreme_values_still_compute) ... ok
test_negative_resistor_rejected (test_dc_bias.ValidationTest.test_negative_resistor_rejected) ... ok
test_zero_beta_rejected (test_dc_bias.ValidationTest.test_zero_beta_rejected) ... ok
test_zero_resistor_rejected (test_dc_bias.ValidationTest.test_zero_resistor_rejected) ... ok
test_zero_vcc_rejected (test_dc_bias.ValidationTest.test_zero_vcc_rejected) ... ok
test_reference_operating_point (test_dc_bias.ReferenceCaseTest.test_reference_operating_point) ... ok
test_cutoff_when_vth_not_above_vbe (test_dc_bias.RegionTest.test_cutoff_when_vth_not_above_vbe) ... ok
test_saturation_reports_unclamped_values (test_dc_bias.RegionTest.test_saturation_reports_unclamped_values) ... ok
test_vbe_outside_normal_range_warns_but_computes (test_dc_bias.RegionTest.test_vbe_outside_normal_range_warns_but_computes) ... ok
test_comma_and_suffix_rejected (test_web.CalculateTest.test_comma_and_suffix_rejected) ... ok
test_cutoff_warning_shown (test_web.CalculateTest.test_cutoff_warning_shown) ... ok
test_non_numeric_shows_error_not_crash (test_web.CalculateTest.test_non_numeric_shows_error_not_crash) ... ok
test_reference_case_renders_results (test_web.CalculateTest.test_reference_case_renders_results) ... ok
test_saturation_warning_shown (test_web.CalculateTest.test_saturation_warning_shown) ... ok
test_zero_resistor_shows_error (test_web.CalculateTest.test_zero_resistor_shows_error) ... ok
test_get_index_prefills_reference_values (test_web.GetFormTest.test_get_index_prefills_reference_values) ... ok
test_get_index_returns_form (test_web.GetFormTest.test_get_index_returns_form) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.045s

OK
```

แบ่งเป็น 9 tests ด้านสมการ/validation และ 8 tests ผ่าน Flask test client
(เกินเกณฑ์ขั้นต่ำ ≥3 + ≥1)

## 4. เกณฑ์ตรวจรับ A1–A7

| เกณฑ์ | หลักฐาน | ผล |
|---|---|---|
| A1 · `GET /` | `test_get_index_returns_form` (200 + ฟิลด์ครบ), ตรวจด้วย HTTP จริงได้ 200 | ✅ |
| A2 · `POST /calculate` | `test_reference_case_renders_results` — ตัวเลขมาจาก `dc_bias.py` | ✅ |
| A3 · Engineering reference | `test_reference_operating_point` ตรงกับตารางข้อ 1 ทุกค่า | ✅ |
| A4 · Validation | `test_zero_resistor_shows_error`, `test_non_numeric_shows_error_not_crash`, `test_comma_and_suffix_rejected` (HTTP 400 + ข้อความ) | ✅ |
| A5 · Outside active region | `test_cutoff_warning_shown`, `test_saturation_warning_shown` + ป้าย region แสดงเสมอ | ✅ |
| A6 · Unit + HTTP tests | 9 engineering tests + 8 Flask client tests | ✅ |
| A7 · GitHub reproducibility | ตรวจด้วยการคัดลอกเฉพาะไฟล์ที่ track ไปยังโฟลเดอร์ใหม่ → `python -m venv .venv` → `pip install -r requirements.txt` → `python -m unittest discover -s tests` ได้ `Ran 17 tests ... OK` (ทำตาม README ทุกขั้น) | ✅ |

## 5. ข้อจำกัดของแบบจำลอง

- ใช้ Forward-Active approximation: β คงที่และ VBE คงที่ ไม่คำนึงถึง Early effect,
  อุณหภูมิ, หรือการเปลี่ยนแปลงของ β ตามกระแส
- ไม่ใช่ SPICE/ngspice จึงไม่มีการแก้สมการแบบ nonlinear จริง
- ค่าใน Saturation รายงานตามสมการ Forward-Active โดยไม่ clamp (อาจติดลบ) เพื่อแสดงว่า
  แบบจำลองใช้ไม่ได้ในย่านนั้น — ไม่ใช่ค่าที่ควรนำไปใช้จริง
- ค่า Cutoff ถูกปรับกระแสเป็นศูนย์ตามพฤติกรรมทางกายภาพของรอยต่อ B-E ที่ไม่ forward bias
