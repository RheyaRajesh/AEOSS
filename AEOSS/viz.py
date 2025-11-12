# viz.py
import os
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def compute_subtree_sizes(G, root):
    """Return dict node -> size (number of leaf positions) for layout spacing."""
    sizes = {}
    def _size(u):
        children = list(G.successors(u))
        if not children:
            sizes[u] = 1
        else:
            s = 0
            for c in children:
                s += _size(c)
            sizes[u] = s
        return sizes[u]
    _size(root)
    return sizes

def hierarchy_pos(G, root=0, vert_gap=0.18, vert_loc=0.9):
    """
    Hierarchical layout that spaces nodes horizontally by subtree size.
    Works without pygraphviz and produces well-separated tree layout.
    """
    if root not in G:
        raise KeyError("root not in graph")

    sizes = compute_subtree_sizes(G, root)

    pos = {}
    def _place(node, left, right, level):
        x = (left + right) / 2.0
        pos[node] = (x, vert_loc - level * vert_gap)
        children = list(G.successors(node))
        if not children:
            return
        # allocate a horizontal span to each child proportional to subtree size
        total = sum(sizes[c] for c in children)
        cur = left
        for c in children:
            span = (sizes[c] / total) * (right - left)
            _place(c, cur, cur + span, level + 1)
            cur += span

    # determine overall width from root subtree size
    width = float(sizes[root])
    _place(root, 0.0, width, 0)
    # normalize x positions into [0,1]
    xs = [p[0] for p in pos.values()]
    minx, maxx = min(xs), max(xs)
    rng = maxx - minx if maxx > minx else 1.0
    for n,(x,y) in pos.items():
        pos[n] = ((x - minx) / rng, y)
    return pos


class Visuals:
    def __init__(self, tree, model):
        """
        tree: list of node dicts produced by your ScheduleBuilder (must include 'sequence' and 'pruned')
        model: your MathematicalModel instance (to access task profits/ids/positions)
        """
        self.tree = tree
        self.model = model
        os.makedirs("visualizations", exist_ok=True)

    def _build_graph(self):
        G = nx.DiGraph()
        # nodes are indices into self.tree
        for i, node in enumerate(self.tree):
            G.add_node(i)
        # add edges by parent-child based on sequence matching (parent sequence == child.sequence[:-1])
        for i, node in enumerate(self.tree):
            seq = node.get("sequence", [])
            if seq:
                parent_seq = seq[:-1]
                # find the parent node index
                for j, cand in enumerate(self.tree):
                    if cand.get("sequence", []) == parent_seq:
                        G.add_edge(j, i)
                        break
        return G

    def search_tree(self, outpath="visualizations/search_tree.png"):
        G = self._build_graph()
        if len(G) == 0:
            print("[AEOSS] No tree nodes to draw.")
            return

        # Ensure it's a tree (or forest) with root at index 0
        root = 0
        if root not in G.nodes:
            root = list(G.nodes)[0]

        # If graph is not strictly a tree (some disconnected nodes), fallback to spring layout for those parts
        # We'll try hierarchical for the connected component containing root
        if nx.is_tree(G.subgraph(nx.descendants(G, root) | {root})):
            pos = hierarchy_pos(G, root=root, vert_gap=0.18, vert_loc=0.9)
        else:
            # fallback: place main component hierarchically if possible, else use spring
            try:
                pos = hierarchy_pos(G, root=root, vert_gap=0.18, vert_loc=0.9)
            except Exception:
                pos = nx.spring_layout(G, seed=42)

        # Colors and labels
        node_colors = []
        labels = {}
        for i, node in enumerate(self.tree):
            # label: Root or T<id>\n$profit
            if not node.get("sequence"):
                lab = "Root"
            else:
                tid = node["sequence"][-1]
                t = self.model.tasks[tid]
                lab = f"T{t.id+1}\n${int(t.profit)}"
            labels[i] = lab

            if i == root:
                node_colors.append("#98e69c")  # green-ish root
            elif node.get("pruned"):
                node_colors.append("#e24a4a")  # red (pruned)
            else:
                node_colors.append("#c3e9f8")  # skyblue (active)

        plt.figure(figsize=(14,8))
        # draw edges slightly thinner
        nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=12, edge_color="#555555", width=1.0)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors="black", linewidths=0.8)
        # draw labels centered
        for n, (x,y) in pos.items():
            plt.text(x, y, labels.get(n, ""), fontsize=9, ha="center", va="center", fontweight='bold')

        plt.title("Branch and Bound Search Tree", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(outpath, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"[AEOSS] {os.path.basename(outpath)} saved")

    def pruning_stats(self, outpath="visualizations/pruning_statistics.png"):
        total = len(self.tree)
        pruned = sum(1 for n in self.tree if n.get("pruned"))
        kept = total - pruned
        plt.figure(figsize=(8,5))
        bars = plt.bar(["Kept","Pruned"], [kept, pruned], color=["#1f77b4","#d62728"])
        plt.title("Pruning Statistics", fontsize=14, fontweight='bold')
        plt.ylabel("Nodes Pruned")
        plt.tight_layout()
        plt.savefig(outpath, dpi=200)
        plt.close()
        print(f"[AEOSS] {os.path.basename(outpath)} saved")

    def orbit(self, schedule, outpath="visualizations/orbital_schedule.png"):
        # 3D orbit plot; save as PNG
        fig = plt.figure(figsize=(8,7))
        ax = fig.add_subplot(111, projection='3d')
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        ax.plot_surface(np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v), color='lightblue', alpha=0.6)
        for tid, st in schedule:
            t = self.model.tasks[tid]
            x,y,z = t.position
            ax.scatter(x,y,z,s=120,edgecolor='k')
            ax.text(x,y,z,f"T{t.id+1}", fontsize=9, ha='center', va='center', fontweight='bold')
        plt.title("Satellite Orbit Schedule", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(outpath, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"[AEOSS] {os.path.basename(outpath)} saved")

    def timeline(self, schedule, outpath="visualizations/schedule_timeline.png"):
        fig, ax = plt.subplots(figsize=(12,4))
        colors = plt.get_cmap("tab20").colors
        for i, (tid, st) in enumerate(schedule):
            t = self.model.tasks[tid]
            ax.barh(i, t.duration, left=st, height=0.6, color=colors[i%len(colors)], edgecolor='black', alpha=0.9)
            ax.text(st + t.duration/2, i, f"T{t.id+1}\n${int(t.profit)}", ha='center', va='center', color='white', fontweight='bold')
        ax.set_yticks(list(range(len(schedule))))
        ax.set_yticklabels([f"Task {self.model.tasks[tid].id+1}" for (tid,_) in schedule])
        ax.set_xlabel("Time (s)")
        plt.title("Schedule Timeline", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(outpath, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"[AEOSS] {os.path.basename(outpath)} saved")
