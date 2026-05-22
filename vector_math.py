import numpy as np
import os
import hashlib

def compute_42_dim_vector(file_path, is_folder, size_bytes, create_time, is_hidden, is_system, is_temp):
    vec = np.zeros(42, dtype=np.float32)
    
    # Dim 0: is_folder
    vec[0] = 1.0 if is_folder else 0.0
    
    # Path characteristics
    name = os.path.basename(file_path)
    vec[1] = 1.0 if any('\u0e00' <= c <= '\u0e7f' for c in name) else 0.0 # contains Thai
    vec[2] = 1.0 if any('a' <= c.lower() <= 'z' for c in name) else 0.0 # contains English
    
    parts = file_path.split(os.sep)
    vec[3] = min(len(parts) / 10.0, 1.0) # Depth
    vec[4] = min(len(file_path) / 100.0, 1.0) # Path length
    vec[5] = min(len(os.path.dirname(file_path)) / 100.0, 1.0) # Parent length
    
    # Drive letter
    drive = os.path.splitdrive(file_path)[0].upper()
    if drive == 'C:': vec[6] = 1.0
    elif drive == 'D:': vec[7] = 1.0
    else: vec[8] = 1.0
    
    # Size and Time
    if not is_folder:
        vec[9] = np.log1p(size_bytes) / 30.0 # Normalized log size
    
    # Normalize time between 2020 and 2030 roughly
    min_time = 1577836800 # 2020
    max_time = 1893456000 # 2030
    vec[10] = max(0.0, min(1.0, (create_time - min_time) / (max_time - min_time)))
    
    vec[11] = 1.0 if is_hidden else 0.0
    vec[12] = 1.0 if is_system else 0.0
    vec[13] = 1.0 if is_temp else 0.0
    
    # Extensions (Dims 14-28)
    ext = os.path.splitext(name)[1].lower()
    exts = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.jpg', '.png', '.pdf', '.zip', '.exe', '.dll', '.csv']
    if not is_folder and ext in exts:
        idx = exts.index(ext)
        vec[14 + idx] = 1.0
    elif not is_folder:
        vec[28] = 1.0 # Other ext
        
    # Name hashing (Dims 29-41)
    hash_val = int(hashlib.md5(name.encode()).hexdigest(), 16)
    for i in range(13):
        vec[29 + i] = ((hash_val >> (i * 8)) & 0xFF) / 255.0

    return vec
