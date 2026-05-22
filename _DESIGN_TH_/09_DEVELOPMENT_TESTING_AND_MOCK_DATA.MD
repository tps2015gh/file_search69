# กลยุทธ์การพัฒนาการทดสอบและข้อมูลจำลอง (Development Testing & Mock Data Strategy)

เอกสารฉบับนี้ให้รายละเอียดเครื่องมือและกลยุทธ์สำหรับการทดสอบระบบเอนจินเวกเตอร์ การตรวจสอบการคำนวณสืบค้น และการส่งข้อมูลจำลองโดยที่ไม่จำเป็นต้องทำการสแกนไฟล์ทั้งระบบ

---

## 1. เมทริกซ์การถ่วงน้ำหนักความคล้ายคลึงของลักษณะข้อมูล (Feature Similarity Weighting Matrix)
เพื่อให้เครื่องมือค้นหาความคล้ายคลึงสามารถปรับแต่งได้ (ตัวอย่างเช่น เลือกให้ความสำคัญกับความคล้ายกันของชื่อไฟล์มากกว่าวันเวลาที่สร้าง) กระบวนการทางคณิตศาสตร์ในการหาระยะห่างต้องรองรับการกำหนดน้ำหนักความสำคัญในลักษณะที่ต่างกัน

### โครงสร้างน้ำหนักเวกเตอร์ (Weighting Vector Structure)
ตัวเลขรูปแบบทศนิยม (float32) สำหรับเวกเตอร์ขนาด 42 ($W$) ถูกกำหนดไว้ดังนี้:
$$W = [w_0, w_1, \dots, w_{41}]$$

- โดยค่าเริ่มต้น ทุกๆองค์ประกอบจะถูกกำหนดให้เท่ากับ $1.0$.
- **กลุ่มกำหนดค่าที่ตั้งผ่าน GUI (GUI Configurable Groups)**:
  - **น้ำหนักเส้นทาง (Path Weights)** (มิติที่ 3, 4, 5): ปรับเพิ่มเพื่อให้ความสำคัญต่อโฟลเดอร์/ไฟล์ ที่มีชื่อเส้นทางที่ตั้งใกล้เคียงกัน
  - **น้ำหนักตัวอักษรไดรฟ์ (Drive letter Weights)** (มิติที่ 6-8): ตั้งค่าให้มีระดับสูง (เช่น 5.0) เพื่อแยกความแตกต่างกรณีค้นเจอของทั้งไดรฟ์ C และ ไดรฟ์ D ออกจากกัน
  - **น้ำหนักวันเวลา (Date Weights)** (มิติที่ 10): ปรับเพิ่มเพื่อจัดลำดับไฟล์ที่ถูกสร้างในเวลาใกล้เคียงกันหรือเวลาเดียวกันให้สำคัญขึ้น
  - **น้ำหนักนามสกุลไฟล์ (Extension Weights)** (มิติที่ 14-28): ตั้งให้สูงไว้เพื่อจับกลุ่มและตีกรอบประเภทของไฟล์ให้มีความเข้มงวดชัดเจน (.py คู่กับ .py).
  
### สมการระยะห่างถ่วงน้ำหนัก (Weighted Distance Equation - Python Pseudocode)
```python
import numpy as np

def weighted_euclidean_distance(v1, v2, weights):
    """Calculates weighted Euclidean distance between two 42-dim vectors."""
    diff = v1 - v2
    squared_diff = diff ** 2
    weighted_diff = weights * squared_diff
    return np.sqrt(np.sum(weighted_diff))
```

---

## 2. ตัวสร้างข้อมูลจำลอง (Mock Data Generator - Seeding Script)
เพื่อทำการประเมินประสิทธิภาพในรูปแบบกราฟให้สามารถจุโหนดนับพันโหนดโดยไม่ต้องทำการตรวจสอบหรือสแกนดิสก์ทั้งหมด ให้ใช้ตัวสคริปต์แม่แบบง่านๆ ที่เขียนโดยภาษา Python สำหรับการกระจายโครงสร้างเป้าหมายดังนี้:

```python
import random
import sqlite3
import numpy as np
# Import the function from 04_SCHEMA.MD
# from vector_generator import compute_42_dim_vector

def generate_mock_db(db_path="mock_file_search.db", num_files=2000):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        full_path TEXT UNIQUE,
        parent_path TEXT,
        name TEXT,
        is_folder BOOLEAN,
        size_bytes INTEGER,
        create_time INTEGER,
        is_hidden BOOLEAN,
        is_system BOOLEAN,
        is_temp BOOLEAN,
        vector_blob BLOB
    )""")
    
    # Predefined mock extensions
    extensions = ['.txt', '.md', '.py', '.js', '.pdf', '.png', '.jpg', '.zip']
    drives = ['C:\\', 'D:\\']
    
    print(f"Generating {num_files} mock file entries...")
    batch = []
    
    for i in range(num_files):
        drive = random.choice(drives)
        # Create randomized folder depth hierarchy
        depth = random.randint(1, 4)
        folders = [f"Folder_{random.randint(1, 10)}" for _ in range(depth)]
        parent_path = drive + "\\".join(folders)
        
        is_folder = (random.random() < 0.15) # 15% are directories
        if is_folder:
            name = f"SubFolder_{random.randint(1, 100)}"
            size = 0
            ext = ""
        else:
            name = f"file_{random.randint(1, 1000)}" + random.choice(extensions)
            size = random.randint(100, 500000000) # 100 bytes to 500MB
            
        full_path = parent_path + "\\" + name
        create_time = random.randint(1577836800, 1735689600) # Dates between 2020 and 2024
        is_hidden = 1 if (random.random() < 0.05) else 0
        is_system = 0
        is_temp = 1 if ("temp" in name or random.random() < 0.02) else 0
        
        # Calculate Mock 42-Dim Vector (simulate function execution)
        mock_vec = np.random.rand(42).astype(np.float32) # Simulated float32 vector
        vector_bytes = mock_vec.tobytes()
        
        batch.append((full_path, parent_path, name, is_folder, size, create_time, is_hidden, is_system, is_temp, vector_bytes))
        
        if len(batch) >= 1000:
            cursor.executemany("INSERT OR REPLACE INTO files (full_path, parent_path, name, is_folder, size_bytes, create_time, is_hidden, is_system, is_temp, vector_blob) VALUES (?,?,?,?,?,?,?,?,?,?)", batch)
            batch = []
            
    if batch:
        cursor.executemany("INSERT OR REPLACE INTO files (full_path, parent_path, name, is_folder, size_bytes, create_time, is_hidden, is_system, is_temp, vector_blob) VALUES (?,?,?,?,?,?,?,?,?,?)", batch)
        
    conn.commit()
    conn.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    generate_mock_db()
```

---

## 3. การบำรุงรักษาฐานข้อมูล & กลยุทธ์การล้างข้อมูล (Database Maintenance & Cleanup Strategy)
เมื่อเวลาผ่านไป ไฟล์อาจถูกลบ, เปลี่ยนชื่อ หรือ ดัดแปลงในดิสก์ ฐานข้อมูลมีความจำเป็นที่จะต้องบำรุงรักษาเพื่อล้างข้อมูลเก่า

### แผนการล้างข้อมูล (Cleanup Execution Plan)
1. **การลบไฟล์กำพร้า (Orphan File Removal)**:
   - นำเส้นทางทั้งหมดมาประมวลผลสืบค้นที่ตัว DB
   - ดำเนินการตรวจสอบการรันในลำดับความสำคัญต่ำผ่าน `os.path.exists` โดยแบ่งเป็นรอบๆ
   - ถอนการบันทึกฐานข้อมูลในส่วนของไฟล์ที่ไม่มีปรากฏอยู่บนดิสก์ 
2. **SQLite VACUUM**:
   - เรียกร้องพื้นที่ว่างกลับมาใช้ในฐานข้อมูลหลักหลังจากการสั่งถอน
   - บังคับการทำงาน `VACUUM` จากการตั้งโปรแกรมในเมนูตั้งค่า หรือรันอัตโนมัติเมื่อตรวจสอบพบโหนดกำพร้าเกิดการสะสมจำนวนมากกว่าร้อยละ 20 ของทั้งหมด
