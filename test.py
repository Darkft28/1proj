import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Colors
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
RED = (255, 180, 180)   # Rose pâle
BLUE = (180, 210, 255)  # Bleu pastel
YELLOW = (255, 255, 180)  # Jaune crème
GREEN = (180, 255, 180)  # Vert menthe



# Grid dimensions
GRID_SIZE = 2
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

# Small board dimensions
SMALL_BOARD_SIZE = 4
SMALL_TILE_SIZE = TILE_SIZE // SMALL_BOARD_SIZE

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

# Function to draw the large board
def draw_large_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

# Function to draw a small board
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

# Main game loop
running = True
while running:
    screen.fill(BLACK)

    # Draw the large board
    draw_large_board()

    # Draw placed small boards
    for idx, board_info in enumerate(placed_boards):
        if board_info is not None:
            board, x, y, rotation = board_info
            draw_small_board(board, x, y, rotation)

    # Draw unplaced small boards
    for idx, board in enumerate(small_boards):
        if idx != selected_board and all(placed_boards[i] is None or placed_boards[i][0] != board for i in range(4)):
            x, y = (idx * TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE)
            draw_small_board(board, x, y, 0)

    # Handle events
    try:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Check if a small board is selected
                for idx, board in enumerate(small_boards):
                    if idx != selected_board and all(placed_boards[i] is None or placed_boards[i][0] != board for i in range(4)):
                        x, y = (idx * TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE)
                        if x <= mouse_x < x + TILE_SIZE and y <= mouse_y < y + TILE_SIZE:
                            selected_board = idx
                            selected_position = (mouse_x, mouse_y)
                            break

                # Check if placed board is clicked
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

                    # Snap to grid
                    grid_x = mouse_x // TILE_SIZE
                    grid_y = mouse_y // TILE_SIZE

                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                        placed_boards[grid_y * GRID_SIZE + grid_x] = (
                            small_boards[selected_board],
                            grid_x * TILE_SIZE,
                            grid_y * TILE_SIZE,
                            selected_rotation
                        )

                    selected_board = None

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
        draw_small_board(small_boards[selected_board], mouse_x - TILE_SIZE // 2, mouse_y - TILE_SIZE // 2, selected_rotation)

    pygame.display.flip()
pygame.quit()