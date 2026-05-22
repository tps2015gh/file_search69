import sys
import os
import json
import numpy as np
import argparse
from scipy.spatial.distance import cdist
from database import get_all_files

def main():
    parser = argparse.ArgumentParser(description="AI Skill: Find structurally similar files.")
    parser.add_argument("target_path", help="The absolute or relative path to the target file.")
    parser.add_argument("--limit", type=int, default=5, help="Number of similar files to return.")
    args = parser.parse_args()

    if not os.path.exists("file_search.db"):
        print(json.dumps({"error": "Database not found. Run crawler.py first."}))
        sys.exit(1)

    files = get_all_files()
    
    # Find target file vector
    target_vec = None
    target_name = os.path.basename(args.target_path)
    for f in files:
        if f['path'].lower().endswith(target_name.lower()):
            target_vec = f['vector']
            break
            
    if target_vec is None:
        print(json.dumps({"error": f"File {target_name} not found in database."}))
        sys.exit(1)
        
    # Calculate distances
    vectors = np.array([f['vector'] for f in files])
    target_vec = np.array([target_vec])
    
    distances = cdist(target_vec, vectors, metric='euclidean')[0]
    
    # Get top N+1 (to exclude self, which has distance 0)
    nearest_indices = np.argsort(distances)[1:args.limit+1]
    
    results = []
    for idx in nearest_indices:
        results.append({
            "name": files[idx]['name'],
            "path": files[idx]['path'],
            "distance": round(float(distances[idx]), 4)
        })
        
    # Return strict JSON for AI Agent consumption
    print(json.dumps({"target": target_name, "similar_files": results}, indent=2))

if __name__ == "__main__":
    main()
