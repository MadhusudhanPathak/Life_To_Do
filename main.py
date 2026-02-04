"""
Main entry point for the Life To Do application.

This module initializes the application and starts the GUI.
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.tkinter_ui import run_gui
from src.config.config import Config
from src.utils.logger import setup_logger


def main():
    """
    Main function to start the Life To Do application.
    """
    # Set up logging
    logger = setup_logger(__name__)
    
    # Load configuration
    config = Config()
    logger.info("Life To Do application starting...")
    
    try:
        # Start the GUI
        run_gui()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        raise


if __name__ == "__main__":
    main()