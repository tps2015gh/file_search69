# File Search 69 - Technical Roadmap & Implementation Status

## 1. Global Search Capacity
**Status:** ✅ IMPLEMENTED
**Description:** Robust text/regex search implemented for both AI and Human pipelines.
- **AI/Headless:** `ai_skill.py --search "query"` implemented.
- **UI:** Integrated search bar in graph visualization.
- **MCP:** `search_files` tool exposed to AI agents.

## 2. Headless Mode Execution Flow
**Status:** ✅ IMPLEMENTED
**Description:** Optimized crawler that runs without a GUI.
- **Execution:** `python main.py "/path" --headless`
- **Workflow:** 
  1. Identifies script location for absolute DB mapping.
  2. Wipes existing `file_search.db`.
  3. Parallelized feature extraction and 42-dim vector math.
  4. Batch SQL commits (100 rows per transaction).
  5. Immediate process termination with `sys.exit(0)` to free RAM.

## 3. Planned Features (Wish List)
- **Incremental Crawling:** Instead of wiping the DB, only update files with changed timestamps.
- **Custom Vector Weights via CLI:** Allow users to pass weight overrides in headless mode (e.g., `--weight-ext 2.0`).
- **Multi-Root Support:** Index multiple disconnected directories into a single unified vector space.
