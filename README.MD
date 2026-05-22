# File Search 69

File Search 69 is an ultra-fast, structural filesystem mapping tool built with Python, PySide6, SQLite, and vis.js. It transforms a local directory structure into a mathematical 42-dimensional vector space.

## The Dual-Role Architecture

This project was built through a collaborative effort between a **Human Developer** and an **AI Agent**. It is intentionally designed with two separate pipelines to serve both:

### 1. For Humans (Visual UI)
The human interface uses a PySide6 WebEngine to render an interactive, physics-based 2D node graph.
- **Run:** `python main.py [optional_path]`
- **Features:** 12-second live arranging animation, Entropy Heatmap (hot nodes turn red and push neighbors away), and Click-to-Copy file paths.

### 2. For AI Agents (Headless Pipeline)
AI Agents don't have eyes to see a GUI, so we built a strict **Headless Pipeline** using the raw SQLite vector database (`PRAGMA journal_mode=WAL` for infinite concurrency). An AI can mathematically query the structural similarities of a codebase instantly without wasting context window tokens reading files.
- **Agent Skill (CLI):** 
  ```bash
  python ai_skill.py "target_file.py" --limit 5
  ```
  Returns a strict JSON array of the most structurally similar files using NumPy Euclidean distance. Zero memory footprint.
- **MCP Server:**
  ```bash
  python mcp_server.py
  ```
  A lightweight JSON-RPC server implementing the Model Context Protocol (MCP) over standard I/O. It exposes the `find_structural_neighbors` tool. It isolates heavy NumPy math to subprocesses to guarantee no memory leaks.

## 🚀 Key Architectural Concepts
1. **42-Dimension Custom Vector**: A highly optimized, handcrafted vector structure where every dimension maps to a strict property (e.g., File Size, Creation Date, File Extension). This guarantees lightning-fast processing without the overhead of AI neural networks.
2. **Dynamic Dimension Weighting**: Real-time GUI sliders that allow the user to instantly adjust the importance of features (e.g., heavily weighting "Date" similarity to group files made on the same day).
3. **SQLite WAL + NumPy**: Choosing a hybrid approach of SQLite for relational metadata and in-memory NumPy/SciPy KD-Trees for vector math over dedicated vector databases like ChromaDB to ensure extreme crawling speeds and math flexibility.
4. **Visual Node Physics**: Built for scale, optimizing physics engines and viewport culling to smoothly render 100,000+ files as interactive nodes on a canvas.

## 👥 The Team
This project's design was entirely developed through an intensive pair-programming and brainstorming session between Human and AI:

- **The Human (tps2015gh)**: Lead Visionary, System Architect, and Director.
- **Antigravity (AI)**: Primary AI Agent, Co-Architect, and Technical Documenter.
- **AI Subagents**: Specialized AI assistants providing research and localized task support.

## 📁 Repository Structure
- `_DESIGN_/`: The core English design documents covering the plan, architecture, database strategy, vector schemas, and UI/UX flows.
- `_DESIGN_TH_/`: The complete Thai translations of all design documents.
- `doc_migrate/`: Task tracking and Kanban boards for the planning phase.
- `generate_audio.py`: A utility script to generate Thai text-to-speech audio of the design documents using Microsoft Edge TTS.

## 📄 License
This project's design is licensed under the **MIT License**. See the `LICENSE` file for more details.
