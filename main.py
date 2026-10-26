"""StudentHub — Main Application Entry Point.
=============================================
Launches the StudentHub Desktop GUI application directly.

Usage:
    python main.py            # Launch Desktop GUI (Default)
    python main.py --cli      # Launch original terminal interactive menu
    python main.py --test     # Run automated test suite
"""

import os
import sys

# Ensure local directory is in search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main routing entry point."""
    args = sys.argv[1:]

    if "--cli" in args or "-c" in args:
        import student_management
        student_management.main()
    elif "--test" in args or "-t" in args:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    elif "--help" in args or "-h" in args:
        print(__doc__)
    else:
        # Launch desktop GUI
        from gui import launch_gui
        launch_gui()


if __name__ == "__main__":
    main()
