# Database Schema & Vector Mapping

## Database Tables

### `files`
Stores file/folder metadata, feature flags, and computed vector representation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique auto-incrementing ID |
| `full_path` | TEXT | UNIQUE, NOT NULL | Complete absolute path |
| `parent_path` | TEXT | NOT NULL | Complete path of parent directory |
| `name` | TEXT | NOT NULL | Filename or folder name |
| `is_folder` | BOOLEAN | NOT NULL | 1 for folder, 0 if file |
| `size_bytes` | INTEGER | NOT NULL | File size in bytes (0 for folder) |
| `create_time` | INTEGER | NOT NULL | Unix epoch timestamp |
| `is_hidden` | BOOLEAN | NOT NULL | 1 if hidden file attribute is set |
| `is_system` | BOOLEAN | NOT NULL | 1 if system file attribute is set |
| `is_temp` | BOOLEAN | NOT NULL | 1 if name contains tmp/temp/~$ indicators |
| `vector_blob` | BLOB | NOT NULL | Binary serialized float32 array (42 dimensions) |

### `directories`
Configured paths to scan.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique ID |
| `path` | TEXT | UNIQUE, NOT NULL | Directory path added by user |
| `last_scanned` | INTEGER | | Last completed sync timestamp |

### `ignores`
Contains `.ignore` configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique ID |
| `pattern` | TEXT | NOT NULL | Glob pattern or folder name to skip |

---

## The 42-Dimension Vector Representation
To compute vector similarity, each file/folder is mapped to a 42-dimensional vector of floating-point values normalized between `[0, 1]` or standard normal `[-1, 1]`.

| Dim Index | Feature Name | Dimension Size | Description & Normalization |
|-----------|--------------|----------------|-----------------------------|
| **0** | `is_folder` | 1 | `1.0` if folder, `0.0` if file |
| **1** | `is_thai` | 1 | `1.0` if Thai characters found in name, `0.0` otherwise |
| **2** | `is_english` | 1 | `1.0` if English characters found, `0.0` otherwise |
| **3** | `folder_depth` | 1 | Number of path separators normalized by dividing by max depth (capped at 20) |
| **4** | `fullpath_len` | 1 | String length of full path normalized by max length (capped at 260) |
| **5** | `parentpath_len` | 1 | String length of parent path normalized (capped at 260) |
| **6-8** | `drive_letter` | 3 | One-hot encoded drive: `[C:, D:, other]` |
| **9** | `file_size_log` | 1 | Log-scaled size: `log(size_bytes + 1) / log(max_size_bytes_cap)` |
| **10** | `create_date_norm`| 1 | Unix timestamp normalized between min and max creation dates in the DB |
| **11** | `is_hidden` | 1 | `1.0` if hidden, `0.0` otherwise |
| **12** | `is_system` | 1 | `1.0` if system, `0.0` otherwise |
| **13** | `is_temp` | 1 | `1.0` if temp, `0.0` otherwise |
| **14-28** | `extension_one_hot`| 15 | One-hot encoded extensions: `[txt, md, py, js, html, css, pdf, docx, xlsx, zip, png, jpg, mp3, mp4, other/folder]` |
| **29-35** | `start_letters_folder`| 7 | Hashed values based on the first two letters of the parent folder name (mapped to 7 bins via sine-wave hash function) |
| **36-41** | `start_letters_file`| 6 | Hashed values based on the first two letters of the file name (mapped to 6 bins) |

---

## Exact Implementation Algorithm (Python Code)
To guarantee consistency across different AI models, implement this exact python mapping logic:

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

## Architectural Decision: Why 42 Dimensions instead of 384 (Semantic Search)?
A core anchor of this project is the deliberate choice of a handcrafted 42-dimension vector over a standard 384-dimension LLM embedding (like `all-MiniLM-L6-v2`).
1. **Explicit Metadata Control (No Black Box)**: In a 384-dimensional semantic vector, the meaning of each dimension is unknown, making it impossible to apply exact weights to specific properties (e.g., "Prioritize Creation Date"). In our 42-dimensional vector, every dimension represents a known, strict property, giving the user total mathematical control via GUI sliders.
2. **Crawling Speed & Zero AI Overhead**: Generating 384-dimensional AI embeddings for every file requires passing strings through a neural network, drastically reducing crawler speed and heavily taxing the CPU/GPU. Our 42-dimension structural math (hashing, log scaling) takes microseconds, allowing the crawler to process thousands of files per second with minimal CPU usage.
3. **RAM & Storage Efficiency**: 42 float32 dimensions consume roughly 168 bytes per file (~16 MB for 100,000 files). A 384-dimensional vector consumes 1536 bytes (~150 MB for 100,000 files). The 42-dimensional approach guarantees lightning-fast memory-mapped comparisons in RAM.
