# Life To Do: Agent Context File

## Project Overview
Life To Do is an innovative goal planning application that combines Large Language Models (LLMs) with graph database technology to help users visualize and manage their life goals and dependencies.

## Purpose
The application transforms subjective human goals and aspirations into an objective, interconnected network, making the planning process more intuitive, efficient, and actionable. It allows users to visualize their life's objectives as a dynamic graph, helping understand complex relationships and identify critical dependencies.

## Architecture
The application follows a modular architecture with clear separation of concerns:

- **src/core/**: Core business logic and data models
  - `goal.py`: Defines the Goal data class
  - `goal_graph.py`: Manages the goal graph structure and persistence
  - `llm_service.py`: Handles communication with Ollama LLM

- **src/ui/**: User interface components
  - `tkinter_ui.py`: Main Tkinter GUI implementation

- **src/utils/**: Utility functions
  - `logger.py`: Logging configuration

- **src/config/**: Configuration management
  - `config.py`: Application configuration

- **src/tests/**: Unit tests for core functionality

## Key Features
1. **Goal Management**: Create, modify, and track goals with rich attributes (name, description, priority, dependencies)
2. **LLM Integration**: Natural language processing with local Ollama models
3. **Graph Visualization**: Visual representation of goal dependencies using matplotlib
4. **Context Loading**: Import text files for goal extraction
5. **Persistent Storage**: Automatic saving/loading of goals and chat history
6. **Modern UI**: Enhanced interface with Times New Roman font, larger input area, and light theme
7. **Keyboard Shortcuts**: Efficient navigation (Ctrl+O, Ctrl+G, etc.)

## Technical Stack
- Python 3.8+
- Ollama for LLM interaction
- NetworkX for graph operations
- Matplotlib for visualization
- Tkinter for GUI
- Requests for HTTP communication

## Core Components

### Goal Class
Represents individual goals with properties:
- name (str): Unique identifier
- description (str): Detailed description
- priority (str): Priority level (High/Medium/Low)
- dependencies (List[str]): List of dependent goal names
- created_at (datetime): Creation timestamp
- completed (bool): Completion status

### GoalGraph Class
Manages the graph structure:
- Add/remove goals and dependencies
- Persistence to JSON files
- Graph traversal and analysis
- Topological sorting for dependency order

### LLMService Class
Handles LLM interactions:
- Goal extraction from text
- Conversational responses
- Model management
- Error handling

### ChatApp Class
Main GUI application:
- Tkinter-based interface
- Real-time goal visualization
- File loading capabilities
- Model selection

## Error Handling
The application includes comprehensive error handling:
- Input validation and sanitization
- Model availability checks
- Graceful degradation for missing dependencies
- Detailed error messages for troubleshooting

## Configuration
The application uses config.json for settings:
- user_data_dir: Directory for user data
- default_model: Default Ollama model
- window_size: GUI dimensions
- logging_level: Logging verbosity

## File Structure
- `main.py`: Main application entry point
- `requirements.txt`: Runtime dependencies
- `requirements-dev.txt`: Development dependencies
- `config.json`: Configuration file
- `User_Data/`: User-specific data directory
  - `goals.json`: Goal graph data
  - `chat_log.txt`: Conversation history

## Current State
The application is production-ready with:
- Comprehensive test coverage
- Modern UI with enhanced UX
- Robust error handling
- Clean, maintainable codebase
- Full backward compatibility
- Extensive documentation

## Development Guidelines
- Follow Python PEP 8 standards
- Maintain type hints throughout
- Write comprehensive docstrings
- Add unit tests for new functionality
- Preserve backward compatibility
- Follow modular architecture principles

## Integration Points
- Ollama server for LLM access
- File system for data persistence
- NetworkX for graph operations
- Matplotlib for visualization
- Tkinter for GUI components

This context file provides essential information for understanding the project structure, functionality, and development practices.