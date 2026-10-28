# Lab notes — PDF to section chunks, week 1

ชื่อ/รหัสนักเรียน: นนร.ธิติพัทธ์ โอภาสเอี่ยมขจร 2302

วันที่: 18/10/2026

OS / CPU: MacOS

Python version / interpreter path: 3.14.6

Ollama version: 0.40.4

Model / dimensions ที่ทดลองได้: all-minilm:22m, embeddinggemma-2:270m

| PDF | หน้า | ไม่มีข้อความที่ดึงได้ | bookmarks | วิธีตรวจ/แก้ boundary | sections | chunks | ข้อสังเกต |
|---|---:|---|---:|---|---:|---:|---|
| What is LLMOps | 62 | 3 หน้า (1, 7, 47) | 49 | planner รับ 42 / unresolved 7 → แก้ line anchor ทั้ง 7 ด้วยมือ (chapter heading 3 จุด, bookmark ชี้หน้าถัดไป 1 หน้า 4 จุด) | 50 | 108 | bookmark บางอันชี้ช้าไป 1 หน้า หัวข้อจริงอยู่ท้ายหน้าก่อนหน้า |
| Introduction to ML with Python | 392 | 5 หน้า (2, 144, 224, 318, 336) | 147 | รับ 146 / unresolved 1 → skip "Copyright" (ไม่มีบรรทัดหัวข้อในข้อความ) | 147 | 956 | bookmark เกือบทั้งหมดตรงกับหัวข้อจริง |
| ML Design Patterns | 408 | 6 หน้า (2, 10, 34, 94, 216, 398) | 197 | รับ 195 / unresolved 2 → skip "Cover", "Copyright" | 196 | 1,200 | Cover เป็นหน้ารูปภาพ ไม่มีข้อความให้ใช้เป็น anchor |
| AI at the Edge | 492 | 1 หน้า (1) | 274 | รับ 232 / unresolved 42 → ใช้ script ช่วยหาหัวข้อ ตรวจ font size ทั้ง 42 รายการ และแก้ "Cleaning Your Dataset" หน้า 387 ให้ชี้บรรทัดหัวข้อแทนบรรทัดโค้ด `};` | 275 | 1,417 | bookmark ใช้ "1. Title" แต่ในหน้าพิมพ์ว่า "Chapter 1. Title" ทำให้ match ไม่ได้ทั้ง 13 บท |
| AI and ML for Coders | 390 | 16 หน้า (1, 2, 14, 22, 24, 44, 108, 150, 214, 236, 238, 252, 286, 314, 350, 380) | 232 | unresolved 232/232 เพราะ bookmark ไม่มีหน้าปลายทาง (`pdf_page = -1`) → ไล่หาชื่อหัวข้อตามลำดับทั้งเล่ม เลือกเฉพาะบรรทัดที่ font ใหญ่กว่าเนื้อหา ได้ 231, skip "Copyright" 1 | 232 | 890 | ตรวจแล้วหน้าเรียงลำดับถูกต้อง "Summary" ทุกบทลงบทของตัวเอง |

ทุกเล่ม: `all_lines_assigned_once = true`, `coverage_complete = true`, max-chars 900 / overlap 100

## หลักฐานจาก PDF แรก

- หัวข้อที่ตรวจ: Autonomous Agents (ใน 1. LLM Applications → The Looming Transformation: Five Key Applications of LLMs)
- PDF page / line ID: bookmark ชี้ PDF page 15 แต่หัวข้อจริงอยู่ PDF page 14, line `p0014-l0020`
- เหตุผลที่แก้หรือ skip boundary (หากมี): ในหน้า 15 ไม่มีบรรทัดหัวข้อนี้ (บรรทัดแรกเป็นเนื้อหาต่อจากหน้าก่อน) จึงย้าย anchor ไปบรรทัดหัวข้อจริงในหน้า 14 ไม่ได้ skip boundary ใด
- all_lines_assigned_once: true
- coverage_complete: true (70,234 / 70,234 characters)
- ตัวอย่าง chunk ID / heading path / source_pages: `e84cd98ddda70c2ea73504ec` / 1. LLM Applications › The Looming Transformation: Five Key Applications of LLMs › Autonomous Agents / [14, 15]

## ผลทดลอง max-chars (overlap 100)

| PDF | chunks @ 900 | chunks @ 600 | เพิ่มขึ้น |
|---|---:|---:|---:|
| What is LLMOps | 108 | 165 | +53% |
| Introduction to ML with Python | 956 | 1,530 | +60% |
| ML Design Patterns | 1,200 | 1,914 | +60% |
| AI at the Edge | 1,417 | 2,244 | +58% |
| AI and ML for Coders | 890 | 1,410 | +58% |

## คำถามท้ายคาบ

1. Ollama, embedding model และ PDF parser ทำหน้าที่ต่างกันอย่างไร?

   ตอบ: ทั้งสามทำงานคนละขั้นกัน PDF parser (PyMuPDF) อ่านไฟล์ PDF แล้วดึงข้อความออกมาเป็นบรรทัด โดยเก็บเลขหน้า ตำแหน่ง (bbox) ขนาด font และ bookmarks ไว้ด้วย ซึ่งเป็นสิ่งที่ step 03–06 ใช้ทั้งหมดโดยไม่ต้องเรียก Ollama เลย Embedding model (เช่น all-minilm:22m, embeddinggemma) คือโมเดลที่รับข้อความเข้าไปแล้วแปลงออกมาเป็นเวกเตอร์ตัวเลขที่แทนความหมายของข้อความนั้น ทำให้นำข้อความมาเปรียบเทียบความใกล้เคียงกันได้ ส่วน Ollama คือโปรแกรมที่ดาวน์โหลดและรันโมเดลบนเครื่องของเราเอง และเปิด API ที่ localhost:11434 ให้ script ส่งข้อความไปขอ embedding ได้ (ใช้ใน 01_check_setup และ 02_embedding_demo) สรุปคือ parser เปลี่ยน PDF → ข้อความ, embedding model เปลี่ยน ข้อความ → เวกเตอร์, Ollama เป็นตัวรันโมเดลนั้น

2. ทำไม 0 characters จึงยังสรุปว่าเป็นหน้าเปล่าไม่ได้?

   ตอบ: ในหน้านั้นอาจเป็นหน้าที่ถูก Scan มาทําให้ไม่สามารถอ่านเป็น character ได้ ทําให้ในหน้านั้นมีเนื้อหาแค่ไม่ถูกอ่านโดยโค้ด python 

3. ทำไมหนึ่งหน้าไม่จำเป็นต้องเป็นหนึ่ง section/chunk?

   ตอบ: สามารถทําให้ chunk เป็นตัวอักษรยาวๆได้เช่น 1,000 ตัวอักษรคือ 1 chunk เพื่อให้เนื้อหามีความละเอียดมากกว่า 

4. เมื่อ bookmark ชี้ไม่ตรงหัวข้อ คุณแก้ page/line anchor อย่างไร?

   ตอบ: เปิด boundaries.json คู่กับ lines.txt แล้วดูรายการที่เป็น unresolved ก่อน จากนั้นไปดูหน้าที่ bookmark ชี้ใน lines.txt ถ้าไม่เจอหัวข้อก็ดูหน้าก่อนหน้าและหน้าถัดไป เลือกบรรทัดที่ข้อความตรงกับชื่อหัวข้อและมี font ใหญ่กว่าเนื้อหาปกติ (เนื้อหาเล่ม LLMOps ขนาด 14.4pt) เพื่อไม่ให้ไปเลือก running header หรือประโยคที่แค่อ้างชื่อหัวข้อ แล้วแก้ pdf_page และ line_id ให้ตรงกับบรรทัดนั้น เปลี่ยน status เป็น accepted และเขียน note อธิบาย ตัวอย่างเช่น "Autonomous Agents" ที่ bookmark ชี้หน้า 15 แต่หัวข้อจริงอยู่หน้า 14 บรรทัด p0014-l0020 จึงย้าย anchor ไปที่นั่น ส่วนรายการที่ไม่มีบรรทัดหัวข้อในข้อความเลย เช่น Cover หรือ Copyright จะใช้ status skip พร้อม note ข้อความของหน้านั้นไม่หายไป แต่จะไปรวมอยู่ใน section ก่อนหน้า เมื่อแก้ครบแล้วตั้ง reviewed เป็น true แล้วรัน 05_build_sections.py เพื่อเช็คว่าลำดับถูกและ all_lines_assigned_once เป็น true

5. เปลี่ยน max-chars จาก 900 เป็น 600 แล้วจำนวน chunks เปลี่ยนอย่างไร และ characters ต่างจาก tokens อย่างไร?

   ตอบ: จำนวน chunks เพิ่มขึ้นประมาณ 53–60% ทุกเล่ม เช่น What is LLMOps จาก 108 เป็น 165 และ AI at the Edge จาก 1,417 เป็น 2,244 (ดูตารางผลทดลองด้านบน) สาเหตุที่เพิ่มขึ้นประมาณ 1.6 เท่า ไม่ใช่ 1.5 เท่า (900/600) เพราะมี overlap 100 ตัวอักษร ทำให้แต่ละ chunk ขยับไปข้างหน้าได้จริงแค่ 800 ตัวอักษร (ตอน 900) กับ 500 ตัวอักษร (ตอน 600) ซึ่ง 800/500 = 1.6 แต่ section ที่สั้นกว่า 600 ตัวอักษรยังได้ 1 chunk เท่าเดิม และ script ตัด chunk ตรงขอบย่อหน้า/บรรทัด/คำ เล่ม LLMOps ที่มี section สั้นจำนวนมากจึงเพิ่มขึ้นน้อยที่สุด (53%) ส่วน characters คือจำนวนตัวอักษร (Unicode code points) ที่ script นับเอง ขณะที่ tokens คือหน่วยที่ tokenizer ของโมเดลแบ่งข้อความ ซึ่งอาจเป็นทั้งคำ ส่วนของคำ หรือเครื่องหมาย จำนวน token ต่อตัวอักษรจึงต่างกันไปตามภาษาและ tokenizer (ภาษาอังกฤษโดยประมาณ 1 token ≈ 3–4 ตัวอักษร ภาษาไทยมักใช้ token มากกว่า) โมเดลจำกัดความยาว input เป็น tokens ไม่ใช่ characters ดังนั้น max-chars 900 จึงไม่ได้รับประกันว่าจะไม่เกิน token limit ของโมเดล ใน chunks-report.json ก็เขียนไว้ว่า "Character limits are not model token limits"
