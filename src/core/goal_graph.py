"""
Goal Graph module for the Life To Do application.

This module manages the goal graph, including adding/removing goals and dependencies,
and persisting the graph to a JSON file using NetworkX.
"""
import json
import os
from typing import Dict, List, Any
import networkx as nx


class GoalGraphError(Exception):
    """Custom exception for GoalGraph-related errors."""
    pass


class GoalGraph:
    """
    Manages the goal graph, including adding/removing goals and dependencies,
    and persisting the graph to a JSON file.
    """

    def __init__(self, filename: str = 'goals.json'):
        """
        Initializes the GoalGraph.

        Args:
            filename: The path to the JSON file for graph persistence.
        """
        self.filename = filename
        self.graph = self.load_graph()

    def load_graph(self) -> nx.DiGraph:
        """
        Loads the graph from the specified JSON file.

        Returns:
            networkx.DiGraph: The loaded graph, or a new empty DiGraph if the file
                              does not exist or is invalid.
        """
        if not os.path.exists(self.filename):
            return nx.DiGraph()
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load the graph using node_link_graph without specifying edges parameter
                # to use the default which is compatible with the saved format
                graph = nx.node_link_graph(data)
                return graph
        except (FileNotFoundError, json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Warning: Could not load graph from {self.filename}. Creating new graph. Error: {e}")
            return nx.DiGraph()

    def save_graph(self) -> None:
        """
        Saves the current graph to the specified JSON file.
        """
        try:
            # Ensure the directory exists before saving
            dir_name = os.path.dirname(self.filename)
            if dir_name:  # Only create directory if filename contains a path
                os.makedirs(dir_name, exist_ok=True)
            data = nx.node_link_data(self.graph)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=str)
        except IOError as e:
            raise GoalGraphError(f"Error saving graph to {self.filename}: {e}")

    def add_goal(self, goal_name: str, **attrs) -> bool:
        """
        Adds a goal (node) to the graph with optional attributes.

        Args:
            goal_name: The unique name of the goal.
            **attrs: Arbitrary keyword arguments for goal attributes (e.g., description, priority).

        Returns:
            bool: True if the goal was added, False if it already exists.

        Raises:
            ValueError: If goal_name is empty or None
        """
        if not goal_name or not isinstance(goal_name, str):
            raise ValueError("Goal name must be a non-empty string")

        # Sanitize the goal name to ensure it's safe for use as a node
        goal_name = goal_name.strip()
        if not goal_name:
            raise ValueError("Goal name cannot be empty after stripping whitespace")

        if not self.graph.has_node(goal_name):
            self.graph.add_node(goal_name, **attrs)
            self.save_graph()
            return True
        return False

    def add_dependency(self, from_goal: str, to_goal: str) -> bool:
        """
        Adds a dependency (edge) from one goal to another.

        Args:
            from_goal: The name of the goal that must be completed first.
            to_goal: The name of the goal that depends on 'from_goal'.

        Returns:
            bool: True if the dependency was added, False if goals don't exist
                  or dependency already exists.

        Raises:
            ValueError: If either goal name is invalid
        """
        if not from_goal or not isinstance(from_goal, str):
            raise ValueError("from_goal must be a non-empty string")
        if not to_goal or not isinstance(to_goal, str):
            raise ValueError("to_goal must be a non-empty string")

        # Sanitize inputs
        from_goal = from_goal.strip()
        to_goal = to_goal.strip()

        if not from_goal or not to_goal:
            raise ValueError("Goal names cannot be empty after stripping whitespace")

        if from_goal == to_goal:
            raise ValueError("A goal cannot depend on itself")

        if self.graph.has_node(from_goal) and self.graph.has_node(to_goal):
            if not self.graph.has_edge(from_goal, to_goal):
                self.graph.add_edge(from_goal, to_goal)
                self.save_graph()
                return True
        return False

    def get_goals(self) -> List[tuple]:
        """
        Returns a list of all goals (nodes) in the graph with their data.

        Returns:
            list: A list of (node, data) tuples.
        """
        return list(self.graph.nodes(data=True))

    def get_dependencies(self, goal_name: str) -> List[str]:
        """
        Returns a list of goals that the given goal depends on.

        Args:
            goal_name: The name of the goal.

        Returns:
            list: A list of goal names that 'goal_name' depends on.
        """
        if goal_name in self.graph:
            return list(self.graph.predecessors(goal_name))
        return []

    def get_dependents(self, goal_name: str) -> List[str]:
        """
        Returns a list of goals that depend on the given goal.

        Args:
            goal_name: The name of the goal.

        Returns:
            list: A list of goal names that depend on 'goal_name'.
        """
        if goal_name in self.graph:
            return list(self.graph.successors(goal_name))
        return []

    def remove_goal(self, goal_name: str) -> bool:
        """
        Removes a goal and all its dependencies from the graph.

        Args:
            goal_name: The name of the goal to remove.

        Returns:
            bool: True if the goal was removed, False if it didn't exist.

        Raises:
            ValueError: If goal_name is invalid
        """
        if not goal_name or not isinstance(goal_name, str):
            raise ValueError("Goal name must be a non-empty string")

        goal_name = goal_name.strip()
        if not goal_name:
            raise ValueError("Goal name cannot be empty after stripping whitespace")

        if self.graph.has_node(goal_name):
            self.graph.remove_node(goal_name)
            self.save_graph()
            return True
        return False

    def get_graph_summary(self) -> str:
        """
        Generates a human-readable summary of the current graph.

        Returns:
            str: A formatted string summarizing the goals and dependencies.
        """
        if not self.graph.nodes:
            return "Current Goal Graph:\n  (Graph is empty)\n"

        # Build summary efficiently
        parts = ["Current Goal Graph:"]

        # Add goals section
        parts.append("  Goals (Nodes):")
        for node, data in self.graph.nodes(data=True):
            attrs = ", ".join([f"{k}={v}" for k, v in data.items()])
            parts.append(f"    - {node} ({attrs})")

        # Add dependencies section
        parts.append("  Dependencies (Edges):")
        if not self.graph.edges:
            parts.append("    (No dependencies)")
        else:
            for u, v in self.graph.edges():
                parts.append(f"    - {u} -> {v}")

        return '\n'.join(parts) + '\n'

    def get_graph(self) -> nx.DiGraph:
        """
        Returns the raw networkx.DiGraph object.

        Returns:
            networkx.DiGraph: The internal graph object.
        """
        return self.graph

    def clear_graph(self) -> None:
        """
        Clears the in-memory graph and saves an empty graph to file.
        """
        self.graph = nx.DiGraph()
        self.save_graph()
        
    def get_topological_sort(self) -> List[str]:
        """
        Returns a topological sort of the graph, representing the order in which
        goals should be completed based on dependencies.

        Returns:
            list: A list of goal names in topological order.
        """
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            raise GoalGraphError("Graph has cycles, cannot determine topological order")