# Life To Do: Augmenting Life Planning with LLMs and Graph

## Overview

This Project is an innovative application designed to assist individuals in their life planning by combining the power of Large Language Models (LLMs) with a structured graph database. The core philosophy is to transform subjective human goals and aspirations into an objective, interconnected network, making the planning process more intuitive, efficient, and actionable. Inspired by the concept of "semantic synesthesia," where abstract ideas are given a tangible, visual form, this tool allows users to visualize their life's objectives as a dynamic graph. This visual representation helps in understanding complex relationships, identifying critical dependencies, and charting the most efficient pathways towards goal achievement.

## Core Functionality

*   **Goal Management:** Users can define and manage their personal and professional goals. Each goal is represented as a node in a directed graph, allowing for the creation of complex relationships.
*   **Dynamic Goal Attributes:** Goals can be enriched with various attributes such as `description`, `priority` (e.g., High, Medium, Low), and `dependencies`. The system is designed to be flexible, allowing for the addition of new attributes as needed.
*   **LLM-Powered Interaction:** A locally hosted LLM (via Ollama) serves as the primary interface. Users interact with the system using natural language, describing their goals, constraints, and context. The LLM intelligently parses this input, extracts structured goal data (in JSON format), and updates the underlying graph. Conversely, it can interpret graph data back into human-readable insights.
*   **Contextual Input:** Users can load external text files to provide broader context to the LLM, enabling more informed goal extraction and conversational responses.
*   **Graph Visualization:** The application generates a visual representation of the goal graph, allowing users to see the interconnectedness of their objectives. This visualization is opened in the system's default image viewer.
*   **Persistent Data Storage:** All goals, their attributes, and relationships are saved to a `goals.json` file within a dedicated `User_Data` directory, ensuring data persistence across sessions.
*   **Chat History Logging:** All interactions with the LLM are logged to a `chat_log.txt` file within the `User_Data` directory, which can be loaded and reviewed later.
*   **Intuitive User Interface (GUI):** Built with Tkinter, the GUI provides a user-friendly experience with:
    *   Automatic selection of the lightest available Ollama model.
    *   Buttons for loading files, viewing the graph, loading chat history, showing graph summaries, and clearing the display.
    *   A multi-line input box with "Enter to Send" functionality.
    *   Robust checks for Ollama server availability on startup.

## Technical Stack

*   **Backend Logic:** Python
*   **Large Language Models (LLMs):** [Ollama](https://ollama.ai/) (for local LLM inference)
*   **Graph Data Structure:** [NetworkX](https://networkx.org/)
*   **Graph Visualization:** [Graphviz](https://graphviz.org/) (requires system-wide installation)
*   **Graphical User Interface (GUI):** [Tkinter](https://docs.python.org/3/library/tkinter.html) (Python's standard GUI library)
*   **Image Handling:** [Pillow (PIL)](https://python-pillow.org/)
*   **HTTP Requests:** [Requests](https://requests.readthedocs.io/en/latest/) (for Ollama connectivity checks)

## Getting Started

### Prerequisites

*   **Python 3.x:** Ensure you have Python installed.
*   **Ollama:** Download and install Ollama from [https://ollama.ai/](https://ollama.ai/). After installation, pull at least one model (e.g., `ollama pull llama2`).
*   **Graphviz:** Download and install Graphviz from [https://graphviz.org/download/](https://graphviz.org/download/). **Crucially, ensure Graphviz executables are added to your system's PATH environment variable.** You can verify this by opening your terminal/command prompt and typing `dot -V`.

### Installation

1.  **Clone the repository (or download the project files).**
2.  **Navigate to the project directory** in your terminal.
3.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Ollama server:** Open your terminal/command prompt and run:
    ```bash
    ollama serve
    ```
2.  **Run the application:** In a separate terminal/command prompt, navigate to the project directory and run:
    ```bash
    python main.py
    ```
    The GUI application window should appear.

## Project Structure

```
.
├── main.py             # Main application logic and Tkinter GUI
├── goal_graph.py       # Handles graph data structure and persistence (NetworkX wrapper)
├── requirements.txt    # Python dependencies
├── .gitignore          # Specifies files/folders to ignore in Git (e.g., User_Data)
├── common_goals_context.txt # Example text file for context loading
├── Future_Prospects.md # What are the possible scalling and future scope.
└── User_Data/          # Directory for user-specific data (created automatically)
    ├── goals.json      # Stores the goal graph data
    └── chat_log.txt    # Stores the chat history
    └── temp_goal_graph.png # Temporary graph visualization image
    └── temp_goal_graph.dot # Temporary graph visualization DOT file
```