import sys
import os
import json
import numpy as np
from scipy.spatial.distance import cdist
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from database import get_all_files, init_db
from crawler import crawl_directory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Search 69 - Core MVP")
        self.resize(1200, 800)
        
        self.webview = QWebEngineView()
        
        # Load HTML Graph Template
        html_path = os.path.abspath("graph.html")
        self.webview.setUrl(QUrl.fromLocalFile(html_path))
        self.webview.loadFinished.connect(self.on_load_finished)
        
        self.setCentralWidget(self.webview)
        
    def on_load_finished(self, ok):
        if not ok:
            print("Failed to load graph.html")
            return
            
        # 1. Fetch files and pre-calculated vectors from DB
        files = get_all_files()
        if not files:
            print("No files in DB. Run crawler first.")
            return
            
        # 2. Prepare nodes for vis.js
        nodes = []
        vectors = []
        for f in files:
            nodes.append({
                'id': f['id'],
                'label': f['name'],
                'title': f['path'] # Tooltip shows full path
            })
            vectors.append(f['vector'])
            
        # 3. Calculate pairwise distances (vector math)
        vectors = np.array(vectors)
        # Using euclidean distance on the 42-dimension vectors
        dist_matrix = cdist(vectors, vectors, metric='euclidean')
        
        # 4. Prepare edges (connect nearest neighbors)
        edges = []
        for i in range(len(files)):
            # argsort sorts ascending, index 0 is self (dist 0), so take 1 to 3
            nearest_indices = np.argsort(dist_matrix[i])[1:4]
            for j in nearest_indices:
                # Add edge if distance is relatively small
                if dist_matrix[i, j] < 10.0: 
                    edges.append({
                        'from': files[i]['id'],
                        'to': files[j]['id']
                    })
                    
        # 5. Send data to JavaScript engine
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)
        
        js_code = f"renderGraph({nodes_json}, {edges_json});"
        self.webview.page().runJavaScript(js_code)

if __name__ == "__main__":
    # For the MVP, automatically run the crawler on the _DESIGN_ folder if DB is empty
    if not os.path.exists("file_search.db"):
        print("First run detected: Crawling _DESIGN_ directory for mock data...")
        crawl_directory(os.path.abspath("_DESIGN_"))

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
