import pygame
import random
import threading
import time
import sys

# Tamanho do tabuleiro e blocos
BOARD_WIDTH = 10
BOARD_HEIGHT = 22
BLOCK_SIZE = 30
PANEL_HEIGHT = 60  # Painel superior aumentado
FOOTER_HEIGHT = 80  # Espaço para exibir controles abaixo do tabuleiro
SIDEBAR_WIDTH = 150  # Largura para hold e preview

# Área total do jogo
GAME_WIDTH = BOARD_WIDTH * BLOCK_SIZE + 2 * SIDEBAR_WIDTH
GAME_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE + PANEL_HEIGHT + FOOTER_HEIGHT

pygame.init()
FONT = pygame.font.SysFont('Arial', 18)
LARGE_FONT = pygame.font.SysFont('Arial', 24, bold=True)
TITLE_FONT = pygame.font.SysFont('Arial', 36, bold=True)

# Cores modernizadas
COLORS = {
    'I': (0, 240, 240),    # Ciano mais suave
    'O': (247, 211, 0),    # Amarelo ouro
    'T': (173, 77, 156),   # Roxo moderno
    'S': (66, 182, 66),    # Verde mais escuro
    'Z': (239, 51, 64),    # Vermelho vibrante
    'J': (0, 101, 182),    # Azul profundo
    'L': (239, 121, 33),   # Laranja
    '': (20, 20, 40),      # Fundo escuro
    'violeta': (80, 50, 120),  # Borda mais escura
    'white': (240, 240, 240),  # Contorno
    'panel': (30, 30, 60),     # Painel escuro
    'ghost': (100, 100, 120, 100),  # Fantasma com transparência
    'highlight': (255, 255, 255, 50)  # Destaque de linha
}

# Formatos das peças (mesmo do original)
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


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        if isinstance(color, str):
            self.color = COLORS.get(color, (random.randint(
                100, 255), random.randint(100, 255), random.randint(100, 255)))
        else:
            self.color = color[:3]
        # Ajustes: Aumentar o tamanho e a vida útil
        self.size = random.randint(5, 10)  # Tamanho maior
        self.speed_x = random.uniform(-3, 3)  # Mais dispersão
        self.speed_y = random.uniform(-6, -2)  # Mais impulso para cima
        self.lifetime = random.randint(40, 80)  # Duração maior
        self.alpha = 255

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - 3)  # Fading mais lento
        # Adicionar uma leve gravidade para que as partículas caiam um pouco
        self.speed_y += 0.2
        return self.lifetime > 0 and self.alpha > 0


class Menu:
    def __init__(self, screen_width, screen_height, game):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.surface = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA)
        self.buttons = [
            {"text": "Iniciar Jogo", "action": "start",
                "rect": pygame.Rect(0, 0, 300, 50)},
            {"text": "Sair", "action": "quit",
                "rect": pygame.Rect(0, 0, 300, 50)}
        ]
        self.title_particles = []
        self.background_particles = []
        self.title = "TETRIS MODERNO"
        self.title_pos_y = -100
        self.title_target_y = 100
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 32)
        self.animation_time = 0
        self.selected_button = 0
        self.transition_alpha = 255
        self.state = "entering"  # "entering", "menu", "exiting"
        self.next_state = None
        self.initialize_particles()

    def initialize_particles(self):
        # Partículas para o título
        for _ in range(30):
            x = random.randint(self.screen_width//2 - 200,
                               self.screen_width//2 + 200)
            y = random.randint(-200, -50)
            shape = random.choice(list(SHAPES.keys()))
            self.title_particles.append({
                "x": x,
                "y": y,
                "shape": shape,
                "speed": random.uniform(2, 5),
                "rotation": 0,
                "rotation_speed": random.uniform(-3, 3),
                "target_y": random.randint(150, 300)
            })

        # Partículas de fundo
        for _ in range(50):
            self.add_background_particle()

    def add_background_particle(self):
        shape = random.choice(list(SHAPES.keys()))
        self.background_particles.append({
            "x": random.randint(0, self.screen_width),
            "y": random.randint(0, self.screen_height),
            "shape": shape,
            "size": random.randint(10, 30),
            "alpha": random.randint(50, 150),
            "speed": random.uniform(0.2, 0.5),
            "rotation": 0,
            "rotation_speed": random.uniform(-0.5, 0.5)
        })

    def update(self):
        self.animation_time += 1

        # Animação de entrada do título
        if self.state == "entering":
            self.title_pos_y += (self.title_target_y - self.title_pos_y) * 0.1
            if abs(self.title_pos_y - self.title_target_y) < 1:
                self.state = "menu"

        # Transição de saída
        elif self.state == "exiting":
            self.transition_alpha += 10
            if self.transition_alpha >= 255:
                return self.next_state

        # Atualizar partículas do título
        for p in self.title_particles:
            if p["y"] < p["target_y"]:
                p["y"] += p["speed"]
            p["rotation"] += p["rotation_speed"]

        # Atualizar partículas de fundo
        for p in self.background_particles:
            p["y"] += p["speed"]
            p["rotation"] += p["rotation_speed"]
            if p["y"] > self.screen_height:
                self.background_particles.remove(p)
                self.add_background_particle()

        # Posicionar botões
        button_start_y = self.screen_height // 2
        for i, button in enumerate(self.buttons):
            target_x = self.screen_width // 2 - 150
            target_y = button_start_y + i * 70
            button["rect"].x += (target_x - button["rect"].x) * 0.1
            button["rect"].y += (target_y - button["rect"].y) * 0.1

        if self.state == "exiting" and self.transition_alpha >= 255:
            return self.next_state  # Retorna o próximo estado ("game")
        return None

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))

        # Desenhar partículas de fundo
        for p in self.background_particles:
            shape_surf = pygame.Surface(
                (p["size"], p["size"]), pygame.SRCALPHA)
            color = COLORS[p["shape"]]
            pygame.draw.rect(shape_surf, (*color, p["alpha"]),
                             (0, 0, p["size"], p["size"]))
            rotated = pygame.transform.rotate(shape_surf, p["rotation"])
            self.surface.blit(rotated, (p["x"] - rotated.get_width()//2,
                                        p["y"] - rotated.get_height()//2))

        # Desenhar título
        title_text = self.title_font.render(self.title, True, COLORS["white"])
        title_rect = title_text.get_rect(
            center=(self.screen_width//2, self.title_pos_y))

        # Efeito de brilho no título
        glow = pygame.Surface(
            (title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*COLORS["white"], 30),
                         (0, 0, glow.get_width(), glow.get_height()), border_radius=10)
        for i in range(3):
            pygame.draw.rect(glow, (*COLORS["white"], 10 + i*10),
                             (i*5, i*5, glow.get_width() -
                              i*10, glow.get_height()-i*10),
                             border_radius=10)

        self.surface.blit(glow, (title_rect.x - 10, title_rect.y - 10))
        self.surface.blit(title_text, title_rect)

        # Desenhar partículas do título
        for p in self.title_particles:
            block_size = 20
            shape = SHAPES[p["shape"]]
            shape_surf = pygame.Surface(
                (block_size * len(shape[0]), block_size * len(shape)), pygame.SRCALPHA)

            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(shape_surf, (*COLORS[p["shape"]], 150),
                                         (j * block_size, i * block_size, block_size, block_size))

            rotated = pygame.transform.rotate(shape_surf, p["rotation"])
            self.surface.blit(rotated, (p["x"] - rotated.get_width()//2,
                                        p["y"] - rotated.get_height()//2))

        # Desenhar botões
        for i, button in enumerate(self.buttons):
            color = COLORS["I"] if i == self.selected_button else COLORS["panel"]
            pygame.draw.rect(self.surface, color,
                             button["rect"], border_radius=10)
            pygame.draw.rect(
                self.surface, COLORS["white"], button["rect"], 2, border_radius=10)

            text = self.button_font.render(
                button["text"], True, COLORS["white"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.surface.blit(text, text_rect)

        # Adicionar instruções de controle
        controls_text = FONT.render(
            "Use SETAS ↑↓ e ENTER para selecionar", True, COLORS["white"])
        controls_rect = controls_text.get_rect(
            center=(self.screen_width//2, self.screen_height - 50))
        self.surface.blit(controls_text, controls_rect)

        # Transição
        if self.state == "exiting":
            overlay = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            self.surface.blit(overlay, (0, 0))

        screen.blit(self.surface, (0, 0))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_DOWN:
                    self.selected_button = (
                        self.selected_button + 1) % len(self.buttons)
                    # Som ao mover para baixo
                    self.game.play_sound(self.game.sound_menu_move)
                elif event.key == pygame.K_UP:
                    self.selected_button = (
                        self.selected_button - 1) % len(self.buttons)
                    # Som ao mover para cima
                    self.game.play_sound(self.game.sound_menu_move)
                elif event.key == pygame.K_RETURN:
                    # Som ao selecionar
                    self.game.play_sound(self.game.sound_menu_select)
                    return self.buttons[self.selected_button]["action"]

        return None

    def start_transition(self, next_state):
        # Som ao iniciar transição
        self.game.play_sound(self.game.sound_menu_select)
        self.state = "exiting"
        self.next_state = next_state
        self.transition_alpha = 0


class TetrisGame:
    def __init__(self):
        # Configuração da janela
        self.fullscreen = True
        self.display_info = pygame.display.Info()
        self.screen_width = self.display_info.current_w
        self.screen_height = self.display_info.current_h
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Tetris Moderno")

        # Superfície onde o jogo é desenhado
        self.game_surface = pygame.Surface(
            (GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)

        # Cria tabuleiro vazio
        self.board = [['' for _ in range(BOARD_WIDTH)]
                      for _ in range(BOARD_HEIGHT)]
        self.lock = threading.Semaphore(1)

        # Estado do jogo
        self.current_shape = None
        self.current_piece = None
        self.piece_x = 0
        self.piece_y = 0
        self.running = False  # Inicia como False, só começa quando selecionado no menu
        self.paused = False
        self.game_state = "menu"  # Começa no menu
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.hold_piece = None
        self.hold_used = False
        self.next_pieces = [random.choice(list(SHAPES.keys())) for _ in range(3)]

        # Efeitos visuais
        self.clear_effect = None
        self.clear_effect_time = 0
        self.rotate_angle = 0
        self.rotate_direction = 1
        self.particles = []

        # Tempo e música
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_over_time = None
        self.pause_start_time = None
        self.total_pause_duration = 0

        # Configurações de áudio
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        try:
            pygame.mixer.init()
            self.sound_available = True
        except pygame.error:
            print("Áudio indisponível.")
            self.sound_available = False

        # Playlist de músicas
        self.playlist = ["./Sons/musica1.mp3", "./Sons/musica2.mp3", "./Sons/musica3.mp3"]
        self.current_song_index = 0
        self.skip_song = False
        self.music_paused = False

        # Volumes
        self.master_volume = 0.5
        self.menu_music_volume = 1.0 * self.master_volume
        self.game_music_volume = 0.7 * self.master_volume
        self.music_volume = self.menu_music_volume * self.master_volume

        # Carrega os sons
        self.load_sounds()

        # Menu
        self.menu = Menu(self.screen_width, self.screen_height, self)

        # Threads
        threading.Thread(target=self.gravity_thread, daemon=True).start()
        threading.Thread(target=self.music_thread, daemon=True).start()

    def load_sounds(self):
        try:
            self.sound_menu_move = pygame.mixer.Sound('./Sons/menu_move.wav')
            self.sound_menu_move.set_volume(0.5)
        except Exception as e:
            print('Erro ao carregar menu_move.wav:', e)
            self.sound_menu_move = None

        try:
            self.sound_menu_select = pygame.mixer.Sound('./Sons/menu_select.wav')
            self.sound_menu_select.set_volume(0.5)
        except Exception as e:
            print('Erro ao carregar menu_select.wav:', e)
            self.sound_menu_select = None

        try:
            self.menu_music = './Sons/menu_music.wav'
            pygame.mixer.music.load(self.menu_music)
            pygame.mixer.music.set_volume(self.menu_music_volume)
        except Exception as e:
            print('Erro ao carregar menu_music.wav:', e)
            self.menu_music = None

        try:
            self.sound_encaixe = pygame.mixer.Sound('./Sons/encaixe.wav')
            self.sound_encaixe.set_volume(0.5)
        except Exception as e:
            print('Erro ao carregar encaixe.wav:', e)
            self.sound_encaixe = None

        try:
            self.sound_linha = pygame.mixer.Sound('./Sons/clear.wav')
            self.sound_linha.set_volume(0.7)
        except Exception as e:
            print('Erro ao carregar clear.wav:', e)
            self.sound_linha = None

        try:
            self.sound_rotate = pygame.mixer.Sound('./Sons/rotate.wav')
            self.sound_rotate.set_volume(0.3)
        except Exception as e:
            print('Erro ao carregar rotate.wav:', e)
            self.sound_rotate = None

        try:
            self.sound_move = pygame.mixer.Sound('./Sons/move.wav')
            self.sound_move.set_volume(0.2)
        except Exception as e:
            print('Erro ao carregar move.wav:', e)
            self.sound_move = None

        try:
            self.sound_hold = pygame.mixer.Sound('./Sons/hold.wav')
            self.sound_hold.set_volume(0.4)
        except Exception as e:
            print('Erro ao carregar hold.wav:', e)
            self.sound_hold = None

    def play_sound(self, sound):
        if self.sound_available and sound:
            try:
                sound.play()
            except:
                pass

    def music_thread(self):
        while True:
            try:
                if not hasattr(self, 'playlist') or not self.playlist:
                    time.sleep(1)
                    continue

                # Verifica se estamos no menu ou no jogo para definir o volume
                if self.game_state == "menu":
                    pygame.mixer.music.set_volume(self.menu_music_volume)
                else:
                    pygame.mixer.music.set_volume(self.game_music_volume)

                # Carrega e toca a música atual
                pygame.mixer.music.load(self.playlist[self.current_song_index])
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Erro ao tocar música: {e}")
                time.sleep(2)
                continue

            # Aguarda a música terminar ou ser interrompida
            while True:
                if self.skip_song:
                    pygame.mixer.music.stop()
                    self.skip_song = False
                    break
                if not pygame.mixer.music.get_busy() and not self.music_paused:
                    break
                time.sleep(0.1)

            # Avança para a próxima música
            if hasattr(self, 'playlist') and self.playlist:
                self.current_song_index = (self.current_song_index + 1) % len(self.playlist)

    def spawn_piece(self):
        try:
            while len(self.next_pieces) < 3:
                self.next_pieces.append(random.choice(list(SHAPES.keys())))

            self.current_shape = self.next_pieces.pop(0)
            self.current_piece = [row[:] for row in SHAPES[self.current_shape]]
            self.piece_x = BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
            self.piece_y = 0
            self.hold_used = False
            self.rotate_angle = 0
            self.last_move_time = time.time()

            if not self.valid_position(self.piece_x, self.piece_y, self.current_piece):
                self.running = False
                self.game_over_time = time.time()
                self.current_piece = None
                self.current_shape = None
                return False
            return True
        except Exception as e:
            print("Erro ao gerar peça:", e)
            return False

    def draw_block(self, surface, x, y, color, size=BLOCK_SIZE, is_current=False):
        rect = pygame.Rect(x, y, size, size)
        
        if color in COLORS and color != '':
            base_color = COLORS[color]
            highlight = (
                min(255, base_color[0] + 40),
                min(255, base_color[1] + 40),
                min(255, base_color[2] + 40))
            shadow = (
                max(0, base_color[0] - 40),
                max(0, base_color[1] - 40),
                max(0, base_color[2] - 40))

            # Centro mais claro
            pygame.draw.rect(surface, highlight, rect)

            # Efeito de gradiente simples
            for i in range(3):
                border_rect = pygame.Rect(x+i, y+i, size-2*i, size-2*i)
                color_component = (
                    base_color[0] + (highlight[0]-base_color[0])*i//3,
                    base_color[1] + (highlight[1]-base_color[1])*i//3,
                    base_color[2] + (highlight[2]-base_color[2])*i//3
                )
                pygame.draw.rect(surface, color_component, border_rect)

            # Borda
            pygame.draw.rect(surface, COLORS['white'], rect, 2)

            # Efeito 3D para peça atual
            if is_current:
                pygame.draw.line(surface, (255, 255, 255, 150),
                                 (x+1, y+1), (x+size-2, y+1), 2)
                pygame.draw.line(surface, (255, 255, 255, 150),
                                 (x+1, y+1), (x+1, y+size-2), 2)
        else:
            pygame.draw.rect(surface, COLORS[''], rect)

    def get_ghost_y(self):
        if self.current_piece is None:
            return 0

        ghost_y = self.piece_y
        while self.valid_position(self.piece_x, ghost_y + 1, self.current_piece):
            ghost_y += 1
        return ghost_y

    def valid_position(self, x, y, shape):
        if shape is None:
            return False

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
        if not self.running or self.paused or self.current_piece is None:
            return False

        new_x = self.piece_x + dx
        new_y = self.piece_y + dy
        if self.valid_position(new_x, new_y, self.current_piece):
            self.piece_x = new_x
            self.piece_y = new_y
            if dx != 0 or dy != 0:
                self.play_sound(self.sound_move)
            return True
        return False

    def rotate(self):
        if not self.running or self.paused:
            return
        rotated = list(zip(*self.current_piece[::-1]))
        rotated = [list(row) for row in rotated]
        if self.valid_position(self.piece_x, self.piece_y, rotated):
            self.current_piece = rotated
            self.rotate_angle = 15 * self.rotate_direction
            self.rotate_direction *= -1
            self.play_sound(self.sound_rotate)

    def hold_current_piece(self):
        if self.hold_used:
            return

        self.play_sound(self.sound_hold)
        if self.hold_piece is None:
            self.hold_piece = self.current_shape
            self.spawn_piece()
        else:
            self.hold_piece, self.current_shape = self.current_shape, self.hold_piece
            self.current_piece = [row[:] for row in SHAPES[self.current_shape]]
            self.piece_x = BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
            self.piece_y = 0
        self.hold_used = True

    def freeze_piece(self):
        if self.current_piece is None:
            return

        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.piece_y + i][self.piece_x + j] = self.current_shape
        self.play_sound(self.sound_encaixe)

    def clear_lines(self):
        lines_cleared = []
        new_board = []

        # Identifica linhas completas
        for i, row in enumerate(self.board):
            if all(cell != '' for cell in row):
                lines_cleared.append(i)
            else:
                new_board.append(row)

        # Cria partículas ANTES de modificar o tabuleiro
        if lines_cleared:
            for y in lines_cleared:
                for x in range(BOARD_WIDTH):
                    if self.board[y][x]:
                        color = COLORS.get(self.board[y][x], (random.randint(
                            100, 255), random.randint(100, 255), random.randint(100, 255)))
                        for _ in range(5):  # Aumentado de 3 para 5 partículas por bloco
                            px = SIDEBAR_WIDTH + x * BLOCK_SIZE + BLOCK_SIZE//2
                            py = PANEL_HEIGHT + y * BLOCK_SIZE + BLOCK_SIZE//2
                            self.particles.append(Particle(px, py, color))

            self.clear_effect = lines_cleared
            self.clear_effect_time = time.time()
            self.lines_cleared += len(lines_cleared)
            self.update_level()

            # Adiciona linhas vazias no topo para substituir as linhas limpas
            lines_to_add = len(lines_cleared)
            for _ in range(lines_to_add):
                new_board.insert(0, ['' for _ in range(BOARD_WIDTH)])

            # Atualiza o tabuleiro com as novas linhas
            self.board = new_board

            # Sistema de pontuação
            if len(lines_cleared) == 1:
                self.score += 100 * self.level
            elif len(lines_cleared) == 2:
                self.score += 300 * self.level
            elif len(lines_cleared) == 3:
                self.score += 500 * self.level
            elif len(lines_cleared) == 4:
                self.score += 800 * self.level

            self.play_sound(self.sound_linha)

    def update_level(self):
        self.level = 1 + self.lines_cleared // 10

    def gravity_thread(self):
        while True:
            if not self.running:
                time.sleep(0.1)
                continue

            if self.paused:
                time.sleep(0.1)
                continue

            with self.lock:
                gravity_delay = max(0.05, 0.8 - (self.level * 0.07))
                time.sleep(gravity_delay)

                # Verifica novamente se o jogo não foi pausado nesse intervalo
                if self.paused or not self.running:
                    continue

                if not self.move(0, 1):
                    self.freeze_piece()
                    self.clear_lines()
                    self.spawn_piece()

    def draw_piece_preview(self, shape, x, y, scale=1.0):
        if shape not in SHAPES:
            return

        piece = SHAPES[shape]
        block_size = int(BLOCK_SIZE * scale * 0.8)

        for i, row in enumerate(piece):
            for j, cell in enumerate(row):
                if cell:
                    block_x = x + j * block_size
                    block_y = y + i * block_size
                    self.draw_block(self.game_surface, block_x, block_y, shape, block_size)

    def draw_sidebar(self):
        # Fundo da sidebar
        sidebar_rect = pygame.Rect(
            0, PANEL_HEIGHT, SIDEBAR_WIDTH, BOARD_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(self.game_surface, COLORS['panel'], sidebar_rect)
        pygame.draw.rect(self.game_surface, COLORS['violeta'], sidebar_rect, 3)

        # Hold piece
        hold_text = LARGE_FONT.render("GUARDAR", True, COLORS['white'])
        self.game_surface.blit(
            hold_text, (SIDEBAR_WIDTH//2 - hold_text.get_width()//2, PANEL_HEIGHT + 10))

        if self.hold_piece:
            # Centraliza a peça hold
            hold_piece_width = len(SHAPES[self.hold_piece][0])
            hold_x = SIDEBAR_WIDTH//2 - (hold_piece_width * BLOCK_SIZE)//2
            self.draw_piece_preview(self.hold_piece, hold_x, PANEL_HEIGHT + 50)

        # Next pieces
        next_text = LARGE_FONT.render("NEXT", True, COLORS['white'])
        self.game_surface.blit(next_text, (GAME_WIDTH - SIDEBAR_WIDTH //
                               2 - next_text.get_width()//2, PANEL_HEIGHT + 10))

        # Garante que temos pelo menos 3 próximas peças para mostrar
        next_pieces_to_show = self.next_pieces[:3]
        for i, piece in enumerate(next_pieces_to_show):
            # Centraliza cada peça next
            piece_width = len(SHAPES[piece][0])
            next_x = GAME_WIDTH - SIDEBAR_WIDTH//2 - \
                (piece_width * BLOCK_SIZE)//2
            self.draw_piece_preview(piece, next_x, PANEL_HEIGHT + 50 + i * 100)

    def draw_panel(self):
        # Painel superior com gradiente
        panel_rect = pygame.Rect(0, 0, GAME_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.game_surface, COLORS['panel'], panel_rect)

        # Gradiente
        for i in range(PANEL_HEIGHT):
            alpha = 255 * (1 - i/PANEL_HEIGHT)
            line_rect = pygame.Rect(0, i, GAME_WIDTH, 1)
            pygame.draw.rect(self.game_surface,
                             (138, 43, 226, alpha), line_rect)

        # Bordas
        pygame.draw.rect(self.game_surface, COLORS['violeta'], panel_rect, 3)
        pygame.draw.line(self.game_surface, (200, 200, 200),
                         (0, PANEL_HEIGHT-1), (GAME_WIDTH, PANEL_HEIGHT-1), 2)

        # Informações
        time_text = FONT.render(
            f"Tempo: {self.elapsed_time//60:02d}:{self.elapsed_time % 60:02d}", True, COLORS['white'])
        score_text = FONT.render(
            f"Pontos: {self.score}", True, COLORS['white'])
        level_text = FONT.render(f"Nível: {self.level}", True, COLORS['white'])
        lines_text = FONT.render(
            f"Linhas: {self.lines_cleared}", True, COLORS['white'])

        # Barra de progresso do nível
        level_progress = self.lines_cleared % 10
        pygame.draw.rect(self.game_surface, (80, 80, 100),
                         (10, PANEL_HEIGHT-15, 100, 8))
        pygame.draw.rect(
            self.game_surface, COLORS['I'], (10, PANEL_HEIGHT-15, level_progress * 10, 8))

        self.game_surface.blit(time_text, (10, 10))
        self.game_surface.blit(score_text, (10, 30))
        self.game_surface.blit(
            level_text, (GAME_WIDTH//2 - level_text.get_width()//2, 10))
        self.game_surface.blit(
            lines_text, (GAME_WIDTH - lines_text.get_width() - 10, 10))

    def draw_board(self):
        if self.running:
            self.elapsed_time = int(
                time.time() - self.start_time - self.total_pause_duration)
        elif self.game_over_time is not None:
            self.elapsed_time = int(
                self.game_over_time - self.start_time - self.total_pause_duration)

        # Fundo do jogo
        self.game_surface.fill(COLORS[''])

        # Desenha os painéis
        self.draw_panel()
        self.draw_sidebar()

        # Área do tabuleiro principal
        board_rect = pygame.Rect(
            SIDEBAR_WIDTH, PANEL_HEIGHT, 
            BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE
        )
        pygame.draw.rect(self.game_surface, COLORS[''], board_rect)
        pygame.draw.rect(self.game_surface, COLORS['violeta'], board_rect, 3)

        # Efeito de linha limpa
        if self.clear_effect and time.time() - self.clear_effect_time < 0.5:
            for y in self.clear_effect:
                highlight_surf = pygame.Surface(
                    (BOARD_WIDTH * BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                highlight_surf.fill(COLORS['highlight'])
                self.game_surface.blit(
                    highlight_surf, (SIDEBAR_WIDTH, PANEL_HEIGHT + y * BLOCK_SIZE))
        else:
            self.clear_effect = None

        # Tabuleiro e peças fixas
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    block_x = SIDEBAR_WIDTH + x * BLOCK_SIZE
                    block_y = PANEL_HEIGHT + y * BLOCK_SIZE
                    self.draw_block(self.game_surface, block_x, block_y, self.board[y][x])

        # Grade do tabuleiro
        grid_surface = pygame.Surface(
            (BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
        grid_color = (200, 200, 200, 50)

        for y in range(BOARD_HEIGHT + 1):
            pygame.draw.line(grid_surface, grid_color,
                             (0, y * BLOCK_SIZE + 0.5),
                             (BOARD_WIDTH * BLOCK_SIZE, y * BLOCK_SIZE + 0.5), 1)

        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(grid_surface, grid_color,
                             (x * BLOCK_SIZE + 0.5, 0),
                             (x * BLOCK_SIZE + 0.5, BOARD_HEIGHT * BLOCK_SIZE), 1)

        self.game_surface.blit(grid_surface, (SIDEBAR_WIDTH, PANEL_HEIGHT))

        # Sombra da peça
        if self.current_piece is not None:
            ghost_y = self.get_ghost_y()
            for i, row in enumerate(self.current_piece):
                for j, cell in enumerate(row):
                    if cell:
                        x = SIDEBAR_WIDTH + (self.piece_x + j) * BLOCK_SIZE
                        y = PANEL_HEIGHT + (ghost_y + i) * BLOCK_SIZE

                        ghost_surf = pygame.Surface(
                            (BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                        ghost_surf.fill(COLORS['ghost'])
                        self.game_surface.blit(ghost_surf, (x, y))

        # Peça atual com rotação
        if self.current_piece is not None:
            for i, row in enumerate(self.current_piece):
                for j, cell in enumerate(row):
                    if cell:
                        x = SIDEBAR_WIDTH + (self.piece_x + j) * BLOCK_SIZE
                        y = PANEL_HEIGHT + (self.piece_y + i) * BLOCK_SIZE

                        # Animação de rotação
                        if abs(self.rotate_angle) > 0:
                            rotated_block = pygame.Surface(
                                (BLOCK_SIZE+10, BLOCK_SIZE+10), pygame.SRCALPHA)
                            block_rect = pygame.Rect(
                                5, 5, BLOCK_SIZE, BLOCK_SIZE)
                            self.draw_block(rotated_block, 5, 5,
                                            self.current_shape, BLOCK_SIZE, True)

                            # Aplica rotação
                            rotated_block = pygame.transform.rotate(
                                rotated_block, self.rotate_angle)
                            self.rotate_angle *= 0.9  # Suaviza a rotação

                            # Centraliza após rotação
                            block_rect = rotated_block.get_rect(
                                center=(x + BLOCK_SIZE//2, y + BLOCK_SIZE//2))
                            self.game_surface.blit(rotated_block, block_rect)
                        else:
                            self.draw_block(
                                self.game_surface, x, y, self.current_shape, BLOCK_SIZE, True)

        # Partículas
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            surf = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color, p.alpha),
                               (p.size, p.size), p.size)
            self.game_surface.blit(
                surf, (int(p.x - p.size), int(p.y - p.size)))

        # Rodapé com controles
        footer_rect = pygame.Rect(
            0, PANEL_HEIGHT + BOARD_HEIGHT * BLOCK_SIZE, GAME_WIDTH, FOOTER_HEIGHT)
        pygame.draw.rect(self.game_surface, COLORS['panel'], footer_rect)
        pygame.draw.rect(self.game_surface, COLORS['violeta'], footer_rect, 3)

        # Ícones e textos de controles
        controls = [
            ("← →", "Mover"),
            ("↑", "Girar"),
            ("↓", "Cair"),
            ("Space", "Drop"),
            ("C", "Guardar"),
            ("P", "Pausa"),
            ("M", "Mudo"),
            ("N", "Próxima Música"),
            ("ESC", "Sair")
        ]

        icon_font = pygame.font.SysFont('Arial', 24, bold=True)
        text_font = pygame.font.SysFont('Arial', 16)

        start_x = 20
        for icon, text in controls:
            icon_surf = icon_font.render(icon, True, COLORS['white'])
            text_surf = text_font.render(text, True, COLORS['white'])

            y_pos = PANEL_HEIGHT + BOARD_HEIGHT * BLOCK_SIZE + 20
            self.game_surface.blit(icon_surf, (start_x, y_pos))
            self.game_surface.blit(
                text_surf, (start_x + (icon_surf.get_width() - text_surf.get_width())//2, y_pos + 30))

            start_x += 100

        # Mensagem de pausa
        if self.paused:
            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.game_surface.blit(overlay, (0, 0))

            pause_text = TITLE_FONT.render("PAUSADO", True, COLORS['white'])
            resume_text = FONT.render(
                "Pressione P para continuar", True, COLORS['white'])

            self.game_surface.blit(
                pause_text, (GAME_WIDTH//2 - pause_text.get_width()//2, GAME_HEIGHT//2 - 50))
            self.game_surface.blit(
                resume_text, (GAME_WIDTH//2 - resume_text.get_width()//2, GAME_HEIGHT//2 + 10))

        # Mensagem de game over
        if not self.running and self.game_over_time is not None:
            overlay = pygame.Surface(
                (GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.game_surface.blit(overlay, (0, 0))

            game_over_text = TITLE_FONT.render(
                "GAME OVER", True, (255, 80, 80))
            score_text = LARGE_FONT.render(
                f"Pontuação: {self.score}", True, COLORS['white'])
            lines_text = LARGE_FONT.render(
                f"Linhas: {self.lines_cleared}", True, COLORS['white'])
            restart_text = FONT.render(
                "Pressione R para reiniciar", True, COLORS['white'])

            self.game_surface.blit(
                game_over_text, (GAME_WIDTH//2 - game_over_text.get_width()//2, GAME_HEIGHT//2 - 80))
            self.game_surface.blit(
                score_text, (GAME_WIDTH//2 - score_text.get_width()//2, GAME_HEIGHT//2 - 20))
            self.game_surface.blit(
                lines_text, (GAME_WIDTH//2 - lines_text.get_width()//2, GAME_HEIGHT//2 + 20))
            self.game_surface.blit(
                restart_text, (GAME_WIDTH//2 - restart_text.get_width()//2, GAME_HEIGHT//2 + 80))

    
    def run(self):
        try:
            clock = pygame.time.Clock()
            running = True

            # Inicia a música do menu
            if self.sound_available and self.menu_music:
                pygame.mixer.music.load(self.menu_music)
                pygame.mixer.music.set_volume(self.menu_music_volume)
                pygame.mixer.music.play(-1)

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if self.game_state == "menu":
                        action = self.menu.handle_event(event)
                        if action == "start":
                            pygame.mixer.music.fadeout(500)
                            while pygame.mixer.music.get_busy():
                                pygame.time.wait(100)

                            self.game_state = "game"
                            self.__init_game()

                            pygame.mixer.music.load(self.playlist[self.current_song_index])
                            pygame.mixer.music.set_volume(self.game_music_volume)
                            pygame.mixer.music.play(-1)

                        elif action == "quit":
                            running = False

                    elif self.game_state == "game":
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.running = False
                                self.paused = False
                                self.current_piece = None
                                self.board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
                                self.menu = Menu(self.screen_width, self.screen_height, self)
                                self.game_state = "menu"
                                pygame.mixer.music.fadeout(300)
                                while pygame.mixer.music.get_busy():
                                    pygame.time.wait(100)
                                if self.sound_available and self.menu_music:
                                    pygame.mixer.music.load(self.menu_music)
                                    pygame.mixer.music.set_volume(self.menu_music_volume)
                                    pygame.mixer.music.play(-1)
                            elif event.key == pygame.K_p:
                                self.toggle_pause()
                            elif event.key == pygame.K_m:
                                self.toggle_music()
                            elif event.key == pygame.K_r and not self.running:
                                self.__init_game()
                            elif event.key == pygame.K_n:
                                self.skip_song = True
                            elif self.running and not self.paused:
                                if event.key == pygame.K_LEFT:
                                    self.move(-1, 0)
                                elif event.key == pygame.K_RIGHT:
                                    self.move(1, 0)
                                elif event.key == pygame.K_DOWN:
                                    self.move(0, 1)
                                elif event.key == pygame.K_UP:
                                    self.rotate()
                                elif event.key == pygame.K_SPACE:
                                    self.hard_drop()
                                elif event.key == pygame.K_c:
                                    self.hold_current_piece()

                if self.game_state == "menu":
                    self.menu.update()
                elif self.game_state == "game":
                    if self.running and not self.paused:
                        self.elapsed_time = int(time.time() - self.start_time - self.total_pause_duration)
                    elif self.game_over_time is not None:
                        self.elapsed_time = int(self.game_over_time - self.start_time - self.total_pause_duration)

                self.screen.fill(COLORS[''])
                if self.game_state == "menu":
                    self.menu.draw(self.screen)
                elif self.game_state == "game":
                    x_offset = (self.screen_width - GAME_WIDTH) // 2
                    y_offset = (self.screen_height - GAME_HEIGHT) // 2
                    self.draw_board()
                    self.screen.blit(self.game_surface, (x_offset, y_offset))

                pygame.display.flip()
                clock.tick(60)

        except Exception as e:
            print('Erro inesperado:', e)
            pygame.quit()
            sys.exit()
        finally:
            pygame.quit()


    def __init_game(self):
            # Reinicializa todas as variáveis do jogo
            self.board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
            self.current_shape = None
            self.current_piece = None
            self.piece_x = 0
            self.piece_y = 0
            self.running = True
            self.paused = False
            self.score = 0
            self.level = 1
            self.lines_cleared = 0
            self.hold_piece = None
            self.hold_used = False
            self.next_pieces = [random.choice(list(SHAPES.keys())) for _ in range(3)]
            self.game_over_time = None

            # Reinicia efeitos visuais
            self.clear_effect = None
            self.clear_effect_time = 0
            self.rotate_angle = 0
            self.rotate_direction = 1

            # Reinicia tempo
            self.start_time = time.time()
            self.elapsed_time = 0
            self.total_pause_duration = 0

            # Limpa partículas
            self.particles = []

            # Inicia novo jogo
            self.spawn_piece()
            self.game_state = "game"
            self.running = True

    def toggle_pause(self):
            self.paused = not self.paused
            if self.paused:
                self.pause_start_time = time.time()
                self.music_paused = True
                pygame.mixer.music.pause()
            else:
                if self.pause_start_time:
                    self.total_pause_duration += time.time() - self.pause_start_time
                    self.pause_start_time = None
                self.music_paused = False
                pygame.mixer.music.unpause()

    def toggle_music(self):
            self.music_paused = not self.music_paused
            if self.music_paused:
                pygame.mixer.music.pause()
            else:
                if not self.paused:
                    pygame.mixer.music.unpause()

    def hard_drop(self):
            if not self.running or self.paused:
                return
            ghost_y = self.get_ghost_y()
            self.piece_y = ghost_y
            self.freeze_piece()
            self.clear_lines()
            self.spawn_piece()

    def music_thread(self):
            while True:
                try:
                    if self.game_state == "menu":
                        time.sleep(1)
                        continue

                    if not hasattr(self, 'playlist') or not self.playlist:
                        time.sleep(1)
                        continue

                    pygame.mixer.music.set_volume(self.game_music_volume)
                    pygame.mixer.music.load(self.playlist[self.current_song_index])
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Erro ao tocar música: {e}")
                    time.sleep(2)
                    continue

                while True:
                    if self.skip_song:
                        pygame.mixer.music.stop()
                        self.skip_song = False
                        break
                    if not pygame.mixer.music.get_busy() and not self.music_paused:
                        break
                    time.sleep(0.1)

                if hasattr(self, 'playlist') and self.playlist:
                    self.current_song_index = (self.current_song_index + 1) % len(self.playlist)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
()


if __name__ == '__main__':
    game = TetrisGame()
    game.run()
