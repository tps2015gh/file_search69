# Development Testing & Mock Data Strategy

This document details tools and strategies for testing the vector engine, checking search calculations, and seeding mock data without needing full system directory scans.

---

## 1. Feature Similarity Weighting Matrix
To allow the similarity engine to be customized (e.g. prioritizing file name similarity over creation dates), the distance math must support custom feature weight weights.

### Weighting Vector Structure
A float32 vector of size 42 ($W$) is defined:
$$W = [w_0, w_1, \dots, w_{41}]$$

- By default, all elements are set to $1.0$.
- **GUI Configurable Groups**:
  - **Path Weights** (Dims 3, 4, 5): Increase to prioritize folders/files close in path naming.
  - **Drive letter Weights** (Dims 6-8): Set to high (e.g. 5.0) to separate C drive matches from D drive matches.
  - **Date Weights** (Dim 10): Increase to prioritize files created on or around the same time.
  - **Extension Weights** (Dims 14-28): Set to high to strictly group matching file types (.py with .py).
  
### Weighted Distance Equation (Python Pseudocode)
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

## 2. Mock Data Generator (Seeding Script)
To test visual graph performance with thousands of nodes without performing lengthy drive scans, use this Python script template to generate structured test records:

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

## 3. Database Maintenance & Cleanup Strategy
Over time, files are deleted, renamed, or modified on disk. The database requires maintenance to clean stale data.

### Cleanup Execution Plan
1. **Orphan File Removal**:
   - Query all paths in the DB.
   - Run low-priority `os.path.exists` validation in batches.
   - Delete records for files that are no longer present on disk.
2. **SQLite VACUUM**:
   - Reclaims free space in the database file after deletes.
   - Run `VACUUM` programmatically from settings or when orphan nodes deleted exceed 20% of total nodes.
