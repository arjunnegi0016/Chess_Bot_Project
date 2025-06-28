import pygame as pg
import chess
import sys
import os
from Chess_Bot import ChessBot

# Constants
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    """Load the chess piece images"""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        # Use the path to the images folder
        image_path = os.path.join("images", piece + ".png")
        IMAGES[piece] = pg.transform.scale(pg.image.load(image_path), (SQ_SIZE, SQ_SIZE))

def draw_board(screen):
    """Draw the chess board"""
    colors = [pg.Color("white"), pg.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pg.draw.rect(screen, color, pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Draw the pieces on the board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def convert_to_chess_notation(row, col):
    """Convert row, col coordinates to chess notation (e.g., e4)"""
    files = "abcdefgh"
    ranks = "87654321"  # Reversed because row 0 is the top row
    return files[col] + ranks[row]

def convert_chess_notation_to_coords(notation):
    """Convert chess notation (e.g., e4) to row, col coordinates"""
    files = "abcdefgh"
    ranks = "87654321"  # Reversed because row 0 is the top row
    col = files.index(notation[0])
    row = ranks.index(notation[1])
    return row, col

def convert_chess_piece_to_pygame(piece):
    """Convert a chess.py piece to the corresponding image key"""
    if piece is None:
        return "--"
    
    piece_symbol = piece.symbol()
    color_prefix = "w" if piece_symbol.isupper() else "b"
    piece_type = piece_symbol.upper()
    
    # Map chess.py piece symbols to our image keys
    if piece_type == "P":
        return color_prefix + "p"
    elif piece_type == "R":
        return color_prefix + "R"
    elif piece_type == "N":
        return color_prefix + "N"
    elif piece_type == "B":
        return color_prefix + "B"
    elif piece_type == "Q":
        return color_prefix + "Q"
    elif piece_type == "K":
        return color_prefix + "K"
    
    return "--"

def convert_board_to_pygame_format(chess_board):
    """Convert a chess.py board to a 2D array for pygame rendering"""
    board_2d = []
    for r in range(8):
        row = []
        for c in range(8):
            square = chess.square(c, r)
            piece = chess_board.piece_at(square)
            row.append(convert_chess_piece_to_pygame(piece))
        board_2d.append(row)
    return board_2d

def main():
    """Main function to run the game"""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for status
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    
    # Initialize the chess board
    chess_board = chess.Board()
    pygame_board = convert_board_to_pygame_format(chess_board)
    
    # Initialize the chess bot
    difficulty = 'medium'  # Default difficulty
    bot = ChessBot(difficulty=difficulty)
    
    # Game state variables
    selected_square = None
    player_moves = []
    player_color = chess.WHITE
    game_over = False
    status_message = "Your turn (White)"
    
    # Load images
    load_images()
    
    # Font for status messages
    font = pg.font.SysFont('Arial', 16)
    
    # Button areas
    button_height = 30
    easy_button = pg.Rect(10, HEIGHT + 10, 100, button_height)
    medium_button = pg.Rect(120, HEIGHT + 10, 100, button_height)
    hard_button = pg.Rect(230, HEIGHT + 10, 100, button_height)
    new_game_button = pg.Rect(340, HEIGHT + 10, 100, button_height)
    
    # Main game loop
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Get mouse position
                location = pg.mouse.get_pos()
                
                # Check if buttons were clicked
                if easy_button.collidepoint(location):
                    difficulty = 'easy'
                    bot = ChessBot(difficulty=difficulty)
                    status_message = f"Difficulty set to Easy"
                elif medium_button.collidepoint(location):
                    difficulty = 'medium'
                    bot = ChessBot(difficulty=difficulty)
                    status_message = f"Difficulty set to Medium"
                elif hard_button.collidepoint(location):
                    difficulty = 'hard'
                    bot = ChessBot(difficulty=difficulty)
                    status_message = f"Difficulty set to Hard"
                elif new_game_button.collidepoint(location):
                    chess_board = chess.Board()
                    pygame_board = convert_board_to_pygame_format(chess_board)
                    selected_square = None
                    player_moves = []
                    game_over = False
                    status_message = "New game started. Your turn (White)"
                
                # Only process board clicks if the game is not over and it's the player's turn
                elif not game_over and chess_board.turn == player_color and location[1] < HEIGHT:
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    # If the same square is selected, deselect it
                    if selected_square == (row, col):
                        selected_square = None
                        player_moves = []
                    else:
                        # Check if a piece was selected previously
                        if selected_square:
                            # Try to make a move
                            start_square = chess.square(selected_square[1], selected_square[0])
                            end_square = chess.square(col, row)
                            
                            move = None
                            # Check for pawn promotion
                            piece = chess_board.piece_at(start_square)
                            if piece is not None and piece.piece_type == chess.PAWN:
                                if (row == 0 and player_color == chess.WHITE) or (row == 7 and player_color == chess.BLACK):
                                    move = chess.Move(start_square, end_square, promotion=chess.QUEEN)
                            
                            # If not a promotion, create a regular move
                            if move is None:
                                move = chess.Move(start_square, end_square)
                            
                            # Check if the move is legal
                            if move in chess_board.legal_moves:
                                # Make the move
                                chess_board.push(move)
                                pygame_board = convert_board_to_pygame_format(chess_board)
                                selected_square = None
                                player_moves = []
                                
                                # Check if the game is over
                                if chess_board.is_checkmate():
                                    status_message = "Checkmate! You win!"
                                    game_over = True
                                elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                    status_message = "Draw!"
                                    game_over = True
                                else:
                                    # Bot's turn
                                    status_message = f"Bot is thinking... ({difficulty} difficulty)"
                                    
                                    # Draw current state before bot moves
                                    draw_board(screen)
                                    draw_pieces(screen, pygame_board)
                                    
                                    # Draw status message
                                    status_text = font.render(status_message, True, pg.Color("black"))
                                    screen.blit(status_text, (10, HEIGHT + 50))
                                    
                                    # Draw buttons
                                    pg.draw.rect(screen, pg.Color("light gray"), easy_button)
                                    pg.draw.rect(screen, pg.Color("light gray"), medium_button)
                                    pg.draw.rect(screen, pg.Color("light gray"), hard_button)
                                    pg.draw.rect(screen, pg.Color("light gray"), new_game_button)
                                    
                                    # Highlight current difficulty
                                    if difficulty == 'easy':
                                        pg.draw.rect(screen, pg.Color("green"), easy_button, 3)
                                    elif difficulty == 'medium':
                                        pg.draw.rect(screen, pg.Color("green"), medium_button, 3)
                                    else:
                                        pg.draw.rect(screen, pg.Color("green"), hard_button, 3)
                                    
                                    # Draw button labels
                                    easy_text = font.render('Easy', True, pg.Color("black"))
                                    medium_text = font.render('Medium', True, pg.Color("black"))
                                    hard_text = font.render('Hard', True, pg.Color("black"))
                                    new_game_text = font.render('New Game', True, pg.Color("black"))
                                    
                                    screen.blit(easy_text, (easy_button.x + 10, easy_button.y + 5))
                                    screen.blit(medium_text, (medium_button.x + 10, medium_button.y + 5))
                                    screen.blit(hard_text, (hard_button.x + 10, hard_button.y + 5))
                                    screen.blit(new_game_text, (new_game_button.x + 10, new_game_button.y + 5))
                                    
                                    pg.display.flip()
                                    
                                    # Get bot's move
                                    bot_move = bot.get_best_move(chess_board)
                                    
                                    # Make bot's move
                                    chess_board.push(bot_move)
                                    pygame_board = convert_board_to_pygame_format(chess_board)
                                    
                                    # Check if the game is over after bot's move
                                    if chess_board.is_checkmate():
                                        status_message = "Checkmate! Bot wins!"
                                        game_over = True
                                    elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                        status_message = "Draw!"
                                        game_over = True
                                    else:
                                        status_message = "Your turn"
                            else:
                                # Illegal move, select the new square if it contains a piece of the player's color
                                square = chess.square(col, row)
                                piece = chess_board.piece_at(square)
                                if piece is not None and piece.color == player_color:
                                    selected_square = (row, col)
                                else:
                                    selected_square = None
                        else:
                            # No piece was selected previously
                            square = chess.square(col, row)
                            piece = chess_board.piece_at(square)
                            if piece is not None and piece.color == player_color:
                                selected_square = (row, col)
        
        # Draw everything
        draw_board(screen)
        
        # Highlight selected square
        if selected_square:
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pg.Color('blue'))
            screen.blit(s, (selected_square[1] * SQ_SIZE, selected_square[0] * SQ_SIZE))
        
        draw_pieces(screen, pygame_board)
        
        # Draw buttons
        pg.draw.rect(screen, pg.Color("light gray"), easy_button)
        pg.draw.rect(screen, pg.Color("light gray"), medium_button)
        pg.draw.rect(screen, pg.Color("light gray"), hard_button)
        pg.draw.rect(screen, pg.Color("light gray"), new_game_button)
        
        # Highlight current difficulty
        if difficulty == 'easy':
            pg.draw.rect(screen, pg.Color("green"), easy_button, 3)
        elif difficulty == 'medium':
            pg.draw.rect(screen, pg.Color("green"), medium_button, 3)
        else:
            pg.draw.rect(screen, pg.Color("green"), hard_button, 3)
        
        # Draw button labels
        easy_text = font.render('Easy', True, pg.Color("black"))
        medium_text = font.render('Medium', True, pg.Color("black"))
        hard_text = font.render('Hard', True, pg.Color("black"))
        new_game_text = font.render('New Game', True, pg.Color("black"))
        
        screen.blit(easy_text, (easy_button.x + 10, easy_button.y + 5))
        screen.blit(medium_text, (medium_button.x + 10, medium_button.y + 5))
        screen.blit(hard_text, (hard_button.x + 10, hard_button.y + 5))
        screen.blit(new_game_text, (new_game_button.x + 10, new_game_button.y + 5))
        
        # Draw status message
        status_text = font.render(status_message, True, pg.Color("black"))
        screen.blit(status_text, (10, HEIGHT + 50))
        
        # Update display
        pg.display.flip()
        clock.tick(MAX_FPS)
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()