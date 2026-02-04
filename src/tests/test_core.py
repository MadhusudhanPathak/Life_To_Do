"""
Basic tests for the Life To Do application core components.
"""
import unittest
import tempfile
import os
from datetime import datetime
from src.core.goal import Goal
from src.core.goal_graph import GoalGraph, GoalGraphError


class TestGoal(unittest.TestCase):
    """Test cases for the Goal class."""
    
    def test_goal_creation(self):
        """Test creating a basic goal."""
        goal = Goal(name="Test Goal", description="A test goal", priority="High")
        self.assertEqual(goal.name, "Test Goal")
        self.assertEqual(goal.description, "A test goal")
        self.assertEqual(goal.priority, "High")
        self.assertIsInstance(goal.created_at, datetime)
        self.assertFalse(goal.completed)
    
    def test_goal_with_dependencies(self):
        """Test creating a goal with dependencies."""
        goal = Goal(
            name="Test Goal", 
            description="A test goal", 
            priority="High", 
            dependencies=["Dep1", "Dep2"]
        )
        self.assertIn("Dep1", goal.dependencies)
        self.assertIn("Dep2", goal.dependencies)
    
    def test_goal_str_representation(self):
        """Test string representation of a goal."""
        goal = Goal(name="Test Goal", description="A test goal", priority="High")
        str_repr = str(goal)
        self.assertIn("Goal: Test Goal", str_repr)
        self.assertIn("Description: A test goal", str_repr)
        self.assertIn("Priority: High", str_repr)


class TestGoalGraph(unittest.TestCase):
    """Test cases for the GoalGraph class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.graph = GoalGraph(filename=self.temp_file.name)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_goal(self):
        """Test adding a goal to the graph."""
        result = self.graph.add_goal("Test Goal", description="A test goal", priority="High")
        self.assertTrue(result)
        self.assertTrue(self.graph.graph.has_node("Test Goal"))
        
        # Test adding duplicate goal
        result = self.graph.add_goal("Test Goal", description="Another test goal", priority="Low")
        self.assertFalse(result)  # Should return False for duplicate
    
    def test_add_dependency(self):
        """Test adding a dependency between goals."""
        self.graph.add_goal("Goal 1", description="First goal", priority="High")
        self.graph.add_goal("Goal 2", description="Second goal", priority="Low")
        
        result = self.graph.add_dependency("Goal 1", "Goal 2")
        self.assertTrue(result)
        self.assertTrue(self.graph.graph.has_edge("Goal 1", "Goal 2"))
        
        # Test adding dependency with non-existent goals
        result = self.graph.add_dependency("Non-existent", "Goal 2")
        self.assertFalse(result)
    
    def test_get_dependencies(self):
        """Test getting dependencies for a goal."""
        self.graph.add_goal("Goal 1")
        self.graph.add_goal("Goal 2")
        self.graph.add_goal("Goal 3")
        
        self.graph.add_dependency("Goal 1", "Goal 3")
        self.graph.add_dependency("Goal 2", "Goal 3")
        
        deps = self.graph.get_dependencies("Goal 3")
        self.assertIn("Goal 1", deps)
        self.assertIn("Goal 2", deps)
        self.assertEqual(len(deps), 2)
    
    def test_get_dependents(self):
        """Test getting dependents of a goal."""
        self.graph.add_goal("Goal 1")
        self.graph.add_goal("Goal 2")
        self.graph.add_goal("Goal 3")
        
        self.graph.add_dependency("Goal 1", "Goal 3")
        self.graph.add_dependency("Goal 1", "Goal 2")
        
        dependents = self.graph.get_dependents("Goal 1")
        self.assertIn("Goal 2", dependents)
        self.assertIn("Goal 3", dependents)
        self.assertEqual(len(dependents), 2)
    
    def test_remove_goal(self):
        """Test removing a goal from the graph."""
        self.graph.add_goal("Goal 1", description="A test goal", priority="High")
        self.assertTrue(self.graph.graph.has_node("Goal 1"))

        result = self.graph.remove_goal("Goal 1")
        self.assertTrue(result)
        self.assertFalse(self.graph.graph.has_node("Goal 1"))

        # Test removing non-existent goal
        result = self.graph.remove_goal("Non-existent")
        self.assertFalse(result)

    def test_add_goal_validation(self):
        """Test validation for add_goal method."""
        # Test with empty name
        with self.assertRaises(ValueError):
            self.graph.add_goal("")

        # Test with None name
        with self.assertRaises(ValueError):
            self.graph.add_goal(None)

        # Test with non-string name
        with self.assertRaises(ValueError):
            self.graph.add_goal(123)

        # Test with whitespace-only name
        with self.assertRaises(ValueError):
            self.graph.add_goal("   ")

    def test_add_dependency_validation(self):
        """Test validation for add_dependency method."""
        # Test with empty from_goal
        with self.assertRaises(ValueError):
            self.graph.add_dependency("", "valid_goal")

        # Test with empty to_goal
        with self.assertRaises(ValueError):
            self.graph.add_dependency("valid_goal", "")

        # Test with same goal for both parameters
        with self.assertRaises(ValueError):
            self.graph.add_dependency("same_goal", "same_goal")

        # Test with non-string parameters
        with self.assertRaises(ValueError):
            self.graph.add_dependency(123, "valid_goal")

        with self.assertRaises(ValueError):
            self.graph.add_dependency("valid_goal", 456)

    def test_remove_goal_validation(self):
        """Test validation for remove_goal method."""
        # Test with empty name
        with self.assertRaises(ValueError):
            self.graph.remove_goal("")

        # Test with None name
        with self.assertRaises(ValueError):
            self.graph.remove_goal(None)

        # Test with non-string name
        with self.assertRaises(ValueError):
            self.graph.remove_goal(123)

        # Test with whitespace-only name
        with self.assertRaises(ValueError):
            self.graph.remove_goal("   ")


if __name__ == '__main__':
    unittest.main()