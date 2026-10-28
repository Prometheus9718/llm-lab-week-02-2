# Lab สัปดาห์ที่ 1: จาก PDF ไปเป็น section chunks ด้วยเครื่องของเราเอง

คู่มือนักเรียน • macOS / Windows / Ubuntu • ตรวจเอกสารติดตั้งวันที่ 17 ตุลาคม 2026

ทุกคนเปิดแอป พิมพ์คำสั่ง และรัน Python บนเครื่องของตนเอง ครูสาธิต PDF แรกพร้อมกัน จากนั้นนักเรียนทำ PDF อีกสองไฟล์ด้วยตนเอง ไฟล์โค้ดทั้งหมดแยกอยู่ใน `scripts/` และเปิดอ่านได้ก่อนรัน

สิ่งที่จะทำได้เมื่อจบคาบ:

- ติดตั้ง Ollama และทดลองเปลี่ยนประโยคสั้นเป็นเวกเตอร์ด้วยโมเดลขนาดเล็ก
- ใช้ VS Code และ Terminal สร้างโปรเจกต์และ Python virtual environment
- อ่าน PDF แสดงจำนวนหน้าและจำนวน characters ของแต่ละหน้า
- เก็บข้อความพร้อมเลขหน้า ตำแหน่งบรรทัด และสารบัญที่ฝังใน PDF
- ตรวจและแก้ขอบเขตหัวข้อ แล้วสร้าง sections และ chunks ที่อ้างอิงกลับไปยังหน้า/บรรทัดได้
- ทำขั้นตอนเดิมกับ PDF ที่สองและสาม โดยเปลี่ยนเฉพาะค่า `--pdf`

สัปดาห์นี้จบที่ไฟล์ `chunks.jsonl` ยังไม่มีขั้นฝังเวกเตอร์ของ PDF ทั้งเล่ม สร้าง vector database หรือถามตอบหนังสือ โมเดล embedding ใช้เป็นการทดลองสั้น ๆ ให้เห็นบทบาทของโมเดลก่อน ส่วนการอ่านข้อความและแยกหัวข้อใช้โค้ดอ่าน PDF และการตรวจของผู้เรียน

## 0. ทำความเข้าใจก่อนเริ่ม

```text
ทดลองโมเดล: ประโยคสั้น → Ollama + all-minilm → เวกเตอร์ตัวเลข

งาน PDF: PDF → ข้อความ/บรรทัด/เลขหน้า → เสนอหัวข้อ → นักเรียนตรวจหัวข้อ
        → sections ตามหัวข้อ → chunks ภายในแต่ละ section → จบคาบ
```

| คำ | ความหมายใน lab นี้ |
|---|---|
| Terminal | หน้าต่างพิมพ์คำสั่ง เช่น Terminal ใน VS Code, Ghostty หรือ PowerShell |
| Shell | โปรแกรมที่อ่านคำสั่ง: macOS ใช้ zsh, Ubuntu ใช้ bash, Windows ใช้ PowerShell |
| Project root | โฟลเดอร์หลัก `llm-lab` ที่มี `scripts`, `data`, `requirements.txt` |
| Python environment | `.venv` เก็บ Python environment และ libraries ของโปรเจกต์นี้ |
| Ollama | โปรแกรมรันโมเดลในเครื่องและเปิด API ให้ Python เรียก |
| Embedding model | แปลงข้อความเป็นเวกเตอร์ตัวเลขเพื่อเปรียบเทียบความหมาย |
| PDF parser | อ่านข้อมูลที่อยู่ใน PDF เช่น text layer, font, ตำแหน่งข้อความ |
| OCR | รู้จำตัวอักษรจากภาพ ใช้เมื่อข้อความอยู่ในภาพสแกน/ภาพถ่าย |
| Section | ส่วนของเอกสารที่อิงหัวข้อและลำดับหัวข้อ |
| Chunk | ชิ้นข้อความขนาดจำกัดภายใน section เพื่อเตรียมนำไปค้นหาในอนาคต |
| JSON / JSONL | JSON เก็บโครงสร้างข้อมูล; JSONL เก็บหนึ่ง JSON record ต่อหนึ่งบรรทัด |

**การเลือก PDF:** เตรียม 3 ไฟล์ ไฟล์แรกควรเป็น PDF ที่เลือกคัดลอกข้อความได้ มีอย่างน้อย 2 หัวข้อ และเป็นหน้าแบบคอลัมน์เดียวประมาณ 5–30 หน้า เพื่อให้ตรวจผลได้ทันในคาบ ไฟล์ที่สอง/สามเลือกต่างรูปแบบได้ หากเป็นภาพสแกนล้วน ให้บันทึกผลว่าไม่พบ text layer แล้วเปลี่ยนเป็นไฟล์มีข้อความสำหรับทำ section chunks ในคาบนี้ เราจะเรียน OCR แยกภายหลัง

ใช้คอมพิวเตอร์ที่เปิด VS Code และ Python ได้ พร้อมพื้นที่ว่างสำหรับตัวติดตั้ง libraries และ PDF ขนาดโมเดล 46 MB เป็นขนาดไฟล์ดาวน์โหลด การใช้ RAM จริงยังขึ้นกับ runtime และงานที่รัน เครื่องไม่มี GPU ใช้ทำแบบฝึกหัดนี้ได้ โดยความเร็วขึ้นกับเครื่อง

**วิธีอ่านคำสั่ง:** คัดลอกเฉพาะข้อความในกรอบ code ไม่คัดลอก `❯`, `$`, `PS>` หรือเครื่องหมายกรอบ ``` รันทีละคำสั่งแล้วรอให้ prompt กลับมา คำสั่งของ Windows กับ macOS/Ubuntu เลือกทำเฉพาะส่วนของ OS ตนเอง หลัง activate environment แล้ว คำสั่ง `python scripts/...` ใช้รูปแบบเดียวกันได้

## 1. ตรวจว่าตนเองใช้ OS และ CPU แบบใด

### macOS

1. คลิกโลโก้ Apple มุมซ้ายบน → **About This Mac**
2. ดูเวอร์ชัน macOS และช่อง Chip/Processor
3. ถ้าขึ้น Apple M1/M2/M3/M4/... ให้เลือกตัวติดตั้ง Apple silicon หรือ Universal; ถ้าขึ้น Intel ให้เลือก Intel หรือ Universal
4. Ollama สำหรับ Mac ต้อง macOS 14 Sonoma ขึ้นไป ตาม [คู่มือ Ollama macOS](https://docs.ollama.com/macos)
5. เปิด Terminal โดยกด `Command + Space` พิมพ์ `Terminal` แล้ว Enter หรือใช้ Ghostty ที่ติดตั้งอยู่แล้ว

### Windows

1. กด `Windows + I` → **System → About**
2. ดู Windows version และ System type โดยเครื่องส่วนใหญ่ในคลาสจะเป็น x64
3. Ollama ระบุ Windows 10 22H2 หรือใหม่กว่า ตาม [คู่มือ Ollama Windows](https://docs.ollama.com/windows)
4. ถ้าเครื่องเป็น Windows ARM หรือระบบเก่ากว่านี้ ให้ครูตรวจตัวติดตั้งและ platform ที่รองรับก่อน
5. เปิด Start พิมพ์ `PowerShell` แล้วเปิดแบบปกติสำหรับทำงานในโปรเจกต์

### Ubuntu

1. เปิด **Settings → About** ดู Ubuntu version
2. เปิด Terminal ด้วย `Ctrl + Alt + T`
3. ดูสถาปัตยกรรมเครื่อง:

   ```bash
   uname -m
   ```

   `x86_64` คือ Intel/AMD 64-bit; `aarch64` คือ ARM64
4. คำสั่งติดตั้งแพ็กเกจระบบด้านล่างต้องใช้สิทธิ์ `sudo` หากเป็นเครื่องของโรงเรียนที่ไม่มีสิทธิ์นี้ ให้ครู/ผู้ดูแลเตรียมโปรแกรมให้ก่อน

## 2. ดาวน์โหลดและติดตั้ง Ollama

เปิดเบราว์เซอร์ ไปที่ [https://ollama.com/download](https://ollama.com/download) แล้วเลือก OS จริงของเครื่อง

### macOS: ใช้ตัวติดตั้งแบบแอป

1. เลือก **macOS** และดาวน์โหลดแบบ manual สำหรับ Mac
2. เปิดไฟล์ `.dmg` ที่ดาวน์โหลดเสร็จ
3. ลาก **Ollama** เข้า **Applications**
4. เปิด **Finder → Applications → Ollama**
5. ถ้ามีคำถามเรื่องเปิดแอปที่ดาวน์โหลดมา ให้ยืนยันเปิดแอปจากแหล่งทางการ หากแอปขอสร้าง CLI link ให้ทำตามหน้าต่างแจ้ง
6. ปิด Terminal เดิมแล้วเปิดใหม่ เพื่อให้เห็นคำสั่งที่เพิ่งติดตั้ง
7. พิมพ์:

   ```bash
   ollama --version
   ```

8. ควรเห็น `ollama version is ...` เลขเวอร์ชันอาจต่างจากของครู เปิด Ollama ค้างไว้เบื้องหลังระหว่างทำ lab

ขั้นตอนลากแอปและ CLI link อ้างอิง [Ollama macOS](https://docs.ollama.com/macos)

### Windows: ใช้ตัวติดตั้ง Windows

1. เลือก **Windows** จากหน้า download
2. เปิดไฟล์ `OllamaSetup.exe`
3. ทำตามตัวติดตั้งสำหรับบัญชีผู้ใช้ของตนเอง
4. เมื่อเสร็จ เปิด Start → ค้นหา **Ollama** → เปิดแอป
5. ปิด PowerShell/Terminal เดิม แล้วเปิดใหม่
6. พิมพ์:

   ```powershell
   ollama --version
   ```

7. ควรเห็นเลขเวอร์ชัน แอป Ollama จะทำงานเบื้องหลัง ไม่ต้องเปิดหน้าต่างแชตเพื่อใช้ embedding API

รายละเอียดจาก [Ollama Windows](https://docs.ollama.com/windows)

### Ubuntu: ติดตั้งผ่าน Terminal

1. ติดตั้งเครื่องมือที่ installer ใช้:

   ```bash
   sudo apt update
   sudo apt install curl zstd
   ```

2. เรียก installer จากเว็บทางการ:

   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. ตรวจเวอร์ชัน:

   ```bash
   ollama --version
   ```

4. ตรวจ service:

   ```bash
   systemctl status ollama --no-pager
   ```

5. ถ้ายังไม่ active ให้เริ่ม service:

   ```bash
   sudo systemctl start ollama
   ```

6. ถ้าเครื่องไม่ได้ใช้ systemd ให้ดู [Ollama Linux](https://docs.ollama.com/linux) และเปิด Terminal แยกเพื่อรัน `ollama serve` ค้างไว้ อีก Terminal ใช้ทำ lab ต่อ หาก server ทำงานแล้วไม่ต้องรัน `serve` ซ้ำ

**Checkpoint:** ทุกคนเรียก `ollama --version` ได้ และมี Ollama server ทำงานอยู่หนึ่งตัว

## 3. รู้จักโมเดล 3 ตัว แล้วดาวน์โหลดตัวเล็กที่สุด

ทั้งสามตัวนี้เป็น **embedding model** มีหน้าที่เปลี่ยนข้อความเป็นตัวเลข ไม่ใช่โมเดลแชตสำหรับตอบคำถามและไม่ใช่ OCR ที่อ่านข้อความจากภาพ

| ตัวเลือก | มาจากไหน / ใช้ทำอะไร | ดาวน์โหลดโดยประมาณ | มิติของเวกเตอร์ |
|---|---|---:|---:|
| **`all-minilm:22m`** — ใช้ร่วมกันในคลาส | Sentence Transformers รุ่น all-MiniLM-L6-v2 พัฒนาต่อจาก MiniLM; ใช้เปรียบเทียบประโยคสั้น เน้นอังกฤษ | **46 MB** | 384 |
| `nomic-embed-text:v1.5` | Nomic AI; embedding สำหรับ retrieval ข้อความ ใช้ task prefixes เมื่อนำไปค้นเอกสาร | 274 MB | 768 |
| `embeddinggemma-2:270m-q8_0-text` | Google DeepMind; ส่วนข้อความของ EmbeddingGemma 2 รองรับข้อความ/โค้ดหลายภาษา | 304 MB สำหรับ tag นี้; `:270m` อาจต่างตาม backend | 768 |

ตรวจรุ่น/ขนาดจาก [Ollama all-minilm](https://ollama.com/library/all-minilm/tags), [Nomic](https://ollama.com/library/nomic-embed-text), [EmbeddingGemma 2 tags](https://ollama.com/library/embeddinggemma-2/tags) และที่มาจาก [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), [Nomic model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) ขนาดเป็นไฟล์โมเดล ไม่รวมแอปและ RAM ขณะรัน

เลือก `all-minilm:22m` เพื่อให้ดาวน์โหลดน้อยและทดลองประโยคอังกฤษสั้นเหมือนกันทั้งคลาส ความเล็กเหมาะกับการเรียนบทบาท embedding ส่วนคุณภาพภาษาไทย/งานจริงต้องประเมินกับข้อมูลจริงภายหลัง ขนาด context ของ runtime กับ model card อาจต่างกัน จึงใช้ประโยคสั้นใน demo และยังไม่ฝังเวกเตอร์ของ chunks ที่สร้างทั้งชุด

รันใน Terminal ของ OS ใดก็ได้:

```text
ollama pull all-minilm:22m
```

รอจนเห็น `success` แล้วรัน:

```text
ollama list
```

ควรมี `all-minilm:22m` ในรายการ ไม่ต้องดาวน์โหลดอีกสองรุ่นเพื่อจบ lab หากเน็ตหลุดให้รัน `pull` คำสั่งเดิมเมื่อเน็ตพร้อม ไม่ต้องลบโฟลเดอร์โมเดล ถ้าหน้าจอยังดาวน์โหลดอยู่ ให้รอ ไม่กด `Control + C` เว้นแต่ต้องการยกเลิกจริง ๆ

## 4. ติดตั้ง VS Code และ Python

### 4.1 VS Code

1. เปิด [https://code.visualstudio.com/download](https://code.visualstudio.com/download)
2. macOS: เลือกตาม Apple silicon/Intel/Universal เปิดตัวติดตั้งแล้วนำ Visual Studio Code เข้า Applications
3. Windows: เลือก **User Installer x64** สำหรับเครื่อง x64 ติดตั้งตามหน้าต่าง เลือก Add to PATH หากมีตัวเลือก แล้วเปิด Terminal ใหม่
4. Ubuntu: ดาวน์โหลด `.deb` ตาม CPU เปิดด้วย Software Install หรือเปิด Terminal ใน Downloads แล้วติดตั้งไฟล์ `.deb` ที่ดาวน์โหลดด้วย `sudo apt install ./ชื่อไฟล์จริง.deb`
5. เปิดแอป **Visual Studio Code**
6. เปิดแท็บ **Extensions** ด้านซ้าย ค้นหา **Python** เลือกผู้เผยแพร่ **Microsoft** แล้วกด Install

คู่มือแยก OS: [Mac](https://code.visualstudio.com/docs/setup/mac), [Windows](https://code.visualstudio.com/docs/setup/windows), [Linux](https://code.visualstudio.com/docs/setup/linux)

### 4.2 Python

ใช้ Python ปกติแบบ 64-bit ในช่วง 3.10–3.14 ที่มี wheel ของ PyMuPDF โดยแนะนำ 3.12–3.14 ในคลาส ไม่เลือก free-threaded/experimental build สำหรับแบบฝึกหัดนี้ [PyMuPDF ระบุ platform และเวอร์ชัน Python ที่รองรับ](https://pymupdf.readthedocs.io/en/latest/installation.html)

**macOS ติดตั้งใหม่**

1. เปิด [Python 3.14.8 release page](https://www.python.org/downloads/release/python-3148/)
2. เลื่อนหัวข้อ Files → เลือก **macOS installer** ไม่เลือก source archive
3. เปิด `.pkg` แล้วทำตาม installer
4. ปิด Terminal เดิม เปิดใหม่ แล้วรัน `python3 --version`
5. ถ้ามี 3.12/3.13/3.14 อยู่แล้วใช้ต่อได้ ถ้ามี Python หลายตัว จดว่าคำสั่ง `python3` เรียกตัวใด

**Windows ติดตั้งใหม่**

1. เปิด [Python 3.14.8 release page](https://www.python.org/downloads/release/python-3148/)
2. หัวข้อ Files เลือก **Windows installer (64-bit)** สำหรับเครื่อง x64 คู่มือนี้ใช้ traditional installer เพื่อให้หน้าจอในคลาสเหมือนกัน
3. เปิดตัวติดตั้ง เลือก **Add python.exe to PATH** แล้ว Install Now
4. ปิด PowerShell เดิม เปิดใหม่ แล้วรัน:

   ```powershell
   py -3.14 --version
   ```

5. หากมี 3.12 หรือ 3.13 อยู่แล้วใช้ได้ ให้ใช้เลขเวอร์ชันที่ติดตั้งจริงตอนสร้าง `.venv` เช่น `py -3.12 -m venv .venv`
6. หากใช้ Python install manager อยู่แล้ว ให้ติดตั้งเวอร์ชัน 3.14 ด้วย `py install 3.14` และตรวจว่าคำสั่งเวอร์ชันข้างต้นทำงานได้

**Ubuntu**

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
python3 --version
```

ใช้ Python ของ Ubuntu ตามปกติ Ubuntu 24.04 มักเป็น 3.12 และ 22.04 เป็น 3.10 ซึ่งใช้สคริปต์นี้ได้ ไม่ต้องเปลี่ยน symlink ของ `/usr/bin/python3` [Ubuntu Python setup](https://ubuntu.com/developers/docs/howto/python-setup/)

## 5. สร้าง project root ของตัวเอง

เปิด Terminal ของ OS ก่อนเพื่อสร้างโฟลเดอร์ จากนั้นเปิดโฟลเดอร์นั้นใน VS Code ชื่อโปรเจกต์คือ `llm-lab` ทุกคนใช้โค้ดเดียวกันได้โดยชื่อผู้ใช้ต่างกัน

**macOS / Ubuntu**

```bash
mkdir -p "$HOME/Documents/llm-lab"
cd "$HOME/Documents/llm-lab"
pwd
```

ตัวอย่าง Mac อาจได้ `/Users/alice/Documents/llm-lab` ส่วน Ubuntu อาจได้ `/home/alice/Documents/llm-lab` หากเครื่องไม่มี Documents คำสั่งนี้จะสร้างให้

**Windows PowerShell**

```powershell
$labRoot = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "llm-lab"
New-Item -ItemType Directory -Force -Path $labRoot
Set-Location $labRoot
Get-Location
```

คำสั่งนี้ใช้โฟลเดอร์ Documents จริงของบัญชี รวมกรณีที่อยู่ใน OneDrive ผลอาจเป็น `C:\Users\alice\Documents\llm-lab` หรือ path ที่โรงเรียนตั้งไว้ ให้ดูผลของ `Get-Location`

ต่อไปใน VS Code:

1. เลือกเมนู **File → Open Folder…**
2. เลือก `llm-lab` ที่เพิ่งสร้าง แล้วกด Open/Select Folder
3. หากถาม workspace trust และเป็นโฟลเดอร์/โค้ด lab ที่ครูแจก ให้เลือกเชื่อถือ workspace นี้
4. Explorer ด้านซ้ายต้องมี `NAV-ECOSYSTEM` เป็นโฟลเดอร์บนสุด
5. เลือก **Terminal → New Terminal** จะเปิดช่อง Terminal ด้านล่างของ VS Code
6. ใช้ลูกศรข้างปุ่ม `+` ของ Terminal เลือก profile ให้ตรง: Windows = PowerShell, macOS = zsh, Ubuntu = bash
7. พิมพ์ `pwd` (macOS/Ubuntu) หรือ `Get-Location` (PowerShell) ยืนยันว่าตำแหน่งลงท้าย `llm-lab`

หากเคยเปลี่ยนไปอยู่โฟลเดอร์อื่น ให้กลับ root ด้วย `cd "$HOME/Documents/llm-lab"` บน macOS/Ubuntu หรือ `Set-Location (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "llm-lab")` บน PowerShell

**ไม่ต้องพึ่ง `code .`** ถ้าติดตั้งคำสั่ง `code` ไว้แล้วใช้ `code .` จาก root ได้ ส่วน Mac เปิด Command Palette แล้วเลือก `Shell Command: Install 'code' command in PATH` เพื่อติดตั้งคำสั่งนี้ได้ แต่ File → Open Folder ใช้ได้เลย

## 6. สร้างโครงสร้างด้วย Terminal แล้วนำโค้ดที่ครูแจกเข้ามา

ใน Terminal ภายใน VS Code ที่อยู่ root:

**macOS / Ubuntu**

```bash
mkdir -p scripts data/pdfs data/extracted data/demo
```

**Windows PowerShell**

```powershell
New-Item -ItemType Directory -Force -Path scripts, data/pdfs, data/extracted, data/demo
```

ครูแจก ZIP ของ workshop ให้ดาวน์โหลดและ Extract ก่อน ไม่รัน Python จากภายใน ZIP จากโฟลเดอร์ที่แตกแล้ว คัดลอกโฟลเดอร์ `scripts` พร้อม `requirements.txt` และ `.gitignore` มาไว้ตรง root `llm-lab` เปิดดูใน Explorer ของ VS Code ให้เห็นดังนี้:

หากมองไม่เห็น `.gitignore` ใน Finder บน Mac ให้กด `Command + Shift + .` เพื่อแสดงไฟล์ซ่อน ส่วน VS Code Explorer แสดงไฟล์นี้ได้ตามปกติ ไฟล์นี้ช่วยกันไม่ให้ `.venv` และข้อมูลที่สร้างขึ้นถูกเพิ่มเข้า Git โดยไม่ตั้งใจ

```text
llm-lab/
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── lab_common.py
│   ├── section_engine.py
│   ├── 01_check_setup.py
│   ├── 02_embedding_demo.py
│   ├── 03_extract_pdf.py
│   ├── 04_plan_sections.py
│   ├── 05_build_sections.py
│   ├── 06_chunk_sections.py
│   └── 07_preview.py
└── data/
    ├── pdfs/
    ├── extracted/
    └── demo/
```

ถ้าลากโฟลเดอร์ผ่านหน้าต่าง file manager ให้ Copy มาที่ root ไม่ลากโฟลเดอร์ ZIP ทั้งชั้นมาซ้อนเป็น `llm-lab/ชื่อแพ็กเกจ/scripts` เพราะ path ในบทเรียนจะคลาดกัน ถ้าต้องสร้างไฟล์ด้วยมือ ให้กด New File ใน Explorer ตั้งชื่อให้ตรง แล้วคัดลอกจากไฟล์ `.py` ที่แจก อย่าพิมพ์ทั้งโปรแกรมลงใน Terminal

ตรวจว่าคัดลอกถูก:

macOS/Ubuntu:

```bash
ls scripts
cat requirements.txt
```

PowerShell:

```powershell
Get-ChildItem scripts
Get-Content requirements.txt
```

ควรเห็น `PyMuPDF==1.28.2` ใน requirements มี external Python library เพียงตัวเดียว โมดูลอื่น เช่น `json`, `pathlib`, `urllib`, `argparse` มากับ Python แล้ว

## 7. นำ PDF สามไฟล์เข้าโฟลเดอร์

1. เปิด Finder / File Explorer / Files หา PDF สามไฟล์ของตนเอง
2. ใน VS Code Explorer ขยาย `data` แล้วขยาย `pdfs`
3. ลากไฟล์จาก file manager วางบนชื่อโฟลเดอร์ `pdfs` ใน Explorer อย่าวางกลาง editor เพราะจะเป็นเพียงการเปิดไฟล์
4. ถ้ามีคำถาม Copy ให้เลือก Copy ถ้าเห็นว่าลากแล้วเปิดอ่านอย่างเดียว ให้ใช้ Copy/Paste ไฟล์เข้า `data/pdfs` ผ่าน file manager แทน
5. เปิดการแสดงนามสกุลไฟล์ก่อนเปลี่ยนชื่อ: Windows File Explorer เลือก View → Show → File name extensions (Windows 10 ใช้ View → File name extensions); macOS Finder เลือก Settings → Advanced → Show all filename extensions; Ubuntu Files แสดง `.pdf` ในชื่อไฟล์อยู่แล้ว
6. เปลี่ยนชื่อสำเนาใน `data/pdfs` ด้วยคลิกขวา → Rename ให้ชื่อเต็มเป็น `pdf1.pdf`, `pdf2.pdf`, `pdf3.pdf` ไฟล์ต้นทางไม่ต้องเปลี่ยนชื่อ คำว่า pdf1, pdf2, pdf3 ในคลาสหมายถึงชื่อก่อนนามสกุล และแต่ละไฟล์ต้องมี `.pdf` ต่อท้ายเพียงครั้งเดียว
7. ตรวจชื่อเต็มใน VS Code ว่าเป็น `pdf1.pdf` ไม่ใช่ `pdf1` หรือ `pdf1.pdf.pdf` จากนั้นใช้ `pdf1.pdf` ทำพร้อมครู อีกสองไฟล์ทำด้วยตนเองช่วงท้าย

ชุดตัวอย่างของคลาสนี้ใช้ **pdf1 = Text Processing with NLTK 3 Cookbook**, **pdf2 = Storytelling with Data**, **pdf3 = Programming the Internet of Things** ดู [รายชื่อและไฟล์ตัวอย่าง](EXAMPLE-PDFS.md) แตก ZIP ตัวอย่าง PDF แยกต่างหาก แล้วลากสามไฟล์เข้า `data/pdfs/` ตามขั้นตอนข้างบน หากใช้สำเนาที่ตั้งชื่อให้แล้ว ไม่ต้อง Rename ซ้ำ หนังสือเต็มเล่มเหล่านี้มี 304–420 หน้า จึงต้องเผื่อเวลาตรวจหัวข้อ

ตรวจรายการ:

macOS/Ubuntu:

```bash
ls -lh data/pdfs
```

PowerShell:

```powershell
Get-ChildItem data/pdfs
```

ไม่จำเป็นต้องเปลี่ยนชื่อหากต้องการเก็บชื่อเดิม แต่ต้องแก้ `--pdf "data/pdfs/ชื่อจริง.pdf"` ในคำสั่งทุกครั้ง และใส่เครื่องหมายคำพูดเมื่อชื่อมีช่องว่าง

## 8. สร้าง Python virtual environment

ตรวจอีกครั้งว่า Terminal อยู่ root `llm-lab` ก่อนสร้าง `.venv`

**macOS / Ubuntu**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell ที่ติดตั้ง Python 3.14**

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

หากใช้ Python 3.12 ให้เปลี่ยนเฉพาะคำสั่งสร้างเป็น `py -3.12 -m venv .venv` รุ่นอื่นใช้เลขที่ติดตั้งจริง

ถ้าขึ้นว่า execution policy ไม่อนุญาต `Activate.ps1` ไม่จำเป็นต้องเปลี่ยนนโยบายเครื่อง เลือก Terminal profile เป็น **Command Prompt** เปิด Terminal ใหม่ใน root แล้วรัน:

```bat
.venv\Scripts\activate.bat
```

อีกวิธีคือเรียก `.\.venv\Scripts\python.exe` ตรงแทนคำว่า `python` ในทุกคำสั่ง เช่น `.\.venv\Scripts\python.exe scripts/01_check_setup.py` การ activate เป็นการปรับ PATH ของ shell; Python ยืนยันว่าเรียก interpreter ตรงได้โดยไม่ activate ([venv docs](https://docs.python.org/3/library/venv.html))

หลัง activate แล้วทุก OS ตรวจด้วย:

```text
python -c "import sys; print(sys.executable)"
```

path ต้องมี `llm-lab` และ `.venv` เช่น `.venv/bin/python` หรือ `.venv\Scripts\python.exe` บาง prompt จะมี `(.venv)` แต่ใช้ path ของ interpreter เป็นหลักฐานได้ชัดกว่า

## 9. ติดตั้ง library และเลือก interpreter ใน VS Code

รันทีละคำสั่ง:

```text
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import pymupdf; print(pymupdf.__version__)"
```

คาดว่า PyMuPDF แสดง `1.28.2` ถ้าติดตั้งไม่สำเร็จ อย่าเปลี่ยนไปติดตั้งด้วย `sudo pip` ให้ตรวจ Python/venv และ error ก่อน

ใน VS Code:

1. เปิด Command Palette: Mac ใช้ `Command + Shift + P`; Windows/Ubuntu ใช้ `Ctrl + Shift + P`
2. พิมพ์ **Python: Select Interpreter**
3. เลือก Python ภายใน `.venv` ของ `llm-lab` ถ้าไม่ปรากฏ เลือก Enter interpreter path แล้วเลือกไฟล์ Python ใน `.venv`
4. กลับ Terminal เดิม ตรวจ `sys.executable` อีกครั้ง การเลือก interpreter ใน editor กับการ activate ใน Terminal ควรชี้ที่ environment เดียวกัน

ดู [VS Code Python environments](https://code.visualstudio.com/docs/python/environments)

## 10. ตรวจ setup แล้วทดลอง embedding

เปิดอ่าน `scripts/01_check_setup.py` ก่อน สังเกตว่ามันแสดง OS, Python ที่ใช้อยู่ และเรียก Ollama API ในเครื่อง จากนั้นรัน:

```text
python scripts/01_check_setup.py
```

ควรเห็น `Virtual environment: yes`, PyMuPDF version, รายชื่อโมเดลที่มี `all-minilm:22m` และ `Setup ready.` หาก Ollama ยังติดต่อไม่ได้ ให้แก้ก่อนทดลองโมเดล ส่วนงาน PDF สามารถตรวจเฉพาะเครื่องมือด้วย `python scripts/01_check_setup.py --offline` แล้วทำบท 11 ต่อได้ โดยจดว่าการทดลองโมเดลยังไม่เสร็จ

เปิดอ่านแล้วรัน:

```text
python scripts/02_embedding_demo.py
```

ตัวอย่างรูปแบบผล:

```text
Model: all-minilm:22m
Dimensions: 384
First 8 values: [...]
Sentence 1: A cat is sleeping on a chair.
Sentence 2: A kitten is resting on a seat.
Sentence 3: A database stores customer transactions.
Cosine similarity 1 vs 2: ...
Cosine similarity 1 vs 3: ...
```

ตัวเลขจริงไม่จำเป็นต้องตรงกับเพื่อน ดูว่าเวกเตอร์มี 384 มิติ และอภิปรายว่าความใกล้ของตัวเลขสัมพันธ์กับประโยคอย่างไร cosine เป็นคะแนนเปรียบเทียบเวกเตอร์ ไม่ใช่เปอร์เซ็นต์ความมั่นใจของคำตอบ ไฟล์ตัวอย่างบันทึกที่ `data/demo/embedding-demo.json`

จุดที่แก้ได้: ตัวแปร `sentences` ใน `02_embedding_demo.py` เปลี่ยนประโยคอังกฤษสั้นเพื่อทดลองได้ โดยใช้สามประโยคตามโครงสร้างเดิม ถ้าจะเปลี่ยนโมเดลให้ pull ก่อน แล้วใช้ `--model ชื่อโมเดล` ในทั้ง `01` และ `02`; ไม่จำเป็นสำหรับงานที่ต้องส่ง

เราเรียก `/api/embed` ผ่าน Python เพื่อให้ใช้คำสั่งเดียวบนทุก OS แทนการจัด quote ของ curl ใน PowerShell กับ bash ที่ต่างกัน ([Ollama embeddings API](https://docs.ollama.com/api/embed))

## 11. ดึงข้อความจาก PDF แรก และนับ characters ทุกหน้า

เปิดไฟล์ `scripts/03_extract_pdf.py` สังเกต `pymupdf.open`, การวนทีละหน้า และ `page.get_text("dict", ...)` ซึ่งเก็บบรรทัด/ขนาด font/พิกัดไว้ใช้หาหัวข้อ

รัน:

```text
python scripts/03_extract_pdf.py --pdf "data/pdfs/pdf1.pdf"
```

ตัวอย่างรูปแบบผล ไม่ใช่ค่าบังคับสำหรับทุกไฟล์:

```text
PDF page    1:    134 characters; 8 lines; images=1
PDF page    2:   1959 characters; 35 lines; images=0
...
Pages: ...
Bookmarks: ...
No extractable text - review visually: [...]
Artifacts: .../data/extracted/pdf1-xxxxxxxxxx
```

จำนวน characters ในสคริปต์นี้คือ `len(text.strip())` โดย text มาจากบรรทัดที่ดึงออกมาคั่นด้วย newline จึงนับช่องว่าง/newline ภายในด้วย เป็นจำนวน Unicode code points ไม่ใช่ tokens และไม่เท่ากับจำนวนอักษรที่ตามองเห็นเสมอ โดยเฉพาะสระ/วรรณยุกต์บางภาษา จำนวนอาจต่างจาก extractor หรือ options ตัวอื่นได้

เลข **PDF page** เริ่มที่ 1 สำหรับหน้าไฟล์จริง ส่วนเลขหน้าที่พิมพ์บนหนังสืออาจเป็น i, ii, 1 หรือค่าอื่น สคริปต์เก็บ `page_label` แยกไว้ อย่าเอาสองเลขนี้มาใช้แทนกัน

ใน VS Code ขยาย `data/extracted` จะเห็นโฟลเดอร์ของเอกสารชื่อ `pdf1-...` ตัวอักษรท้ายมาจาก SHA-256 ของไฟล์ ช่วยให้ไฟล์คนละเนื้อหาที่ชื่อเหมือนกันไม่เขียนทับกัน สคริปต์พิมพ์ path จริงให้แล้ว ไม่ต้องคำนวณเอง

| ไฟล์ที่สร้าง | เปิดดูเพื่ออะไร |
|---|---|
| `document.json` | ข้อมูลเอกสารทุกหน้าและ outline ในไฟล์เดียว |
| `pages.jsonl` | หนึ่ง record ต่อหนึ่งหน้า รวมหน้าที่ไม่มีข้อความ |
| `page-stats.csv` | จำนวนตัวอักษร/บรรทัด/ภาพต่อหน้า |
| `lines.txt` | ข้อความแต่ละบรรทัดพร้อม `line_id` และขนาด font |

เปิด `page-stats.csv` และ `lines.txt` ใน editor ดูว่าเลขหน้าและข้อความสัมพันธ์กับ PDF หรือไม่ เปิด PDF ใน Preview/Edge/Document Viewer ที่มีในเครื่องเพื่อตรวจเทียบได้ VS Code บางเครื่องไม่มี PDF viewer จึงไม่จำเป็นต้องติดตั้ง extension เพิ่มเพื่อจบขั้นนี้

**หน้า 0 characters ต้องตรวจ:** อาจเป็นหน้าเปล่าจริง ภาพประกอบ ภาพสแกน หรือ encoding ที่อ่านกลับไม่ได้ การมี/ไม่มี image object ไม่ใช่หลักฐานสรุปว่าหน้าเปล่า หากหน้าเป็นสแกนที่มีข้อความ ให้จดไว้ว่า OCR จำเป็น ขั้นตอนนี้เก็บแต่ text layer; ให้เลือกไฟล์มีข้อความสำหรับทำจนจบในสัปดาห์นี้

## 12. ดูบรรทัดและชื่อหัวข้อของ PDF แรก

ดูบรรทัดบน PDF หน้าที่เลือก เช่นหน้า 3:

```text
python scripts/07_preview.py --pdf "data/pdfs/pdf1.pdf" --page 3
```

เปลี่ยน `3` เป็นหน้าที่มีหัวข้อจริง ไม่จำเป็นต้องเป็นหน้าเดียวกันทุกคน ตัวอย่างรูปแบบบรรทัด:

```text
[p0003-l0001] Introduction
[p0003-l0002] First paragraph ...
[p0003-l0010] Background
```

`p0003-l0010` หมายถึง PDF หน้า 3 บรรทัดที่ 10 ในผล extraction ชุดนี้ เป็น anchor สำหรับแบ่งหัวข้อ ไม่ใช่เลขบรรทัดที่หนังสือพิมพ์ไว้ บันทึก anchor ของหัวข้ออย่างน้อย 2 หัวข้อไว้ใช้ตรวจในบทต่อไป

การอ่านเรียงตำแหน่งของ PDF มีข้อจำกัดเมื่อหลายคอลัมน์ ตาราง หรือโค้ด การเก็บครบทุกบรรทัดหมายถึงครบจากผล extractor นี้ ส่วนความถูกต้องเมื่อเทียบหน้าจริงยังต้องตรวจ ([PyMuPDF text extraction](https://pymupdf.readthedocs.io/en/latest/app1.html))

## 13. สร้างแผนแบ่งหัวข้อ

รัน:

```text
python scripts/04_plan_sections.py --pdf "data/pdfs/pdf1.pdf"
```

สคริปต์ทำดังนี้:

1. หากมี PDF bookmarks จะลองจับชื่อหัวข้อกับข้อความ 1–4 บรรทัดบนหน้าเป้าหมาย รองรับหัวข้อขึ้นหลายบรรทัดและรูปแบบ `Chapter 4.` ที่แยกจากชื่อเรื่อง
2. ถ้าหาไม่พบ จะให้คำแนะนำจากหน้าข้างเคียง โดยคงสถานะให้ผู้เรียนตรวจ ไม่ย้ายขอบเขตเองเงียบ ๆ
3. ถ้าไม่มี bookmarks จะเสนอหัวข้อจากขนาด font ที่เด่นกว่าข้อความหลัก เป็น heuristic ที่ต้องตรวจ
4. หากไม่มีข้อเสนอเลย นักเรียนกำหนดหัวข้อเองจาก line IDs ของเอกสารจริงได้

ไฟล์ผลอยู่ในโฟลเดอร์เอกสารเดิม:

- `boundaries.proposed.json`: ข้อเสนอที่โปรแกรมสร้างใหม่ได้
- `boundaries.json`: สำเนาสำหรับนักเรียนตรวจและแก้ สร้างครั้งแรกเท่านั้น การรัน planner ซ้ำจะเก็บไฟล์ที่นักเรียนแก้ไว้
- `section-plan-report.json`: จำนวน accepted/unresolved และวิธีที่ใช้เสนอหัวข้อ

## 14. ตรวจและแก้ boundaries.json ใน VS Code

นี่คือขั้นตอนจำแนกหัวข้อก่อนสร้าง section chunks เปิด `boundaries.json`, `lines.txt` และ PDF เทียบกัน จะใช้ Split Editor เพื่อดูสองไฟล์ข้างกันก็ได้

สถานะที่พบ:

| status | ความหมายและสิ่งที่ต้องทำ |
|---|---|
| `accepted` | โปรแกรมมี anchor หรือเราใส่ anchor แล้ว ยังต้องตรวจให้ถูกก่อนยืนยันทั้งไฟล์ |
| `unresolved` | ยังไม่มีตำแหน่งแน่นอน ต้องใส่ line/page จริง หรือระบุว่าเป็น bookmark ที่ไม่ใช่ขอบเขตหัวข้อ |
| `skip` | ข้ามเฉพาะ bookmark/ข้อเสนอที่ไม่ใช่หัวข้อ เช่น navigation ซ้ำ หรือ font candidate ที่เป็นคำบนปก พร้อมเหตุผลใน `note`; ข้อความต้นทางยังอยู่ |

ตัวอย่าง boundary หนึ่งรายการ รูปแบบนี้อยู่ภายใน list `boundaries` ของไฟล์ที่โปรแกรมสร้าง ตัวเลข/line ID ต้องใช้ของ PDF ตนเอง:

```json
{
  "level": 1,
  "title": "Introduction",
  "pdf_page": 3,
  "line_id": "p0003-l0001",
  "method": "manual_review",
  "status": "accepted",
  "note": "Checked against the heading on PDF page 3"
}
```

ตรวจทีละรายการ:

1. `title` ตรงหัวข้อจริงหรือไม่; `level` เป็นจำนวนเต็มบวก เช่น 1 = บท, 2 = หัวข้อย่อย, 3 = หัวข้อย่อยอีกชั้น
2. ใช้ `07_preview.py --page N` หา `line_id` ที่เป็นบรรทัดเริ่มหัวข้อ ถ้าหัวข้อสองบรรทัด ให้ชี้บรรทัดแรก
3. `pdf_page` ต้องตรงหน้าของ line ID
4. หาก bookmark ชี้หน้าท้ายบทหรือคลาดหน้า ให้หาหัวข้อจริงและแก้ anchor การไม่พบชื่อบนหน้า bookmark ไม่ได้แปลว่า OCR เสีย ไม่ควร skip บทที่มีเนื้อหาจริงเพื่อให้โปรแกรมผ่าน เพราะอาจทำให้ hierarchy สืบทอดผิดบท
5. หากเป็น navigation bookmark ซ้ำจริง ๆ หรือ font candidate ที่ตรวจแล้วไม่ใช่หัวข้อ จึงใช้ `status: "skip"` และใส่เหตุผลใน `note`
6. เรียง boundary ตามลำดับที่ปรากฏในเอกสาร หัวข้อหลายอันอยู่หน้าเดียวกันได้ แต่ต้องเป็น line ID คนละจุดตามจริง กรณี parent/child ใช้ anchor เดียวกัน ต้องเรียง parent ก่อน child และ level เพิ่มขึ้น
7. สำหรับไฟล์ไม่มี TOC ตรวจ font candidates ว่าเป็นหัวข้อจริงหรือเพียงชื่อบนปก/หัวกระดาษ เพิ่ม/ลบ/แก้ให้ตรงกับเอกสาร หากไม่มี candidate ให้เพิ่ม boundary อย่างน้อยสองรายการแบบตัวอย่าง
8. คง `document_id` เดิมที่โปรแกรมสร้าง ห้ามคัดลอกจาก PDF ของเพื่อน
9. เมื่อครบแล้วเปลี่ยนค่าบนสุด `"reviewed": false` เป็น `"reviewed": true` และ Save ด้วย `Ctrl+S` หรือ `Command+S`

JSON ใช้ double quotes, `true`/`false` ตัวเล็ก ไม่มี comments และไม่มี comma หลังรายการสุดท้าย VS Code จะแสดงจุดที่ JSON ผิด อย่าแทรกคำอธิบายภาษาไทยนอก string

หากต้องการเริ่มการ review ใหม่ทั้งหมด ให้เปลี่ยนชื่อ `boundaries.json` เป็น `boundaries.backup.json` ใน Explorer แล้วรัน planner อีกครั้ง โปรแกรมจะสร้าง review file ใหม่ ส่วนข้อความต้นทางไม่เปลี่ยน

## 15. สร้าง sections ตามหัวข้อที่ตรวจแล้ว

รัน:

```text
python scripts/05_build_sections.py --pdf "data/pdfs/pdf1.pdf"
```

ถ้ารายการยัง unresolved หรือ `reviewed` ยัง false โปรแกรมจะอธิบายจุดที่ต้องแก้ ให้แก้ไฟล์ review แล้วรันใหม่

ผลสำคัญ:

```text
Sections: ...
Accepted boundaries: ...; skipped: ...
Line coverage: 123/123 (every source line exactly once)
Original line characters retained: ...
```

ตัวเลข 123 เป็นตัวอย่างเท่านั้น ตัวตั้งและตัวหารต้องเท่ากันสำหรับ PDF ของตนเอง

ได้ `sections.jsonl` และ `sections-report.json` หนึ่ง section อาจกินหลายหน้า และหนึ่งหน้ามีหลาย section ได้ โครงสร้างเช่น `Part I > Chapter 1 > Background` เก็บใน `heading_path` ข้อความก่อนหัวข้อแรกเก็บเป็น `Front matter` เพื่อรักษาข้อความที่ดึงออกมาได้ รายการ parent ที่เริ่มจุดเดียวกับ child จะใช้ประกอบ path โดยไม่คัดลอกเนื้อหาซ้ำ

เปิดดูรายงานและตัวอย่าง:

```text
python scripts/07_preview.py --pdf "data/pdfs/pdf1.pdf"
```

ถ้าไม่มี boundaries เลย โปรแกรมจะได้ section ชื่อ `Document` เดียว ซึ่งเป็น fallback ที่ซื่อสัตย์ต่อข้อมูล แต่ยังไม่ผ่านงานแบ่งหัวข้อของคาบนี้ ให้กลับไปเพิ่มอย่างน้อยสองหัวข้อที่มีอยู่จริงก่อน

## 16. แบ่งแต่ละ section เป็น chunks

รัน:

```text
python scripts/06_chunk_sections.py --pdf "data/pdfs/pdf1.pdf" --max-chars 900 --overlap-chars 100
```

ความหมาย:

- `--max-chars 900`: ขนาดข้อความแต่ละ chunk ไม่เกิน 900 Unicode code points ตามผล extraction
- `--overlap-chars 100`: ย้อนข้อความประมาณ 100 ตัวอักษรภายใน section เพื่อคงบริบทต่อเนื่อง
- พยายามจบชิ้นตรงย่อหน้า/บรรทัด/ช่องว่างก่อน หากบรรทัดยาวเกินก็แบ่งด้วยขอบเขตตัวอักษร
- chunks อยู่ภายใน section เดียว ไม่ลากข้อความข้ามหัวข้อ
- heading path อยู่ใน metadata; ข้อความต้นทางของ heading เก็บไว้ใน section

ได้ `chunks.jsonl` และ `chunks-report.json` ที่รายงาน `Coverage complete: True` หมายถึงข้อความทุกส่วนของ sections มีอยู่ใน chunk อย่างน้อยหนึ่งครั้ง การซ้ำใน overlap เป็นสิ่งที่ตั้งใจ **characters ไม่ใช่ tokens** และค่า 900 นี้ไม่ใช่คำรับรองว่าจะพอดีกับ context ของ all-minilm ทุกข้อความ การใช้ tokenizer และฝังเวกเตอร์ของ chunks เป็นคาบถัดไป

ตัวอย่างข้อมูลในหนึ่ง chunk แบบย่อ:

```json
{
  "chunk_id": "...",
  "source_file": "pdf1.pdf",
  "section_id": "...",
  "heading_path": ["Chapter 1", "Background"],
  "text": "ข้อความจริงจาก PDF ...",
  "char_count": 740,
  "pdf_page_start": 3,
  "pdf_page_end": 4,
  "source_pages": [3, 4],
  "source_spans": [
    {"pdf_page": 3, "line_id": "p0003-l0010", "start_char": 0, "end_char": 23}
  ]
}
```

ตัวอย่างย่อข้างบนไม่ได้แสดง fields ทั้งหมด ชื่อหัวข้อและเลขหน้าของนักเรียนจะต่างกัน

## 17. ตรวจผล PDF แรกให้เห็นภาพ

รัน:

```text
python scripts/07_preview.py --pdf "data/pdfs/pdf1.pdf" --chunks 5
```

โปรแกรมแสดงรายการ section paths, ช่วงหน้า, จำนวน characters และตัวอย่าง chunks สั้น ๆ พร้อมเขียน `preview.md` ในโฟลเดอร์เอกสารเดียวกัน เปิดไฟล์นี้ใน VS Code แล้วกด Open Preview เพื่ออ่านง่ายขึ้น

ตรวจพร้อมครู:

1. เลือกหัวข้อสองอันที่อยู่หน้าเดียวกัน ถ้ามี ดูว่าเนื้อหาแยกถูกตาม anchor
2. เลือก section ที่ยาวหลายหน้า ดู page ranges และ `source_pages` ของ chunk
3. เปิด chunk สองชิ้นที่ต่อกันใน section เดียว ดูข้อความ overlap
4. ดู `sections-report.json` ว่า `all_lines_assigned_once` เป็น true และไม่มี missing/duplicate line IDs
5. ดู `chunks-report.json` ว่า `coverage_complete` เป็น true ตัวเลขครอบคลุมข้อความที่ดึงได้ ไม่ได้พิสูจน์ว่า OCR/layout ของ PDF ทุกแบบถูกต้อง

ลองรัน chunk อีกครั้งด้วย `--max-chars 600 --overlap-chars 80` ดูว่าจำนวน chunks เปลี่ยนอย่างไร จากนั้นรันกลับ 900/100 หากครูกำหนดค่าร่วมกัน การรันขั้น chunk ซ้ำเขียนผล chunks ของเอกสารนั้นใหม่

## 18. ทำ PDF ที่สองและสามด้วยตนเอง

ไม่ต้องสร้าง venv ใหม่ ไม่ต้องติดตั้ง library ซ้ำ และไม่ต้องแก้ path ชื่อผู้ใช้ใน Python เปลี่ยนค่า `--pdf` ตามไฟล์

**PDF ที่สอง**

```text
python scripts/03_extract_pdf.py --pdf "data/pdfs/pdf2.pdf"
python scripts/04_plan_sections.py --pdf "data/pdfs/pdf2.pdf"
```

หยุดที่นี่เพื่อเปิด `boundaries.json` ของ **pdf2** ตรวจแก้หัวข้อและตั้ง `reviewed: true` แล้วจึงรัน:

```text
python scripts/05_build_sections.py --pdf "data/pdfs/pdf2.pdf"
python scripts/06_chunk_sections.py --pdf "data/pdfs/pdf2.pdf" --max-chars 900 --overlap-chars 100
python scripts/07_preview.py --pdf "data/pdfs/pdf2.pdf" --chunks 3
```

**PDF ที่สาม**

```text
python scripts/03_extract_pdf.py --pdf "data/pdfs/pdf3.pdf"
python scripts/04_plan_sections.py --pdf "data/pdfs/pdf3.pdf"
```

ตรวจ `boundaries.json` ของ **pdf3** ให้ครบก่อน แล้วรัน:

```text
python scripts/05_build_sections.py --pdf "data/pdfs/pdf3.pdf"
python scripts/06_chunk_sections.py --pdf "data/pdfs/pdf3.pdf" --max-chars 900 --overlap-chars 100
python scripts/07_preview.py --pdf "data/pdfs/pdf3.pdf" --chunks 3
```

แต่ละ PDF มีโฟลเดอร์ผลของตนเอง ตรวจชื่อ path ที่สคริปต์พิมพ์ อย่าเปิด review file ของ PDF แรกมาแก้แทนไฟล์ใหม่

ถ้าต้องการฝึกใช้ชื่อจริง ให้ Rename สำเนาเป็นชื่ออื่นใน `data/pdfs` แล้วเปลี่ยน `--pdf "data/pdfs/ชื่อใหม่.pdf"` ทุกคำสั่ง สคริปต์ตั้ง output ตามชื่อและเนื้อหาใหม่เอง จึงต้อง review file ในโฟลเดอร์ผลใหม่นั้น ไม่ต้องแก้โค้ด `.py`

## 19. ส่งงานและจบคาบ

ทำตาราง 3 แถว ลงไฟล์ `lab-notes.md` ด้วย New File ใน VS Code หรือคัดลอก [lab-notes.template.md](lab-notes.template.md) ที่แจกแล้วเปลี่ยนชื่อ:

| PDF | จำนวนหน้า | หน้าที่ไม่มี text | จำนวน bookmarks | วิธีหา/แก้หัวข้อ | sections | chunks | สิ่งที่พบ |
|---|---:|---|---:|---|---:|---:|---|
| pdf1.pdf | ... | ... | ... | bookmarks/manual | ... | ... | ... |
| pdf2.pdf | ... | ... | ... | ... | ... | ... | ... |
| pdf3.pdf | ... | ... | ... | ... | ... | ... | ... |

ส่ง `lab-notes.md` และไฟล์ผลที่ครูกำหนดจากแต่ละเอกสาร เช่น `page-stats.csv`, `boundaries.json`, `sections-report.json`, `chunks-report.json`, `preview.md` รวมถึงโค้ดถ้ามีแก้ ไม่ต้องส่ง `.venv` และไม่ต้องรวม PDF ต้นฉบับเมื่อครูขอเฉพาะรายงาน ไฟล์ผลบางตัวมีข้อความจาก PDF ให้ส่งตามช่องทางและขอบเขตข้อมูลที่ครูกำหนด

ตอบสั้น ๆ ใน notes:

1. Ollama, embedding model และ PDF parser ทำหน้าที่ต่างกันอย่างไร?
2. ทำไม 0 characters จึงยังสรุปว่าเป็นหน้าเปล่าไม่ได้?
3. ทำไมหนึ่งหน้าไม่จำเป็นต้องเป็นหนึ่ง section/chunk?
4. เมื่อ bookmark ชี้ไม่ตรงหัวข้อ คุณแก้ page/line anchor อย่างไร?
5. เปลี่ยน max-chars แล้วจำนวน chunks เปลี่ยนอย่างไร และ characters ต่างจาก tokens อย่างไร?

หาก activate environment ไว้ ให้ปิดเมื่อเสร็จด้วย `deactivate` หากเรียก Python ใน `.venv` ตรงโดยไม่ได้ activate ก็ปิด Terminal ได้เลย ถ้าเปิด Terminal ใหม่ในวันอื่น ให้กลับ root แล้ว activate `.venv` ใหม่หรือเรียก interpreter ตรงตามวิธีเดิม ส่วนข้อมูลที่บันทึกบนดิสก์ยังอยู่

**สิ้นสุด lab workshop สัปดาห์นี้: ทุกคนได้ section chunks ของ PDF แรก และฝึกทำอีกสองไฟล์ด้วยตนเอง**

## ตารางไฟล์ Python: ต้องแก้อะไรบนเครื่องส่วนตัว?

| ไฟล์ | หน้าที่ | ส่วนที่นักเรียนอาจเปลี่ยน |
|---|---|---|
| `lab_common.py` | หา root และจัดการไฟล์/JSON | ไม่ต้องแก้ชื่อผู้ใช้หรือ root ในไฟล์ |
| `section_engine.py` | จับหัวข้อและประกอบ sections | ไม่ต้องแก้เพื่อเปลี่ยน PDF |
| `01_check_setup.py` | ตรวจ Python/library/Ollama | `--model` ถ้าเลือกโมเดลอื่น |
| `02_embedding_demo.py` | ทดลองข้อความ → เวกเตอร์ | เปลี่ยน `sentences` ได้; ค่า default ใช้ร่วมกันได้เลย |
| `03_extract_pdf.py` | อ่าน PDF แสดง characters และบันทึก lines | เปลี่ยน `--pdf` |
| `04_plan_sections.py` | เสนอ boundary จาก bookmarks/font | เปลี่ยน `--pdf`; แก้ผล `boundaries.json` ตามเอกสารจริง |
| `05_build_sections.py` | ใช้ boundary ที่ตรวจแล้วสร้าง sections | เปลี่ยน `--pdf` |
| `06_chunk_sections.py` | แบ่ง section เป็น chunks | `--pdf`, `--max-chars`, `--overlap-chars` |
| `07_preview.py` | ดู lines/section/chunk และสร้าง preview | `--pdf`, `--page`, `--chunks` |

พิมพ์ `python scripts/ชื่อไฟล์.py --help` ดู options ได้ โดย `lab_common.py` และ `section_engine.py` เป็น helper ที่ scripts เรียกใช้ ไม่ใช่ขั้นตอนที่ต้องรันแยก

## หากติดปัญหา

| อาการ | ตรวจ/แก้ |
|---|---|
| `ollama: command not found` / not recognized | เปิดแอปหลังติดตั้ง ปิดเปิด Terminal ใหม่ ตรวจ PATH ตามคู่มือ OS |
| `address already in use` ที่ 11434 | Ollama server อาจทำงานอยู่แล้ว ใช้ตัวเดิม ไม่เปิด `ollama serve` ซ้ำ |
| โหลดโมเดลค้าง/error หลังเปลี่ยนเน็ต | ใช้เครือข่ายที่พร้อม แล้ว retry `ollama pull all-minilm:22m`; บันทึก error จริง |
| Python command เปิด Store หรือไม่พบ | ตรวจ installer/PATH; Windows ลอง `py -3.14 --version` และใช้ launcher สร้าง venv |
| `Activate.ps1 cannot be loaded` | ใช้ Command Prompt activate.bat หรือเรียก `.venv\Scripts\python.exe` ตรง |
| `No module named pymupdf` | ตรวจ `sys.executable` ต้องเป็น `.venv`; ติดตั้งด้วย `python -m pip install -r requirements.txt` |
| pip หาตัวติดตั้ง PyMuPDF ไม่ได้ | ตรวจ Python3.10–3.14 ปกติ/CPU architecture; ใช้เวอร์ชัน class-tested ก่อน source-build |
| `can't open file scripts/...` | ตรวจ root ด้วย pwd/Get-Location และตำแหน่งโฟลเดอร์ scripts |
| `PDF not found` | ตรวจชื่อไฟล์จริง ตัวพิมพ์ใหญ่/เล็ก นามสกุลซ้ำ และ quotes; Ubuntu แยก case |
| ข้อความเป็นศูนย์ทุกหน้า | อาจเป็น scan/encoding อ่านไม่ได้ เปิดดูไฟล์แล้วบันทึกว่า OCR ต้องทำก่อน ใช้ born-digital PDF ทำส่วนที่เหลือ |
| ข้อความสลับคอลัมน์/ตารางเสีย | เป็นข้อจำกัด extraction/reading order เลือกตัวอย่างคอลัมน์เดียวก่อนและบันทึกปัญหา |
| มี unresolved boundaries | แก้ page/line จริงจาก lines.txt; skip เฉพาะที่ไม่ใช่หัวข้อจริงพร้อมเหตุผล |
| `reviewed` error | ตรวจทุก boundary แล้วตั้ง `"reviewed": true` ในไฟล์ของ PDF นั้นและ Save |
| JSON invalid | double quotes, ไม่มี comments/trailing comma; ใช้ error line ใน VS Code |
| boundary out of document order | เรียงตามตำแหน่งจริงใน lines.txt ไม่ใช่แค่เลขหัวข้อ |
| ได้ section `Document` เดียว | ไม่มี accepted boundaries; เพิ่มหัวข้อจริงเพื่อทำโจทย์ section chunks |
| หา output ไม่เจอ | อ่าน `Artifacts:` จากสคริปต์ แล้วกด Refresh ใน VS Code Explorer |

แหล่งเอกสารทางการรวมไว้ใน [SOURCES.md](SOURCES.md) แผนสอนและเกณฑ์ตรวจงานอยู่ใน [INSTRUCTOR.th.md](INSTRUCTOR.th.md)

## ผลทดสอบและชุดตรวจสำหรับครู

ดู [ผลรันจริงบน macOS และ Ubuntu container](VALIDATION.md) พร้อมจำนวน sections/chunks ของ PDF ตัวอย่างทั้งสาม ส่วน Windows ยังไม่มีผลรันจริงในรอบนี้ มี [ขั้นตอนตรวจบน Windows](VERIFY-ON-WINDOWS.md) ให้ครูดำเนินการก่อนใช้ในชั้นเรียน ชุดทดสอบและเฉลยครูเป็นอุปกรณ์ตรวจ lab ไม่ใช่ขั้นตอนส่งงานของนักเรียน
