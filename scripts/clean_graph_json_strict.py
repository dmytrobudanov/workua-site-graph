import json
import re
from urllib.parse import urlsplit, urlunsplit

INP = "graph_clean.json"
OUT = "graph_clean_strict.json"

# Регекс «включаем только эти шаблоны»
KEEP_PATTERNS = [
    re.compile(r"^https?://www\.work\.ua/?$"),
    re.compile(r"^https?://www\.work\.ua/jobs(?:[-/].*)?$"),
    re.compile(r"^https?://www\.work\.ua/articles(?:[-/].*)?$"),
    re.compile(r"^https?://www\.work\.ua/news(?:[-/].*)?$"),
    re.compile(r"^https?://www\.work\.ua/employer(?:[-/].*)?$"),
]

# Регекс для **исключения** даже внутри этих разделов
DROP_PATTERNS = [
    re.compile(r"/jobseeker/"),
    re.compile(r"/login"),
    re.compile(r"/signup"),
    re.compile(r"/auth"),
    re.compile(r"/saved-jobs"),
    re.compile(r"/my/"),
    re.compile(r"/faq"),
    re.compile(r"/help"),
    re.compile(r"\?"),   # любые query-параметры
    re.compile(r"#"),    # якоря
    re.compile(r"^https?://www\.work\.ua/articles/jobseeker/"),

]

def canon_url(url):
    """Убрать query/fragment и нормализовать."""
    parts = urlsplit(url)
    clean = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    if clean.endswith("/") and len(parts.path) > 1:
        clean = clean[:-1]
    return clean

def keep_url(url):
    # сначала канонизируем и приводим к единообразному формату
    u = canon_url(url)

    # фильтр по запрещённым паттернам
    for dp in DROP_PATTERNS:
        if dp.search(u):
            return False

    # теперь проверяем, что есть подходящий “allowed” шаблон
    for kp in KEEP_PATTERNS:
        if kp.match(u):
            return True

    return False

# Загружаем граф
with open(INP, "r", encoding="utf-8") as f:
    data = json.load(f)

# Фильтруем узлы
allowed_nodes = {}
for n in data.get("nodes", []):
    u = n.get("id")
    if keep_url(u):
        allowed_nodes[u] = {"id": u}

# Фильтруем связи, где оба узла допустимы
allowed_links = []
for l in data.get("links", []):
    s = l.get("source")
    t = l.get("target")
    if s in allowed_nodes and t in allowed_nodes:
        allowed_links.append({"source": s, "target": t})

# Готовим итоговый graph
clean = {
    "nodes": list(allowed_nodes.values()),
    "links": allowed_links
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)

print(
    f"STRICT CLEANED GRAPH: nodes {len(data['nodes'])} -> {len(clean['nodes'])}, "
    f"links {len(data['links'])} -> {len(clean['links'])} | saved {OUT}"
)
