import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000  # Increased width for side panel
GAME_WIDTH = 800     # Original game area width
SCREEN_HEIGHT = 800

# Colors
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
RED = (173, 7, 60)   # Rose pâle
BLUE = (29, 185, 242)  # Bleu pastel
YELLOW = (235, 226, 56)  # Jaune crème
GREEN = (24, 181, 87)  # Vert menthe

# Grid dimensions
GRID_SIZE = 2
TILE_SIZE = GAME_WIDTH // GRID_SIZE

# Small board dimensions
SMALL_BOARD_SIZE = 4
SMALL_TILE_SIZE = TILE_SIZE // SMALL_BOARD_SIZE

# Editor panel constants
PANEL_X = GAME_WIDTH
PANEL_WIDTH = SCREEN_WIDTH - GAME_WIDTH
PREVIEW_SIZE = 150
PANEL_PADDING = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Board Placement and Rotation")

# Create small boards
small_boards = [
    [[RED, BLUE, YELLOW, GREEN], [BLUE, GREEN, RED, YELLOW], [YELLOW, RED, GREEN, BLUE], [GREEN, YELLOW, BLUE, RED]],
    [[BLUE, GREEN, RED, YELLOW], [YELLOW, RED, GREEN, BLUE], [GREEN, YELLOW, BLUE, RED], [RED, BLUE, YELLOW, GREEN]],
    [[YELLOW, RED, GREEN, BLUE], [GREEN, YELLOW, BLUE, RED], [RED, BLUE, YELLOW, GREEN], [BLUE, GREEN, RED, YELLOW]],
    [[GREEN, YELLOW, BLUE, RED], [RED, BLUE, YELLOW, GREEN], [BLUE, GREEN, RED, YELLOW], [YELLOW, RED, GREEN, BLUE]]
]

# Variables for dragging
selected_board = None
selected_position = None
selected_rotation = 0
placed_boards = [None, None, None, None]  # To track boards placed in the 2x2 grid

def draw_large_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_small_board(board, x, y, rotation):
    for row in range(SMALL_BOARD_SIZE):
        for col in range(SMALL_BOARD_SIZE):
            # Adjust for rotation
            if rotation == 0:
                color = board[row][col]
            elif rotation == 90:
                color = board[SMALL_BOARD_SIZE - 1 - col][row]
            elif rotation == 180:
                color = board[SMALL_BOARD_SIZE - 1 - row][SMALL_BOARD_SIZE - 1 - col]
            elif rotation == 270:
                color = board[col][SMALL_BOARD_SIZE - 1 - row]

            rect = pygame.Rect(
                x + col * SMALL_TILE_SIZE, y + row * SMALL_TILE_SIZE, SMALL_TILE_SIZE, SMALL_TILE_SIZE
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_editor_panel():
    # Draw panel background
    panel_rect = pygame.Rect(PANEL_X, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (60, 60, 60), panel_rect)
    
    # Draw title
    font = pygame.font.Font(None, 36)
    title = font.render("Board Editor", True, WHITE)
    screen.blit(title, (PANEL_X + PANEL_PADDING, PANEL_PADDING))
    
    # Draw available boards preview
    for idx, board in enumerate(small_boards):
        if all(placed_boards[i] is None or placed_boards[i][0] != board for i in range(4)):
            y_pos = idx * (PREVIEW_SIZE + PANEL_PADDING) + 80
            preview_rect = pygame.Rect(PANEL_X + PANEL_PADDING, y_pos, PREVIEW_SIZE, PREVIEW_SIZE)
            pygame.draw.rect(screen, (80, 80, 80), preview_rect)
            pygame.draw.rect(screen, WHITE, preview_rect, 2)
            
            # Draw miniature version of the board
            mini_tile = PREVIEW_SIZE // SMALL_BOARD_SIZE
            for row in range(SMALL_BOARD_SIZE):
                for col in range(SMALL_BOARD_SIZE):
                    color = board[row][col]
                    mini_rect = pygame.Rect(
                        PANEL_X + PANEL_PADDING + col * mini_tile,
                        y_pos + row * mini_tile,
                        mini_tile,
                        mini_tile
                    )
                    pygame.draw.rect(screen, color, mini_rect)
                    pygame.draw.rect(screen, WHITE, mini_rect, 1)

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    
    # Draw the game area
    draw_large_board()
    
    # Draw the editor panel
    draw_editor_panel()
    
    # Draw placed small boards
    for idx, board_info in enumerate(placed_boards):
        if board_info is not None:
            board, x, y, rotation = board_info
            draw_small_board(board, x, y, rotation)

    try:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Check if click is in editor panel
                if PANEL_X <= mouse_x <= SCREEN_WIDTH:
                    idx = (mouse_y - 80) // (PREVIEW_SIZE + PANEL_PADDING)
                    if 0 <= idx < len(small_boards):
                        if all(placed_boards[i] is None or placed_boards[i][0] != small_boards[idx] for i in range(4)):
                            selected_board = idx
                            selected_position = (PANEL_X + PANEL_PADDING, 80 + idx * (PREVIEW_SIZE + PANEL_PADDING))
                
                # Check if placed board is clicked
                else:
                    for idx, board_info in enumerate(placed_boards):
                        if board_info is not None:
                            board, x, y, rotation = board_info
                            if x <= mouse_x < x + TILE_SIZE and y <= mouse_y < y + TILE_SIZE:
                                selected_board = small_boards.index(board)
                                selected_position = (mouse_x, mouse_y)
                                placed_boards[idx] = None
                                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_board is not None:
                    mouse_x, mouse_y = event.pos
                    
                    if mouse_x < GAME_WIDTH:  # Only place if in game area
                        grid_x = mouse_x // TILE_SIZE
                        grid_y = mouse_y // TILE_SIZE
                        
                        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                            target_index = grid_y * GRID_SIZE + grid_x
                            
                            existing_board_info = placed_boards[target_index]
                            placed_boards[target_index] = (
                                small_boards[selected_board],
                                grid_x * TILE_SIZE,
                                grid_y * TILE_SIZE,
                                selected_rotation
                            )
                            
                            if existing_board_info is not None:
                                old_board, _, _, old_rotation = existing_board_info
                                selected_board = small_boards.index(old_board)
                                selected_rotation = old_rotation
                                selected_position = (mouse_x, mouse_y)
                            else:
                                selected_board = None
                                selected_position = None

            elif event.type == pygame.KEYDOWN:
                if selected_board is not None:
                    if event.key == pygame.K_r:  # Rotate the board
                        selected_rotation = (selected_rotation + 90) % 360

            elif event.type == pygame.MOUSEMOTION:
                if selected_board is not None and selected_position is not None:
                    selected_position = event.pos

    except Exception as e:
        print(f"Unhandled exception: {e}")
        pygame.event.clear()

    # Draw the currently dragged board
    if selected_board is not None and selected_position is not None:
        mouse_x, mouse_y = selected_position
        draw_small_board(small_boards[selected_board], 
                        mouse_x - SMALL_TILE_SIZE * 2,
                        mouse_y - SMALL_TILE_SIZE * 2,
                        selected_rotation)

    pygame.display.flip()

pygame.quit()