import pygame
import random
import threading
import time

# Tamanho do tabuleiro e blocos
BOARD_WIDTH = 10
BOARD_HEIGHT = 22
BLOCK_SIZE = 30
PANEL_HEIGHT = 40  # Painel superior com pontuação e tempo

# Área total do jogo
GAME_WIDTH = BOARD_WIDTH * BLOCK_SIZE
GAME_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE + PANEL_HEIGHT

pygame.init()
FONT = pygame.font.SysFont('Arial', 24)

# Cores usadas no jogo
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    '': (0, 0, 0),  # fundo vazio
    'gray': (128, 128, 128),  # borda
    'white': (255, 255, 255)  # contorno
}

# Formatos das peças
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

class TetrisGame:
    def __init__(self):
        # Janela em fullscreen (usa a tela toda)
        self.fullscreen = True
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Tetris Centralizado")

        # Superfície onde o jogo é desenhado
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # Cria tabuleiro vazio
        self.board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.lock = threading.Semaphore(1)  # Para usar com threads

        # Estado do jogo
        self.current_shape = None
        self.current_piece = None
        self.piece_x = 0
        self.piece_y = 0
        self.running = True
        self.paused = False
        self.score = 0

        self.spawn_piece()  # Gera primeira peça

        self.start_time = time.time()
        self.elapsed_time = 0

        # Thread para gravidade (queda automática da peça)
        threading.Thread(target=self.gravity_thread, daemon=True).start()

    def spawn_piece(self):
        # Gera nova peça e coloca no topo
        self.current_shape = random.choice(list(SHAPES.keys()))
        self.current_piece = [row[:] for row in SHAPES[self.current_shape]]
        self.piece_x = BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        if not self.valid_position(self.piece_x, self.piece_y, self.current_piece):
            self.running = False  # Fim de jogo

    def valid_position(self, x, y, shape):
        # Verifica se a posição é válida
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    nx, ny = x + j, y + i
                    if nx < 0 or nx >= BOARD_WIDTH or ny < 0 or ny >= BOARD_HEIGHT:
                        return False
                    if self.board[ny][nx]:
                        return False
        return True

    def move(self, dx, dy):
        # Tenta mover a peça
        if not self.running or self.paused:
            return False
        new_x = self.piece_x + dx
        new_y = self.piece_y + dy
        if self.valid_position(new_x, new_y, self.current_piece):
            self.piece_x = new_x
            self.piece_y = new_y
            return True
        return False

    def rotate(self):
        # Roda a peça 90 graus
        if not self.running or self.paused:
            return
        rotated = list(zip(*self.current_piece[::-1]))
        rotated = [list(row) for row in rotated]
        if self.valid_position(self.piece_x, self.piece_y, rotated):
            self.current_piece = rotated

    def freeze_piece(self):
        # Grava a peça no tabuleiro
        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.piece_y + i][self.piece_x + j] = self.current_shape

    def clear_lines(self):
        # Remove linhas completas e soma pontuação
        lines_cleared = 0
        new_board = []
        for row in self.board:
            if all(cell != '' for cell in row):
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, ['' for _ in range(BOARD_WIDTH)])
        self.board = new_board
        self.score += lines_cleared * 100

    def gravity_thread(self):
        # Faz a peça cair a cada 0.5s
        while self.running:
            time.sleep(0.5)
            if not self.paused:
                with self.lock:
                    if not self.move(0, 1):
                        self.freeze_piece()
                        self.clear_lines()
                        self.spawn_piece()

    def draw_board(self):
        # Prepara a tela de jogo
        self.game_surface.fill((0, 0, 0))

        # Painel com tempo e pontuação
        pygame.draw.rect(self.game_surface, (40, 40, 40), (0, 0, GAME_WIDTH, PANEL_HEIGHT))
        self.elapsed_time = int(time.time() - self.start_time)
        time_text = FONT.render(f"Tempo: {self.elapsed_time//60:02d}:{self.elapsed_time%60:02d}", True, (255,255,255))
        score_text = FONT.render(f"Pontos: {self.score}", True, (255,255,255))
        self.game_surface.blit(time_text, (10, 5))
        self.game_surface.blit(score_text, (GAME_WIDTH - score_text.get_width() - 10, 5))

        # Tabuleiro e peças fixas
        board_top = PANEL_HEIGHT
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                color = COLORS[self.board[y][x]] if self.board[y][x] else COLORS['']
                rect = pygame.Rect(x*BLOCK_SIZE, board_top + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.game_surface, color, rect)
                pygame.draw.rect(self.game_surface, COLORS['gray'], rect, 1)

        # Peça atual em movimento
        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    x = (self.piece_x + j) * BLOCK_SIZE
                    y = board_top + (self.piece_y + i) * BLOCK_SIZE
                    rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.game_surface, COLORS[self.current_shape], rect)
                    pygame.draw.rect(self.game_surface, COLORS['white'], rect, 1)

        # Mensagem se estiver pausado
        if self.paused:
            pause_text = FONT.render("PAUSADO - Pressione P para continuar", True, (255, 255, 255))
            self.game_surface.blit(pause_text, (GAME_WIDTH//2 - pause_text.get_width()//2, GAME_HEIGHT//2))

        # Mensagem de Game Over
        if not self.running:
            gameover_text = FONT.render("GAME OVER", True, (255, 0, 0))
            final_score_text = FONT.render(f"Pontos finais: {self.score}", True, (255, 255, 255))
            self.game_surface.blit(gameover_text, (GAME_WIDTH//2 - gameover_text.get_width()//2, GAME_HEIGHT//2 - 30))
            self.game_surface.blit(final_score_text, (GAME_WIDTH//2 - final_score_text.get_width()//2, GAME_HEIGHT//2 + 10))

        # Centraliza o jogo na tela cheia
        self.screen.fill((0, 0, 0))  # fundo preto
        x_offset = (self.screen_width - GAME_WIDTH) // 2
        y_offset = (self.screen_height - GAME_HEIGHT) // 2
        self.screen.blit(self.game_surface, (x_offset, y_offset))

    def run(self):
        # Loop principal do jogo
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif self.running and not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate()

            self.draw_board()
            pygame.display.flip()
            clock.tick(30)  # Limita a 30 quadros por segundo

# Inicia o jogo
if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()
