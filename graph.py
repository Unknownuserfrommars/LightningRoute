# backend/graph.py
import networkx as nx

class GraphGenerator:
    def __init__(self):
        self.graph = nx.Graph()

    def generate_graph(self, knowledge_points):
        # Clear existing graph
        self.graph.clear()
        
        def add_nodes_edges(data, parent=None):
            # Add node
            node_id = data.get('id')
            node_title = data.get('title')
            self.graph.add_node(node_id, title=node_title)
            
            # Add edge to parent if exists
            if parent:
                self.graph.add_edge(parent, node_id)
            
            # Process children recursively
            children = data.get('children', [])
            for child in children:
                add_nodes_edges(child, node_id)

        # Process the knowledge points
        for point in knowledge_points:
            add_nodes_edges(point)

        # Convert to dictionary format for visualization
        graph_data = {
            'nodes': [{'id': node, 'label': self.graph.nodes[node]['title']} 
                     for node in self.graph.nodes()],
            'edges': [{'from': u, 'to': v} for (u, v) in self.graph.edges()]
        }

        return graph_data
