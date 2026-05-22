# Development Policy

This document details the environment requirements, language/technology selections, and coding rules for the project.

---

## 1. Environment & Target Platform
- **Primary Target OS**: Windows 11.
  - Development must prioritize Windows 11 directory structures, paths (e.g., backslashes vs forward slashes), and system file attributes (hidden, system, temp).
  - The application must support scanning of root drive letters (e.g., `C:\`, `D:\`, etc.) and handle drive-specific errors.
- **Secondary Target OS**: macOS, Linux (Cross-platform compatibility must be maintained where possible, but Windows 11 is the primary focus).

---

## 2. Technology Stack & Language Selection
- **Programming Language**: **Python (Version 3.10+)**
  - **GUI Framework**: `PySide6` (Qt for Python). Provides native-looking UI widgets, CSS-like styling (QSS), and robust threading utilities.
  - **Vector Computations**: `NumPy` & `SciPy` (KD-Tree) for high-speed matrix distances.
  - **Reasoning**: While Go (Golang) offers extremely fast multi-threaded file traversal, Python provides a unified ecosystem for both advanced vector mathematics (NumPy) and complex UI/graph rendering. Combining Go and Python introduces inter-process/C-binding complexity. Using Python with optimized system calls (`os.scandir`) and background workers provides the best balance of speed, mathematical capability, and GUI richness.

---

## 3. Crawler Ignore Policies
To prevent scanning files that cause performance degradation or access violations, the crawler must enforce ignore rules:

### A. Default Ignore Paths
The system must skip the following paths by default:
- `.git` folders
- Windows system paths:
  - `C:\Windows`
  - `C:\System Volume Information`
  - `C:\$Recycle.Bin`
  - `C:\$WINDOWS.~BT`
  - `C:\$WinREAgent`
  - System paging files: `pagefile.sys`, `hiberfil.sys`, `swapfile.sys`
- Temporary folders (e.g., User AppData Temp folders).

### B. User-defined Ignore Rules
- The application will support a `.ignore` file (placed in the root of any scanned folder) where users can specify glob patterns (e.g., `*.tmp`, `node_modules/`, `dist/`).

---

## 4. Safety & Performance Policies
To prevent PC/notebook slowdown and crash loops:

### Policy A: CPU Throttling
- The crawler thread must sleep for at least `5ms` after processing every block of `100` files to yield CPU time back to the OS.
- Never run filesystem walks on the UI main thread.

### Policy B: Exception Immunity
- File system walking must gracefully catch `PermissionError`, `FileNotFoundError`, and `OSError` without halting the indexing process. Any failed paths should be logged silently.

### Policy C: Thread-Safe SQLite Writes
- SQLite operations must use separate database connections per thread. 
- The crawler must write in transactions (chunk size: 1000 files) rather than single statements to prevent disk-write bottlenecks.

### Policy D: Adaptive Throttling & UI Responsiveness
- The GUI must implement a responsiveness monitor that tests event loop latency.
- If main thread event loop latency exceeds `50ms`, the background crawler thread must be throttled by dynamically increasing its micro-sleep duration.
- Live progress indicators (e.g., Progress bar and statistics dashboard) must receive updates via safe thread signals to prevent race conditions.

---

## 5. Review & Verification Policy
- **Unit Testing Requirement**: Every mathematical dimension calculation (0 to 41) must have a corresponding unit test verifying value bounds `[0.0, 1.0]` or `[-1.0, 1.0]` (refer to the dimension definitions in [04_SCHEMA.MD](file:///C:/dev3/file_search69/_DESIGN_/04_SCHEMA.MD)).
- **Validation**: Mock filesystem directory scans must be used in testing to prevent dependency on real user directories.
