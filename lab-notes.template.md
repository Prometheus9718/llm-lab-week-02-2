# Lab notes — PDF to section chunks, week 1

ชื่อ/รหัสนักเรียน: นนร.ธิติพัทธ์ โอภาสเอี่ยมขจร 2302

วันที่: 18/10/2026

OS / CPU: MacOS

Python version / interpreter path: 3.14.6

Ollama version: 0.40.4

Model / dimensions ที่ทดลองได้: all-minilm:22m, embeddinggemma-2:270m

| PDF | หน้า | ไม่มีข้อความที่ดึงได้ | bookmarks | วิธีตรวจ/แก้ boundary | sections | chunks | ข้อสังเกต |
|---|---:|---|---:|---|---:|---:|---|
| pdf1.pdf | ... | ... | ... | ... | ... | ... | ... |
| pdf2.pdf | ... | ... | ... | ... | ... | ... | ... |
| pdf3.pdf | ... | ... | ... | ... | ... | ... | ... |

## หลักฐานจาก PDF แรก

- หัวข้อที่ตรวจ: ...
- PDF page / line ID: ...
- เหตุผลที่แก้หรือ skip boundary (หากมี): ...
- all_lines_assigned_once: ...
- coverage_complete: ...
- ตัวอย่าง chunk ID / heading path / source_pages: ...

## คำถามท้ายคาบ

1. Ollama, embedding model และ PDF parser ทำหน้าที่ต่างกันอย่างไร?

   ตอบ: ...

2. ทำไม 0 characters จึงยังสรุปว่าเป็นหน้าเปล่าไม่ได้?

   ตอบ: ในหน้านั้นอาจเป็นหน้าที่ถูก Scan มาทําให้ไม่สามารถอ่านเป็น character ได้ ทําให้ในหน้านั้นมีเนื้อหาแค่ไม่ถูกอ่านโดยโค้ด python 

3. ทำไมหนึ่งหน้าไม่จำเป็นต้องเป็นหนึ่ง section/chunk?

   ตอบ: สามารถทําให้ chunk เป็นตัวอักษรยาวๆได้เช่น 1,000 ตัวอักษรคือ 1 chunk เพื่อให้เนื้อหามีความละเอียดมากกว่า 

4. เมื่อ bookmark ชี้ไม่ตรงหัวข้อ คุณแก้ page/line anchor อย่างไร?

   ตอบ: ...

5. เปลี่ยน max-chars จาก 900 เป็น 600 แล้วจำนวน chunks เปลี่ยนอย่างไร และ characters ต่างจาก tokens อย่างไร?

   ตอบ: ...
