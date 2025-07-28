import networkx as nx
import json
import os

class GoalGraph:
    """Manages the goal graph, including adding/removing goals and dependencies,
    and persisting the graph to a JSON file.
    """

    def __init__(self, filename='goals.json'):
        """Initializes the GoalGraph.

        Args:
            filename (str): The path to the JSON file for graph persistence.
        """
        self.filename = filename
        self.graph = self.load_graph()

    def load_graph(self):
        """Loads the graph from the specified JSON file.

        Returns:
            networkx.DiGraph: The loaded graph, or a new empty DiGraph if the file
                              does not exist or is invalid.
        """
        if not os.path.exists(self.filename):
            return nx.DiGraph()
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # Explicitly set edges='links' for compatibility with nx.node_link_data
                # and to suppress FutureWarning in NetworkX 3.x
                graph = nx.node_link_graph(data, edges="links")
                return graph
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load graph from {self.filename}. Creating new graph. Error: {e}")
            return nx.DiGraph()

    def save_graph(self):
        """Saves the current graph to the specified JSON file.
        """
        try:
            # Ensure the directory exists before saving
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            data = nx.node_link_data(self.graph)
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving graph to {self.filename}: {e}")

    def add_goal(self, goal_name, **attrs):
        """Adds a goal (node) to the graph with optional attributes.

        Args:
            goal_name (str): The unique name of the goal.
            **attrs: Arbitrary keyword arguments for goal attributes (e.g., description, priority).

        Returns:
            bool: True if the goal was added, False if it already exists.
        """
        if not self.graph.has_node(goal_name):
            self.graph.add_node(goal_name, **attrs)
            self.save_graph()
            return True
        return False

    def add_dependency(self, from_goal, to_goal):
        """Adds a dependency (edge) from one goal to another.

        Args:
            from_goal (str): The name of the goal that must be completed first.
            to_goal (str): The name of the goal that depends on 'from_goal'.

        Returns:
            bool: True if the dependency was added, False if goals don't exist
                  or dependency already exists.
        """
        if self.graph.has_node(from_goal) and self.graph.has_node(to_goal):
            if not self.graph.has_edge(from_goal, to_goal):
                self.graph.add_edge(from_goal, to_goal)
                self.save_graph()
                return True
        return False

    def get_goals(self):
        """Returns a list of all goals (nodes) in the graph with their data.

        Returns:
            list: A list of (node, data) tuples.
        """
        return list(self.graph.nodes(data=True))

    def get_dependencies(self, goal_name):
        """Returns a list of goals that the given goal depends on.

        Args:
            goal_name (str): The name of the goal.

        Returns:
            list: A list of goal names that 'goal_name' depends on.
        """
        if goal_name in self.graph:
            return list(self.graph.predecessors(goal_name))
        return []

    def get_graph_summary(self):
        """Generates a human-readable summary of the current graph.

        Returns:
            str: A formatted string summarizing the goals and dependencies.
        """
        summary = "Current Goal Graph:\n"
        if not self.graph.nodes:
            summary += "  (Graph is empty)\n"
            return summary

        summary += "  Goals (Nodes):\n"
        for node, data in self.graph.nodes(data=True):
            attrs = ", ".join([f"{k}={v}" for k, v in data.items()])
            summary += f"    - {node} ({attrs})\n"

        summary += "  Dependencies (Edges):\n"
        if not self.graph.edges:
            summary += "    (No dependencies)\n"
        else:
            for u, v in self.graph.edges():
                summary += f"    - {u} -> {v}\n"
        return summary

    def get_graph(self):
        """Returns the raw networkx.DiGraph object.

        Returns:
            networkx.DiGraph: The internal graph object.
        """
        return self.graph

    def clear_graph(self):
        """Clears the in-memory graph and saves an empty graph to file.
        """
        self.graph = nx.DiGraph()
        self.save_graph()