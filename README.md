# work.ua site graph

Interactive 3D visualization of work.ua internal link structure.

## How it works
1. Crawl site → edges.csv
2. Clean noisy URLs → edges_clean.csv
3. Build graph.json
4. Strict clean → graph_clean_strict.json
5. Visualize with 3d-force-graph

## Live demo
👉 https://<username>.github.io/workua-site-graph/

## Structure
- graph.html – visualization UI
- graph_clean_strict.json – data used by UI
- scripts/ – cleaning & conversion scripts
- data/ – raw and intermediate datasets
