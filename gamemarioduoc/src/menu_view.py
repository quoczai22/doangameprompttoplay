import arcade
import os
from sound_manager import play_effect, play_menu_music, stop_all_sounds
from Settings import (
    ASSETS_PATH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    UI_MAIN_TEXT_COLOR,
    UI_MUTED_TEXT_COLOR,
    UI_SECONDARY_TEXT_COLOR,
    UI_SHADOW_COLOR,
    UI_TITLE_COLOR,
)
from pixel_text import PixelText


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.camera.Camera2D(
            viewport=arcade.LBWH(left=0, bottom=0, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        )
        self.ui_list = arcade.SpriteList()
        self.selected_index = 0
        self.menu_items = [
            {
                "label": "BẮT ĐẦU",
                "hint": "ENTER",
                "action": "start",
                "y": SCREEN_HEIGHT // 2 - 5,
                "size": 21,
                "color": UI_MAIN_TEXT_COLOR,
            },
            {
                "label": "CÀI ĐẶT",
                "hint": "G",
                "action": "settings",
                "y": SCREEN_HEIGHT // 2 - 58,
                "size": 15,
                "color": UI_SECONDARY_TEXT_COLOR,
            },
            {
                "label": "THOÁT",
                "hint": "ESC",
                "action": "exit",
                "y": SCREEN_HEIGHT // 2 - 100,
                "size": 15,
                "color": UI_MUTED_TEXT_COLOR,
            },
        ]

        image_path = os.path.join(ASSETS_PATH, "images", "menu_background_pixel.png")
        if os.path.exists(image_path):
            bg_sprite = arcade.Sprite(image_path)
            bg_sprite.center_x = SCREEN_WIDTH / 2
            bg_sprite.center_y = SCREEN_HEIGHT / 2
            bg_sprite.width = SCREEN_WIDTH
            bg_sprite.height = SCREEN_HEIGHT
            self.ui_list.append(bg_sprite)

        self.blink_timer = 0.0
        self.show_press_text = True

        self.title_text = PixelText(
            SCREEN_TITLE,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 140,
            UI_TITLE_COLOR,
            size=40,
            anchor_x="center",
            bold=True
        )
        self.title_shadow_text = PixelText(
            SCREEN_TITLE,
            SCREEN_WIDTH // 2 + 4,
            SCREEN_HEIGHT // 2 + 136,
            UI_SHADOW_COLOR,
            size=40,
            anchor_x="center",
            bold=True
        )

    def draw_menu_item(self, item, is_selected):
        prefix = "> " if is_selected else ""
        suffix = " <" if is_selected else ""
        label = f"{prefix}{item['label']}{suffix}"
        size = item["size"] + 6 if is_selected else item["size"]
        y = item["y"] + 2 if is_selected else item["y"]
        color = UI_TITLE_COLOR if is_selected else item["color"]

        should_draw = (not is_selected) or self.show_press_text
        if not should_draw:
            return

        PixelText(
            label,
            SCREEN_WIDTH // 2 + 3,
            y - 3,
            UI_SHADOW_COLOR,
            size=size,
            anchor_x="center",
            bold=is_selected
        ).draw()
        PixelText(
            label,
            SCREEN_WIDTH // 2,
            y,
            color,
            size=size,
            anchor_x="center",
            bold=is_selected
        ).draw()

    def on_show_view(self):
        self.window.set_mouse_visible(True)
        self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.camera.use()
        arcade.set_background_color((20, 20, 20))
        play_menu_music()

    def on_update(self, delta_time):
        self.blink_timer += delta_time
        if self.blink_timer >= 0.5:
            self.show_press_text = not self.show_press_text
            self.blink_timer = 0.0

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.ui_list.draw()

        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 55)
        )

        self.title_shadow_text.draw()
        self.title_text.draw()

        for index, item in enumerate(self.menu_items):
            self.draw_menu_item(item, index == self.selected_index)

    def move_selection(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.menu_items)
        play_effect("selectbutton", volume=0.65)

    def activate_selected(self):
        play_effect("selectbutton", volume=0.78)
        action = self.menu_items[self.selected_index]["action"]
        if action == "start":
            from level_select_view import LevelSelectView
            self.window.show_view(LevelSelectView())
        elif action == "settings":
            from settings_view import SettingsView
            self.window.show_view(SettingsView())
        elif action == "exit":
            stop_all_sounds()
            arcade.close_window()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.move_selection(-1)

        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_selection(1)

        elif key == arcade.key.ENTER:
            self.activate_selected()

        elif key == arcade.key.G:
            play_effect("selectbutton", volume=0.78)
            from settings_view import SettingsView
            self.window.show_view(SettingsView())

        elif key == arcade.key.ESCAPE:
            stop_all_sounds()
            arcade.close_window()
