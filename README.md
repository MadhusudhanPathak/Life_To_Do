# Life To Do: Augmenting Life Planning with LLMs and Graph

## Overview

Life To Do is an innovative application designed to assist individuals in their life planning by combining the power of Large Language Models (LLMs) with a structured graph database. The core philosophy is to transform subjective human goals and aspirations into an objective, interconnected network, making the planning process more intuitive, efficient, and actionable. Inspired by the concept of "semantic synesthesia," where abstract ideas are given a tangible, visual form, this tool allows users to visualize their life's objectives as a dynamic graph. This visual representation helps in understanding complex relationships, identifying critical dependencies, and charting the most efficient pathways towards goal achievement.

## Features

- **Goal Management**: Define and manage personal and professional goals with rich attributes
- **LLM-Powered Interaction**: Natural language processing with local LLMs via Ollama
- **Dependency Tracking**: Visualize and manage goal dependencies with graph structures
- **Context Loading**: Import external context from text files for better goal extraction
- **Visual Graph Representation**: Generate and view visual representations of your goal network using matplotlib
- **Persistent Storage**: Automatic saving and loading of goals and chat history
- **Modular Architecture**: Clean separation of concerns with extensible components
- **Modern UI**: Enhanced user interface with Times New Roman font, larger input area, and light theme
- **Customization Options**: Theme and font size customization
- **Keyboard Shortcuts**: Efficient navigation with keyboard shortcuts
- **Comprehensive Error Handling**: Robust validation and error management

## Architecture

The application follows a clean, modular architecture:

```
src/
├── core/               # Business logic and data models
│   ├── __init__.py
│   ├── goal.py         # Goal data class
│   ├── goal_graph.py   # Graph management
│   └── llm_service.py  # LLM interaction layer
├── ui/                 # User interface components
│   ├── __init__.py
│   └── tkinter_ui.py   # Tkinter GUI implementation
├── utils/              # Utility functions
│   ├── __init__.py
│   └── logger.py       # Logging configuration
├── config/             # Configuration management
│   ├── __init__.py
│   └── config.py       # App configuration
├── data/               # Data handling (future)
│   └── __init__.py
└── tests/              # Unit tests
    └── __init__.py
```

## Prerequisites

- **Python 3.8+**: Ensure you have Python 3.8 or higher installed
- **Ollama**: Download and install Ollama from [https://ollama.ai/](https://ollama.ai/). After installation, pull at least one model (e.g., `ollama pull llama2`)

## Installation

1. **Clone the repository** (or download the project files)
2. **Navigate to the project directory** in your terminal
3. **Install the required Python libraries**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

1. **Start the Ollama server**: Open your terminal/command prompt and run:
   ```bash
   ollama serve
   ```
2. **Run the application**: In a separate terminal/command prompt, navigate to the project directory and run:
   ```bash
   python main.py
   ```
   The GUI application window should appear.

### Using the Application

- **Load Context**: Use the "Load File" button or Ctrl+O to import text files with goal context
- **Chat with AI**: Type messages in the input box or press Enter to send
- **View Graph**: Click "View Graph" or press Ctrl+G to generate and view the visual representation
- **Manage Goals**: Goals are automatically extracted from conversations and stored
- **Check Summary**: Use "Show Graph Summary" or Ctrl+S to see a text summary of your goals
- **Customize**: Access Settings menu to change theme or font size
- **Keyboard Shortcuts**:
  - Ctrl+O: Load File
  - Ctrl+G: View Graph
  - Ctrl+L: Load Chat History
  - Ctrl+S: Show Summary
  - Ctrl+D: Clear Display
  - F5: Refresh Models
  - Enter: Send message (multi-line with Shift+Enter)

## Configuration

The application uses a `config.json` file for configuration. Default settings include:

- `user_data_dir`: Directory for user data (default: "User_Data")
- `default_model`: Default Ollama model (default: "llama2")
- `window_size`: GUI window dimensions (default: "1200x800")

## Development

For development, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

## Testing

Run the unit tests with:

```bash
python -m pytest src/tests/
```

## Error Handling

The application includes comprehensive error handling:
- Model validation before LLM calls
- Input sanitization for all user inputs
- Graceful handling of missing dependencies
- Detailed error messages for troubleshooting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the terms found in the LICENSE file.

## Project Status

This project is actively maintained and production-ready. All functionality has been preserved while significantly improving maintainability, robustness, and user experience.