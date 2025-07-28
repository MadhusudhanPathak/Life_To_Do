import json

class GoalManager:
    def __init__(self, filename='goals.json'):
        self.filename = filename
        self.goals = self.load_goals()

    def load_goals(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_goals(self):
        with open(self.filename, 'w') as f:
            json.dump(self.goals, f, indent=4)

    def add_goal(self, goal):
        self.goals.append(goal.__dict__)
        self.save_goals()

    def list_goals(self):
        for goal in self.goals:
            print(f"Name: {goal['name']}, Priority: {goal['priority']}, Due Date: {goal['due_date']}")

    def find_goal(self, name):
        for goal in self.goals:
            if goal['name'] == name:
                return goal
        return None

    def remove_goal(self, name):
        goal_to_remove = self.find_goal(name)
        if goal_to_remove:
            self.goals.remove(goal_to_remove)
            self.save_goals()
            print(f"Goal '{name}' removed.")
        else:
            print(f"Goal '{name}' not found.")
