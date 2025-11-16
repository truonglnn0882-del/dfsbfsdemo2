from flask import Flask, render_template, request
import folium, json, networkx as nx, os
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

with open(os.path.join(BASE_DIR, "map_data.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
edges = data["edges"]

# Đồ thị logic
G = nx.Graph()
for a, b in edges:
    x1, y1 = nodes[a]
    x2, y2 = nodes[b]
    G.add_edge(a, b, weight=((x1 - x2)**2 + (y1 - y2)**2)**0.5)

# BFS
def bfs(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for nb in G.neighbors(node):
                if nb not in visited:
                    queue.append(path + [nb])
    return None

# DFS
def dfs(start, goal):
    stack = [[start]]
    visited = set()
    while stack:
        path = stack.pop()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for nb in reversed(list(G.neighbors(node))):
                if nb not in visited:
                    stack.append(path + [nb])
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    path = []
    algo = None

    avg_lat = sum(v[0] for v in nodes.values()) / len(nodes)
    avg_lon = sum(v[1] for v in nodes.values()) / len(nodes)

    if request.method == "POST":
        start = request.form["start"]
        goal = request.form["goal"]
        algo = request.form["algorithm"]
        path = bfs(start, goal) if algo == "bfs" else dfs(start, goal)

    # Vẽ bản đồ bình thường
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    # Vẽ marker
    for name, coord in nodes.items():
        folium.Marker(coord, tooltip=name).add_to(m)

    # Vẽ đường đi
    if path and len(path) >= 2:
        coords = [nodes[p] for p in path]
        color = "green" if algo == "bfs" else "blue"
        folium.PolyLine(coords, color=color, weight=5, opacity=0.8).add_to(m)

    return render_template("index.html",
                           map_html=m._repr_html_(),
                           nodes=nodes.keys(),
                           path=path,
                           algo=algo)

if __name__ == "__main__":
    app.run(debug=True)
