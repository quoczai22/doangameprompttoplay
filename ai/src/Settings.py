import pathlib
import os

# --- 1. ĐƯỜNG DẪN TÀI NGUYÊN (QUAN TRỌNG NHẤT) ---
FILE_PATH = pathlib.Path(__file__).parent.absolute()
ROOT_DIR = FILE_PATH.parent
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

# --- 2. CẤU HÌNH MÀN HÌNH (SPLIT SCREEN) ---
GAME_WIDTH = 1000
GAME_HEIGHT = 600
SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT
SCREEN_TITLE = "Thử thách phiêu lưu (mario)"

# --- 3. TỶ LỆ SCALE ---
TILE_SCALING = 1.5
CHARACTER_SCALING = 1.7

# --- 4. VẬT LÝ & TỐC ĐỘ ---
GRAVITY = 1.0
PLAYER_JUMP_SPEED = 17
PLAYER_WALK_SPEED =3
PLAYER_RUN_SPEED = 7
# True: Hill Climbing vẫn là chính, A*/Dijkstra hỗ trợ khi bot bị kẹt/chặn đường.
ENABLE_PATHFINDING_SUPPORT = True
ENABLE_BOT_PLATFORM_DROP_TEST = True
BOT_MAX_SAFE_DROP_TILES = 8

# --- 5. MÀU SẮC ---
BACKGROUND_COLOR = (59, 122, 87) # Mã RGB thay vì dùng arcade.color
UI_TITLE_COLOR = (255, 214, 72)
UI_MAIN_TEXT_COLOR = (245, 248, 230)
UI_SECONDARY_TEXT_COLOR = (190, 230, 220)
UI_MUTED_TEXT_COLOR = (210, 220, 215)
UI_SELECTED_COLOR = (255, 96, 64)
UI_SHADOW_COLOR = (35, 25, 35)
UI_PANEL_COLOR = (28, 32, 42)
UI_PANEL_SELECTED_COLOR = (45, 50, 65)
