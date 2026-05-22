# UI/UX & Graph Interaction Specification

This document details the interface layout, styling palettes, and interactive behaviors for the node graph visualization components.

---

## 1. Visual Design & Aesthetics (Premium Dark Theme)
To create a high-fidelity visual experience inspired by modern graph databases and IDE editors:

| UI Component | Color (HEX/HSL) | Design Style |
|--------------|-----------------|--------------|
| **App Background** | `#11111b` (Deep Slate) | Solid dark canvas |
| **Sidebar Panels** | `#1e1e2e` (Charcoal) | Semi-transparent glassmorphism (`backdrop-filter`) |
| **Grid Lines** | `#313244` (Muted Blue-Gray) | Subtle crosshairs, 25% opacity |
| **Default Node** | `#cba6f7` (Soft Lavender) | Circular node with smooth outer glow |
| **Active/Selected Node** | `#89b4fa` (Vibrant Cyan) | High-contrast neon pulse |
| **Path Links (Edges)** | `#45475a` (Steel Gray) | Solid connecting line |
| **Similarity Links** | `rgba(166, 227, 161, 0.4)` (Neon Green) | Semi-transparent glowing connection |

---

## 2. Interactive Graph Behaviors (Obsidian-Style)

### A. Physics-Engine Layout & Density Management
To prevent dense clusters where nodes overlap and file/folder names become unreadable (common in high-similarity vector spaces or nested directories), the graph visualizer provides two distinct separation controls:

1. **"Separate More" (Global Spacing Slider)**:
   - **Target**: The entire network layout.
   - **Mechanism**: Adjusts the global electrostatic repulsion force (gravitational constant) and spring length between all connected nodes.
   - **UI Controls**: Slider ranging from `1.0x` to `4.0x` (default `1.0x`).
   - **Implementation Details**:
     - In **vis.js (ForceAtlas2)**: Scales the `gravitationalConstant` from `-50` (dense) to `-400` (widely spaced) and `springLength` from `80` to `350`.
     - In **D3.js**: Scales the charge force `d3.forceManyBody().strength()` and the link distance `d3.forceLink().distance()`.
     - **Result**: Expands the entire graph canvas uniformly, pushing all nodes further apart.

2. **"Separate Near" (Local Collision/Overlap Slider)**:
   - **Target**: Closely packed, overlapping, or high-density clusters.
   - **Mechanism**: Adjusts the collision radius threshold or overlap avoidance multiplier. Unlike global spacing, this only pushes nodes apart if they violate a mutual proximity boundary, leaving distant nodes unaffected.
   - **UI Controls**: Slider ranging from `1.0x` to `3.5x` (default `1.5x` text width buffer).
   - **Implementation Details**:
     - **Dynamic Proximity Boundary**: Each node's text length is measured (e.g., $W = \text{length(filename)} \times 8\text{ pixels}$). The base collision radius is $R = W / 2 + 10$.
     - The **Separate Near** slider multiplies this radius: $R_{\text{effective}} = R \times \text{slider\_value}$.
     - In **vis.js**: Dynamically updates the `avoidOverlap` force setting (from `0.0` to `1.0`) and adjusts the padding between nodes.
     - In **D3.js**: Dynamically updates the collision force `d3.forceCollide().radius(d => d.baseRadius * slider_value)`.
     - **Result**: Dense, overlapping nodes are forced apart to preserve readability, while cleanly spaced nodes remain in place.

3. **Collision Detection**: Enforces a minimum radial distance buffer around each node equivalent to $1.5\text{x}$ the text width of the node's full file name, preventing overlapping text.
4. **Adaptive Central Gravity**: Prevents disconnected nodes from flying off-screen while keeping central clusters spaced out.

---

### B. Graph Shaking Options (Anti-Hanging & De-clustering)
When nodes get stuck in local energy minima during force-directed layout calculations, text overlap can persist. Shaking injects thermal energy (random coordinate offsets) to force simulation recalculations:

1. **Shake All Nodes (Global Jitter)**:
   - **Action**: Perturbs the coordinates of *every* node on the canvas.
   - **Formula**:
     $$x_i \leftarrow x_i + \Delta x, \quad y_i \leftarrow y_i + \Delta y \quad (\text{where } \Delta x, \Delta y \in [-100, 100] \text{ pixels})$$
   - **Trigger**: Click **[ SHAKE ALL NODES ]** button in the sidebar.
   - **Use Case**: When the entire graph contains multiple overlapping clusters or is locked in a cluttered configuration.

2. **Shake Cluster / Some Nodes (Neighborhood Jitter)**:
   - **Action**: Applies a localized perturbation to a clicked node and its immediate topological neighbors.
   - **Formula**: Applies coordinate offsets ($\Delta \in [-50, 50]$px) only to the target node and nodes within $N$ steps (default $N = 1$ or $N = 2$ hops).
   - **Trigger**: Click **[ Jitter Selected Cluster ]** or double-click a node cluster region.
   - **Use Case**: Breaking up a single dense group of highly similar vectors without altering the layout of other well-spaced parts of the graph.

3. **Shake Overlapping Nodes (Proximity Jitter)**:
   - **Action**: Automatically detects nodes whose center-to-center distance is less than their combined collision radius, and injects a tiny random displacement ($\Delta \in [-25, 25]$px) to resolve the overlap.
   - **Trigger**: Runs automatically when the physics engine detects a layout stall with unresolved collisions.


### C. Node Styling Options
- **Node Size**:
  - *Standard*: Uniform size.
  - *By File Size*: Logarithmic scaling `size = log(file_bytes) * factor`.
- **Node Color**:
  - *By File Type*: Colors representing program files, documents, images, folders, etc.
  - *By Folder Depth*: Nodes fade color based on directory structure depth.

### D. Hover & Selection Cards
- **Hover**: Displays a floating card listing: Full Filename, Absolute Path, Size, Create Time, and Text Encoding.
- **Selection**: Highlights the selected node and dims non-connected components.
- **Double-Click**: Opens the file in the default Windows system application.

### E. Viewport Navigation & Keybinds (Mouse & Keyboard Panning)
To support rapid and intuitive navigation across small and large graph structures alike:
1. **Mouse Drag Panning**: Dragging the mouse left-click on any empty canvas area moves the viewport camera dynamically. Enabled via vis.js `interaction: { dragView: true }`.
2. **Keyboard Panning (WASD & Arrow Keys)**:
   - Registers a `keydown` window event listener to intercept navigation keys:
     - **W** or **Arrow Up**: Pans the camera Up.
     - **S** or **Arrow Down**: Pans the camera Down.
     - **A** or **Arrow Left**: Pans the camera Left.
     - **D** or **Arrow Right**: Pans the camera Right.
3. **Zoom-Compensated Speed Control**:
   - The scroll displacement step is dynamically divided by the current network zoom scale factor:
     $$\Delta_{\text{scroll}} = \frac{40\text{ pixels}}{\text{CurrentScale}}$$
   - This ensures camera movement speed remains visually constant relative to the screen size, preventing extremely sluggish movement when zoomed in and overly hyperactive jumps when zoomed out.


---

## 3. Sidebar Controls Layout
The left panel houses all controls for managing drives, search criteria, and graph density metrics:

```
+------------------------------------------------------+
|  [Search bar...]  [View: Path+Sim | Pure Sim]        |
+------------------------------------------------------+
|  Added Drives/Folders:                               |
|  [x] C:\Projects (2,450 files) [Remove]              |
|  [ + Add Path ]                                      |
+------------------------------------------------------+
|  Similarity Near Distance Threshold:                 |
|  Min <==================[ 0.72 ]==================> Max|
+------------------------------------------------------+
|  Max Rendered Nodes (Scale Limit):                   |
|  100 <=================[ 1,000 ]=================> 5k|
+------------------------------------------------------+
|  Graph Spacing & Spacing Controls:                    |
|  Separate More (Global Spacing): <=====[ 1.0x ]=====> |
|  Separate Near (Proximity Buffer): <===[ 1.5x ]=====> |
|  [x] Avoid Text Overlap (Collision Engine)            |
+------------------------------------------------------+
|  Node Shake & Jitter Functions:                      |
|  [ SHAKE ALL ]  [ SHAKE SELECTED ]  [ SHAKE OVERLAPS] |
+------------------------------------------------------+
|  Node Size Mode: [x] Uniform  [ ] By File Size        |
|  Node Color Mode: [x] File Type [ ] Directory Depth   |
+------------------------------------------------------+
```

---

## 4. Bottom Status & Resource Bar
The bottom bar displays crucial system resource statistics and highlights the real-time node count split (total indexed/calculated vs. currently rendered on canvas):

```
+--------------------------------------------------------------------------------------------------------------------------+
| Status: Ready | Nodes: 115,240 total (1,200 rendered) | RAM: 45.2 MB | Disk: 62% (128.5 GB free) | Log: import_progress.log |
+--------------------------------------------------------------------------------------------------------------------------+
```

---

## 5. High-Scale Optimization & Node Pruning (100,000+ Nodes)
To maintain 60 FPS UI responsiveness on Windows 11 when scanning massive volumes (e.g. 100,000+ files), the system uses a tiered pruning architecture that prevents database, memory, and GPU bottlenecks.

### A. Backend Pruning & Importance Weighting
Instead of loading all 100,000+ nodes, the Python backend calculates similarity weights and importance scores to prune the payload:
1. **Max Rendered Nodes Limit ($N_{\text{max}}$)**: A GUI slider (default `1,000` nodes, range `100` to `5,000`) acts as a hard filter for active graph rendering.
2. **Importance Scoring Algorithm**:
   Each file node is assigned an importance score $S_i$ relative to the user's active search parameters:
   $$S_i = w_{\text{similarity}} \cdot \text{CosineSimilarity} + w_{\text{size}} \cdot \log_{10}(\text{FileSizeBytes}) + w_{\text{recency}} \cdot \text{RecencyScore}$$
   - Only the top $N_{\text{max}}$ nodes with the highest importance scores are queried and sent to the frontend graph.
3. **Database-Level Windowing**:
   The SQLite query utilizes SQL-level LIMIT and ORDER BY clauses to fetch only the top $N_{\text{max}}$ nodes. This avoids reading millions of rows into Python memory.
4. **Calculated vs. Rendered Counter**:
   - The SQLite query counts the full dataset match count (e.g. 115,240 nodes) using `COUNT(*)` (fast via indexed queries).
   - The backend sends both the **Calculated Count** and the **Pruned Node Dataset** (e.g. 1,200 nodes) to the GUI. The GUI displays the real calculated count in the status bar: `Nodes: 115,240 total (1,200 rendered)`.

### B. Frontend Rendering & Physics Optimization (vis.js/D3.js)
If the rendering subset is still large (e.g., $1,000$ to $5,000$ nodes), the HTML canvas implements these runtime optimizations:
1. **Dynamic Physics Freeze**:
   - For graphs under 1,500 nodes: Physics engine runs continuously.
   - For graphs over 1,500 nodes: The physics engine is stabilized for exactly 50 iterations upon load, then automatically frozen (`physics: false`). Interactive dragging of a single node runs physics locally for that node only, preventing global CPU spikes.
2. **Level of Detail (LoD) Scaling**:
   - **Zoom level < 0.4 (Far Out)**: Hide all text labels. Render nodes as simple 4px circles. Draw edges as thin 0.5px gray lines without glowing effects.
   - **Zoom level 0.4 to 0.8 (Medium)**: Render text labels only for nodes with high importance scores ($S_i > 0.8$) or folder nodes.
   - **Zoom level > 0.8 (Close Up)**: Render all text labels, node glows, and similarity links.
3. **Viewport Frustum Culling**:
   - Nodes whose visual coordinates lie outside the current viewport boundaries $+ 100\text{px}$ padding are skipped during the canvas draw loop.
   - Edges connecting two culled nodes are not drawn.

