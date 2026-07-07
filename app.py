from flask import Flask, request, render_template_string
import heapq

app = Flask(__name__)

# --- Union-Find for Kruskal ---
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

def kruskal(n, edges):
    edges.sort()
    uf   = UnionFind(n)
    mst  = []
    cost = 0
    for w, u, v in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            cost += w
            if len(mst) == n - 1:
                break
    return mst, cost

def prim(n, adj, start=0):
    INF    = float('inf')
    key    = [INF] * n
    parent = [-1]  * n
    inMST  = [False] * n
    key[start] = 0
    pq = [(0, start)]
    mst = []
    cost = 0
    while pq:
        w, u = heapq.heappop(pq)
        if inMST[u]: continue
        inMST[u] = True
        if parent[u] != -1:
            mst.append((parent[u], u, w))
            cost += w
        for v, wt in adj.get(u, []):
            if not inMST[v] and wt < key[v]:
                key[v] = wt
                parent[v] = u
                heapq.heappush(pq, (wt, v))
    return mst, cost

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        n = int(request.form["vertices"])
        edges_input = request.form["edges"].strip().split("\n")

        edges = []
        adj = {}
        for line in edges_input:
            u, v, w = map(int, line.split())
            edges.append((w, u, v))
            adj.setdefault(u, []).append((v, w))
            adj.setdefault(v, []).append((u, w))

        k_mst, k_cost = kruskal(n, edges[:])
        p_mst, p_cost = prim(n, adj)

        result = {
            "kruskal": {"mst": k_mst, "cost": k_cost},
            "prim": {"mst": p_mst, "cost": p_cost}
        }

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MST Visualizer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            textarea { width: 400px; height: 150px; }
            .result { margin-top: 20px; padding: 15px; border: 1px solid #ccc; }
            h2 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>Minimum Spanning Tree (MST)</h1>
        <form method="POST">
            <label>Number of Vertices:</label><br>
            <input type="number" name="vertices" required><br><br>

            <label>Edges (format: u v w, one per line):</label><br>
            <textarea name="edges" placeholder="Example:\\n0 1 7\\n0 3 5\\n1 2 8" required></textarea><br><br>

            <button type="submit">Compute MST</button>
        </form>

        {% if result %}
        <div class="result">
            <h2>Kruskal's MST</h2>
            <ul>
                {% for u,v,w in result.kruskal.mst %}
                    <li>Edge ({{u}} - {{v}}) Weight: {{w}}</li>
                {% endfor %}
            </ul>
            <strong>Total Cost: {{result.kruskal.cost}}</strong>

            <h2>Prim's MST</h2>
            <ul>
                {% for u,v,w in result.prim.mst %}
                    <li>Edge ({{u}} - {{v}}) Weight: {{w}}</li>
                {% endfor %}
            </ul>
            <strong>Total Cost: {{result.prim.cost}}</strong>
        </div>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
