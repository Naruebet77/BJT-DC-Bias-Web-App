# Design Note — BJT DC Bias Web App

ENG29 2121 · Lab 02 · Voltage-Divider Bias

## เหตุผลการออกแบบ

1. **แยกสมการออกจาก Flask** (`dc_bias.py` ไม่รู้จัก HTML/HTTP) ตามที่เอกสาร Lab §04 กำหนดไว้ ช่วยให้ทดสอบสมการวิศวกรรมได้เองโดยไม่ต้องรันเว็บเซิร์ฟเวอร์
2. **อินพุตตัวต้านทานเป็น Ω** ตามตาราง §06 ของเอกสาร แล้วแสดงค่าเทียบเป็น kΩ กำกับในผลลัพธ์ เพื่อให้เห็นการแปลงหน่วยอย่างชัดเจน
3. **ไม่ clamp ค่าใน Saturation** — รายงานผลจากสมการ Forward-Active ตรง ๆ แล้วเตือนว่าแบบจำลองใช้ไม่ได้ ตัวเลขติดลบคือหลักฐานว่าออกนอกสมมติฐาน ไม่ใช่ข้อผิดพลาดของโปรแกรม
4. **แสดงป้าย region เสมอ** (Active / Cutoff / Saturation) ให้เห็นหลักฐานของการตรวจสอบเขตการทำงาน ตามเกณฑ์ตรวจรับ A5
5. **ไม่มี JavaScript framework** — ใช้ฟอร์ม HTML ส่งไป Flask แบบเดิมตามที่ใบแล็บกำหนด

## โครงสร้างไฟล์

| ไฟล์ | ความรับผิดชอบ |
|---|---|
| `dc_bias.py` | สมการวิศวกรรมล้วน, validation, region classification |
| `app.py` | รับค่าจากฟอร์ม, เรียก `dc_bias.py`, แปลงหน่วยแสดงผล, render template |
| `templates/index.html` | ฟอร์ม 7 ช่อง, ตารางผล, ป้าย region, error/warning block |
| `static/style.css` | การจัดหน้าและการตอบสนองต่อขนาดจอ |
| `tests/test_dc_bias.py` | เทสต์สมการ, region, validation |
| `tests/test_web.py` | เทสต์ HTTP ผ่าน Flask test client |

## ข้อจำกัดที่ยอมรับ

- β และ VBE คงที่ ตามสมมติฐาน Forward-Approximation ที่ใบแล็บกำหนดให้ทำใน Lab 2
- ไม่รองรับ Bias type อื่น, AC analysis, หรือ SPICE
- รันได้เฉพาะเครื่องพัฒนาผ่าน `http://127.0.0.1:5000/` เท่านั้น
