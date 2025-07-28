class Goal:
    def __init__(self, name, description, priority, due_date):
        self.name = name
        self.description = description
        self.priority = priority
        self.due_date = due_date

    def __str__(self):
        return f"Goal: {self.name}\nDescription: {self.description}\nPriority: {self.priority}\nDue Date: {self.due_date}"