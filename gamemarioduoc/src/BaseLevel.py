import arcade
import random
from Settings import *
from utils import load_game_map
from spiked_ball import SpikedBall
from fruit_item import FruitItem
from ai_algorithms import csp_spawn_positions
from pixel_text import PixelText
from sound_manager import play_effect, stop_all_sounds, stop_menu_music


class BaseLevel(arcade.View):
    def __init__(self):
        super().__init__()

        self.tile_map = None
        self.scene = None
        self.map_width_pixels = 0
        self.player = None
        self.physics_engine = None

        self.camera = None
        self.view_left = 0
        self.fade_alpha = 255
        self.fade_state = "FADE_IN"
        self.fade_speed = 5

        self.start_points = arcade.SpriteList()
        self.checkpoints = arcade.SpriteList()
        self.end_points = arcade.SpriteList()
        self.fruits_list = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.moving_platforms_list = arcade.SpriteList()
        self.saw_moving_list = arcade.SpriteList()
        self.ball_moving_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.enemy_physics_engines = {}
        self.csp_items = []

        self.left_pressed = False
        self.right_pressed = False
        self.shift_pressed = False
        self.respawn_x = 0
        self.respawn_y = 0
        self.is_dying = False
        self.death_timer = 0.0
        self.level_complete = False
        self.respawn_invincible_time = 1.0
        self.is_paused = False
        self.pause_selected_index = 0
        self.pause_options = [
            {"label": "TIẾP TỤC", "action": "resume"},
            {"label": "TRANG CHỦ", "action": "home"},
            {"label": "THOÁT", "action": "exit"},
        ]

    def on_show_view(self):
        stop_menu_music()

    def load_level_setup(self, map_name):
        self.tile_map, self.scene, self.map_width_pixels = load_game_map(map_name)
        if self.tile_map is None:
            return

        self.camera = arcade.camera.Camera2D(
            viewport=arcade.LBWH(left=0, bottom=0, width=GAME_WIDTH, height=GAME_HEIGHT)
        )
        arcade.set_background_color(self.tile_map.background_color or BACKGROUND_COLOR)

    def spawn_items(self):
        ground_tiles = set()
        floating_tiles = set()
        walls = set()
        static_hazards = set()

        tile_w = self.tile_map.tile_width * TILE_SCALING
        tile_h = self.tile_map.tile_height * TILE_SCALING

        if "Ground" in self.tile_map.sprite_lists:
            for sprite in self.tile_map.sprite_lists["Ground"]:
                gx, gy = int(sprite.center_x // tile_w), int(sprite.center_y // tile_h)
                ground_tiles.add((gx, gy))
                walls.add((gx, gy))

        if "Solid Floating Platforms" in self.tile_map.sprite_lists:
            for sprite in self.tile_map.sprite_lists["Solid Floating Platforms"]:
                gx, gy = int(sprite.center_x // tile_w), int(sprite.center_y // tile_h)
                floating_tiles.add((gx, gy))
                walls.add((gx, gy))

        if "Boundary Walls" in self.tile_map.sprite_lists:
            for sprite in self.tile_map.sprite_lists["Boundary Walls"]:
                gx, gy = int(sprite.center_x // tile_w), int(sprite.center_y // tile_h)
                walls.add((gx, gy))

        if "Hazards" in self.tile_map.sprite_lists:
            for sprite in self.tile_map.sprite_lists["Hazards"]:
                hx, hy = int(sprite.center_x // tile_w), int(sprite.center_y // tile_h)
                static_hazards.add((hx, hy))

        invalid_x_zones = set()

        start_gx = int(self.respawn_x // tile_w)
        for i in range(start_gx - 15, start_gx + 16):
            invalid_x_zones.add(i)

        for ep in self.end_points:
            gx = int(ep.center_x // tile_w)
            for i in range(gx - 15, gx + 16):
                invalid_x_zones.add(i)

        def get_valid_spawn_positions(source_tiles):
            valid_pos = []
            for gx, gy in source_tiles:
                if gx in invalid_x_zones:
                    continue
                spawn_pos = (gx, gy + 1)
                if spawn_pos not in walls and spawn_pos not in static_hazards:
                    valid_pos.append(spawn_pos)
            return valid_pos

        candidate_positions = get_valid_spawn_positions(floating_tiles) + get_valid_spawn_positions(ground_tiles)
        candidate_positions = sorted(set(candidate_positions), key=lambda p: (p[0], p[1]))
        target_total = min(len(candidate_positions), random.randint(12, 18))

        final_item_positions = []
        if candidate_positions and target_total > 0:
            csp_result = csp_spawn_positions(
                target_total,
                candidate_positions,
                forbidden_positions=static_hazards,
                min_distance=2,
                trace_limit=0,
                detail_variable_limit=3,
            )
            final_item_positions = csp_result.get("positions", [])

        self.fruits_list.clear()
        for gx, gy in final_item_positions:
            apple = FruitItem(
                gx * tile_w + tile_w / 2,
                gy * tile_h + tile_h / 2,
                fruit_name="Apple.png",
                scale=1.5
            )
            self.fruits_list.append(apple)

        self.scene.add_sprite_list("CSP_Fruits", sprite_list=self.fruits_list)

    def on_update(self, delta_time):
        if self.is_paused:
            if self.player:
                self.player.change_x = 0
            return

        if self.fade_state == "FADE_IN":
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
            if self.fade_alpha == 0:
                self.fade_state = "PLAYING"

        if self.fade_state == "PLAYING" and self.player:
            if self.level_complete:
                self.player.change_x = 0
                self.player.update_animation(delta_time)
                return

            if self.is_dying:
                self.player.change_x = 0
                self.player.update_animation(delta_time)
                self.death_timer += delta_time
                if self.death_timer >= 0.4:
                    self.is_dying = False
                    self.reset_player()
                return

            speed = 4 if not self.shift_pressed else 7
            self.player.change_x = 0

            if self.left_pressed and not self.right_pressed:
                self.player.change_x = -speed
            elif self.right_pressed and not self.left_pressed:
                self.player.change_x = speed

            target_x = max(
                0,
                min(self.player.center_x - GAME_WIDTH / 2, self.map_width_pixels - GAME_WIDTH)
            )
            self.view_left = arcade.math.lerp(self.view_left, target_x, 0.1)

            if self.player.center_y < -100:
                play_effect("die", volume=0.75)
                self.reset_player()
                return

            self.moving_platforms_list.update(delta_time)

            # Saw di chuyển theo trục X và xoay
            for saw in self.saw_moving_list:
                saw.center_x += saw.change_x
                saw.angle += saw.spin_speed

                if saw.center_x >= saw.boundary_right:
                    saw.center_x = saw.boundary_right
                    saw.change_x *= -1
                    saw.spin_speed *= -1
                elif saw.center_x <= saw.boundary_left:
                    saw.center_x = saw.boundary_left
                    saw.change_x *= -1
                    saw.spin_speed *= -1

            # Ball_Moving di chuyển theo trục Y, không xoay
            for ball in self.ball_moving_list:
                ball.center_y += ball.change_y

                if ball.center_y >= ball.boundary_top:
                    ball.center_y = ball.boundary_top
                    ball.change_y *= -1
                elif ball.center_y <= ball.boundary_bottom:
                    ball.center_y = ball.boundary_bottom
                    ball.change_y *= -1

            self.projectiles.update(delta_time)

            if self.physics_engine:
                self.physics_engine.update()

            self.player.update_animation(delta_time)
            self.start_points.update_animation(delta_time)
            self.checkpoints.update_animation(delta_time)
            self.end_points.update_animation(delta_time)
            self.fruits_list.update_animation(delta_time)

            for ball in self.projectiles:
                wall_lists = []
                if "Ground" in self.tile_map.sprite_lists:
                    wall_lists.append(self.tile_map.sprite_lists["Ground"])
                if arcade.check_for_collision_with_lists(ball, wall_lists):
                    ball.remove_from_sprite_lists()

            if self.player.invincible_timer > 0:
                self.player.invincible_timer -= delta_time
                self.player.alpha = 150 if int(self.player.invincible_timer * 10) % 2 == 0 else 255
            else:
                self.player.alpha = 255

            hit_fruits = arcade.check_for_collision_with_list(self.player, self.fruits_list)
            for fruit in hit_fruits:
                fruit.remove_from_sprite_lists()
                play_effect("collectitem", volume=0.72)
                if not self.player.is_big and not self.player.has_grown_big_once:
                    self.player.is_big = True
                    self.player.has_grown_big_once = True
                    old_bottom = self.player.bottom
                    self.player.scale = (
                        self.player.normal_scale[0] * 1.3,
                        self.player.normal_scale[1] * 1.3
                    )
                    self.player.bottom = old_bottom
                else:
                    self.player.spiked_ball_stock += 1

            hazard_hit = False

            if self.player.invincible_timer <= 0:
                if "Hazards" in self.tile_map.sprite_lists:
                    if arcade.check_for_collision_with_list(self.player, self.tile_map.sprite_lists["Hazards"]):
                        hazard_hit = True

                if not hazard_hit and len(self.saw_moving_list) > 0:
                    if arcade.check_for_collision_with_list(self.player, self.saw_moving_list):
                        hazard_hit = True

                if not hazard_hit and len(self.ball_moving_list) > 0:
                    if arcade.check_for_collision_with_list(self.player, self.ball_moving_list):
                        hazard_hit = True

            if hazard_hit:
                if self.player.is_big:
                    self.player.is_big = False
                    old_bottom = self.player.bottom
                    self.player.scale = self.player.normal_scale
                    self.player.bottom = old_bottom
                    self.player.invincible_timer = 1.5
                    self.player.play_hit()
                else:
                    self.is_dying = True
                    self.death_timer = 0.0
                    play_effect("die", volume=0.75)
                    self.player.play_disappear()
                    return

            for cp in arcade.check_for_collision_with_list(self.player, self.checkpoints):
                if not cp.activated:
                    cp.activate()
                    self.respawn_x, self.respawn_y = cp.center_x, cp.center_y

            for ep in arcade.check_for_collision_with_list(self.player, self.end_points):
                if not ep.activated:
                    ep.activate()
                    play_effect("finish", volume=0.85)
                    self.level_complete = True
                    self.player.play_disappear()

        if self.camera:
            self.camera.position = (self.view_left + GAME_WIDTH / 2, GAME_HEIGHT / 2)

    def on_draw(self):
        self.clear()

        if self.camera:
            self.camera.use()

        if self.scene:
            self.scene.draw()

        if self.fade_alpha > 0 and self.camera:
            self.camera.use()
            arcade.draw_rect_filled(
                arcade.LBWH(self.view_left, 0, GAME_WIDTH, GAME_HEIGHT),
                (0, 0, 0, int(self.fade_alpha))
            )

        if self.is_paused:
            self.draw_pause_menu()

    def draw_pause_menu(self):
        panel_center_x = self.view_left + GAME_WIDTH / 2
        panel_center_y = GAME_HEIGHT / 2

        arcade.draw_rect_filled(
            arcade.XYWH(panel_center_x, panel_center_y, GAME_WIDTH, GAME_HEIGHT),
            (0, 0, 0, 125)
        )
        arcade.draw_rect_filled(
            arcade.XYWH(panel_center_x, panel_center_y + 10, 430, 330),
            UI_PANEL_COLOR
        )
        arcade.draw_rect_outline(
            arcade.XYWH(panel_center_x, panel_center_y + 10, 430, 330),
            UI_SELECTED_COLOR,
            4
        )

        PixelText(
            "TẠM DỪNG",
            panel_center_x,
            panel_center_y + 120,
            UI_TITLE_COLOR,
            size=30,
            anchor_x="center",
            bold=True
        ).draw()

        start_y = panel_center_y + 40
        for index, option in enumerate(self.pause_options):
            is_selected = index == self.pause_selected_index
            y = start_y - index * 62
            fill_color = UI_PANEL_SELECTED_COLOR if is_selected else UI_PANEL_COLOR
            border_color = UI_SELECTED_COLOR if is_selected else UI_MUTED_TEXT_COLOR
            text_color = UI_TITLE_COLOR if is_selected else UI_SECONDARY_TEXT_COLOR

            arcade.draw_rect_filled(
                arcade.XYWH(panel_center_x, y, 250, 44),
                fill_color
            )
            arcade.draw_rect_outline(
                arcade.XYWH(panel_center_x, y, 250, 44),
                border_color,
                3 if is_selected else 2
            )
            PixelText(
                option["label"],
                panel_center_x,
                y - 8,
                text_color,
                size=16,
                anchor_x="center",
                bold=is_selected
            ).draw()

        PixelText(
            "W/S hoặc ↑/↓ để chọn  |  ENTER xác nhận  |  ESC tiếp tục",
            panel_center_x,
            panel_center_y - 135,
            UI_MAIN_TEXT_COLOR,
            size=10,
            anchor_x="center"
        ).draw()

    def reset_player(self):
        self.player.center_x, self.player.center_y = self.respawn_x, self.respawn_y
        self.player.change_x = self.player.change_y = 0
        self.player.is_big = False
        self.player.scale = self.player.normal_scale
        self.player.invincible_timer = self.respawn_invincible_time
        self.player.alpha = 255
        self.player.play_appear()
        play_effect("spawn", volume=0.65)

    def toggle_pause(self):
        if self.fade_state != "PLAYING" or self.level_complete:
            return

        self.is_paused = not self.is_paused
        self.left_pressed = False
        self.right_pressed = False
        self.shift_pressed = False
        if self.player:
            self.player.change_x = 0
        play_effect("selectbutton", volume=0.7)

    def move_pause_selection(self, direction):
        self.pause_selected_index = (self.pause_selected_index + direction) % len(self.pause_options)
        play_effect("selectbutton", volume=0.65)

    def activate_pause_selection(self):
        action = self.pause_options[self.pause_selected_index]["action"]
        play_effect("selectbutton", volume=0.78)

        if action == "resume":
            self.is_paused = False
        elif action == "home":
            from menu_view import MenuView
            self.window.show_view(MenuView())
        elif action == "exit":
            stop_all_sounds()
            arcade.close_window()

    def on_key_press(self, key, modifiers):
        if self.is_paused:
            if key in (arcade.key.UP, arcade.key.W):
                self.move_pause_selection(-1)
            elif key in (arcade.key.DOWN, arcade.key.S):
                self.move_pause_selection(1)
            elif key == arcade.key.ENTER:
                self.activate_pause_selection()
            elif key == arcade.key.ESCAPE:
                self.toggle_pause()
            return

        if self.fade_state != "PLAYING" or not self.player:
            return

        if key == arcade.key.ESCAPE:
            self.toggle_pause()
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = True
        elif key in (arcade.key.SPACE, arcade.key.W, arcade.key.UP):
            if self.physics_engine and self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                play_effect("jump", volume=0.72)
        elif key == arcade.key.F:
            if self.player.spiked_ball_stock > 0:
                self.player.spiked_ball_stock -= 1
                play_effect("throw", volume=0.72)
                direction = 1 if self.player.character_face_direction == 0 else -1
                ball = SpikedBall(self.player.center_x, self.player.center_y, direction)
                self.projectiles.append(ball)
                self.scene.add_sprite("Projectiles", ball)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.shift_pressed = False
