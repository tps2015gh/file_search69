import sys
import os
import json
import numpy as np
from scipy.spatial.distance import cdist
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl
from database import get_all_files, init_db
from crawler import crawl_directory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Search 69 - Core MVP")
        self.resize(1200, 800)
        
        self.webview = QWebEngineView()
        
        # Allow local HTML to load remote scripts (unpkg)
        settings = self.webview.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        
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
        
        # 4. Prepare edges and track node entropy (degree)
        edges = []
        node_degrees = { f['id']: 0 for f in files }
        
        for i in range(len(files)):
            # argsort sorts ascending, index 0 is self (dist 0), so take 1 to 3
            nearest_indices = np.argsort(dist_matrix[i])[1:4]
            for j in nearest_indices:
                # Add edge if distance is relatively small
                if dist_matrix[i, j] < 10.0: 
                    from_id = files[i]['id']
                    to_id = files[j]['id']
                    edges.append({
                        'from': from_id,
                        'to': to_id
                    })
                    node_degrees[from_id] += 1
                    node_degrees[to_id] += 1
                    
        # Apply Heatmap (Entropy) and Dynamic Distance
        for node in nodes:
            d = node_degrees[node['id']]
            # Calculate heat: Assume ~15 edges is max heat
            heat = min(d / 15.0, 1.0)
            
            # Color gradient: Cold (Blue) -> Hot (Red)
            r = int(heat * 255)
            b = int((1 - heat) * 255)
            node['color'] = {
                'background': f'#{r:02x}22{b:02x}',
                'border': '#ffffff'
            }
            # Hot nodes grow slightly larger
            node['size'] = 12 + (heat * 15)
            
        for edge in edges:
            d1 = node_degrees[edge['from']]
            d2 = node_degrees[edge['to']]
            # Heatmap Force: If nodes have high entropy, force the spring length to be much longer!
            edge['length'] = 100 + ((d1 + d2) * 15)
                    
        # 5. Send data to JavaScript engine
        nodes_json = json.dumps(nodes)
        edges_json = json.dumps(edges)
        
        js_code = f"renderGraph({nodes_json}, {edges_json});"
        self.webview.page().runJavaScript(js_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check if user provided a custom path via command line
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        if os.path.isdir(target_path):
            print(f"Custom path provided. Wiping old database and crawling: {target_path}")
            if os.path.exists("file_search.db"):
                os.remove("file_search.db")
            crawl_directory(os.path.abspath(target_path))
        else:
            print(f"Error: {target_path} is not a valid directory.")
            sys.exit(1)
            
    # If no DB exists, prompt the user with a GUI folder selection
    elif not os.path.exists("file_search.db"):
        from PySide6.QtWidgets import QFileDialog
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setWindowTitle("Select a Folder to Index for File Search 69")
        
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            print(f"Crawling selected directory: {selected_dir}")
            crawl_directory(os.path.abspath(selected_dir))
        else:
            print("No folder selected. Falling back to crawling the _DESIGN_ directory...")
            crawl_directory(os.path.abspath("_DESIGN_"))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
