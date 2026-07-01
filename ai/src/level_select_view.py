import os

import arcade
from sound_manager import play_effect, play_menu_music

from Settings import (
    ASSETS_PATH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_MAIN_TEXT_COLOR,
    UI_MUTED_TEXT_COLOR,
    UI_PANEL_COLOR,
    UI_PANEL_SELECTED_COLOR,
    UI_SECONDARY_TEXT_COLOR,
    UI_SELECTED_COLOR,
    UI_SHADOW_COLOR,
    UI_TITLE_COLOR,
)
from game_settings import get_selected_character_folder
from pixel_text import PixelText


LEVEL_OPTIONS = [
    {
        "label": "MÀN 1",
        "subtitle": "Chương 1 - Bắt đầu",
        "preview": "level_preview_map1.png",
        "accent": (90, 190, 110),
    },
    {
        "label": "MÀN 2",
        "subtitle": "Chương 2 - Sa mạc",
        "preview": "level_preview_map2.png",
        "accent": (86, 176, 218),
    },
    {
        "label": "MÀN 3",
        "subtitle": "Chương 3 - Thử thách khốc liệt",
        "preview": "level_preview_map3.png",
        "accent": (230, 120, 92),
    },
]


class LevelSelectView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.preview_sprites = []
        self.preview_sprite_lists = []
        self.card_centers = []
        self.blink_timer = 0.0
        self.show_selected = True

        spacing = 285
        start_x = SCREEN_WIDTH / 2 - spacing
        y = SCREEN_HEIGHT / 2 + 20

        for index, option in enumerate(LEVEL_OPTIONS):
            center_x = start_x + spacing * index
            self.card_centers.append((center_x, y))

            image_path = os.path.join(ASSETS_PATH, "images", option["preview"])
            if os.path.exists(image_path):
                sprite = arcade.Sprite(image_path)
                sprite.center_x = center_x
                sprite.center_y = y + 25
                sprite.width = 210
                sprite.height = 126
                sprite_list = arcade.SpriteList()
                sprite_list.append(sprite)
            else:
                sprite = None
                sprite_list = None
            self.preview_sprites.append(sprite)
            self.preview_sprite_lists.append(sprite_list)

        self.title_text = PixelText(
            "CHỌN MÀN CHƠI",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 90,
            UI_TITLE_COLOR,
            size=34,
            anchor_x="center",
            bold=True
        )
        self.help_text = PixelText(
            "A/D hoặc ←/→ để đổi màn  |  ENTER để chơi  |  ESC để quay lại",
            SCREEN_WIDTH / 2,
            62,
            UI_MAIN_TEXT_COLOR,
            size=13,
            anchor_x="center"
        )

    def on_show_view(self):
        arcade.set_background_color((18, 20, 30))
        self.window.set_mouse_visible(False)
        play_menu_music()

    def on_update(self, delta_time):
        self.blink_timer += delta_time
        if self.blink_timer >= 0.45:
            self.show_selected = not self.show_selected
            self.blink_timer = 0.0

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        for index, option in enumerate(LEVEL_OPTIONS):
            self.draw_level_card(index, option)

        self.help_text.draw()

    def draw_level_card(self, index, option):
        center_x, center_y = self.card_centers[index]
        is_selected = index == self.selected_index
        card_width = 245 if is_selected else 225
        card_height = 270 if is_selected else 250
        border_width = 4 if is_selected else 2
        border_color = UI_SELECTED_COLOR if is_selected else UI_MUTED_TEXT_COLOR
        fill_color = UI_PANEL_SELECTED_COLOR if is_selected else UI_PANEL_COLOR

        if is_selected and not self.show_selected:
            border_color = UI_TITLE_COLOR

        arcade.draw_rect_filled(
            arcade.XYWH(center_x + 5, center_y - 5, card_width, card_height),
            UI_SHADOW_COLOR
        )
        arcade.draw_rect_filled(
            arcade.XYWH(center_x, center_y, card_width, card_height),
            fill_color
        )
        arcade.draw_rect_outline(
            arcade.XYWH(center_x, center_y, card_width, card_height),
            border_color,
            border_width
        )

        preview_sprite = self.preview_sprites[index]
        if preview_sprite:
            preview_sprite.center_x = center_x
            preview_sprite.center_y = center_y + 48
            preview_sprite.width = 210 if not is_selected else 222
            preview_sprite.height = 126 if not is_selected else 134
            self.preview_sprite_lists[index].draw()
        else:
            self.draw_fallback_preview(center_x, center_y + 48, option["accent"], is_selected)

        PixelText(
            option["label"],
            center_x,
            center_y - 68,
            UI_TITLE_COLOR if is_selected else UI_SECONDARY_TEXT_COLOR,
            size=19 if is_selected else 16,
            anchor_x="center",
            bold=is_selected
        ).draw()
        PixelText(
            option["subtitle"],
            center_x,
            center_y - 104,
            UI_MAIN_TEXT_COLOR if is_selected else UI_MUTED_TEXT_COLOR,
            size=11,
            anchor_x="center"
        ).draw()

    def draw_fallback_preview(self, center_x, center_y, accent_color, is_selected):
        width = 210 if not is_selected else 222
        height = 126 if not is_selected else 134
        left = center_x - width / 2
        bottom = center_y - height / 2

        arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, (80, 204, 222))
        arcade.draw_lbwh_rectangle_filled(left, bottom, width, height * 0.36, (114, 224, 140))
        arcade.draw_lbwh_rectangle_filled(left, bottom, width, 28, accent_color)

        for offset in (30, 86, 152):
            arcade.draw_lbwh_rectangle_filled(left + offset, bottom + 44, 48, 12, accent_color)

        arcade.draw_circle_filled(left + 42, bottom + 92, 18, (255, 214, 72))
        arcade.draw_rect_outline(
            arcade.XYWH(center_x, center_y, width, height),
            UI_SHADOW_COLOR,
            3
        )

    def select_previous(self):
        self.selected_index = (self.selected_index - 1) % len(LEVEL_OPTIONS)
        play_effect("selectbutton", volume=0.65)

    def select_next(self):
        self.selected_index = (self.selected_index + 1) % len(LEVEL_OPTIONS)
        play_effect("selectbutton", volume=0.65)

    def start_selected_level(self):
        play_effect("selectbutton", volume=0.78)
        from LoadMap1 import LoadMap1
        from LoadMap2 import LoadMap2
        from LoadMap3 import LoadMap3
        from how_to_play_view import HowToPlayView

        level_classes = [LoadMap1, LoadMap2, LoadMap3]
        selected_level_class = level_classes[self.selected_index]
        selected_label = LEVEL_OPTIONS[self.selected_index]["label"]
        next_view = HowToPlayView(
            character_folder=get_selected_character_folder(),
            level_class=selected_level_class,
            level_label=selected_label
        )
        self.window.show_view(next_view)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.UP, arcade.key.W):
            self.select_previous()
        elif key in (arcade.key.RIGHT, arcade.key.D, arcade.key.DOWN, arcade.key.S):
            self.select_next()
        elif key == arcade.key.ENTER:
            self.start_selected_level()
        elif key == arcade.key.ESCAPE:
            play_effect("selectbutton", volume=0.7)
            from menu_view import MenuView
            self.window.show_view(MenuView())
