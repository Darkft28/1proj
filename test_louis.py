import pygame
import sys

class Colors:
    """Class to store color constants"""
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 40)
    RED = (173, 7, 60)       # Rose pâle
    BLUE = (29, 185, 242)    # Bleu pastel
    YELLOW = (235, 226, 56)  # Jaune crème
    GREEN = (24, 181, 87)    # Vert menthe


class SmallBoard:
    """Class representing a small 4x4 board with colors"""
    def __init__(self, color_grid):
        self.color_grid = color_grid
        self.rotation = 0
        
    def draw(self, screen, x, y, tile_size):
        """Draw the small board at position (x, y) with current rotation"""
        small_board_size = len(self.color_grid)
        small_tile_size = tile_size // small_board_size
        
        for row in range(small_board_size):
            for col in range(small_board_size):
                # Adjust for rotation
                if self.rotation == 0:
                    color = self.color_grid[row][col]
                elif self.rotation == 90:
                    color = self.color_grid[small_board_size - 1 - col][row]
                elif self.rotation == 180:
                    color = self.color_grid[small_board_size - 1 - row][small_board_size - 1 - col]
                elif self.rotation == 270:
                    color = self.color_grid[col][small_board_size - 1 - row]

                rect = pygame.Rect(
                    x + col * small_tile_size, 
                    y + row * small_tile_size, 
                    small_tile_size, 
                    small_tile_size
                )
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, Colors.WHITE, rect, 1)
    
    def rotate(self):
        """Rotate the board 90 degrees clockwise"""
        self.rotation = (self.rotation + 90) % 360


class GridPosition:
    """Class representing a position in the 2x2 grid"""
    def __init__(self, row, col, tile_size):
        self.row = row
        self.col = col
        self.x = col * tile_size
        self.y = row * tile_size
        self.board = None
        
    def place_board(self, board):
        """Place a board at this position"""
        self.board = board
        
    def remove_board(self):
        """Remove board from this position and return it"""
        board = self.board
        self.board = None
        return board
        
    def has_board(self):
        """Check if position has a board"""
        return self.board is not None
        
    def draw(self, screen, tile_size):
        """Draw grid cell and board if present"""
        # Draw grid cell
        rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        pygame.draw.rect(screen, Colors.WHITE, rect, 1)
        
        # Draw board if present
        if self.board:
            self.board.draw(screen, self.x, self.y, tile_size)


class GameBoard:
    """Class representing the main 2x2 game board"""
    def __init__(self, grid_size, screen_width):
        self.grid_size = grid_size
        self.tile_size = screen_width // grid_size
        self.positions = []
        
        # Initialize grid positions
        for row in range(grid_size):
            for col in range(grid_size):
                self.positions.append(GridPosition(row, col, self.tile_size))
    
    def draw(self, screen):
        """Draw the game board and all placed boards"""
        for position in self.positions:
            position.draw(screen, self.tile_size)
    
    def get_position_at(self, x, y):
        """Get grid position at screen coordinates (x, y)"""
        col = x // self.tile_size
        row = y // self.tile_size
        
        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            idx = row * self.grid_size + col
            return self.positions[idx]
        return None
        
    def swap_boards(self, pos1_idx, pos2_idx):
        """Swap boards between two positions"""
        temp_board = self.positions[pos1_idx].board
        self.positions[pos1_idx].board = self.positions[pos2_idx].board
        self.positions[pos2_idx].board = temp_board


class BoardsInventory:
    """Class representing the inventory of unused boards"""
    def __init__(self, boards, screen_height, tile_size):
        self.boards = boards
        self.screen_height = screen_height
        self.tile_size = tile_size
        
    def draw(self, screen, used_boards):
        """Draw all unused boards at the bottom of the screen"""
        for idx, board in enumerate(self.boards):
            if board not in used_boards:
                x = idx * self.tile_size
                y = self.screen_height - self.tile_size
                board.draw(screen, x, y, self.tile_size)
    
    def get_board_at(self, x, y, used_boards):
        """Get board at screen coordinates (x, y) if it's in inventory"""
        if self.screen_height - self.tile_size <= y < self.screen_height:
            col = x // self.tile_size
            if 0 <= col < len(self.boards):
                board = self.boards[col]
                if board not in used_boards:
                    return board
        return None


class Game:
    """Main game class"""
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 800
        
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Board Placement and Rotation")
        
        # Grid dimensions
        self.GRID_SIZE = 2
        self.TILE_SIZE = self.SCREEN_WIDTH // self.GRID_SIZE
        
        # Small board dimensions
        self.SMALL_BOARD_SIZE = 4
        
        # Create boards
        self.create_boards()
        
        # Create game elements
        self.game_board = GameBoard(self.GRID_SIZE, self.SCREEN_WIDTH)
        self.inventory = BoardsInventory(self.boards, self.SCREEN_HEIGHT, self.TILE_SIZE)
        
        # Variables for dragging
        self.selected_board = None
        self.selected_from_position = None
        self.selected_position = None
        
    def create_boards(self):
        """Create the four boards with their color patterns"""
        # Color patterns for the boards
        color_grids = [
            [[Colors.RED, Colors.BLUE, Colors.YELLOW, Colors.GREEN], 
             [Colors.BLUE, Colors.GREEN, Colors.RED, Colors.YELLOW], 
             [Colors.YELLOW, Colors.RED, Colors.GREEN, Colors.BLUE], 
             [Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.RED]],
            
            [[Colors.BLUE, Colors.GREEN, Colors.RED, Colors.YELLOW], 
             [Colors.YELLOW, Colors.RED, Colors.GREEN, Colors.BLUE], 
             [Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.RED], 
             [Colors.RED, Colors.BLUE, Colors.YELLOW, Colors.GREEN]],
            
            [[Colors.YELLOW, Colors.RED, Colors.GREEN, Colors.BLUE], 
             [Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.RED], 
             [Colors.RED, Colors.BLUE, Colors.YELLOW, Colors.GREEN], 
             [Colors.BLUE, Colors.GREEN, Colors.RED, Colors.YELLOW]],
            
            [[Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.RED], 
             [Colors.RED, Colors.BLUE, Colors.YELLOW, Colors.GREEN], 
             [Colors.BLUE, Colors.GREEN, Colors.RED, Colors.YELLOW], 
             [Colors.YELLOW, Colors.RED, Colors.GREEN, Colors.BLUE]]
        ]
        
        self.boards = [SmallBoard(grid) for grid in color_grids]
        
    def get_used_boards(self):
        """Get list of boards currently placed on the game board"""
        used_boards = []
        for position in self.game_board.positions:
            if position.has_board():
                used_boards.append(position.board)
        return used_boards
    
    def handle_events(self):
        """Handle all game events"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos)
                    
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_down(event)
                        
                elif event.type == pygame.MOUSEMOTION:
                    if self.selected_board is not None:
                        self.selected_position = event.pos
                        
        except Exception as e:
            print(f"Unhandled exception: {e}")
            pygame.event.clear()
            
        return True
        
    def handle_mouse_down(self, pos):
        """Handle mouse button down event"""
        mouse_x, mouse_y = pos
        
        # Check if a grid position with a board is clicked
        for idx, position in enumerate(self.game_board.positions):
            if position.has_board() and position.x <= mouse_x < position.x + self.TILE_SIZE and position.y <= mouse_y < position.y + self.TILE_SIZE:
                self.selected_board = position.remove_board()
                self.selected_from_position = idx
                self.selected_position = pos
                return
                
        # Check if a board in inventory is clicked
        used_boards = self.get_used_boards()
        board = self.inventory.get_board_at(mouse_x, mouse_y, used_boards)
        if board:
            self.selected_board = board
            self.selected_from_position = None
            self.selected_position = pos
            
    def handle_mouse_up(self, pos):
        """Handle mouse button up event"""
        if self.selected_board is None:
            return
            
        mouse_x, mouse_y = pos
        
        # Find grid position at mouse coordinates
        target_position = self.game_board.get_position_at(mouse_x, mouse_y)
        
        if target_position:
            # Get index of target position
            target_idx = self.game_board.positions.index(target_position)
            
            # Handle board exchange
            if target_position.has_board():
                # Store the board that's already there
                existing_board = target_position.board
                
                # Place selected board at target position
                target_position.place_board(self.selected_board)
                
                # If selected board was from game board, place existing board there
                if self.selected_from_position is not None:
                    self.game_board.positions[self.selected_from_position].place_board(existing_board)
            else:
                # Simple placement with no exchange
                target_position.place_board(self.selected_board)
                
        elif self.selected_from_position is not None:
            # Return board to original position if not dropped on valid target
            self.game_board.positions[self.selected_from_position].place_board(self.selected_board)
            
        # Reset selection
        self.selected_board = None
        self.selected_from_position = None
        self.selected_position = None
        
    def handle_key_down(self, event):
        """Handle key down event"""
        if self.selected_board is not None and event.key == pygame.K_r:
            self.selected_board.rotate()
    
    def draw(self):
        """Draw the game"""
        # Fill background
        self.screen.fill(Colors.BLACK)
        
        # Draw game board
        self.game_board.draw(self.screen)
        
        # Draw inventory
        used_boards = self.get_used_boards()
        self.inventory.draw(self.screen, used_boards)
        
        # Draw selected board if any
        if self.selected_board is not None and self.selected_position is not None:
            mouse_x, mouse_y = self.selected_position
            self.selected_board.draw(
                self.screen, 
                mouse_x - self.TILE_SIZE // 2, 
                mouse_y - self.TILE_SIZE // 2, 
                self.TILE_SIZE
            )
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()