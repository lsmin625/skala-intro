# tetris.py
import pygame
import random
from dataclasses import dataclass

# -----------------------------
# Config
# -----------------------------
CELL = 30
COLS = 10
ROWS = 20

BOARD_W = COLS * CELL
BOARD_H = ROWS * CELL

FPS = 60
DROP_MS = 500          # 자동 낙하 간격 (ms)
SOFT_DROP_MS = 50      # 아래키 누를 때 낙하 간격 (ms)

# 색상 (RGB)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (230, 230, 230)

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}

# 각 테트로미노(4x4) 형태 - 회전은 행렬 회전으로 처리
SHAPES = {
    "I": [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "O": [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "T": [
        [0, 1, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "S": [
        [0, 1, 1, 0],
        [1, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "Z": [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "J": [
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "L": [
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
}

# -----------------------------
# Helpers
# -----------------------------
def rotate_cw(mat):
    """4x4 행렬을 시계방향 90도 회전"""
    return [list(row) for row in zip(*mat[::-1])]

def new_board():
    # board[y][x] = None or color tuple
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def inside(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS

@dataclass
class Piece:
    kind: str
    mat: list
    x: int
    y: int

    @property
    def color(self):
        return COLORS[self.kind]

def spawn_piece():
    kind = random.choice(list(SHAPES.keys()))
    mat = [row[:] for row in SHAPES[kind]]
    # 4x4 기준 중앙쯤에서 시작
    x = COLS // 2 - 2
    y = 0
    return Piece(kind, mat, x, y)

def can_place(board, piece: Piece, dx=0, dy=0, new_mat=None):
    mat = new_mat if new_mat is not None else piece.mat
    for r in range(4):
        for c in range(4):
            if mat[r][c] == 0:
                continue
            nx = piece.x + c + dx
            ny = piece.y + r + dy

            if nx < 0 or nx >= COLS or ny >= ROWS:
                return False
            if ny >= 0 and board[ny][nx] is not None:
                return False
    return True

def lock_piece(board, piece: Piece):
    for r in range(4):
        for c in range(4):
            if piece.mat[r][c] == 0:
                continue
            x = piece.x + c
            y = piece.y + r
            if 0 <= y < ROWS and 0 <= x < COLS:
                board[y][x] = piece.color

def clear_lines(board):
    """가득 찬 줄 삭제 후 위에서 내려오게"""
    new_rows = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_rows)
    for _ in range(cleared):
        new_rows.insert(0, [None for _ in range(COLS)])
    return new_rows, cleared

def hard_drop(board, piece):
    """가능한 만큼 아래로 즉시 떨어뜨린다."""
    dist = 0
    while can_place(board, piece, dy=dist + 1):
        dist += 1
    piece.y += dist

# -----------------------------
# Rendering
# -----------------------------
def draw_board(screen, board, piece: Piece, score, lines):
    screen.fill(BLACK)

    # 격자 + 고정 블록
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, GRAY, rect, 1)
            if board[y][x] is not None:
                pygame.draw.rect(screen, board[y][x], rect.inflate(-2, -2))

    # 현재 떨어지는 블록
    for r in range(4):
        for c in range(4):
            if piece.mat[r][c] == 0:
                continue
            x = piece.x + c
            y = piece.y + r
            if y < 0:
                continue
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, piece.color, rect.inflate(-2, -2))

    # 텍스트
    font = pygame.font.SysFont("consolas", 20)
    info = font.render(f"Score: {score}   Lines: {lines}", True, WHITE)
    screen.blit(info, (8, 8))

# -----------------------------
# Game loop
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_W, BOARD_H))
    pygame.display.set_caption("Tetris (pygame)")
    clock = pygame.time.Clock()

    board = new_board()
    piece = spawn_piece()

    # 게임 상태
    running = True
    game_over = False
    score = 0
    lines = 0

    drop_timer = 0
    current_drop_ms = DROP_MS

    while running:
        dt = clock.tick(FPS)
        drop_timer += dt

        # 입력 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    board = new_board()
                    piece = spawn_piece()
                    game_over = False
                    score = 0
                    lines = 0
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if can_place(board, piece, dx=-1):
                        piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if can_place(board, piece, dx=1):
                        piece.x += 1
                elif event.key == pygame.K_UP:
                    rotated = rotate_cw(piece.mat)
                    if can_place(board, piece, new_mat=rotated):
                        piece.mat = rotated
                elif event.key == pygame.K_SPACE:
                    hard_drop(board, piece)
                    lock_piece(board, piece)
                    board, cleared = clear_lines(board)
                    if cleared:
                        lines += cleared
                        score += cleared * 100
                    piece = spawn_piece()
                    if not can_place(board, piece):
                        game_over = True
                elif event.key == pygame.K_DOWN:
                    current_drop_ms = SOFT_DROP_MS

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    current_drop_ms = DROP_MS

        if game_over:
            screen.fill(BLACK)
            font = pygame.font.SysFont("consolas", 28)
            msg1 = font.render("GAME OVER", True, WHITE)
            msg2 = pygame.font.SysFont("consolas", 20).render("Press R to restart", True, WHITE)
            screen.blit(msg1, (BOARD_W // 2 - msg1.get_width() // 2, BOARD_H // 2 - 30))
            screen.blit(msg2, (BOARD_W // 2 - msg2.get_width() // 2, BOARD_H // 2 + 10))
            pygame.display.flip()
            continue

        # 자동 낙하
        if drop_timer >= current_drop_ms:
            drop_timer = 0
            if can_place(board, piece, dy=1):
                piece.y += 1
            else:
                # 바닥에 쌓기
                lock_piece(board, piece)
                board, cleared = clear_lines(board)
                if cleared:
                    lines += cleared
                    score += cleared * 100
                piece = spawn_piece()
                if not can_place(board, piece):
                    game_over = True

        draw_board(screen, board, piece, score, lines)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
