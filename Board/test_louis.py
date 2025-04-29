import pygame
import sys

class BoardGame:
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (40, 40, 40)
    RED = (173, 7, 60)      # Rose pâle
    BLUE = (29, 185, 242)   # Bleu pastel
    YELLOW = (235, 226, 56) # Jaune crème
    GREEN = (24, 181, 87)   # Vert menthe

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen dimensions
        self.SCREEN_WIDTH = 1000  # Increased width for side panel
        self.GAME_WIDTH = 800     # Original game area width
        self.SCREEN_HEIGHT = 800
        
        # Grid dimensions
        self.GRID_SIZE = 2
        self.TILE_SIZE = self.GAME_WIDTH // self.GRID_SIZE
        
        # Small board dimensions
        self.SMALL_BOARD_SIZE = 4
        self.SMALL_TILE_SIZE = self.TILE_SIZE // self.SMALL_BOARD_SIZE
        
        # Combined board
        self.COMBINED_BOARD_SIZE = self.SMALL_BOARD_SIZE * self.GRID_SIZE  # 8x8
        
        # Editor panel constants
        self.PANEL_X = self.GAME_WIDTH
        self.PANEL_WIDTH = self.SCREEN_WIDTH - self.GAME_WIDTH
        self.PREVIEW_SIZE = 150
        self.PANEL_PADDING = 20
        
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Board Placement and Rotation")
        
        # Create small boards
        self.small_boards = [
            [[self.RED, self.BLUE, self.YELLOW, self.GREEN], 
             [self.BLUE, self.GREEN, self.RED, self.YELLOW], 
             [self.YELLOW, self.RED, self.GREEN, self.BLUE], 
             [self.GREEN, self.YELLOW, self.BLUE, self.RED]],
            
            [[self.BLUE, self.GREEN, self.RED, self.YELLOW], 
             [self.YELLOW, self.RED, self.GREEN, self.BLUE], 
             [self.GREEN, self.YELLOW, self.BLUE, self.RED], 
             [self.RED, self.BLUE, self.YELLOW, self.GREEN]],
            
            [[self.YELLOW, self.RED, self.GREEN, self.BLUE], 
             [self.GREEN, self.YELLOW, self.BLUE, self.RED], 
             [self.RED, self.BLUE, self.YELLOW, self.GREEN], 
             [self.BLUE, self.GREEN, self.RED, self.YELLOW]],
            
            [[self.GREEN, self.YELLOW, self.BLUE, self.RED], 
             [self.RED, self.BLUE, self.YELLOW, self.GREEN], 
             [self.BLUE, self.GREEN, self.RED, self.YELLOW], 
             [self.YELLOW, self.RED, self.GREEN, self.BLUE]]
        ]
        
        # Variables for dragging
        self.selected_board = None
        self.selected_position = None
        self.selected_rotation = 0
        self.placed_boards = [None, None, None, None]  # To track boards placed in the 2x2 grid
        
        # Mode
        self.edit_mode = True  # True: editing mode, False: display mode
        self.combined_board = None  # 8x8 combined board
        
    def draw_large_board(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                rect = pygame.Rect(col * self.TILE_SIZE, row * self.TILE_SIZE, 
                                  self.TILE_SIZE, self.TILE_SIZE)
                pygame.draw.rect(self.screen, self.WHITE, rect, 1)
    
    def draw_small_board(self, board, x, y, rotation):
        for row in range(self.SMALL_BOARD_SIZE):
            for col in range(self.SMALL_BOARD_SIZE):
                # Adjust for rotation
                if rotation == 0:
                    color = board[row][col]
                elif rotation == 90:
                    color = board[self.SMALL_BOARD_SIZE - 1 - col][row]
                elif rotation == 180:
                    color = board[self.SMALL_BOARD_SIZE - 1 - row][self.SMALL_BOARD_SIZE - 1 - col]
                elif rotation == 270:
                    color = board[col][self.SMALL_BOARD_SIZE - 1 - row]
    
                rect = pygame.Rect(
                    x + col * self.SMALL_TILE_SIZE, 
                    y + row * self.SMALL_TILE_SIZE, 
                    self.SMALL_TILE_SIZE, 
                    self.SMALL_TILE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.WHITE, rect, 1)
    
    def draw_editor_panel(self):
        # Draw panel background
        panel_rect = pygame.Rect(self.PANEL_X, 0, self.PANEL_WIDTH, self.SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (60, 60, 60), panel_rect)
        
        # Draw title
        font = pygame.font.Font(None, 36)
        title = font.render("Board Editor", True, self.WHITE)
        self.screen.blit(title, (self.PANEL_X + self.PANEL_PADDING, self.PANEL_PADDING))
        
        if self.edit_mode:
            # Draw available boards preview
            for idx, board in enumerate(self.small_boards):
                if all(self.placed_boards[i] is None or self.placed_boards[i][0] != board for i in range(4)):
                    y_pos = idx * (self.PREVIEW_SIZE + self.PANEL_PADDING) + 80
                    preview_rect = pygame.Rect(self.PANEL_X + self.PANEL_PADDING, y_pos, 
                                             self.PREVIEW_SIZE, self.PREVIEW_SIZE)
                    pygame.draw.rect(self.screen, (80, 80, 80), preview_rect)
                    pygame.draw.rect(self.screen, self.WHITE, preview_rect, 2)
                    
                    # Draw miniature version of the board
                    mini_tile = self.PREVIEW_SIZE // self.SMALL_BOARD_SIZE
                    for row in range(self.SMALL_BOARD_SIZE):
                        for col in range(self.SMALL_BOARD_SIZE):
                            color = board[row][col]
                            mini_rect = pygame.Rect(
                                self.PANEL_X + self.PANEL_PADDING + col * mini_tile,
                                y_pos + row * mini_tile,
                                mini_tile,
                                mini_tile
                            )
                            pygame.draw.rect(self.screen, color, mini_rect)
                            pygame.draw.rect(self.screen, self.WHITE, mini_rect, 1)
            
            # Check if all boards are placed
            all_boards_placed = all(board is not None for board in self.placed_boards)
            
            # Draw the accept button only if all boards are placed
            if all_boards_placed:
                button_x = self.PANEL_X + self.PANEL_PADDING
                button_y = self.SCREEN_HEIGHT - self.PANEL_PADDING - 50
                button_width = self.PANEL_WIDTH - (2 * self.PANEL_PADDING)
                button_height = 40
                
                # Draw the button
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                # Change color on hover
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_x, mouse_y):
                    button_color = (100, 200, 100)  # Lighter green on hover
                else:
                    button_color = (50, 150, 50)  # Normal green
                
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)
                
                # Button text
                font = pygame.font.Font(None, 30)
                text = font.render("Accepter", True, self.WHITE)
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)
                
                return button_rect  # Return the rectangle for click detection
            
        return None
    
    def handle_mouse_down(self, pos):
        mouse_x, mouse_y = pos
        
        # Check if click is in editor panel
        if self.PANEL_X <= mouse_x <= self.SCREEN_WIDTH:
            # Check for button click
            button_rect = self.draw_editor_panel()
            if button_rect and button_rect.collidepoint(mouse_x, mouse_y):
                if self.edit_mode:
                    # Check if all boards are placed
                    if all(board is not None for board in self.placed_boards):
                        self.create_combined_board()
                        self.edit_mode = False
                else:
                    # Reset button clicked
                    self.edit_mode = True
                    self.combined_board = None
                    self.placed_boards = [None, None, None, None]
                    self.selected_board = None
                    self.selected_position = None
                    self.selected_rotation = 0
                return
            
            # Only handle board selection in edit mode
            if self.edit_mode:
                idx = (mouse_y - 80) // (self.PREVIEW_SIZE + self.PANEL_PADDING)
                if 0 <= idx < len(self.small_boards):
                    if all(self.placed_boards[i] is None or self.placed_boards[i][0] != self.small_boards[idx] for i in range(4)):
                        self.selected_board = idx
                        self.selected_position = (self.PANEL_X + self.PANEL_PADDING, 
                                                80 + idx * (self.PREVIEW_SIZE + self.PANEL_PADDING))
        
        # Check if placed board is clicked (only in edit mode)
        elif self.edit_mode:
            for idx, board_info in enumerate(self.placed_boards):
                if board_info is not None:
                    board, x, y, rotation = board_info
                    if x <= mouse_x < x + self.TILE_SIZE and y <= mouse_y < y + self.TILE_SIZE:
                        self.selected_board = self.small_boards.index(board)
                        self.selected_position = (mouse_x, mouse_y)
                        self.placed_boards[idx] = None
                        break
    
    def handle_mouse_up(self, pos):
        # Only handle in edit mode
        if not self.edit_mode:
            return
            
        if self.selected_board is not None:
            mouse_x, mouse_y = pos
            
            if mouse_x < self.GAME_WIDTH:  # Only place if in game area
                grid_x = mouse_x // self.TILE_SIZE
                grid_y = mouse_y // self.TILE_SIZE
                
                if 0 <= grid_x < self.GRID_SIZE and 0 <= grid_y < self.GRID_SIZE:
                    target_index = grid_y * self.GRID_SIZE + grid_x
                    
                    existing_board_info = self.placed_boards[target_index]
                    self.placed_boards[target_index] = (
                        self.small_boards[self.selected_board],
                        grid_x * self.TILE_SIZE,
                        grid_y * self.TILE_SIZE,
                        self.selected_rotation
                    )
                    
                    if existing_board_info is not None:
                        old_board, _, _, old_rotation = existing_board_info
                        self.selected_board = self.small_boards.index(old_board)
                        self.selected_rotation = old_rotation
                        self.selected_position = (mouse_x, mouse_y)
                    else:
                        self.selected_board = None
                        self.selected_position = None
    
    def handle_key_down(self, key):
        # Only handle in edit mode
        if not self.edit_mode:
            return
            
        if self.selected_board is not None:
            if key == pygame.K_r:  # Rotate the board
                self.selected_rotation = (self.selected_rotation + 90) % 360
    
    def handle_mouse_motion(self, pos):
        # Only handle in edit mode
        if not self.edit_mode:
            return
            
        if self.selected_board is not None and self.selected_position is not None:
            self.selected_position = pos
            
    def create_combined_board(self):
        """Create 8x8 combined board from the four 4x4 placed boards"""
        # Initialize 8x8 board
        self.combined_board = [[None for _ in range(self.COMBINED_BOARD_SIZE)] for _ in range(self.COMBINED_BOARD_SIZE)]
        
        # Process each placed board
        for idx, board_info in enumerate(self.placed_boards):
            if board_info is not None:
                board, _, _, rotation = board_info
                
                # Calculate position in the large grid
                grid_x = idx % self.GRID_SIZE
                grid_y = idx // self.GRID_SIZE
                
                # Fill the combined board with colors from this small board
                for small_row in range(self.SMALL_BOARD_SIZE):
                    for small_col in range(self.SMALL_BOARD_SIZE):
                        # Get color based on rotation
                        if rotation == 0:
                            color = board[small_row][small_col]
                        elif rotation == 90:
                            color = board[self.SMALL_BOARD_SIZE - 1 - small_col][small_row]
                        elif rotation == 180:
                            color = board[self.SMALL_BOARD_SIZE - 1 - small_row][self.SMALL_BOARD_SIZE - 1 - small_col]
                        elif rotation == 270:
                            color = board[small_col][self.SMALL_BOARD_SIZE - 1 - small_row]
                            
                        # Calculate position in the combined board
                        combined_row = (grid_y * self.SMALL_BOARD_SIZE) + small_row
                        combined_col = (grid_x * self.SMALL_BOARD_SIZE) + small_col
                        
                        # Set the color
                        self.combined_board[combined_row][combined_col] = color
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        if self.edit_mode:
            # Draw the game area
            self.draw_large_board()
            
            # Draw placed small boards
            for idx, board_info in enumerate(self.placed_boards):
                if board_info is not None:
                    board, x, y, rotation = board_info
                    self.draw_small_board(board, x, y, rotation)
            
            # Draw the currently dragged board
            if self.selected_board is not None and self.selected_position is not None:
                mouse_x, mouse_y = self.selected_position
                self.draw_small_board(self.small_boards[self.selected_board], 
                                  mouse_x - self.SMALL_TILE_SIZE * 2,
                                  mouse_y - self.SMALL_TILE_SIZE * 2,
                                  self.selected_rotation)
        else:
            # Draw the combined board
            if self.combined_board:
                self.draw_combined_board()
        
        # Draw the editor panel (always)
        self.draw_editor_panel()
        
        pygame.display.flip()
        
    def draw_combined_board(self):
        # Draw the 8x8 combined board
        cell_size = self.GAME_WIDTH // self.COMBINED_BOARD_SIZE
        
        for row in range(self.COMBINED_BOARD_SIZE):
            for col in range(self.COMBINED_BOARD_SIZE):
                color = self.combined_board[row][col]
                
                if color:
                    rect = pygame.Rect(
                        col * cell_size, 
                        row * cell_size, 
                        cell_size, 
                        cell_size
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, self.WHITE, rect, 1)
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            try:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # Exit with Escape key
                            running = False
                        else:
                            self.handle_key_down(event.key)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_down(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_mouse_up(event.pos)
                    elif event.type == pygame.MOUSEMOTION:
                        self.handle_mouse_motion(event.pos)
            
            except Exception as e:
                print(f"Unhandled exception: {e}")
                pygame.event.clear()
            
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
        
        pygame.quit()
        sys.exit()

# Main entry point
if __name__ == "__main__":
    game = BoardGame()
    game.run()