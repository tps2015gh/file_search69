import os
import stat
from vector_math import compute_42_dim_vector
from database import insert_files, init_db

def is_hidden(filepath):
    try:
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    except:
        return False

def crawl_directory(target_dir):
    init_db()
    batch = []
    count = 0
    print(f"Crawling {target_dir}...")
    
    for root, dirs, files in os.walk(target_dir):
        # Exclude .git folder from being scanned
        if '.git' in dirs:
            dirs.remove('.git')
            
        # Process files
        for name in files:
            full_path = os.path.join(root, name)
            try:
                st = os.stat(full_path)
                size = st.st_size
                ctime = st.st_ctime
                hidden = is_hidden(full_path)
                is_temp = 'temp' in name.lower()
                
                vec = compute_42_dim_vector(full_path, False, size, ctime, hidden, False, is_temp)
                batch.append((full_path, root, name, False, size, ctime, hidden, False, is_temp, vec.tobytes()))
                count += 1
                
                if len(batch) >= 100:
                    insert_files(batch)
                    batch = []
            except Exception as e:
                pass
                
        # Short circuit for MVP (max 500 files to keep it small)
        if count >= 500:
            break
            
    if batch:
        insert_files(batch)
    print(f"Crawled {count} files and saved vectors to DB.")

if __name__ == '__main__':
    # Crawl the design directory as a test run
    crawl_directory(r"C:\dev3\file_search69\_DESIGN_")
