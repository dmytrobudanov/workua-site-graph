import csv, json

INP = "edges.csv"
OUT = "graph.json"

nodes = {}
links = []
seen = set()

def add_node(u):
    if u not in nodes:
        nodes[u] = {"id": u}

with open(INP, "r", encoding="utf-8", newline="") as f:
    sample = f.read(4096)
    f.seek(0)
    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    r = csv.reader(f, dialect)

    header = next(r, [])
    header_l = [h.strip().lower() for h in header]

    # Если есть parent/child — используем их, иначе берём первые 2 колонки
    try:
        i_parent = header_l.index("parent")
        i_child = header_l.index("child")
    except ValueError:
        i_parent, i_child = 0, 1

    for row in r:
        if len(row) <= max(i_parent, i_child):
            continue
        p = row[i_parent].strip()
        c = row[i_child].strip()
        if not p or not c or p == c:
            continue

        add_node(p); add_node(c)
        key = (p, c)
        if key in seen:
            continue
        seen.add(key)
        links.append({"source": p, "target": c})

with open(OUT, "w", encoding="utf-8") as w:
    json.dump({"nodes": list(nodes.values()), "links": links}, w, ensure_ascii=False)

print(f"OK: nodes={len(nodes)}, links={len(links)}, saved={OUT}")
