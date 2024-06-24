from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import networkx as nx
import matplotlib.pyplot as plt
import base64
import io

app = Flask(__name__)
Bootstrap(app)


def plot_graph(graph):
    fig = plt.figure()
    nx.draw(graph, with_labels=True)
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


def search_graph(graph, source, destination, method):
    cost = None
    path = None
    if method == 'BFS':
        successors = nx.bfs_successors(graph, source)
        successors_dict = dict(successors)
        for node, children in successors_dict.items():
            if destination in children:
                path = [destination, node]
                break
        if path:
            current_node = path[-1]
            cost = 0
            while current_node != source:
                for node, children in successors_dict.items():
                    if current_node in children:
                        edge_weight = graph[current_node][node].get('weight', 0)
                        cost += edge_weight  # Add the edge weight to the cost
                        path.append(node)
                        current_node = node
                        break
            path.reverse()
    elif method == 'DFS':
        predecessors = nx.dfs_predecessors(graph, source)
        path = []
        node = destination
        while node is not None:
            path.append(node)
            node = predecessors.get(node, None)
        path.reverse()
        if path[0] != source:
            path = None  # No valid path found
    elif method == 'Dijkstra':
        try:
            length, path = nx.single_source_dijkstra(graph, source)
            cost = length[destination]
            path = path[destination]
        except nx.NetworkXNoPath:
            path = None
    return cost, path


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    nodes = [node.strip() for node in data['nodes'].split(',')]
    edges = [(edge.split('-')[0].strip(), edge.split('-')[1].strip()) for edge in data['edges'].split(',')]
    weights = [(weight.split('-')[0].strip(), weight.split('-')[1].strip(), float(weight.split('-')[2].strip())) for
               weight in data['weights'].split(',')]

    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    for u, v, w in weights:
        graph[u][v]['weight'] = w

    plot_url = plot_graph(graph)
    method = data['method']
    source = data['source']
    destination = data['destination']
    cost, path = search_graph(graph, source, destination, method)

    return render_template('submit.html', plot_url=plot_url, cost=cost, path=path)


if __name__ == '__main__':
    app.run(debug=True)
