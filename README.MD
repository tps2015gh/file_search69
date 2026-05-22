# File Search 69 (Design Only)

**File Search 69** is the blueprint for a high-performance, real-time filesystem indexer and visualizer. It is designed to group and map local files by their structural similarities into an interactive, physics-based node graph, bringing an "Obsidian-like" visual experience to your entire operating system.

> **Note:** This repository is currently dedicated **exclusively to the architectural design, schemas, and planning documents**. There is no implementation code included here.

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
