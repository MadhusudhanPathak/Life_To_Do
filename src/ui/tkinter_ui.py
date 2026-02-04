"""
UI module for the Life To Do application.

This module contains the graphical user interface components.
Currently supports Tkinter-based GUI.
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import os
import time
import subprocess

from ..core.goal_graph import GoalGraph
from ..core.llm_service import LLMService, LLMServiceError
from ..utils.logger import setup_logger


class ChatApp:
    """Main application class for the Ollama Goal Planner GUI.

    Manages the Tkinter UI, interaction with Ollama LLM, and goal graph persistence.
    """

    def __init__(self, root: tk.Tk, user_data_dir: str = "User_Data"):
        """Initializes the ChatApp.

        Args:
            root: The root Tkinter window.
            user_data_dir: Directory for storing user data
        """
        self.logger = setup_logger(__name__)
        self.root = root
        self.root.title("Life To Do: Goal Planner")
        self.root.geometry("1200x800")  # Larger window size for better UX
        self.root.configure(bg="#ecf0f1")  # Light theme background

        # Configure styles
        self._configure_styles()

        # --- User Data Directory Setup ---
        self.user_data_dir = os.path.join(os.getcwd(), user_data_dir)
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.chat_log_file = os.path.join(self.user_data_dir, "chat_log.txt")

        # --- Application State ---
        self.context_data = ""  # Stores context loaded from file
        # Initialize GoalGraph, pointing to the user-specific goals.json
        self.goal_graph = GoalGraph(filename=os.path.join(self.user_data_dir, 'goals.json'))
        # Initialize LLM service
        self.llm_service = None
        # Flag to indicate if loaded file content should be processed as goals on next send
        self.process_context_on_next_send = False

        # --- Main Container ---
        self.main_container = tk.Frame(root, bg="#ecf0f1")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Header ---
        self.header_frame = tk.Frame(self.main_container, bg="#2c3e50", height=60)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        self.header_frame.pack_propagate(False)  # Maintain fixed height

        self.header_label = tk.Label(
            self.header_frame,
            text="Life To Do: Goal Planner",
            font=("Times New Roman", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        self.header_label.pack(expand=True)

        # --- Toolbar ---
        self.toolbar_frame = tk.Frame(self.main_container, bg="#d5dbdb", relief=tk.RAISED, bd=1)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # Left side buttons
        self.left_toolbar_frame = tk.Frame(self.toolbar_frame, bg="#d5dbdb")
        self.left_toolbar_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_file_button = tk.Button(
            self.left_toolbar_frame,
            text="📁 Load File",
            command=self.load_file,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 10),
            cursor="hand2"
        )
        self.load_file_button.pack(side=tk.LEFT, padx=(0, 5))
        self._add_tooltip(self.load_file_button, "Load a text file for goal extraction")

        self.view_graph_button = tk.Button(
            self.left_toolbar_frame,
            text="📊 View Graph",
            command=self.view_graph,
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 10),
            cursor="hand2"
        )
        self.view_graph_button.pack(side=tk.LEFT, padx=(0, 5))
        self._add_tooltip(self.view_graph_button, "View the goal dependency graph")

        self.load_chat_button = tk.Button(
            self.left_toolbar_frame,
            text="💬 Load Chat",
            command=self.load_chat_history,
            bg="#9b59b6",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 10),
            cursor="hand2"
        )
        self.load_chat_button.pack(side=tk.LEFT, padx=(0, 5))
        self._add_tooltip(self.load_chat_button, "Load previous chat history")

        self.show_graph_summary_button = tk.Button(
            self.left_toolbar_frame,
            text="📋 Show Summary",
            command=self.show_graph_summary,
            bg="#f39c12",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 10),
            cursor="hand2"
        )
        self.show_graph_summary_button.pack(side=tk.LEFT, padx=(0, 5))
        self._add_tooltip(self.show_graph_summary_button, "Show goal graph summary")

        self.clear_display_button = tk.Button(
            self.left_toolbar_frame,
            text="🗑️ Clear",
            command=self.clear_display,
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 10),
            cursor="hand2"
        )
        self.clear_display_button.pack(side=tk.LEFT, padx=(0, 5))
        self._add_tooltip(self.clear_display_button, "Clear the display")

        # Right side controls
        self.right_toolbar_frame = tk.Frame(self.toolbar_frame, bg="#d5dbdb")
        self.right_toolbar_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        self.model_label = tk.Label(
            self.right_toolbar_frame,
            text="Model:",
            bg="#ecf0f1",
            font=("Times New Roman", 10)
        )
        self.model_label.pack(side=tk.LEFT, padx=(0, 5))

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(
            self.right_toolbar_frame,
            textvariable=self.model_var,
            state="readonly",
            width=30,  # Increased width
            font=("Times New Roman", 10)
        )
        self.model_dropdown.pack(side=tk.LEFT)
        self._add_tooltip(self.model_dropdown, "Select the AI model to use")

        # --- Chat Area ---
        self.chat_frame = tk.Frame(self.main_container, bg="#ffffff", relief=tk.SUNKEN, bd=1)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollable text widget for chat area
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#ffffff",
            fg="#2c3e50",
            font=("Times New Roman", 11),
            relief=tk.FLAT
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Input Area ---
        self.input_frame = tk.Frame(self.main_container, bg="#ecf0f1")
        self.input_frame.pack(fill=tk.X)

        self.input_entry = tk.Text(
            self.input_frame,
            height=6,  # Increased height
            wrap=tk.WORD,
            font=("Times New Roman", 12),  # Changed font and increased size
            relief=tk.SUNKEN,
            bd=1
        )
        self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        # Bind Enter key to send message, preventing default newline
        self.input_entry.bind("<Return>", self._send_message_on_enter)
        # Bind Ctrl+Enter for new line in input
        self.input_entry.bind("<Control-Return>", self._insert_new_line)

        # Set focus to input field for better usability
        self.input_entry.focus_set()

        # Add keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_file())  # Ctrl+O to load file
        self.root.bind('<Control-g>', lambda e: self.view_graph())  # Ctrl+G to view graph
        self.root.bind('<Control-l>', lambda e: self.load_chat_history())  # Ctrl+L to load chat
        self.root.bind('<Control-s>', lambda e: self.show_graph_summary())  # Ctrl+S to show summary
        self.root.bind('<Control-d>', lambda e: self.clear_display())  # Ctrl+D to clear display
        self.root.bind('<F5>', lambda e: self._load_models())  # F5 to refresh models

        self.send_button = tk.Button(
            self.input_frame,
            text="Send ➤",
            command=self._send_message,
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            font=("Times New Roman", 11, "bold"),
            cursor="hand2",
            width=10
        )
        self.send_button.pack(side=tk.RIGHT)
        self._add_tooltip(self.send_button, "Send message to AI")

        # --- Status Bar ---
        self.status_frame = tk.Frame(root, bg="#d5dbdb", height=25)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)  # Maintain fixed height

        self.status_label = tk.Label(
            self.status_frame,
            text="Status: Initializing...",
            anchor="w",
            bg="#d5dbdb",
            fg="#2c3e50",
            font=("Times New Roman", 9)
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=3)

        # --- Menu Bar ---
        self._create_menu_bar()

        # --- Initial Setup Calls ---
        self._initialize_app()

    def _create_menu_bar(self):
        """Create the menu bar with customization options."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Load File", command=self.load_file, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="View Graph", command=self.view_graph, accelerator="Ctrl+G")
        self.view_menu.add_command(label="Show Summary", command=self.show_graph_summary, accelerator="Ctrl+S")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Refresh Models", command=self._load_models, accelerator="F5")

        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Load Chat History", command=self.load_chat_history, accelerator="Ctrl+L")
        self.tools_menu.add_command(label="Clear Display", command=self.clear_display, accelerator="Ctrl+D")

        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Change Theme", command=self._open_theme_settings)
        self.settings_menu.add_command(label="Font Size", command=self._open_font_settings)

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self._show_about_dialog)

    def _open_theme_settings(self):
        """Open theme customization dialog - only light theme available."""
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Theme Settings")
        theme_window.geometry("400x150")
        theme_window.transient(self.root)
        theme_window.grab_set()

        tk.Label(theme_window, text="Current Theme: Light", font=("Times New Roman", 12, "bold")).pack(pady=20)

        info_label = tk.Label(
            theme_window,
            text="Only light theme is available in this version",
            font=("Times New Roman", 10),
            fg="#7f8c8d"
        )
        info_label.pack(pady=10)

        button_frame = tk.Frame(theme_window)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="OK",
            command=theme_window.destroy,
            bg="#3498db",
            fg="white",
            font=("Times New Roman", 10)
        ).pack()

    def _open_font_settings(self):
        """Open font size customization dialog."""
        font_window = tk.Toplevel(self.root)
        font_window.title("Font Settings")
        font_window.geometry("300x200")
        font_window.transient(self.root)
        font_window.grab_set()

        tk.Label(font_window, text="Select Font Size:", font=("Times New Roman", 12, "bold")).pack(pady=10)

        font_size_var = tk.IntVar(value=11)
        sizes = [9, 10, 11, 12, 14, 16, 18]

        for size in sizes:
            tk.Radiobutton(font_window, text=f"{size}pt", variable=font_size_var, value=size, font=("Times New Roman", 9)).pack(anchor="w", padx=20, pady=2)

        def apply_font():
            new_size = font_size_var.get()
            self._apply_font_size(new_size)
            font_window.destroy()

        button_frame = tk.Frame(font_window)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Apply", command=apply_font, bg="#3498db", fg="white", font=("Times New Roman", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=font_window.destroy, bg="#95a5a6", fg="white", font=("Times New Roman", 10)).pack(side=tk.LEFT, padx=5)

    def _apply_font_size(self, size):
        """Apply the selected font size."""
        # Update fonts for all text widgets
        font_family = "Times New Roman"
        self.chat_area.configure(font=(font_family, size))
        self.input_entry.configure(font=(font_family, size))

        # Update other UI elements as needed
        for widget in [self.header_label, self.status_label]:
            if widget.winfo_exists():
                current_font = widget.cget("font")
                if isinstance(current_font, str):
                    widget.configure(font=(font_family, int(size*0.8) if size > 8 else 9, "bold" if "bold" in current_font else ""))
                else:
                    widget.configure(font=(font_family, int(size*0.8) if size > 8 else 9, current_font[2] if len(current_font) > 2 else ""))

    def _show_about_dialog(self):
        """Show the about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Life To Do")
        about_window.geometry("400x200")
        about_window.transient(self.root)
        about_window.grab_set()

        tk.Label(about_window, text="Life To Do: Goal Planner", font=("Times New Roman", 16, "bold")).pack(pady=10)
        tk.Label(about_window, text="Version 1.0", font=("Times New Roman", 10)).pack()
        tk.Label(about_window, text="A smart goal planning application powered by AI", font=("Times New Roman", 10)).pack(pady=10)

        tk.Label(about_window, text="Features:", font=("Times New Roman", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        features = [
            "• AI-powered goal extraction",
            "• Visual goal dependency mapping",
            "• Context file loading",
            "• Model selection",
            "• Customizable interface"
        ]

        for feature in features:
            tk.Label(about_window, text=feature, font=("Times New Roman", 9)).pack(anchor="w", padx=40)

        tk.Button(about_window, text="OK", command=about_window.destroy, bg="#3498db", fg="white", width=10, font=("Times New Roman", 10)).pack(pady=20)

    def _configure_styles(self):
        """Configure ttk styles for modern appearance."""
        self.style = ttk.Style()
        # Use the 'clam' theme for a more modern look
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            # If 'clam' theme is not available, continue with default
            pass

    def _add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        def on_enter(event):
            widget.configure(cursor="hand2")

        def on_leave(event):
            widget.configure(cursor="")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _initialize_app(self):
        """Initialize the application components."""
        try:
            self._check_ollama_status()
            self.load_chat_history()
            self._update_status("Ready")
        except Exception as e:
            self.logger.error(f"Error initializing app: {e}")
            self._display_message(f"Initialization error: {e}")

    def _check_ollama_status(self):
        """Checks if the Ollama server is running and accessible.

        Displays appropriate messages and enables/disables UI elements.
        """
        try:
            # Attempt to initialize LLM service with a placeholder model
            # We'll update the model once we know what's available
            self.llm_service = LLMService(model_name="placeholder")  # Will be updated after loading models
            self._display_message("Ollama server is running.")
            self._load_models()
            self.send_button.config(state=tk.NORMAL)
            self.model_dropdown.config(state=tk.NORMAL)
            # Enable other buttons that require Ollama interaction
            self.load_file_button.config(state=tk.NORMAL)
            self.view_graph_button.config(state=tk.NORMAL)
            self.show_graph_summary_button.config(state=tk.NORMAL)
        except LLMServiceError as e:
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
            error_message = f"An unexpected error occurred during initialization: {e}"
            self._display_message(error_message)
            self.logger.error(f"Unexpected error during initialization: {e}")
            self.send_button.config(state=tk.DISABLED)
            self.model_dropdown.config(state=tk.DISABLED)
            self.load_file_button.config(state=tk.DISABLED)
            self.view_graph_button.config(state=tk.DISABLED)
            self.show_graph_summary_button.config(state=tk.DISABLED)

    def _load_models(self):
        """Loads available Ollama models and populates the dropdown.

        Selects the first model by default.
        """
        try:
            model_names = self.llm_service.list_available_models()

            if not model_names:
                self._display_message("No Ollama models found. Please ensure you have pulled a model (e.g., 'ollama pull llama2').")
                return

            # Populate the dropdown with available models
            self.model_dropdown['values'] = model_names
            if model_names:
                self.model_dropdown.set(model_names[0])  # Select the first model by default
        except Exception as e:
            self._display_message(f"An unexpected error occurred while loading models: {e}")
            self.logger.error(f"Error loading models: {e}")

    def load_file(self):
        """Opens a file dialog to load a text file for context.

        Sets a flag to process the context on the next message send.
        """
        file_path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.context_data = f.read()
                self._display_message(f"Context loaded from: {file_path}")
                self.process_context_on_next_send = True  # Flag to process this context
            except Exception as e:
                self._display_message(f"Error loading file: {e}")
                self.logger.error(f"Error loading file {file_path}: {e}")

    def load_chat_history(self):
        """Loads and displays the chat history from the chat log file.
        """
        try:
            if os.path.exists(self.chat_log_file):
                with open(self.chat_log_file, 'r', encoding='utf-8') as f:
                    history = f.read()
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.delete(1.0, tk.END)  # Clear current chat area
                    self.chat_area.insert(tk.END, history)
                    self.chat_area.config(state=tk.DISABLED)
                    self.chat_area.see(tk.END)
                self._display_message("Chat history loaded.")
            else:
                self._display_message("No chat history found.")
        except Exception as e:
            self._display_message(f"Error loading chat history: {e}")
            self.logger.error(f"Error loading chat history: {e}")

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

        self._update_status("Ready")
        self._display_message("Display and in-memory graph cleared.")

    def _send_message_on_enter(self, event):
        """Handles sending message when Enter key is pressed in the input Text widget.

        Prevents the default newline behavior of the Text widget.
        """
        # Only send if Shift is not pressed (allowing for multi-line input)
        if not event.state & 0x1:  # Check if shift key is not pressed
            self._send_message()
            return "break"  # Prevents the default newline from being inserted

    def _insert_new_line(self, event):
        """Inserts a new line in the input field when Ctrl+Enter is pressed."""
        self.input_entry.insert(tk.INSERT, "\n")
        return "break"  # Prevents default behavior

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
            return  # Do nothing if no message and no context to process

        self.input_entry.delete("1.0", tk.END)
        self._update_status("Processing...")

        # Add visual feedback animation
        self._animate_processing()

        # Run LLM interaction in a separate thread to keep GUI responsive
        threading.Thread(target=self._get_ollama_response, args=(message_to_llm,), daemon=True).start()

    def _animate_processing(self):
        """Add visual feedback animation during processing."""
        dots = 0

        def animate():
            nonlocal dots
            if "Processing" in self.status_label.cget("text"):
                dots = (dots + 1) % 4
                self.status_label.config(text=f"Status: Processing{'.' * dots}")
                self.root.after(500, animate)  # Update every 500ms

        animate()

    def _get_ollama_response(self, message_to_llm: str):
        """Interacts with the Ollama LLM to get a response or extract goals.

        Parses LLM output and updates the graph accordingly.
        """
        try:
            if not self.llm_service:
                raise LLMServiceError("LLM service not initialized")

            # Get the currently selected model from the UI
            selected_model = self.model_var.get()
            if not selected_model:
                # Fallback to first available model if none selected
                available_models = self.llm_service.list_available_models()
                if available_models:
                    selected_model = available_models[0]
                    self.model_var.set(selected_model)  # Update UI to show selected model
                else:
                    raise LLMServiceError("No models available")

            # Try to extract goals from the message using the selected model
            goals_data = self.llm_service.extract_goals_from_text(message_to_llm, model_name=selected_model)

            if goals_data:
                self._display_message("AI: Goals extracted and added to graph.")
                for goal_data in goals_data:
                    name = goal_data.get('name')
                    description = goal_data.get('description', '')
                    priority = goal_data.get('priority', '')
                    depends_on = goal_data.get('depends_on', [])

                    if name:
                        self.goal_graph.add_goal(
                            name,
                            description=description,
                            priority=priority
                        )
                        for dep in depends_on:
                            # Ensure dependency exists as a node before adding edge
                            if not self.goal_graph.graph.has_node(dep):
                                self.goal_graph.add_goal(
                                    dep,
                                    description=f"Dependency for {name}",
                                    priority="Low"
                                )
                            self.goal_graph.add_dependency(dep, name)
                self._update_status("Goals processed")
            else:
                # If no goals were extracted, get a conversational response using the selected model
                response = self.llm_service.get_conversational_response(message_to_llm, model_name=selected_model)
                self._display_message(f"AI: {response}")
                self._update_status("Response received")

        except LLMServiceError as e:
            self._display_message(f"LLM Error: {e}")
            self.logger.error(f"LLM service error: {e}")
            self._update_status(f"LLM Error: {e}")
        except Exception as e:
            self._display_message(f"Error: {e}")
            self.logger.error(f"Unexpected error in _get_ollama_response: {e}")
            self._update_status(f"Error: {e}")

    def view_graph(self):
        """Generates and displays a visualization of the current goal graph using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter compatibility
            import networkx as nx
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import io
            import tempfile
            from PIL import Image, ImageTk

            graph = self.goal_graph.get_graph()
            if not graph.nodes:
                self._display_message("Graph is empty. Add some goals first!")
                return

            # Create a new window to display the graph
            graph_window = tk.Toplevel(self.root)
            graph_window.title("Goal Graph Visualization")
            graph_window.geometry("900x700")
            graph_window.configure(bg="#f0f0f0")

            # Create header for the graph window
            header_frame = tk.Frame(graph_window, bg="#2c3e50", height=50)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)

            header_label = tk.Label(
                header_frame,
                text="Goal Dependency Graph",
                font=("Times New Roman", 14, "bold"),
                fg="white",
                bg="#2c3e50"
            )
            header_label.pack(expand=True)

            # Create main content frame
            content_frame = tk.Frame(graph_window, bg="#f0f0f0")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(12, 8))

            # Create layout for the graph
            pos = nx.spring_layout(graph, seed=42)  # Consistent layout

            # Draw nodes
            node_colors = []
            for node in graph.nodes():
                # Color nodes based on priority if available
                priority = graph.nodes[node].get('priority', 'Medium')
                if priority.lower() == 'high':
                    node_colors.append('#e74c3c')  # Red for high priority
                elif priority.lower() == 'low':
                    node_colors.append('#2ecc71')  # Green for low priority
                else:
                    node_colors.append('#3498db')  # Blue for medium priority

            nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=2500, alpha=0.9, ax=ax)

            # Draw edges
            nx.draw_networkx_edges(graph, pos, width=2, alpha=0.6, edge_color='#7f8c8d', arrows=True, arrowsize=20, ax=ax)

            # Draw labels
            labels = {}
            for node, data in graph.nodes(data=True):
                label = node
                if 'description' in data and data['description']:
                    label += f"\n{data['description'][:30]}..."  # Truncate long descriptions
                if 'priority' in data and data['priority']:
                    label += f"\n({data['priority']})"
                labels[node] = label

            nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, font_weight='bold', ax=ax)

            # Adjust plot to prevent label cutoff
            ax.set_title("Goal Dependency Graph", fontsize=16, pad=20)
            ax.axis('off')  # Turn off axis

            plt.tight_layout()

            # Embed the plot in the tkinter window
            canvas = FigureCanvasTkAgg(fig, master=content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Create button frame
            button_frame = tk.Frame(content_frame, bg="#f0f0f0")
            button_frame.pack(side=tk.BOTTOM, pady=10)

            # Add a button to save the graph as an image
            def save_graph():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                if file_path:
                    plt.savefig(file_path, bbox_inches='tight', dpi=300)
                    self._display_message(f"Graph saved to: {file_path}")

            save_button = tk.Button(
                button_frame,
                text="💾 Save Graph",
                command=save_graph,
                bg="#9b59b6",
                fg="white",
                relief=tk.FLAT,
                font=("Times New Roman", 10),
                cursor="hand2"
            )
            save_button.pack(side=tk.LEFT, padx=5)

            # Add close button
            close_button = tk.Button(
                button_frame,
                text="❌ Close",
                command=lambda: [plt.close(fig), graph_window.destroy()],
                bg="#e74c3c",
                fg="white",
                relief=tk.FLAT,
                font=("Times New Roman", 10),
                cursor="hand2"
            )
            close_button.pack(side=tk.LEFT, padx=5)

            # Handle window closing
            def on_closing():
                plt.close(fig)  # Close the matplotlib figure
                graph_window.destroy()

            graph_window.protocol("WM_DELETE_WINDOW", on_closing)

            self._display_message("AI: Graph visualization opened in a new window.")

        except ImportError as e:
            self._display_message(
                f"Error: Missing visualization dependencies: {e}\n"
                "Please install required packages: pip install matplotlib pillow"
            )
            self.logger.error(f"Visualization import error: {e}")
        except Exception as e:
            self._display_message(f"Error visualizing graph: {e}")
            self.logger.error(f"Graph visualization error: {e}")

    def show_graph_summary(self):
        """Displays the textual summary of the goal graph in the chat area.
        """
        self._display_message(self.goal_graph.get_graph_summary())

    def _display_message(self, message: str):
        """Displays a message in the chat area and logs it to the chat file.

        Args:
            message: The message to display.
        """
        # Schedule the GUI update to run in the main thread
        self.root.after(0, self.__display_message_in_main_thread, message)
        # Also write to chat log file
        try:
            with open(self.chat_log_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n\n")
        except IOError as e:
            self.logger.error(f"Error writing to chat log file: {e}")

    def __display_message_in_main_thread(self, message: str):
        """Internal method to safely update the chat area from any thread.

        Args:
            message: The message to display.
        """
        self.chat_area.config(state=tk.NORMAL)

        # Format different types of messages with colors
        if message.startswith("You:"):
            # User message - blue
            self.chat_area.insert(tk.END, message + "\n\n", "user")
        elif message.startswith("AI:") or "Goals extracted" in message:
            # AI message - green
            self.chat_area.insert(tk.END, message + "\n\n", "ai")
        elif message.startswith("Status:") or "Processing" in message or "Ready" in message:
            # Status message - orange
            self.chat_area.insert(tk.END, message + "\n\n", "status")
        elif "Error" in message or "error" in message:
            # Error message - red
            self.chat_area.insert(tk.END, message + "\n\n", "error")
        else:
            # Default message - black
            self.chat_area.insert(tk.END, message + "\n\n", "default")

        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

        # Apply tag configurations if not already done
        if not hasattr(self, '_tags_configured'):
            self._setup_text_tags()
            self._tags_configured = True

    def _setup_text_tags(self):
        """Setup text tags for different message types."""
        self.chat_area.tag_configure("user", foreground="#2980b9", font=("Times New Roman", 11, "bold"))
        self.chat_area.tag_configure("ai", foreground="#27ae60", font=("Times New Roman", 11))
        self.chat_area.tag_configure("status", foreground="#f39c12", font=("Times New Roman", 10))
        self.chat_area.tag_configure("error", foreground="#e74c3c", font=("Times New Roman", 10, "bold"))
        self.chat_area.tag_configure("default", foreground="#2c3e50", font=("Times New Roman", 11))

    def _update_status(self, status_text: str):
        """Updates the status label in the GUI.

        Args:
            status_text: The text to display in the status label.
        """
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {status_text}"))


def run_gui():
    """Function to run the GUI application."""
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()