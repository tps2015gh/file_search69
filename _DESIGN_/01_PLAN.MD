# Implementation Plan

## Project Overview
A high-performance GUI application for searching files and folders using a custom vector-based similarity engine. The application visually represents file relationships and vector similarities using an Obsidian-style node graph.

## Core Features
1. **File System Crawler**: Recursively scans user-defined directories and drives (such as `C:\`, `D:\`), respecting `.ignore` files. Default ignore settings skip `.git` folders and Windows system paths (e.g. `C:\Windows`, `C:\System Volume Information`).
2. **Vector Extractor**: Calculates a numerical vector (up to 42 dimensions) based on file properties (path, size, encoding, type, etc.).
3. **Similarity Search Engine**: Queries files by comparing their multi-dimensional vectors.
4. **Interactive Graph GUI**: 
   - View 1: Physical path-based graph showing links of path AND links to very similar files/folders within a specified near distance.
   - View 2: Vector similarity graph showing links of near vector similarity (nearest neighbors).
5. **Node Overlap Prevention & Density Settings**: Includes sliders for "Separate More" (global spacing repulsion) and "Separate Near" (local collision/overlap padding multiplier) to dynamically expand node distances and prevent name overlaps.
6. **"Shake Graph" Jitter Controls**: Interactive options to shake all nodes (global jitter), shake a selected cluster (neighborhood jitter), or shake overlapping nodes (proximity jitter) to break up dense clusters.
7. **Multi-Drive & Directory Support**: Add multiple root paths or entire drive letters to the search index.
8. **Progress Reporting & Non-blocking UI**: As paths are entered, the system crawls and computes vectors on background threads. Real-time progress is reflected in the GUI.
9. **Run-time Kanban Process Board**: Instead of a simple progress bar, the import/indexing UI displays a real-time Kanban board showing files moving through processing columns (Discovered, Extracting, Writing, Indexed).
10. **Crash & Hang Detection Log**: A dedicated log file (`import_progress.log`) tracks indexing steps to diagnose crash or hang events.
   - Automatically cleared (truncated to blank) upon application startup.
   - Writes the start date and time as the first line of the log on every new import run.
11. **Real-time Resource Dashboard**: The GUI screen displays system performance stats during runs:
   - **Total Nodes**: Total files/folders currently loaded/indexed, split by calculated vs rendered (e.g. `115,240 total (1,200 rendered)`).
   - **Memory Usage**: Current RAM consumption of the application process.
   - **Disk Usage**: Total storage utilization of the host drive(s) being crawled.
12. **Adaptive UI Throttling**: Checks UI event loop latency and overall CPU/IO load. If responsiveness drops, it dynamically throttles the crawling/indexing worker thread.
13. **High-Scale Graph Optimization (100k+ Nodes)**: Dynamic SQL-level LIMIT windowing and relevance ranking (importance score) limits GUI rendering to $N_{\text{max}}$ nodes. Features frontend viewport frustum culling, Level of Detail (LoD) zoom-based labels, and automatic physics freezes when node count exceeds 1,500.

---

## Development Progress (Kanban Board)
During project development, progress is tracked using the following Kanban board layout:

### Backlog
- [ ] Implement command line argument handler for debugging
- [ ] Implement manual database maintenance / vacuuming option in settings

### To Do
- [ ] Set up project structure & test runner
- [ ] Define the exact character hash algorithms for start letters (dimensions 29-41)
- [ ] Build PyQt6 styling sheet (QSS) for dark mode Obsidian-like interface

### In Progress
- [ ] Implement high-speed multi-threaded filesystem walker with default ignores
- [ ] Implement progress log file writer with startup auto-clearing
- [ ] Implement resource monitoring dashboard (Memory, Disk, Node counts)

### Testing / Verification
- [ ] Unit tests for 42-dimensional vector normalization bounds

### Done
- [x] Read prompt01.txt and clarify constraints
- [x] Design core system architecture (ARCHITECH.MD)
- [x] Design database strategy and table schemas (DATABASE.MD & SCHEMA.MD)
- [x] Define agent team roles and development policies (AGENT_DEV_TEAM.MD & DEVELOPMENT_POLICY.MD)

---

## Step-by-Step Plan
1. **Phase 1: Foundation & Crawler**
   - Implement the file system walker with multi-threading and CPU throttling.
   - Add `.ignore` parsing logic (similar to `.gitignore` glob patterns) and bake in default ignores.
   - Set up an incremental directory watcher using Win32 API (`ReadDirectoryChangesW`) or `watchdog`.
   - Implement background worker threading using Qt's `QThread` / `QRunnable` so indexing never blocks the GUI event loop.
2. **Phase 2: Logging & Crash Detection System**
   - Implement the `ImportLogger` class that truncates `import_progress.log` on startup and appends timestamps upon new import starts.
   - Log crucial milestones to detect where the process hangs.
3. **Phase 3: Vector Engine**
   - Define the mathematical representation of the 42 properties.
   - Implement feature extraction from file paths, parent paths, and metadata.
   - Normalize features (e.g., log-scale file size, normalize timestamps, one-hot encode extensions).
4. **Phase 4: Database & Storage**
   - Set up SQLite local database for persisting metadata and vector blobs.
   - Design indices for fast retrieval of sub-paths.
5. **Phase 5: Search & Resource Monitoring Logic**
   - Implement distance calculations (Cosine Similarity and Euclidean Distance).
   - Build a spatial index (e.g., KD-Tree or HNSW) for sub-millisecond similarity queries.
   - Integrate system resource monitors using `psutil` or standard OS library calls.
6. **Phase 6: GUI, Graph, & Kanban Progress View**
   - Build a PyQt6 / PySide6 interface with a search bar, folder manager, and a switchable dual-view graph canvas.
   - Design the **Run-time Kanban Process Board widget** to visually stack and move file counts/previews through columns.
   - Add the bottom status bar displaying: **Nodes (Calculated vs. Rendered Split)**, **Memory (RAM) Usage**, and **Disk Space Usage**.
   - Implement sliders in the GUI for **Separate More (Global Spacing)** and **Separate Near (Collision/Overlap)** that update options dynamically via Javascript in the WebEngine page.
   - Add a slider/control to adjust the **Max Rendered Nodes ($N_{\text{max}}$)** limit for backend pruning.
   - Add **[SHAKE ALL]**, **[SHAKE SELECTED]**, and **[SHAKE OVERLAPS]** GUI button interfaces.
   - Add a slider/control to adjust the "near distance" threshold for path similarity links.
   - Implement Level of Detail (LoD) zoom-based labels and automatic physics freezes in Javascript.
   - Implement mouse drag-panning and WASD/arrow key panning with zoom-compensated movement speed.
7. **Phase 7: Adaptive Performance Tuning**
   - Implement a heartbeat/latency monitor in the GUI event loop.
   - If the main thread's response latency rises above 50ms, send a signal to the worker threads to increase their sleep delay.
   - Apply node clustering/hiding for massive file counts to keep the UI interactive.
