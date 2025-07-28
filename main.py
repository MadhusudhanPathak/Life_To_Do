import tkinter as tk
from tkinter import ttk, filedialog
import ollama
import threading
import json
import os
import time
import subprocess
import operator
import requests

from goal_graph import GoalGraph
import graphviz
from PIL import Image, ImageTk

class ChatApp:
    """Main application class for the Ollama Goal Planner GUI.

    Manages the Tkinter UI, interaction with Ollama LLM, and goal graph persistence.
    """

    def __init__(self, root):
        """Initializes the ChatApp.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Ollama Goal Planner")
        self.root.geometry("1000x700") # Set initial window size

        # --- User Data Directory Setup ---
        self.user_data_dir = os.path.join(os.getcwd(), "User_Data")
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.chat_log_file = os.path.join(self.user_data_dir, "chat_log.txt")

        # --- Application State ---
        self.context_data = ""  # Stores context loaded from file
        # Initialize GoalGraph, pointing to the user-specific goals.json
        self.goal_graph = GoalGraph(filename=os.path.join(self.user_data_dir, 'goals.json'))
        # Flag to indicate if loaded file content should be processed as goals on next send
        self.process_context_on_next_send = False

        # --- UI Layout --- (Using frames for better organization)

        # Top Control Frame: Holds buttons and model selector
        self.top_control_frame = tk.Frame(root)
        self.top_control_frame.pack(pady=5, fill=tk.X)

        # Buttons Frame: Left side of Top Control Frame
        self.buttons_frame = tk.Frame(self.top_control_frame)
        self.buttons_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.load_file_button = tk.Button(self.buttons_frame, text="Load File", command=self.load_file)
        self.load_file_button.pack(side=tk.LEFT, padx=(0, 5))

        self.view_graph_button = tk.Button(self.buttons_frame, text="View Graph", command=self.view_graph)
        self.view_graph_button.pack(side=tk.LEFT, padx=(0, 5))

        self.load_chat_button = tk.Button(self.buttons_frame, text="Load Chat", command=self.load_chat_history)
        self.load_chat_button.pack(side=tk.LEFT, padx=(0, 5))

        self.show_graph_summary_button = tk.Button(self.buttons_frame, text="Show Graph Summary", command=self.show_graph_summary)
        self.show_graph_summary_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_display_button = tk.Button(self.buttons_frame, text="Clear Display", command=self.clear_display)
        self.clear_display_button.pack(side=tk.LEFT, padx=(0, 5))

        # Model Selector Frame: Right side of Top Control Frame
        self.model_selector_frame = tk.Frame(self.top_control_frame)
        self.model_selector_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.model_label = tk.Label(self.model_selector_frame, text="Select Model:")
        self.model_label.pack(side=tk.LEFT, padx=(0, 5))
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(self.model_selector_frame, textvariable=self.model_var)
        self.model_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Chat Area
        self.chat_area = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Input Frame: Bottom of the window
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.input_entry = tk.Text(self.input_frame, height=3, wrap=tk.WORD)
        self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        # Bind Enter key to send message, preventing default newline
        self.input_entry.bind("<Return>", self._send_message_on_enter)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self._send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Status Label
        self.status_label = tk.Label(root, text="Status: Idle", anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 5))

        # --- Initial Setup Calls ---
        self._check_ollama_status()
        self.load_chat_history()

    def _check_ollama_status(self):
        """Checks if the Ollama server is running and accessible.

        Displays appropriate messages and enables/disables UI elements.
        """
        try:
            # Attempt to list models to check connectivity
            ollama.list()
            self._display_message("Ollama server is running.")
            self._load_models()
            self.send_button.config(state=tk.NORMAL)
            self.model_dropdown.config(state=tk.NORMAL)
            # Enable other buttons that require Ollama interaction
            self.load_file_button.config(state=tk.NORMAL)
        except (ollama.ResponseError, requests.exceptions.ConnectionError) as e:
            error_message = (
                "Error: Could not connect to Ollama server.\n"
                "Please ensure Ollama is installed and running in the background.\n"
                "You can start it by running 'ollama serve' in your terminal.\n"
                f"Details: {e}"
            )
            self._display_message(error_message)
            # Disable all interactive elements if Ollama is not available
            self.send_button.config(state=tk.DISABLED)
            self.model_dropdown.config(state=tk.DISABLED)
            self.load_file_button.config(state=tk.DISABLED)
            self.view_graph_button.config(state=tk.DISABLED)
            self.show_graph_summary_button.config(state=tk.DISABLED)
        except Exception as e:
            error_message = f"An unexpected error occurred during Ollama check: {e}"
            self._display_message(error_message)
            self.send_button.config(state=tk.DISABLED)
            self.model_dropdown.config(state=tk.DISABLED)
            self.load_file_button.config(state=tk.DISABLED)
            self.view_graph_button.config(state=tk.DISABLED)
            self.show_graph_summary_button.config(state=tk.DISABLED)

    def _load_models(self):
        """Loads available Ollama models and populates the dropdown.

        Selects the lightest model by default.
        """
        try:
            response = ollama.list()
            models = response.models

            if not models:
                self._display_message("No Ollama models found. Please ensure you have pulled a model (e.g., 'ollama pull llama2').")
                return

            # Sort models by size (smallest first) to select the lightest by default
            models.sort(key=operator.attrgetter('size'))
            model_names = [model.model for model in models]

            self.model_dropdown['values'] = model_names
            if model_names:
                self.model_dropdown.set(model_names[0]) # Select the lightest model by default
        except Exception as e:
            self._display_message(f"An unexpected error occurred while loading models: {e}")
            print(f"An unexpected error occurred while loading models: {e}") # Print to console for detailed error

    def load_file(self):
        """Opens a file dialog to load a text file for context.

        Sets a flag to process the context on the next message send.
        """
        file_path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*" ))
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.context_data = f.read()
                self._display_message(f"Context loaded from: {file_path}")
                self.process_context_on_next_send = True # Flag to process this context
            except Exception as e:
                self._display_message(f"Error loading file: {e}")

    def load_chat_history(self):
        """Loads and displays the chat history from the chat log file.
        """
        try:
            if os.path.exists(self.chat_log_file):
                with open(self.chat_log_file, 'r', encoding='utf-8') as f:
                    history = f.read()
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.delete(1.0, tk.END) # Clear current chat area
                    self.chat_area.insert(tk.END, history)
                    self.chat_area.config(state=tk.DISABLED)
                    self.chat_area.see(tk.END)
                self._display_message("Chat history loaded.")
            else:
                self._display_message("No chat history found.")
        except Exception as e:
            self._display_message(f"Error loading chat history: {e}")

    def clear_display(self):
        """Clears the chat display and resets the in-memory graph.

        Does NOT delete saved files (goals.json, chat_log.txt).
        """
        # Clear chat area
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self._display_message("Chat display cleared.")

        # Clear context data
        self.context_data = ""
        self.process_context_on_next_send = False

        # Re-initialize graph in memory (does not delete file)
        self.goal_graph = GoalGraph(filename=os.path.join(self.user_data_dir, 'goals.json'))

        self._update_status("Idle")
        self._display_message("Display and in-memory graph cleared.")

    def _send_message_on_enter(self, event):
        """Handles sending message when Enter key is pressed in the input Text widget.

        Prevents the default newline behavior of the Text widget.
        """
        self._send_message()
        return "break" # Prevents the default newline from being inserted

    def _send_message(self):
        """Sends the user's message or processes loaded context to the LLM.
        """
        user_message = self.input_entry.get("1.0", tk.END).strip()
        message_to_llm = ""

        if self.process_context_on_next_send:
            message_to_llm = f"Process the following context for goals: {self.context_data}"
            self._display_message("AI: Processing loaded context for goals...")
            self.process_context_on_next_send = False
        elif user_message:
            message_to_llm = user_message
            self._display_message(f"You: {user_message}")
        else:
            return # Do nothing if no message and no context to process

        self.input_entry.delete("1.0", tk.END)
        self._update_status("Processing...")
        # Run LLM interaction in a separate thread to keep GUI responsive
        threading.Thread(target=self._get_ollama_response, args=(message_to_llm,)).start()

    def _get_ollama_response(self, message_to_llm):
        """Interacts with the Ollama LLM to get a response or extract goals.

        Parses LLM output and updates the graph accordingly.
        """
        try:
            # Prompt for LLM to act as a router: extract JSON goals or respond conversationally
            prompt = f"""You are a goal planning assistant. Your task is to analyze the provided text. If the text describes goals, tasks, or plans, extract them into a JSON object. Each goal should have a 'name' (string), 'description' (string), 'priority' (string, e.g., 'High', 'Medium', 'Low'), and an optional 'depends_on' (list of strings, names of goals this goal depends on). If the text is a general question or statement not related to defining goals, respond conversationally in plain text.

Example JSON structure for goals:
{{"goals": [
    {{"name": "Learn Python", "description": "Master Python programming", "priority": "High", "depends_on": []}},
    {{"name": "Build Web App", "description": "Develop a full-stack web application", "priority": "Medium", "depends_on": ["Learn Python"]}}
]}}

Text to analyze: {message_to_llm}
"""

            messages = [{'role': 'user', 'content': prompt}]

            response = ollama.chat(model=self.model_var.get(), messages=messages)
            llm_response_content = response['message']['content']

            # Debugging: Print raw LLM response to console
            print(f"--- Raw LLM Response ---\n{llm_response_content}\n------------------------")

            try:
                # Attempt to find and parse JSON object from LLM response
                json_start = llm_response_content.find('{')
                json_end = llm_response_content.rfind('}')

                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = llm_response_content[json_start : json_end + 1]
                else:
                    # If no valid JSON structure is found, treat as conversational
                    raise json.JSONDecodeError("No JSON object found in response", llm_response_content, 0)

                parsed_json = json.loads(json_string)
                # Debugging: Print parsed JSON to console
                print(f"--- Parsed JSON ---\n{parsed_json}\n---------------------")

                if "goals" in parsed_json and isinstance(parsed_json["goals"], list):
                    self._display_message("AI: Goals extracted and added to graph.")
                    for goal_data in parsed_json["goals"]:
                        name = goal_data.get('name')
                        description = goal_data.get('description', '')
                        priority = goal_data.get('priority', '')
                        depends_on = goal_data.get('depends_on', [])

                        # Debugging: Print goal data before adding
                        print(f"Attempting to add goal: {name}, Desc: {description}, Pri: {priority}, Depends: {depends_on}")

                        if name:
                            self.goal_graph.add_goal(name, description=description, priority=priority)
                            for dep in depends_on:
                                # Ensure dependency exists as a node before adding edge
                                if not self.goal_graph.graph.has_node(dep):
                                    self.goal_graph.add_goal(dep, description=f"Dependency for {name}", priority="Low")
                                self.goal_graph.add_dependency(dep, name)
                    self._update_status("Done")
                else:
                    # If JSON is valid but doesn't contain 'goals' list, treat as conversational
                    self._display_message(f"AI: {llm_response_content}")
                    self._update_status("Done")
            except json.JSONDecodeError as e:
                # If LLM response is not valid JSON, treat as conversational
                self._display_message(f"AI: {llm_response_content}")
                self._display_message(f"JSON Decode Error (for debugging): {e}") # Keep for debugging if needed
                self._update_status("Done")

        except Exception as e:
            self._display_message(f"Error: {e}")
            self._update_status(f"Error: {e}")

    def view_graph(self):
        """Generates and opens a PNG visualization of the current goal graph.

        Requires Graphviz to be installed and in system's PATH.
        """
        graph = self.goal_graph.get_graph()
        if not graph.nodes:
            self._display_message("Graph is empty. Add some goals first!")
            return

        # Configure Graphviz layout
        dot = graphviz.Digraph(comment='Goal Graph', graph_attr={'rankdir': 'LR'}) # Left to Right layout

        # Add nodes with attributes to Graphviz dot object
        for node, data in graph.nodes(data=True):
            label = f"{node}"
            if 'description' in data and data['description']:
                label += f"\nDesc: {data['description']}"
            if 'priority' in data and data['priority']:
                label += f"\nPriority: {data['priority']}"
            dot.node(node, label=label, shape='box') # Use box shape for better text display

        # Add edges to Graphviz dot object
        for u, v in graph.edges():
            dot.edge(u, v)

        # Debugging: Print DOT source to console
        print(f"--- DOT Source ---\n{dot.source}\n------------------")

        try:
            temp_file_base = os.path.join(self.user_data_dir, "temp_goal_graph")
            temp_dot_file = f"{temp_file_base}.dot"
            temp_png_file = f"{temp_file_base}.png"

            self._display_message("AI: Generating graph image...")
            # Render to PNG. cleanup=False keeps the .dot file for inspection.
            dot.render(temp_file_base, format='png', cleanup=False, view=False)

            # Add a small delay to ensure the file is fully written by Graphviz
            time.sleep(0.1)

            if not os.path.exists(temp_png_file):
                raise FileNotFoundError(f"Graphviz failed to create {temp_png_file}. Check Graphviz installation and PATH.")

            # Open the PNG file using the default system viewer
            self._display_message(f"AI: Opening graph image: {temp_png_file}")
            if os.name == 'nt': # For Windows
                os.startfile(temp_png_file)
            elif os.uname().sysname == 'Darwin': # For macOS
                subprocess.run(['open', temp_png_file])
            else: # For Linux/Unix
                subprocess.run(['xdg-open', temp_png_file])

        except Exception as e:
            self._display_message(f"Error visualizing graph: {e}. Make sure Graphviz is installed and in your PATH.")
            print(f"Graphviz rendering error: {e}") # Print to console for detailed error

        finally:
            # Clean up temporary files (optional, can be re-enabled after debugging)
            # For now, keeping them for inspection
            pass

    def show_graph_summary(self):
        """Displays the textual summary of the goal graph in the chat area.
        """
        self._display_message(self.goal_graph.get_graph_summary())

    def _display_message(self, message):
        """Displays a message in the chat area and logs it to the chat file.

        Args:
            message (str): The message to display.
        """
        # Schedule the GUI update to run in the main thread
        self.root.after(0, self.__display_message_in_main_thread, message)
        # Also write to chat log file
        try:
            with open(self.chat_log_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n\n")
        except IOError as e:
            print(f"Error writing to chat log file: {e}")

    def __display_message_in_main_thread(self, message):
        """Internal method to safely update the chat area from any thread.

        Args:
            message (str): The message to display.
        """
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + "\n\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def _update_status(self, status_text):
        """Updates the status label in the GUI.

        Args:
            status_text (str): The text to display in the status label.
        """
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {status_text}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
