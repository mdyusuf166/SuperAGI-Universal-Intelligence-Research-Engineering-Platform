class Circuit:
    def __init__(self, nodes=(), required_nodes=()):
        self.nodes = set(nodes)
        self.required_nodes = set(required_nodes)
        self.components = []
        self.connections = []

    def add(self, component):
        self.components.append(component)
        return component

    def connect(self, component, terminal, node):
        self.connections.append({"component": component, "terminal": terminal, "node": node})
        return self
