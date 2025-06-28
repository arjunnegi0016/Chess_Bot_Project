"""
Chess Bot with Minimax, Alpha-Beta Pruning, and Dynamic Programming
Main script to run the chess game
"""
import os
import sys

# Make sure we're in the correct directory
chess_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(chess_dir)

# Import essential modules first
try:
    import pygame
    import chess
except ImportError as e:
    print(f"Missing core package: {e}")
    print("Please install the required packages using:")
    print("pip install pygame python-chess")
    sys.exit(1)

# Choose which interface to run
# 1. Simple pygame interface (without SVG rendering)
# 2. Cairo-based SVG interface (more visually appealing but requires additional dependencies)

INTERFACE_TYPE = 1  # Using simple Pygame interface by default

# Only import Cairo-related modules if actually using that interface
if INTERFACE_TYPE == 1:
    print("Starting simple Pygame interface...")
    import Chess_pygame
    Chess_pygame.main()
else:
    print("Starting Cairo-based SVG interface...")
    # Only try to import Cairo dependencies when needed
    try:
        import cairosvg
        from PIL import Image
        from Chess_GUI import ChessGame
        game = ChessGame()
        game.run()
    except ImportError as e:
        print(f"Error importing Cairo dependencies: {e}")
        print("Falling back to simple Pygame interface...")
        import Chess_pygame
        Chess_pygame.main()