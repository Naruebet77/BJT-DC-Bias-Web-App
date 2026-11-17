# Validation Evidence — BJT DC Bias Web App

ENG29 2121 · Lab 02 + Lab 03 · Voltage-Divider / Fixed / Emitter Bias

## 1. ผลการรัน Automated Tests (รันจริง)

```
.venv\Scripts\python.exe -m unittest discover -s tests -v

test_calculate... (test_web.CalculateTest) ... ok
test_comma_and_suffix_rejected ... ok
test_cutoff_warning_shown ... ok
test_get_index_prefills_reference_values ... ok
test_get_index_returns_form ... ok
test_non_numeric_shows_error_not_crash ... ok
test_reference_case_renders_results ... ok
test_saturation_warning_shown ... ok
test_zero_resistor_shows_error ... ok
test_cutoff_when_vth_not_above_vbe ... ok
test_extreme_values_still_compute ... ok
test_negative_resistor_rejected ... ok
test_reference_operating_point ... ok
test_saturation_reports_unclamped_values ... ok
test_vbe_outside_normal_range_warns_but_computes ... ok
test_zero_beta_rejected ... ok
test_zero_vcc_rejected ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.041s

OK
```

รวม **17 Automated Tests** (engineering 9 ตัว + HTTP 8 ตัว) เกินเกณฑ์ขั้นต่ำ (≥3 unit + ≥1 Flask test client)

## 2. ค่าอ้างอิงจากแบบจำลอง (ตรงกับตารางในใบแล็บ §06)

| ปริมาณ | ค่าที่คำนวณได้ | หน่วย |
|---|---|---|
| VTH | 2.163934 | V |
| RTH | 18032.787 | Ω |
| IB | 12.2986 | µA |
| IC | 1.229858 | mA |
| IE | 1.242157 | mA |
| VE | 1.242157 | V |
| VB | 1.942157 | V |
| VC | 9.294312 | V |
| VCE | 8.052155 | V |

อินพุตอ้างอิง: VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V  
สถานะ: **Active** (ไม่มี warning)

## 3. ตารางกรณีทดสอบสำหรับเดโม (A1–A5)

| # | กรณี | VCC | R1 | R2 | RC | RE | β | VBE | ผลที่คาด / สถานะ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Typical (Active) | 12 V | 100 kΩ | 22 kΩ | 2.2 kΩ | 1 kΩ | 100 | 0.70 V | IC 1.230 mA, VCE 8.052 V, ป้าย Active |
| 2 | Cutoff | 12 V | 100 kΩ | 4.7 kΩ | 2.2 kΩ | 1 kΩ | 100 | 0.70 V | VTH 0.5387 V ≤ VBE → IC = 0, warning "Forward-Active ใช้ไม่ได้" |
| 3 | Saturation | 12 V | 47 kΩ | 10 kΩ | 4.7 kΩ | 470 Ω | 150 | 0.70 V | VCE −1.765 V → warning "แบบจำลองใช้ไม่ได้ (ไม่ clamp)" |
| 4 | Invalid input | 12 V | 0 Ω | 22 kΩ | 2.2 kΩ | 1 kΩ | 100 | 0.70 V | Error "R1 ต้องมากกว่า 0 โอห์ม", HTTP 400, หน้าไม่ล่ม |

## 4. เกณฑ์ตรวจรับ A1–A7

| เกณฑ์ | สถานะ | หลักฐาน |
|---|---|---|
| A1: GET / → 200 เห็นฟอร์ม | ✅ | `test_get_index_returns_form`, `test_get_index_prefills_reference_values` |
| A2: POST คำนวณจริงด้วย Python | ✅ | `test_reference_case_renders_results` (ตัวเลขมาจาก `dc_bias.py` ไม่ฮาร์ดโค้ด) |
| A3: ตรงกับค่าอ้างอิง | ✅ | `test_reference_operating_point` (VB 1.942, VE 1.242, VC 9.294, VCE 8.052 V, IC 1.230 mA) |
| A4: Validation ค่าผิด | ✅ | `test_zero_resistor_shows_error`, `test_non_numeric_shows_error_not_crash`, `test_comma_and_suffix_rejected` |
| A5: Warning นอก Active region | ✅ | `test_cutoff_warning_shown`, `test_saturation_warning_shown`, ป้าย Cutoff/Saturation แสดงเสมอ |
| A6: Unit + HTTP Tests | ✅ | 17 tests รวม Flask test client |
| A7: Reproducible | ⏳ | ต้อง clone แล้วรันตาม `README.md` อีกครั้ง (ยังไม่ได้ push) |

## 5. ข้อจำกัดของแบบจำลอง

- β และ VBE คงที่ (Forward-Active Approximation) — ไม่ใช่ ngspice/SPICE
- ผลที่อยู่ใน Cutoff หรือ Saturation แสดงพร้อม Warning และไม่ควรอ้างว่าแม่นยำ
- รันได้เฉพาะเครื่องพัฒนาผ่าน `http://127.0.0.1:5000/`

---

## 6. Lab 03 — Browser acceptance A1–A5 (รันจริง)

**วิธีตรวจ:** OpenCode Browser (Browser Tool ที่มีใน Desktop) — **Playwright MCP: NOT RUN**
(ยังไม่ได้เพิ่ม `playwright` ใน `opencode.json` ของโปรเจกต์ ใบงานอนุญาตให้ใช้ Browser Tool
ที่มากับ OpenCode แทน และให้คะแนนการตรวจผลเท่ากัน) หลักฐานคือข้อความจริงที่อ่านจาก
`.results-table`, `.region-badge` และ `.error` ของหน้าเว็บหลังคลิกปุ่มคำนวณ

**ค่าคาดหมายอิสระ** คำนวณจากสมการในใบงานด้วยสคริปต์แยกต่างหาก (ไม่ import `dc_bias.py`
และไม่ได้อ่านค่าจากเว็บ) ที่ `VCC=12 V, RC=2.2 kΩ, β=100, VBE=0.70 V`:

| กรณี | สมการที่ใช้ | IC คาดหมาย (ก่อนปัด) | VCE คาดหมาย (ก่อนปัด) |
|---|---|---|---|
| A2 Fixed · RB=1 MΩ | IB=(12−0.70)/1e6, VE=0 | 1.130000 mA | 9.514000 V |
| A3 Emitter · RB=1 MΩ, RE=1 kΩ | IB=11.3/(1e6+101·1000) | 1.026340 mA | 8.705450 V |
| A4 Emitter · RB=1 MΩ, RE=2 kΩ | IB=11.3/(1e6+101·2000) | 0.940100 mA | 8.032779 V |

เกณฑ์: |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V เทียบกับค่าก่อนปัด

| ID | วิธีตรวจ | อินพุต | คาดหมาย | ผลที่เห็นจริง (พร้อมหน่วย) | สถานะ | หลักฐาน |
|---|---|---|---|---|---|---|
| A1 · โหมดเดิม | OpenCode Browser | Divider · R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | ตรงกับ Lab 2 ก่อนแก้: IC 1.230 mA, VCE 8.052 V | `IC 1.230 mA`, `VCE 8.052 V`, `สถานะทำงาน: ACTIVE` + VTH 2.164 V, RTH 18.033 kΩ | **PASS** | ข้อความในตารางผลของหน้า `/calculate` |
| A2 · Fixed | OpenCode Browser | Fixed · RB=1 MΩ (ไม่กรอก RE) | IC 1.130000 mA, VCE 9.514000 V | `IC 1.130 mA`, `VCE 9.514 V`, `VE 0.000 V`, `IB 11.30 µA`, ACTIVE — ไม่มีช่อง RE ในฟอร์ม | **PASS** | `(A2−คาดหมาย)=0.000000 mA / 0.000 V` |
| A3 · Emitter | OpenCode Browser | Emitter · RB=1 MΩ, RE=1 kΩ | IC 1.026340 mA, VCE 8.705450 V | `IC 1.026 mA`, `VCE 8.705 V`, `VE 1.037 V`, `VB 1.737 V`, ACTIVE | **PASS** | ΔIC 0.000340 mA, ΔVCE 0.000450 V |
| A4 · เปลี่ยนค่าเดียว | OpenCode Browser | Emitter · เหมือน A3 แต่ RE=2 kΩ (อย่างอื่นคงเดิม) | ทำนายว่า **IC ลดลง** เพราะตัวหาร RB+(β+1)RE เพิ่มขึ้น → IB ลดลง | `IC 0.940 mA` (ลดจาก 1.026), `VCE 8.033 V`, `VE 1.899 V` — อินพุตที่อ่านกลับ: vcc=12, rb=1000000, rc=2200, re=2000, beta=100, vbe=0.70 | **PASS** | ΔIC 0.000100 mA, ΔVCE 0.000221 V |
| A5 · อินพุตผิด | OpenCode Browser | Fixed · RB=0 | ข้อความให้แก้ RB, เว็บไม่ล่ม, ไม่แสดงผลรอบก่อน | ข้อความจาก Flask: `⚠ RB ต้องมากกว่า 0 โอห์ม`, ไม่มีตารางผล (`hasTable=false`), HTTP 400, โหมดยังเป็น Fixed Bias | **PASS** | ข้อความ `.error` ที่อ่านจากหน้าเว็บ |

**การปรับกรณีที่เกิดขึ้นระหว่างพัฒนา:** เทสต์เดิมของ Lab 2 โพสต์ `/calculate` โดยไม่ส่งฟิลด์
`mode` → ยังถือเป็น Divider เพื่อความเข้ากันได้ (17 เทสต์เดิมผ่านครบ) แต่ถ้าส่งค่า mode ที่
ไม่รู้จักมา (`mode=bogus`) ระบบตอบ 400 พร้อมข้อความ "ไม่รู้จักโหมด" **ไม่เดาเป็น Divider**
ตามข้อกำหนด

**ผลลัพธ์หลังแก้:** รัน `.venv\Scripts\python.exe -m unittest discover -s tests -v` อีกครั้ง →
`Ran 17 tests ... OK` (ไม่เพิ่ม unittest ใหม่ตามใบงาน Lab 3)
