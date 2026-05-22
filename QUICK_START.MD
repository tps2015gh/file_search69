# File Search 69 - Core MVP Quick Start

Welcome to the File Search 69 MVP! This quick start guide will get you up and running with the interactive, physics-based file visualization graph.

## Prerequisites
- Python 3.10+
- Windows OS (Tested on Windows 11)

## 1. Install Dependencies
Open your terminal in the project directory (`C:\dev3\file_search69`) and install the required Python packages:
```powershell
pip install -r requirements.txt
```

## 2. Run the Application
Start the main PySide6 application:
```powershell
python main.py
```

### What happens on the first run?
1. The application will detect that no local database exists.
2. It will automatically run the background crawler to scan the `_DESIGN_` folder.
3. It extracts file metadata, calculates the custom 42-dimension structural vector for each file, and saves it to a local SQLite database (`file_search.db`).
4. The application window will open, rendering an interactive graph where files are connected by lines based on their mathematical similarity.

## 3. Interact with the Graph
- **Scroll Wheel**: Zoom in and out of the graph.
- **Click & Drag Background**: Pan around the canvas.
- **Click & Drag Node**: Pull individual files around. The Barnes-Hut physics engine will automatically react and adjust the surrounding nodes.
- **Hover**: Hover your mouse over any node to reveal a tooltip showing the file's full path.
