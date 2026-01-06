import pygame
import sys
import random
import os
import time
import math

pygame.init()

# Advanced audio setup with larger buffer for smoother playback and reduced crackling
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.mixer.init()

# ==========================
# EXTENSIVE CONSTANTS & GAME SETTINGS - DETAILED AND EXPANDED FOR CLARITY AND FLEXIBILITY
# ==========================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
MAP_WIDTH = 20
MAP_HEIGHT = 15

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slice City - Extreme Night Shift Rush!")
clock = pygame.time.Clock()

# Comprehensive color palette for all visual elements, effects, and states
RED = (255, 0, 0)
PIZZA_ORANGE = (255, 100, 0)
CHEESE_YELLOW = (255, 220, 100)
NEON_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (60, 60, 80)
GRAY = (90, 90, 110)
LIGHT_GRAY = (140, 140, 160)
WINDOW_BLUE = (100, 150, 255)
WINDOW_YELLOW = (255, 255, 150)
DARK_BLUE = (10, 10, 40)
BROWN = (80, 50, 20)
BUTTON_COLOR = (100, 40, 20)
BUTTON_HOVER = (140, 60, 30)
BUTTON_TEXT_COLOR = WHITE
HEALTH_BAR_BG = (50, 50, 50)
HEALTH_BAR_BORDER = (200, 200, 200)
FLASH_RED = (255, 100, 100)
SHAKE_COLOR_OVERLAY = (255, 0, 0, 30)
DELIVERY_FLASH = (0, 255, 0, 40)
VICTORY_GOLD = (255, 215, 0)
DEATH_RED = (139, 0, 0)
TIME_BOOST_COLOR = (0, 200, 255)
TIME_BOOST_GLOW = (100, 255, 255)
TITLE_SHADOW = (0, 0, 0)
TITLE_GLOW = (255, 150, 0)
INTRO_BG_OVERLAY = (0, 0, 50, 180)

# Extensive font collection for varied text presentation across all screens
title_font = pygame.font.Font(None, 68)
huge_font = pygame.font.Font(None, 64)
big_font = pygame.font.Font(None, 46)
medium_font = pygame.font.Font(None, 38)
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 26)
tiny_font = pygame.font.Font(None, 20)
micro_font = pygame.font.Font(None, 16)

# ==========================
# ASSET LOADING WITH ROBUST ERROR HANDLING AND FALLBACKS
# ==========================
def load_image(path, scale=None):
    full_path = os.path.join("assets", path)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except pygame.error as e:
            print(f"[ERROR] Failed to load image {full_path}: {e}")
    print(f"[WARNING] Image not found: {full_path} - using procedural fallback")
    return None

def load_sound(path, volume=0.7):
    full_path = os.path.join("assets", path)
    if os.path.exists(full_path):
        try:
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(volume)
            return sound
        except pygame.error as e:
            print(f"[ERROR] Failed to load sound {full_path}: {e}")
    print(f"[WARNING] Sound not found: {full_path} - action will be silent")
    return None

def load_music(path):
    full_path = os.path.join("assets", path)
    if os.path.exists(full_path):
        try:
            pygame.mixer.music.load(full_path)
            return True
        except pygame.error as e:
            print(f"[ERROR] Failed to load music {full_path}: {e}")
    print(f"[WARNING] Music not found: {full_path}")
    return False

# Load visual assets
background = load_image("nyc_background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = load_image("chef.png", (TILE_SIZE + 8, TILE_SIZE + 20))
pizza_img = load_image("pizza_slice.png", (80, 80))
pizzeria_img = load_image("pizzeria.png", (TILE_SIZE*3, TILE_SIZE*3))
shop_img = load_image("shop.png", (TILE_SIZE*2, TILE_SIZE*2))
time_boost_img = load_image("time_boost.png", (TILE_SIZE, TILE_SIZE))

enemy_images = {
    "Street Thug": load_image("thug.png", (180, 180)),
    "Rival Driver": load_image("delivery_guy.png", (180, 180)),
    "Gang Enforcer": load_image("gangster.png", (180, 180)),
    "Rat King": load_image("rat_king.png", (220, 220)),
}

# Sound effects (MP3)
throw_sound = load_sound("throw.mp3", 0.7)
hit_sound = load_sound("hit.mp3", 0.8)
deliver_sound = load_sound("deliver.mp3", 0.9)
buy_sound = load_sound("buy.mp3", 0.6)
run_sound = load_sound("run.mp3", 0.7)
damage_sound = load_sound("damage.mp3", 0.8)
time_boost_sound = load_sound("time_boost.mp3", 0.8)

# Music files
main_music_path = os.path.join("assets", "italian_music.mp3")
victory_music_path = os.path.join("assets", "victory.mp3")
loss_music_path = os.path.join("assets", "times_up.mp3")

main_music_loaded = os.path.exists(main_music_path)
victory_music_loaded = os.path.exists(victory_music_path)
loss_music_loaded = os.path.exists(loss_music_path)

# Start with main music
if main_music_loaded:
    pygame.mixer.music.load(main_music_path)
    pygame.mixer.music.set_volume(0.45)
    pygame.mixer.music.play(-1)

# ==========================
# TIME BOOSTERS ON MAP - 2 pickups for +3 seconds each
# ==========================
time_booster_positions = [(4, 8), (14, 6)]
time_boosters_active = [True, True]

def draw_time_booster(x, y):
    tx = x * TILE_SIZE
    ty = y * TILE_SIZE
    if time_boost_img:
        screen.blit(time_boost_img, (tx, ty))
    else:
        pygame.draw.circle(screen, TIME_BOOST_COLOR, (tx + 20, ty + 20), 18)
        pygame.draw.circle(screen, TIME_BOOST_GLOW, (tx + 20, ty + 20), 25, 5)
        clock_text = small_font.render("+3s", True, WHITE)
        screen.blit(clock_text, (tx + 8, ty + 12))

# ==========================
# CUSTOMER DELIVERY TRACKING
# ==========================
pizzeria_pos = (7, 10)
customer_positions = [(3,5), (12,13), (5,12), (15,8), (10,3)]
important_tiles = [pizzeria_pos] + customer_positions

delivered_customers = set()

# ==========================
# GAME MAP GENERATION
# ==========================
game_map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        if (x, y) in important_tiles or (x, y) in time_booster_positions:
            continue
        if random.random() < 0.45:
            game_map[y][x] = 1

game_map[pizzeria_pos[1]][pizzeria_pos[0]] = 2
for cx, cy in customer_positions:
    game_map[cy][cx] = 3

# ==========================
# PLAYER CLASS
# ==========================
class Player:
    def __init__(self):
        self.x = pizzeria_pos[0] * TILE_SIZE
        self.y = pizzeria_pos[1] * TILE_SIZE
        self.health = 120
        self.max_health = 120
        self.pepperonis = 0

player = Player()

# ==========================
# ENEMIES - Stronger
# ==========================
enemy_templates = {
    "Thug": {"name": "Street Thug", "health": 96, "attack": 16, "pepperonis": 10},
    "Driver": {"name": "Rival Driver", "health": 120, "attack": 21, "pepperonis": 18},
    "Gangster": {"name": "Gang Enforcer", "health": 192, "attack": 32, "pepperonis": 40},
    "Rat King": {"name": "Rat King", "health": 264, "attack": 40, "pepperonis": 90},
}

ENEMY_ENCOUNTER_CHANCE = 0.12

# Enemy cooldown system - player must move at least 3 tiles before next encounter
last_encounter_tile = None
moves_since_encounter = 0

# ==========================
# GAME STATE MANAGER
# ==========================
class GameState:
    def __init__(self):
        self.state = "intro"
        self.previous_state = None
        self.current_enemy = None
        self.pizza_projectiles = []
        self.screen_shake = 0
        self.combat_message = ""
        self.combat_message_timer = 0
        self.shop_message = ""
        self.shop_message_timer = 0
        self.deliveries_made = 0
        self.extra_time_bought = 0
        self.game_start_time = None

    def reset(self):
        global delivered_customers, time_boosters_active, last_encounter_tile, moves_since_encounter
        self.__init__()
        delivered_customers = set()
        time_boosters_active = [True, True]
        last_encounter_tile = None
        moves_since_encounter = 0
        player.x = pizzeria_pos[0] * TILE_SIZE
        player.y = pizzeria_pos[1] * TILE_SIZE
        player.health = 120
        player.pepperonis = 0
        if main_music_loaded:
            pygame.mixer.music.load(main_music_path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)

game_state = GameState()

deliveries_needed = 5
base_time_limit = 20
health_replenish_cost = 20

# ==========================
# SHOP BUTTON - Larger
# ==========================
shop_button_rect = pygame.Rect(SCREEN_WIDTH - 180, 10, 170, 60)
shop_button_hover = False

def draw_shop_button():
    global shop_button_hover
    mouse_pos = pygame.mouse.get_pos()
    shop_button_hover = shop_button_rect.collidepoint(mouse_pos)

    color = BUTTON_HOVER if shop_button_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, shop_button_rect, border_radius=20)
    pygame.draw.rect(screen, WHITE, shop_button_rect, 5, border_radius=20)

    text = small_font.render("SHOP (.)", True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=shop_button_rect.center)
    screen.blit(text, text_rect)

# ==========================
# HUD WITH DETAILED ELEMENTS
# ==========================
def draw_hud():
    if game_state.game_start_time is None:
        return

    elapsed = time.time() - game_state.game_start_time
    remaining = max(0, base_time_limit + game_state.extra_time_bought - elapsed)
    mins = int(remaining // 60)
    secs = int(remaining % 60)
    time_color = RED if remaining < 8 else NEON_YELLOW if remaining < 12 else WHITE

    # Timer
    pygame.draw.circle(screen, WHITE, (35, 35), 20, 4)
    time_text = font.render(f"{mins:02}:{secs:02}", True, time_color)
    screen.blit(time_text, (70, 20))

    # Pepperoni count
    pygame.draw.circle(screen, RED, (35, 90), 18)
    for i in range(8):
        angle = i * 45
        px = 35 + int(12 * math.cos(math.radians(angle)))
        py = 90 + int(12 * math.sin(math.radians(angle)))
        pygame.draw.circle(screen, PIZZA_ORANGE, (px, py), 5)
    pep_text = font.render(f" {player.pepperonis}", True, PIZZA_ORANGE)
    screen.blit(pep_text, (70, 80))

    # Delivery progress
    del_text = font.render(f"Deliveries: {game_state.deliveries_made}/{deliveries_needed}", True, CHEESE_YELLOW)
    screen.blit(del_text, (SCREEN_WIDTH - del_text.get_width() - 200, 20))

    # Shop button
    if game_state.state in ("overworld", "combat"):
        draw_shop_button()

    if game_state.state == "overworld":
        guide = tiny_font.render("Reach each customer once → Deliver | Press . to open SHOP anytime", True, WHITE)
        screen.blit(guide, (SCREEN_WIDTH//2 - guide.get_width()//2, SCREEN_HEIGHT - 35))

# ==========================
# DRAW FUNCTIONS - DETAILED AND POLISHED WITH IMPROVED TITLE SCREEN
# ==========================
def draw_intro():
    screen.fill(DARK_BLUE)
    if background:
        dark = background.copy()
        dark.set_alpha(70)
        screen.blit(dark, (0, 0))

    # Dark overlay for depth
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(120)
    overlay.fill(INTRO_BG_OVERLAY)
    screen.blit(overlay, (0, 0))

    # Glowing title with multiple layers
    title = title_font.render("SLICE CITY", True, PIZZA_ORANGE)
    title_glow = title_font.render("SLICE CITY", True, TITLE_GLOW)
    title_shadow = title_font.render("SLICE CITY", True, TITLE_SHADOW)
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    title_y = 80
    screen.blit(title_shadow, (title_x + 5, title_y + 5))
    screen.blit(title_glow, (title_x + 2, title_y + 2))
    screen.blit(title, (title_x, title_y))

    # Subtitle with neon effect
    subtitle = big_font.render("Extreme Night Shift Rush", True, NEON_YELLOW)
    subtitle_shadow = big_font.render("Extreme Night Shift Rush", True, BLACK)
    screen.blit(subtitle_shadow, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2 + 3, title_y + 100 + 3))
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, title_y + 100))

    # Story text with improved spacing and styling - removed "Tough fights = big rewards!"
    story_lines = [
        "Night falls over the city...",
        "The ruthless Pizza Mafia is sabotaging your deliveries",
        "to steal every last customer!",
        "",
        "20 seconds to deliver 5 unique pizzas",
        "to 5 different customers across the city.",
        "",
        "Each customer accepts only one delivery.",
        "Defeat enemies for PEPPERONIS.",
        "Buy health restore in the SHOP.",
        "Collect +3 second boosters on the map (2 available)."
    ]

    y_pos = 220
    line_height = 34

    for line in story_lines:
        if line == "":
            y_pos += line_height // 2
            continue
        text = font.render(line, True, WHITE)
        text_shadow = font.render(line, True, BLACK)
        screen.blit(text_shadow, (SCREEN_WIDTH // 2 - text.get_width() // 2 + 2, y_pos + 2))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += line_height

    # Pulsing "Press SPACE" prompt at the very bottom
    pulse = 127 + int(128 * math.sin(pygame.time.get_ticks() / 300))
    prompt_color = (pulse, pulse, 255)
    prompt = big_font.render("PRESS SPACE TO START", True, prompt_color)
    prompt_shadow = big_font.render("PRESS SPACE TO START", True, BLACK)
    prompt_y = SCREEN_HEIGHT - 80
    screen.blit(prompt_shadow, (SCREEN_WIDTH // 2 - prompt.get_width() // 2 + 3, prompt_y + 3))
    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, prompt_y))

def draw_overworld():
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(DARK_BLUE)

    # Time boosters
    for i, (bx, by) in enumerate(time_booster_positions):
        if time_boosters_active[i]:
            draw_time_booster(bx, by)

    # Buildings
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tx = x * TILE_SIZE
            ty = y * TILE_SIZE
            tile = game_map[y][x]
            if tile == 1:
                pygame.draw.rect(screen, DARK_GRAY, (tx + 6, ty + 6, TILE_SIZE - 12, TILE_SIZE - 12))
                if random.random() < 0.4:
                    color = WINDOW_YELLOW if random.random() < 0.6 else WINDOW_BLUE
                    pygame.draw.rect(screen, color, (tx + 10, ty + 12, 8, 10))
                    pygame.draw.rect(screen, color, (tx + 22, ty + 18, 8, 10))
            elif tile == 2 and pizzeria_img:
                screen.blit(pizzeria_img, (tx - 40, ty - 70))
            elif tile == 3 and shop_img:
                screen.blit(shop_img, (tx - 25, ty - 55))
                if (x, y) in delivered_customers:
                    check = medium_font.render("✓", True, GREEN)
                    screen.blit(check, (tx + 10, ty + 5))

    if player_img:
        screen.blit(player_img, (player.x - 10, player.y - 25))

    draw_hud()

def draw_shop():
    screen.fill(BROWN)
    title = big_font.render("HEALTH REPLENISH SHOP", True, NEON_YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

    item = font.render(f"Full Health Restore — Cost: {health_replenish_cost} pepperonis", True, WHITE)
    screen.blit(item, (SCREEN_WIDTH // 2 - item.get_width() // 2, 200))

    can_buy = player.pepperonis >= health_replenish_cost
    buy_prompt = font.render("Press SPACE to Buy" if can_buy else "Not enough pepperonis!", True, GREEN if can_buy else RED)
    screen.blit(buy_prompt, (SCREEN_WIDTH // 2 - buy_prompt.get_width() // 2, 280))

    exit_text = small_font.render("Press . or ESC to Leave", True, WHITE)
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 400))

    if game_state.shop_message_timer > 0:
        msg = big_font.render(game_state.shop_message, True, GREEN)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 350))
        game_state.shop_message_timer -= 1

    draw_hud()

def draw_combat():
    shake_x = random.randint(-15, 15) if game_state.screen_shake > 0 else 0
    shake_y = random.randint(-15, 15) if game_state.screen_shake > 0 else 0
    if game_state.screen_shake > 0:
        game_state.screen_shake -= 1

    screen.fill(BLACK)
    if background:
        dark = background.copy()
        dark.set_alpha(100)
        screen.blit(dark, (shake_x, shake_y))

    enemy_x = SCREEN_WIDTH - 280 + shake_x
    enemy_y = 180 + shake_y

    img = enemy_images.get(game_state.current_enemy["name"])
    if img:
        enemy_surf = img.copy()
        if game_state.current_enemy.get("flash", 0) > 0:
            enemy_surf.fill(FLASH_RED, special_flags=pygame.BLEND_ADD)
            game_state.current_enemy["flash"] -= 1
        screen.blit(enemy_surf, (enemy_x, enemy_y))

    health_bar_y = enemy_y - 50
    pygame.draw.rect(screen, HEALTH_BAR_BG, (enemy_x - 20, health_bar_y, 220, 30))
    health_ratio = max(game_state.current_enemy["health"] / game_state.current_enemy["max_health"], 0)
    pygame.draw.rect(screen, GREEN, (enemy_x - 20, health_bar_y, int(220 * health_ratio), 30))
    pygame.draw.rect(screen, HEALTH_BAR_BORDER, (enemy_x - 20, health_bar_y, 220, 30), 4)

    name_text = medium_font.render(game_state.current_enemy["name"], True, RED)
    screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, health_bar_y - 40))

    pygame.draw.rect(screen, HEALTH_BAR_BG, (40, 490, 300, 45))
    pygame.draw.rect(screen, GREEN, (40, 490, int(300 * player.health / player.max_health), 45))
    pygame.draw.rect(screen, HEALTH_BAR_BORDER, (40, 490, 300, 45), 4)

    if player_img:
        screen.blit(pygame.transform.scale(player_img, (260, 300)), (40 + shake_x, 220 + shake_y))

    for p in game_state.pizza_projectiles[:]:
        p["pos"][0] += p["vel"]
        if pizza_img:
            rot = pygame.transform.rotate(pizza_img, -p["pos"][0] * 7)
            screen.blit(rot, (p["pos"][0] - 45 + shake_x, p["pos"][1] - 45 + shake_y))

        if p["pos"][0] > 650:
            game_state.pizza_projectiles.remove(p)
            damage = random.randint(30, 50)
            game_state.current_enemy["health"] -= damage
            game_state.current_enemy["flash"] = 18
            game_state.screen_shake = 25
            if hit_sound:
                hit_sound.play()
            game_state.combat_message = f"-{damage}!"
            game_state.combat_message_timer = 90

            if game_state.current_enemy["health"] <= 0:
                reward = game_state.current_enemy["pepperonis"]
                player.pepperonis += reward
                game_state.combat_message = f"Defeated! +{reward} pepperonis!"
                game_state.combat_message_timer = 160
                game_state.state = "overworld"
                game_state.current_enemy = None
                game_state.pizza_projectiles.clear()

    if game_state.combat_message_timer > 0:
        msg = big_font.render(game_state.combat_message, True, NEON_YELLOW)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 160))
        game_state.combat_message_timer -= 1

    instr = medium_font.render("F = Throw Pizza Slice    |    R = Run Away", True, WHITE)
    screen.blit(instr, (40, 560))

    draw_hud()

def draw_victory():
    screen.fill((0, 70, 0))
    win = title_font.render("VICTORY!", True, VICTORY_GOLD)
    screen.blit(win, (SCREEN_WIDTH // 2 - win.get_width() // 2, 120))
    msg = big_font.render("You delivered to all 5 customers in 20 seconds!", True, WHITE)
    screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 220))
    score = big_font.render(f"Final Pepperonis: {player.pepperonis}", True, PIZZA_ORANGE)
    screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, 300))
    restart = font.render("Press R to Rush Again", True, WHITE)
    screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 400))

    # Play victory music - stops main music
    if victory_music_loaded:
        pygame.mixer.music.load(victory_music_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play()

def draw_gameover():
    screen.fill(BLACK)
    over = title_font.render("YOU GOT WHACKED!", True, DEATH_RED)
    screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, 120))
    final = big_font.render(f"Pepperonis Earned: {player.pepperonis}", True, PIZZA_ORANGE)
    screen.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, 240))
    restart = font.render("Press R to Try Again", True, WHITE)
    screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 380))

    # Play loss music - stops main music
    if loss_music_loaded:
        pygame.mixer.music.load(loss_music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

# ==========================
# MAIN GAME LOOP - EXTENSIVE EVENT HANDLING
# ==========================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Global shop access
            if event.key == pygame.K_PERIOD and game_state.state in ("overworld", "combat"):
                game_state.previous_state = game_state.state
                game_state.state = "shop"
                continue

            if game_state.state in ("victory", "gameover"):
                if event.key == pygame.K_r:
                    game_state.reset()
                    continue

            if game_state.state == "intro":
                if event.key == pygame.K_SPACE:
                    game_state.state = "overworld"
                    game_state.game_start_time = time.time()

            elif game_state.state == "overworld":
                old_tile_x = player.x // TILE_SIZE
                old_tile_y = player.y // TILE_SIZE

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.x -= TILE_SIZE
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.x += TILE_SIZE
                elif event.key in (pygame.K_UP, pygame.K_w):
                    player.y -= TILE_SIZE
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    player.y += TILE_SIZE

                player.x = max(0, min(player.x, (MAP_WIDTH - 1) * TILE_SIZE))
                player.y = max(0, min(player.y, (MAP_HEIGHT - 1) * TILE_SIZE))

                tile_x = player.x // TILE_SIZE
                tile_y = player.y // TILE_SIZE
                current_tile = (tile_x, tile_y)

                if (tile_x, tile_y) != (old_tile_x, old_tile_y):
                    moves_since_encounter += 1

                if game_map[tile_y][tile_x] == 3 and current_tile not in delivered_customers:
                    game_state.deliveries_made += 1
                    delivered_customers.add(current_tile)
                    if deliver_sound:
                        deliver_sound.play()
                    if game_state.deliveries_made >= deliveries_needed:
                        game_state.state = "victory"

                # Time booster pickup
                for i, (bx, by) in enumerate(time_booster_positions):
                    if current_tile == (bx, by) and time_boosters_active[i]:
                        game_state.extra_time_bought += 3
                        time_boosters_active[i] = False
                        if time_boost_sound:
                            time_boost_sound.play()
                        game_state.shop_message = "Time Booster Collected +3s!"
                        game_state.shop_message_timer = 120

                if moves_since_encounter >= 3 and random.random() < ENEMY_ENCOUNTER_CHANCE and current_tile not in important_tiles:
                    key = random.choice(list(enemy_templates.keys()))
                    game_state.current_enemy = enemy_templates[key].copy()
                    game_state.current_enemy["max_health"] = game_state.current_enemy["health"]
                    game_state.current_enemy["flash"] = 0
                    game_state.state = "combat"
                    game_state.pizza_projectiles.clear()
                    last_encounter_tile = current_tile
                    moves_since_encounter = 0

            elif game_state.state == "combat":
                if event.key == pygame.K_f:
                    game_state.pizza_projectiles.append({"pos": [80, 340], "vel": 32})
                    if throw_sound:
                        throw_sound.play()
                elif event.key == pygame.K_r:
                    if random.random() < 0.7:
                        if run_sound:
                            run_sound.play()
                        game_state.state = "overworld"
                        game_state.current_enemy = None
                        game_state.pizza_projectiles.clear()
                        moves_since_encounter = 0

            elif game_state.state == "shop":
                if event.key == pygame.K_SPACE and player.pepperonis >= health_replenish_cost:
                    player.pepperonis -= health_replenish_cost
                    player.health = player.max_health
                    game_state.shop_message = "Health Fully Restored!"
                    game_state.shop_message_timer = 120
                    if buy_sound:
                        buy_sound.play()
                elif event.key in (pygame.K_ESCAPE, pygame.K_PERIOD):
                    game_state.state = game_state.previous_state or "overworld"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if shop_button_hover and game_state.state in ("overworld", "combat"):
                game_state.previous_state = game_state.state
                game_state.state = "shop"

    # Timer
    if game_state.game_start_time and game_state.state in ("overworld", "combat", "shop"):
        if time.time() - game_state.game_start_time > base_time_limit + game_state.extra_time_bought:
            game_state.state = "gameover"

    # Enemy attack
    if game_state.state == "combat" and random.random() < 0.035 and not game_state.pizza_projectiles:
        dmg = game_state.current_enemy["attack"]
        player.health -= dmg
        game_state.screen_shake = 30
        game_state.combat_message = f"-{dmg} HP!"
        game_state.combat_message_timer = 90
        if damage_sound:
            damage_sound.play()
        if player.health <= 0:
            game_state.state = "gameover"

    # Draw current state
    if game_state.state == "intro":
        draw_intro()
    elif game_state.state == "overworld":
        draw_overworld()
    elif game_state.state == "combat":
        draw_combat()
    elif game_state.state == "shop":
        draw_shop()
    elif game_state.state == "victory":
        draw_victory()
    elif game_state.state == "gameover":
        draw_gameover()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()