import pygame as pg
import chess
import chess.svg
import cairosvg
import io
from Chess_Bot import ChessBot
import sys
import time
from PIL import Image

class ChessGame:
    def __init__(self, width=600, height=600):
        pg.init()
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption("Chess Bot")
        
        # Initialize chess board
        self.board = chess.Board()
        
        # Initialize the bot with medium difficulty by default
        self.bot = ChessBot(difficulty='medium')
        
        # Game state
        self.selected_square = None
        self.player_color = chess.WHITE
        self.game_over = False
        self.result_message = ""
        
        # Initialize the board image
        self.update_board_image()
        
        # Font for rendering text
        self.font = pg.font.SysFont('Arial', 20)
        
        # Difficulty button areas
        button_height = 30
        self.easy_button = pg.Rect(10, height - button_height - 10, 100, button_height)
        self.medium_button = pg.Rect(120, height - button_height - 10, 100, button_height)
        self.hard_button = pg.Rect(230, height - button_height - 10, 100, button_height)
        self.new_game_button = pg.Rect(340, height - button_height - 10, 100, button_height)
        self.flip_board_button = pg.Rect(450, height - button_height - 10, 140, button_height)
        
        # Current difficulty
        self.difficulty = 'medium'
        
        # Board orientation (True if white at bottom)
        self.white_at_bottom = True
        
        # Status messages
        self.status_message = "Your turn (White)"
        self.thinking = False
        
    def update_board_image(self):
        """Update the board image based on current state"""
        # Generate SVG of the board
        orientation = chess.WHITE if self.white_at_bottom else chess.BLACK
        last_move = self.board.peek() if self.board.move_stack else None
        check_square = self.board.king(self.board.turn) if self.board.is_check() else None
        
        svg_data = chess.svg.board(
            self.board, 
            size=self.width,
            orientation=orientation,
            lastmove=last_move,
            check=check_square,
            arrows=[],
            squares=self.selected_square
        )
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        
        # Convert PNG to pygame surface
        image = Image.open(io.BytesIO(png_data))
        mode = image.mode
        size = image.size
        data = image.tobytes()
        
        self.board_image = pg.image.fromstring(data, size, mode)
        
    def handle_click(self, pos):
        """Handle mouse click at position pos"""
        x, y = pos
        
        # Check if user clicked on difficulty buttons
        if self.easy_button.collidepoint(x, y):
            self.difficulty = 'easy'
            self.bot = ChessBot(difficulty='easy')
            self.status_message = f"Difficulty set to Easy"
            return
        elif self.medium_button.collidepoint(x, y):
            self.difficulty = 'medium'
            self.bot = ChessBot(difficulty='medium')
            self.status_message = f"Difficulty set to Medium"
            return
        elif self.hard_button.collidepoint(x, y):
            self.difficulty = 'hard'
            self.bot = ChessBot(difficulty='hard')
            self.status_message = f"Difficulty set to Hard"
            return
        elif self.new_game_button.collidepoint(x, y):
            self.board = chess.Board()
            self.game_over = False
            self.result_message = ""
            self.selected_square = None
            self.status_message = "New game started. Your turn (White)"
            self.update_board_image()
            return
        elif self.flip_board_button.collidepoint(x, y):
            self.white_at_bottom = not self.white_at_bottom
            self.update_board_image()
            return
        
        # If game is over, ignore board clicks
        if self.game_over or self.thinking:
            return
        
        # If it's not the player's turn, ignore clicks
        if self.board.turn != self.player_color:
            return
        
        # Get the square that was clicked
        file = int(x * 8 / self.width)
        rank = 7 - int(y * 8 / self.height)
        
        # If board is flipped, reverse coordinates
        if not self.white_at_bottom:
            file = 7 - file
            rank = 7 - rank
        
        square = chess.square(file, rank)
        
        # If a square was already selected
        if self.selected_square:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            # Check if it's a promotion
            if self.board.piece_at(self.selected_square) and self.board.piece_at(self.selected_square).piece_type == chess.PAWN:
                # Check if pawn is moving to the last rank
                if (self.player_color == chess.WHITE and rank == 7) or (self.player_color == chess.BLACK and rank == 0):
                    # Promote to queen (simplification - always promote to queen)
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            
            # Check if the move is legal
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.update_board_image()
                self.check_game_over()
                
                # If game is not over, let the bot make a move
                if not self.game_over:
                    self.thinking = True
                    self.status_message = f"Bot is thinking... ({self.difficulty} difficulty)"
                    self.draw()
                    pg.display.flip()
                    self.make_bot_move()
            else:
                # Invalid move, select the new square if it has a piece of the player's color
                piece = self.board.piece_at(square)
                if piece and piece.color == self.player_color:
                    self.selected_square = square
                    self.update_board_image()
                else:
                    self.selected_square = None
                    self.update_board_image()
        else:
            # No square was selected yet, select the clicked square if it has a piece of the player's color
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.update_board_image()
    
    def make_bot_move(self):
        """Let the bot make a move"""
        # Add a small delay to show "thinking" status
        start_time = time.time()
        bot_move = self.bot.get_best_move(self.board)
        elapsed_time = time.time() - start_time
        
        # Ensure minimum thinking time for UI feedback
        if elapsed_time < 0.5:
            time.sleep(0.5 - elapsed_time)
        
        # Make the move
        self.board.push(bot_move)
        self.update_board_image()
        self.check_game_over()
        
        if not self.game_over:
            self.status_message = "Your turn"
        
        self.thinking = False
    
    def check_game_over(self):
        """Check if the game is over"""
        if self.board.is_checkmate():
            self.game_over = True
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.result_message = f"{winner} wins by checkmate!"
            self.status_message = self.result_message
        elif self.board.is_stalemate():
            self.game_over = True
            self.result_message = "Draw by stalemate!"
            self.status_message = self.result_message
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.result_message = "Draw by insufficient material!"
            self.status_message = self.result_message
        elif self.board.is_fifty_moves():
            self.game_over = True
            self.result_message = "Draw by fifty-move rule!"
            self.status_message = self.result_message
        elif self.board.is_repetition():
            self.game_over = True
            self.result_message = "Draw by repetition!"
            self.status_message = self.result_message
    
    def draw(self):
        """Draw the game state"""
        # Draw the board
        self.screen.blit(self.board_image, (0, 0))
        
        # Draw difficulty buttons
        pg.draw.rect(self.screen, (200, 200, 200), self.easy_button)
        pg.draw.rect(self.screen, (200, 200, 200), self.medium_button)
        pg.draw.rect(self.screen, (200, 200, 200), self.hard_button)
        pg.draw.rect(self.screen, (200, 200, 200), self.new_game_button)
        pg.draw.rect(self.screen, (200, 200, 200), self.flip_board_button)
        
        # Highlight current difficulty
        if self.difficulty == 'easy':
            pg.draw.rect(self.screen, (150, 255, 150), self.easy_button, 3)
        elif self.difficulty == 'medium':
            pg.draw.rect(self.screen, (150, 255, 150), self.medium_button, 3)
        else:
            pg.draw.rect(self.screen, (150, 255, 150), self.hard_button, 3)
        
        # Draw button texts
        easy_text = self.font.render('Easy', True, (0, 0, 0))
        medium_text = self.font.render('Medium', True, (0, 0, 0))
        hard_text = self.font.render('Hard', True, (0, 0, 0))
        new_game_text = self.font.render('New Game', True, (0, 0, 0))
        flip_board_text = self.font.render('Flip Board', True, (0, 0, 0))
        
        self.screen.blit(easy_text, (self.easy_button.x + 10, self.easy_button.y + 5))
        self.screen.blit(medium_text, (self.medium_button.x + 10, self.medium_button.y + 5))
        self.screen.blit(hard_text, (self.hard_button.x + 10, self.hard_button.y + 5))
        self.screen.blit(new_game_text, (self.new_game_button.x + 10, self.new_game_button.y + 5))
        self.screen.blit(flip_board_text, (self.flip_board_button.x + 10, self.flip_board_button.y + 5))
        
        # Draw status message
        status_text = self.font.render(self.status_message, True, (0, 0, 0))
        self.screen.blit(status_text, (10, 10))
        
    def run(self):
        """Run the game loop"""
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handle_click(pg.mouse.get_pos())
            
            self.draw()
            pg.display.flip()
            
        pg.quit()