# เค้าโครงฐานข้อมูล & การจับคู่เวกเตอร์ (Database Schema & Vector Mapping)

## ตารางในฐานข้อมูล (Database Tables)

### `files`
จัดเก็บข้อมูลเมทาดาตาของไฟล์/โฟลเดอร์, ธงคุณสมบัติ (feature flags), และค่าเวกเตอร์ตัวแทนที่คำนวณแล้ว

| คอลัมน์ (Column) | ประเภท (Type) | ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | ไอดีที่ไม่ซ้ำและเพิ่มขึ้นอัตโนมัติ |
| `full_path` | TEXT | UNIQUE, NOT NULL | เส้นทางแบบสมบูรณ์ |
| `parent_path` | TEXT | NOT NULL | เส้นทางสมบูรณ์ของไดเรกทอรีต้นทาง |
| `name` | TEXT | NOT NULL | ชื่อไฟล์ หรือ ชื่อโฟลเดอร์ |
| `is_folder` | BOOLEAN | NOT NULL | เป็น 1 หากเป็นโฟลเดอร์, 0 หากเป็นไฟล์ |
| `size_bytes` | INTEGER | NOT NULL | ขนาดไฟล์ในหน่วยไบต์ (0 หากเป็นโฟลเดอร์) |
| `create_time` | INTEGER | NOT NULL | สแตมป์เวลาแบบ Unix epoch |
| `is_hidden` | BOOLEAN | NOT NULL | เป็น 1 หากเปิดคุณสมบัติการซ่อนไฟล์ |
| `is_system` | BOOLEAN | NOT NULL | เป็น 1 หากเปิดคุณสมบัติของไฟล์ระบบ |
| `is_temp` | BOOLEAN | NOT NULL | เป็น 1 หากชื่อไฟล์ประกอบด้วย tmp/temp/~$ ซึ่งเป็นตัวบ่งชี้ |
| `vector_blob` | BLOB | NOT NULL | ข้อมูลอาร์เรย์แบบ Binary ของค่า float32 ที่แปลงเรียงกัน (42 มิติ) |

### `directories`
กำหนดเส้นทางสำหรับการสแกนค้นหา

| คอลัมน์ (Column) | ประเภท (Type) | ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | ไอดีที่ไม่ซ้ำกัน |
| `path` | TEXT | UNIQUE, NOT NULL | เส้นทางไดเรกทอรีที่ถูกเพิ่มโดยผู้ใช้งาน |
| `last_scanned` | INTEGER | | สแตมป์เวลาของการตรวจสอบหรือซิงค์ที่ทำเสร็จล่าสุด |

### `ignores`
ประกอบด้วยการตั้งค่าตัวจำกัดละเว้นไฟล์ `.ignore`

| คอลัมน์ (Column) | ประเภท (Type) | ข้อจำกัด (Constraints) | คำอธิบาย (Description) |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | ไอดีที่ไม่ซ้ำกัน |
| `pattern` | TEXT | NOT NULL | รูปแบบ Glob หรือชื่อโฟลเดอร์ให้ข้ามไป |

---

## ตัวแทนเวกเตอร์แบบ 42 มิติ (The 42-Dimension Vector Representation)
เพื่อคำนวณหาความคล้ายคลึงของเวกเตอร์ ไฟล์/โฟลเดอร์แต่ละอันจะถูกจับคู่เข้ากับตัวแทนเวกเตอร์ 42 มิติซึ่งเป็นค่าจำนวนทศนิยมที่กำหนดมาตรฐานให้มีค่าอยู่ระหว่าง `[0, 1]` หรือตามค่ามาตรฐานระหว่าง `[-1, 1]`

| ดัชนีมิติ (Dim Index) | ชื่อคุณสมบัติ (Feature Name) | ขนาดมิติ (Dimension Size) | คำอธิบายและการกำหนดค่ามาตรฐาน (Description & Normalization) |
|-----------|--------------|----------------|-----------------------------|
| **0** | `is_folder` | 1 | `1.0` หากเป็นโฟลเดอร์, `0.0` หากเป็นไฟล์ |
| **1** | `is_thai` | 1 | `1.0` หากพบตัวอักษรภาษาไทยในชื่อ, `0.0` ในกรณีอื่น |
| **2** | `is_english` | 1 | `1.0` หากพบตัวอักษรภาษาอังกฤษ, `0.0` ในกรณีอื่น |
| **3** | `folder_depth` | 1 | จำนวนของตัวคั่นเส้นทางที่ถูกทำเป็นค่าปกติโดยหารความลึกระดับสูงสุด (จำกัดสูงสุด 20) |
| **4** | `fullpath_len` | 1 | ความยาวข้อความของเส้นทางแบบสมบูรณ์ที่ถูกทำเป็นค่าปกติโดยความยาวระดับสูงสุด (จำกัดสูงสุด 260) |
| **5** | `parentpath_len` | 1 | ความยาวข้อความของเส้นทางต้นทางที่ถูกทำเป็นค่าปกติ (จำกัดสูงสุด 260) |
| **6-8** | `drive_letter` | 3 | การเข้ารหัส One-hot ไดรฟ์: `[C:, D:, other]` |
| **9** | `file_size_log` | 1 | ขนาดพิกัด Log-scale: `log(size_bytes + 1) / log(max_size_bytes_cap)` |
| **10** | `create_date_norm`| 1 | สแตมป์เวลาของ Unix ถูกทำเป็นค่าปกติระหว่างวันที่สร้างต่ำสุดและสูงสุดจากตารางฐานข้อมูล |
| **11** | `is_hidden` | 1 | `1.0` หากถูกซ่อน, `0.0` ในกรณีอื่น |
| **12** | `is_system` | 1 | `1.0` หากเป็นไฟล์ระบบ, `0.0` ในกรณีอื่น |
| **13** | `is_temp` | 1 | `1.0` หากเป็นไฟล์สำรอง (temp), `0.0` ในกรณีอื่น |
| **14-28** | `extension_one_hot`| 15 | การเข้ารหัส One-hot ไฟล์นามสกุล: `[txt, md, py, js, html, css, pdf, docx, xlsx, zip, png, jpg, mp3, mp4, other/folder]` |
| **29-35** | `start_letters_folder`| 7 | ค่าประมวลแบบ Hashed สกัดตัวอักษร 2 ตัวแรกในชื่อโฟลเดอร์ (จับคู่ส่งไป 7 bins คลื่นไซน์ ฟังก์ชันแฮช) |
| **36-41** | `start_letters_file`| 6 | ค่าประมวลแบบ Hashed สกัดตัวอักษร 2 ตัวแรกในชื่อไฟล์ (จับคู่ส่งไป 6 bins) |

---

## ขั้นตอนอัลกอริทึมปฏิบัติงานจริง (Exact Implementation Algorithm - Python Code)
เพื่อให้แน่ใจว่าเกิดความต่อเนื่องกันในโมเดล AI ต่างๆ ให้ดำเนินการสร้างแบบแผนตรรกะสำหรับการจับคู่นี้ผ่านภาษา Python:

```python
import os
import re
import numpy as np

# Capped maximum bounds
MAX_DEPTH = 20
MAX_PATH_LEN = 260
MAX_SIZE_CAP = 10 * 1024 * 1024 * 1024 # 10 GB
MIN_DATE = 946684800   # 2000-01-01
MAX_DATE = 2524608000  # 2050-01-01

# Mapping Extensions to Index (0-13), 14 is other
EXT_MAP = {
    '.txt': 0, '.md': 1, '.py': 2, '.js': 3, '.html': 4,
    '.css': 5, '.pdf': 6, '.docx': 7, '.xlsx': 8, '.zip': 9,
    '.png': 10, '.jpg': 11, '.mp3': 12, '.mp4': 13
}

def string_sine_hash(text, num_bins):
    """Produces a deterministic float array of size num_bins between [0.0, 1.0]."""
    res = np.zeros(num_bins, dtype=np.float32)
    if not text:
        return res
    # Sum character values multiplied by prime positions
    val = sum(ord(c) * (i + 1) for i, c in enumerate(text[:2]))
    # Map to multiple sine wave hashes to populate bins
    for b in range(num_bins):
        res[b] = float((np.sin(val * (b + 1.234)) + 1.0) / 2.0)
    return res

def compute_42_dim_vector(full_path, parent_path, name, is_folder, size_bytes, create_time, is_hidden, is_system, is_temp):
    vector = np.zeros(42, dtype=np.float32)

    # 0. is_folder
    vector[0] = 1.0 if is_folder else 0.0

    # 1. contains Thai
    has_thai = 1.0 if re.search(r'[\u0e00-\u0e7f]', name) else 0.0
    vector[1] = has_thai

    # 2. contains English
    has_english = 1.0 if re.search(r'[a-zA-Z]', name) else 0.0
    vector[2] = has_english

    # 3. depth
    depth = len(full_path.replace('\\', '/').split('/')) - 1
    vector[3] = float(min(depth, MAX_DEPTH) / MAX_DEPTH)

    # 4. fullpath length
    vector[4] = float(min(len(full_path), MAX_PATH_LEN) / MAX_PATH_LEN)

    # 5. parentpath length
    vector[5] = float(min(len(parent_path), MAX_PATH_LEN) / MAX_PATH_LEN)

    # 6-8. drive letter
    drive = os.path.splitdrive(full_path)[0].upper()
    if drive == 'C:':
        vector[6] = 1.0
    elif drive == 'D:':
        vector[7] = 1.0
    else:
        vector[8] = 1.0 # Other drive

    # 9. file_size_log
    size_val = size_bytes if not is_folder else 0
    vector[9] = float(np.log1p(size_val) / np.log1p(MAX_SIZE_CAP))

    # 10. create_date_norm
    norm_date = (create_time - MIN_DATE) / (MAX_DATE - MIN_DATE)
    vector[10] = float(np.clip(norm_date, 0.0, 1.0))

    # 11-13. file flags
    vector[11] = 1.0 if is_hidden else 0.0
    vector[12] = 1.0 if is_system else 0.0
    vector[13] = 1.0 if is_temp else 0.0

    # 14-28. extension one-hot
    ext_idx = 14 # default to other/folder
    if not is_folder:
        _, ext = os.path.splitext(name.lower())
        if ext in EXT_MAP:
            ext_idx = EXT_MAP[ext]
    vector[14 + ext_idx] = 1.0

    # 29-35. parent folder start letters (7 dims)
    folder_name = os.path.basename(parent_path)
    vector[29:36] = string_sine_hash(folder_name, 7)

    # 36-41. filename start letters (6 dims)
    vector[36:42] = string_sine_hash(name, 6)

    return vector
```

---

## การตัดสินใจเชิงสถาปัตยกรรม (Architectural Decision): ทำไมจึงใช้ 42 มิติแทนที่จะเป็น 384 มิติ (Semantic Search)?
หลักยึดเหนี่ยวที่สำคัญของโปรเจกต์นี้คือความตั้งใจที่จะใช้เวกเตอร์ 42 มิติที่สร้างขึ้นเอง แทนที่จะใช้การฝังตัว (embedding) ของ LLM มาตรฐานแบบ 384 มิติ (เช่น `all-MiniLM-L6-v2`)
1. **การควบคุมเมทาดาตาอย่างชัดเจน (Explicit Metadata Control)**: ในเวกเตอร์เชิงความหมาย (semantic vector) 384 มิติ เราไม่สามารถรู้ความหมายของแต่ละมิติได้ ทำให้เป็นไปไม่ได้ที่จะกำหนดน้ำหนักเฉพาะเจาะจงลงไป (เช่น "ให้ความสำคัญกับวันที่สร้าง") แต่ในเวกเตอร์ 42 มิติของเรา ทุกๆ มิติเป็นตัวแทนของคุณสมบัติที่ชัดเจนและรู้ที่มา ทำให้ผู้ใช้สามารถควบคุมคณิตศาสตร์ได้อย่างสมบูรณ์ผ่านแถบเลื่อนบน GUI
2. **ความเร็วในการรวบรวมข้อมูล & ไม่มีภาระจาก AI (Crawling Speed & Zero AI Overhead)**: การสร้างการฝังตัว AI 384 มิติสำหรับทุกๆ ไฟล์จำเป็นต้องประมวลผลข้อความผ่านโครงข่ายประสาทเทียม ซึ่งจะลดความเร็วของตัวรวบรวมข้อมูลอย่างรุนแรงและกินทรัพยากร CPU/GPU อย่างมาก ในขณะที่การคำนวณทางคณิตศาสตร์เชิงโครงสร้าง 42 มิติของเรา (การแฮช, การปรับสเกลล็อก) ใช้เวลาเพียงไม่กี่ไมโครวินาที ช่วยให้ตัวรวบรวมข้อมูลสามารถประมวลผลได้หลายพันไฟล์ต่อวินาทีโดยใช้ CPU น้อยที่สุด
3. **ประสิทธิภาพ RAM และการจัดเก็บ (RAM & Storage Efficiency)**: มิติแบบ float32 จำนวน 42 มิติใช้พื้นที่ประมาณ 168 ไบต์ต่อไฟล์ (~16 MB สำหรับ 100,000 ไฟล์) ในขณะที่ 384 มิติใช้พื้นที่ 1536 ไบต์ (~150 MB สำหรับ 100,000 ไฟล์) แนวทาง 42 มิติจึงรับประกันการเปรียบเทียบในหน่วยความจำ RAM ที่รวดเร็วปานสายฟ้าแลบ
