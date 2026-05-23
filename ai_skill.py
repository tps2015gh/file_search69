import sys
import os
import json
import numpy as np
import argparse
from scipy.spatial.distance import cdist
from database import get_all_files, DB_PATH

def main():
    parser = argparse.ArgumentParser(description="AI Skill: Find structurally similar files.")
    parser.add_argument("target_path", nargs="?", default="", help="The absolute or relative path to the target file.")
    parser.add_argument("--limit", type=int, default=5, help="Number of similar files to return.")
    parser.add_argument("--search", type=str, help="Search files by path or name directly, bypassing structural math.")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(json.dumps({"error": f"Database not found at {DB_PATH}. Run crawler.py first."}))
        sys.exit(1)

    files = get_all_files()
    
    if args.search:
        results = []
        search_query = args.search.lower()
        for f in files:
            if search_query in f['path'].lower():
                results.append({
                    "name": f['name'],
                    "path": f['path']
                })
        print(json.dumps({"search_query": args.search, "matches": results[:args.limit]}, indent=2))
        sys.exit(0)
        
    if not args.target_path:
        print(json.dumps({"error": "Must provide either target_path or --search."}))
        sys.exit(1)
    
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
