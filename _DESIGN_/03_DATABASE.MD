# Database Strategy

## Overview
To ensure extremely fast search times and prevent computer slowdown, the application employs a hybrid indexing strategy utilizing a local SQLite database for relational metadata and a memory-mapped/in-memory vector index for similarity queries.

## Technology Stack
1. **SQLite Database**
   - Stores paths, file attributes, ignore configs, and pre-calculated vectors.
   - Run in Write-Ahead Logging (`WAL`) mode with `synchronous = NORMAL` to ensure fast writes during heavy crawler operations without locking the GUI.
2. **In-Memory Similarity Index**
   - Keeps vector embeddings (NumPy float32 arrays) loaded in memory as a matrix.
   - When a search is performed, distance calculations are computed in parallel using NumPy vectorized operations (matrix-vector multiplication for Cosine distance).
   - For scale (e.g., >100,000 files), a SciPy KD-Tree is constructed to query neighbors within a specific Euclidean radius efficiently.

## Optimization Techniques
- **Bulk Insertions**: Crawler results are inserted in batches (e.g., 500-1000 records per transaction) to minimize write overhead.
- **Dirty Flagging**: Stored files have a `dirty` flag. When the filesystem watcher registers a modified file, only that file's properties/vectors are updated.
- **Pruned Graphs**: For visualization, graph queries are bounded to the top-K similar files (e.g., K=50) to avoid overloading the visualization canvas.

## Architectural Decision: Why not ChromaDB?
A core anchor of this project is the rejection of dedicated vector databases like ChromaDB in favor of SQLite + NumPy/SciPy.
1. **Dynamic Dimension Weighting**: ChromaDB (and HNSW indices in general) requires the distance metric to be fixed at index time. Our project requires a "Feature Similarity Weighting Matrix" allowing the user to dynamically adjust weights via GUI sliders (e.g., prioritizing Date over Extension). A pre-built HNSW graph cannot support dynamic dimension weighting without a full re-index. NumPy handles this instantly in-memory.
2. **Write Overhead**: SQLite in WAL mode is significantly faster for rapid, small-batch disk inserts during a live crawler operation. ChromaDB carries overhead from maintaining HNSW graphs, slowing down the crawler.
