# Official sources and version notes

ตรวจเอกสารประกอบชุดสอนวันที่ **17 ตุลาคม 2026** ลิงก์ด้านล่างเป็นเอกสารผู้พัฒนาและ model card ของผู้เผยแพร่ ขนาดดาวน์โหลด ตัวติดตั้ง และ tag เปลี่ยนได้ ให้ครูตรวจล่วงหน้าก่อนใช้ซ้ำในคาบอื่น

## Ollama installation and API

| Source | ใช้ยืนยันเรื่องใดใน lab |
|---|---|
| [Ollama download](https://ollama.com/download) | จุดเริ่มดาวน์โหลดสำหรับ macOS, Windows และ Linux |
| [Ollama macOS](https://docs.ollama.com/macos) | macOS 14 ขึ้นไป; Apple silicon/Intel; ติดตั้ง DMG ลง Applications และ CLI ใน PATH |
| [Ollama Windows](https://docs.ollama.com/windows) | Windows 10 22H2 ขึ้นไป; native Windows; installer ต่อบัญชีผู้ใช้; server เบื้องหลังและ localhost:11434 |
| [Ollama Linux](https://docs.ollama.com/linux) | official install script, manual archive, systemd และ `ollama serve` |
| [Ollama embeddings](https://docs.ollama.com/capabilities/embeddings) | บทบาท embedding models และการสร้างเวกเตอร์ผ่าน API |
| [Ollama API: embed](https://docs.ollama.com/api/embed) | POST `/api/embed`, `model`, `input`, `embeddings`, การ truncate และผลลัพธ์ |

Linux official installation ใช้สิทธิ์ติดตั้งระบบ เอกสารที่ตรวจไม่ให้ workflow แบบ user-only ที่รับรองไว้ หากเครื่องเรียนไม่มี sudo ควรให้ผู้ดูแลเตรียมเครื่องก่อน นักเรียน Mac/Windows ไม่ต้องเปิด Docker หรือ WSL สำหรับเส้นทาง native ของ lab นี้

Ollama app และ `ollama serve` ต่างเป็นทางเปิด server หาก server ทำงานอยู่แล้ว ให้ใช้ตัวเดิม ปัญหา port in use จึงไม่แก้ด้วยการเปิด server ซ้ำหลายชุด

## Three embedding model options

| Model / official source | ข้อมูลที่ใช้ใน lab | ข้อจำกัดหรือ caveat |
|---|---|---|
| [Ollama all-minilm:22m](https://ollama.com/library/all-minilm:22m) และ [Sentence Transformers model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | คำสั่ง `ollama pull all-minilm:22m`; 46 MB; เวกเตอร์ 384 มิติ; แปลงประโยค/ย่อหน้าสั้นเพื่อ semantic similarity และ retrieval | ต้นทางเน้นภาษาอังกฤษ; Ollama ระบุ 512 context ขณะที่ Sentence Transformers model card ระบุ default truncation ที่ 256 word pieces ใน runtime นั้น จึงไม่ใช้สองตัวเลขนี้แทนกัน; ขนาดดาวน์โหลดไม่เท่ากับ RAM ที่ใช้จริง |
| [Ollama nomic-embed-text](https://ollama.com/library/nomic-embed-text) และ [Nomic AI model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) | `nomic-embed-text:v1.5`; 274 MB; เวกเตอร์พื้นฐาน 768 มิติ; โมเดลจาก Nomic AI | ภาษาอังกฤษเป็นหลัก; model card กำหนด task prefix `search_document:` และ `search_query:` สำหรับ retrieval; tag ของ Ollama ระบุ context 2K แม้ต้นทางมีวิธีตั้งค่าขยายถึง 8192 |
| [Ollama EmbeddingGemma 2 tags](https://ollama.com/library/embeddinggemma-2/tags) และ [270m details](https://ollama.com/library/embeddinggemma-2:270m) | Google DeepMind; text backbone ราว 270M ของตระกูล EmbeddingGemma 2; native output 768 มิติ; multilingual และ code | tag `270m` แสดงขนาด 304–378 MB ขึ้นกับ backend ณ วันที่ตรวจ; explicit `270m-q8_0-text` 304 MB; บาง variant ระบุ MLX จึงต้องตรวจ runtime/เครื่องก่อนเลือก; รุ่น text-only ไม่ได้เปิดทุก modality ของรุ่นเต็ม |

all-MiniLM ต้นทางเผยแพร่โดย Sentence Transformers และพัฒนาในโครงการชุมชนที่ Hugging Face จัด โดย fine-tune จาก MiniLM คำว่า Ollama ในคำสั่งหมายถึงเครื่องมือดาวน์โหลด/ให้บริการโมเดล ไม่ใช่องค์กรผู้ฝึก all-MiniLM

คลาสเลือกโหลดเพียง **all-minilm:22m** เพื่อทดลองเวกเตอร์จากข้อความสั้น นักเรียนไม่จำเป็นต้องโหลดอีกสองโมเดล โครงสร้าง section/chunk เกิดจากข้อมูล PDF และการตรวจของคน; สัปดาห์นี้ยังไม่สร้าง embeddings จาก chunks ทั้งคลัง

มิติและพื้นที่เก็บต่างกันไม่ได้แทนผลประเมินคุณภาพ retrieval ไม่มีการรับประกันว่าเครื่องที่มี RAM เท่ากันจะใช้เวลาเท่ากัน หรือการใช้โมเดลที่ใหญ่ขึ้นจะทำให้ผลภาษาไทยแม่นยำขึ้นเสมอ

## VS Code and Python

| Source | ใช้ยืนยันเรื่องใด |
|---|---|
| [VS Code download](https://code.visualstudio.com/download) | จุดเริ่มเลือก installer ตาม OS และ architecture |
| [VS Code on macOS](https://code.visualstudio.com/docs/setup/mac) | DMG/Applications และ `Shell Command: Install 'code' command in PATH` |
| [VS Code on Windows](https://code.visualstudio.com/docs/setup/windows) | User Installer, PATH และเปิด terminal ใหม่ |
| [VS Code on Linux](https://code.visualstudio.com/docs/setup/linux) | Ubuntu `.deb` และ Snap อย่างเป็นทางการ |
| [VS Code terminal basics](https://code.visualstudio.com/docs/terminal/basics) | เปิด integrated terminal และ terminal profile |
| [VS Code Python environments](https://code.visualstudio.com/docs/python/environments) | เลือก `.venv` ผ่าน `Python: Select Interpreter` |
| [Python downloads](https://www.python.org/downloads/) | เวอร์ชันและสถานะการดูแลปัจจุบัน |
| [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/) | ตัวติดตั้งสำหรับเครื่องใหม่; อยู่ในช่วงเวอร์ชันที่ใช้ใน lab |
| [Python on Windows](https://docs.python.org/3.12/using/windows.html) | launcher, installer PATH และการเรียก interpreter |
| [Python venv](https://docs.python.org/3.12/library/venv.html) | สร้าง venv; activation ต่าง shell; เรียก interpreter ตรงได้โดยไม่ต้อง activate |
| [Ubuntu Python setup](https://ubuntu.com/developers/docs/howto/python-setup/) | ใช้ Python distro, `python3-full`, pip และแยก dependency ด้วย virtual environments |

ชุดสอนรองรับ Python **3.10–3.14** และแนะนำ **3.12–3.14** เครื่อง Ubuntu 22.04 ที่มี Python 3.10 จาก distro ใช้ทำ lab นี้ได้ เครื่องที่มีเวอร์ชันในช่วงรองรับอยู่แล้วไม่ต้องอัปเกรดเพียงเพื่อให้หมายเลขเหมือนเพื่อน สำหรับติดตั้งใหม่บน Mac/Windows เลือก 3.14.8 ที่มี binary installer แทนการย้อนติดตั้ง 3.12.10 เพียงเพื่อเหมือนเครื่องครู ทั้งนี้ปุ่มดาวน์โหลด latest อาจชี้ 3.15 ซึ่งเพิ่งออกเมื่อ 9 ตุลาคม 2026 จึงควรเลือกเวอร์ชันตามแผนห้องเรียนให้ชัด บน Windows ใช้ `py -3.14 -m venv .venv` หรือระบุเวอร์ชันที่ติดตั้งจริง แทนการใช้ `py` แบบไม่ระบุเวอร์ชันซึ่งอาจเลือก 3.15

Python docs ยืนยันว่าการ activate เป็นตัวช่วยเปลี่ยน PATH ไม่ใช่เงื่อนไขบังคับในการใช้ environment กรณี PowerShell ปิดกั้น Activate.ps1 จึงเรียก `.venv\Scripts\python.exe` ตรงได้ โดยไม่ต้องเปลี่ยน execution policy ทุกเครื่อง

## PDF extraction, bookmarks, and provenance

| Source | ใช้ยืนยันเรื่องใด |
|---|---|
| [PyMuPDF installation](https://pymupdf.readthedocs.io/en/latest/installation.html) | ติดตั้ง `pymupdf`; official wheels และ Python Stable ABI; ข้อควรระวังแพ็กเกจคนละตัวชื่อ `fitz` |
| [PyMuPDF text extraction](https://pymupdf.readthedocs.io/en/latest/recipes-text.html) | ข้อความบนหน้ากับ reading order; text blocks, แบบอักษร และ sort |
| [PyMuPDF Page API](https://pymupdf.readthedocs.io/en/latest/page.html) | `get_text`, dict/spans/bbox, font information, page labels และ image metadata |
| [PyMuPDF Document API](https://pymupdf.readthedocs.io/en/latest/document.html) | `get_toc(simple=False)` และข้อมูลปลายทางของ bookmarks |
| [pypdf: extracting text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | เหตุที่ reading order, ตาราง และเอกสารสแกนไม่อาจตีความเป็นข้อความสะอาดได้เสมอ |

PyMuPDF docs ระบุว่าลำดับการอ่านอาจต่างจากที่มองเห็น การใช้ `sort=True` เป็นการเรียงจากตำแหน่ง ไม่ใช่หลักประกันการแปล layout หลายคอลัมน์อย่างถูกความหมาย เลือกเอกสารคอลัมน์เดียวที่มี text layer เป็นงานหลักของคาบนี้

`get_toc()` คืน bookmarks ไม่ใช่การอ่านสารบัญที่พิมพ์บนหน้าด้วย OCR ปลายทางจึงต้องตรวจร่วมกับข้อความและ PDF จริง ไม่ถือว่าทุกรายการเป็นหัวข้อที่ปรากฏตรงหน้าเป้าหมาย และไม่ถือว่าการค้นชื่อไม่เจอเป็นข้อความสูญหายโดยอัตโนมัติ หากเป็นชื่อบทหรือหัวข้อจริงที่ชี้ผิดไปท้ายบทก่อนหน้า ต้องแก้ anchor ให้ตรงตำแหน่งหัวข้อจริง ไม่ข้ามชื่อบทนั้นเพียงเพราะค้นบนหน้าเป้าหมายไม่เจอ สถานะ `skip` ของชุดสอนใช้กับ bookmark สำหรับนำทางที่ไม่ใช่หัวข้อจริงหรือรายการซ้ำเท่านั้น

หน้าไม่มี extractable text ต้องตรวจด้วยตาก่อน อาจเป็นหน้าว่าง ภาพประกอบ ภาพสแกน หรือข้อความที่ดึงออกมาไม่ได้ lab จึงใช้สถานะ `no_extractable_text_review` และเก็บหลักฐานไว้ แทนการตัดสินจากจำนวน characters หรือ images เพียงอย่างเดียว

## What is specific to this workshop

กติกา `boundaries.json`, สถานะ accepted/unresolved/skip, `reviewed: true`, SHA directory, การเก็บ source line IDs, การตรวจ line coverage และหน้าต่าง 900 characters/overlap 100 เป็นการออกแบบของ starter scripts ในชุดนี้ ไม่ใช่มาตรฐานบังคับของ PyMuPDF หรือ Ollama

การตรวจ coverage ของสคริปต์รับรองเฉพาะว่าข้อความที่ extraction ดึงออกมาได้ถูกส่งต่อครบตามกติกา ไม่ยืนยันว่าข้อความทุกอย่างใน PDF ถูกดึงออกมาแล้ว หรือทุก heading เป็นความหมายที่ถูกต้อง การตรวจเทียบต้นฉบับของนักเรียนยังเป็นส่วนหนึ่งของผลงาน

โค้ดใช้ character budget เพื่อสอนการแบ่ง chunk โดยไม่เพิ่ม tokenizer dependency; characters ไม่เท่ากับ tokens เมื่อต่อยอดสัปดาห์หน้า ให้ใช้ tokenizer/runtime ของโมเดลจริงและไม่ปล่อยให้ truncate ข้อมูลเงียบ ๆ
