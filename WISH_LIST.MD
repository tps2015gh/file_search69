# File Search 69 - Wish List

This document tracks future features and architectural upgrades to be implemented when development resumes.

## 1. Global Search Capacity
**Status:** Planned
**Description:** Implement a robust text/regex search capacity that returns multiple rows/items matching a query, bypassing or complimenting the vector distance calculations.

### For AI Agents (Headless Pipeline)
- Add a `--search` flag to `ai_skill.py` (e.g., `python ai_skill.py --search "config"`).
- Allows the AI to instantly locate groups of files by name or partial string match using the SQLite database instead of doing slow terminal `grep` commands across the whole drive.
- Update `mcp_server.py` to expose a `search_files` tool alongside the existing `find_structural_neighbors` tool.

### For Humans (Visual UI)
- Add a floating UI Search Bar to the PySide6 / vis.js graph.
- When a human types a query, instantly filter, highlight, or zoom the camera to the nodes that match the search result.
- Provides an immediate visual cluster of where certain types of files (e.g., "auth" or ".js") live in the project's physical architecture.
