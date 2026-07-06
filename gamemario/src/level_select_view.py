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
    {
        "label": "MÀN 4",
        "subtitle": "Chương 4 - Vùng hiểm trở",
        "preview": "level_preview_map4.png",
        "accent": (144, 214, 92),
    },
    {
        "label": "MÀN 5",
        "subtitle": "Chương 5 - Thử thách cuối",
        "preview": "level_preview_map5.png",
        "accent": (238, 204, 82),
    },
    {
        "label": "MÀN 6",
        "subtitle": "Chương 6 - Chặng đường cuối",
        "preview": "level_preview_map6.png",
        "accent": (96, 174, 238),
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

        self.columns = 3
        self.card_width = 210
        self.selected_card_width = self.card_width + 14
        self.card_height = 190
        self.selected_card_height = self.card_height + 12
        self.preview_width = self.card_width - 28
        self.selected_preview_width = self.selected_card_width - 28
        self.preview_height = 86
        self.selected_preview_height = self.selected_preview_width * 0.6
        self.column_spacing = 245
        self.row_spacing = 218
        top_y = SCREEN_HEIGHT / 2 + 92

        for index, option in enumerate(LEVEL_OPTIONS):
            row = index // self.columns
            column = index % self.columns
            row_count = min(self.columns, len(LEVEL_OPTIONS) - row * self.columns)
            row_width = self.column_spacing * (row_count - 1)
            start_x = SCREEN_WIDTH / 2 - row_width / 2
            center_x = start_x + self.column_spacing * column
            center_y = top_y - self.row_spacing * row
            self.card_centers.append((center_x, center_y))

            image_path = os.path.join(ASSETS_PATH, "images", option["preview"])
            if os.path.exists(image_path):
                sprite = arcade.Sprite(image_path)
                sprite.center_x = center_x
                sprite.center_y = center_y + 34
                sprite.width = self.preview_width
                sprite.height = self.preview_height
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
            SCREEN_HEIGHT - 64,
            UI_TITLE_COLOR,
            size=34,
            anchor_x="center",
            bold=True
        )
        self.help_text = PixelText(
            "A/D hoặc ←/→ để đổi màn  |  ENTER để chơi  |  ESC để quay lại",
            SCREEN_WIDTH / 2,
            38,
            UI_MAIN_TEXT_COLOR,
            size=12,
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
        card_width = self.selected_card_width if is_selected else self.card_width
        card_height = self.selected_card_height if is_selected else self.card_height
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
            preview_sprite.center_y = center_y + 36
            preview_sprite.width = self.preview_width if not is_selected else self.selected_preview_width
            preview_sprite.height = self.preview_height if not is_selected else self.selected_preview_height
            self.preview_sprite_lists[index].draw()
        else:
            self.draw_fallback_preview(center_x, center_y + 36, option["accent"], is_selected)

        PixelText(
            option["label"],
            center_x,
            center_y - 48,
            UI_TITLE_COLOR if is_selected else UI_SECONDARY_TEXT_COLOR,
            size=14,
            anchor_x="center",
            bold=False
        ).draw()
        PixelText(
            option["subtitle"],
            center_x,
            center_y - 80,
            UI_MAIN_TEXT_COLOR if is_selected else UI_MUTED_TEXT_COLOR,
            size=9,
            anchor_x="center"
        ).draw()

    def draw_fallback_preview(self, center_x, center_y, accent_color, is_selected):
        width = self.preview_width if not is_selected else self.selected_preview_width
        height = self.preview_height if not is_selected else self.selected_preview_height
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

    def move_selection(self, delta_row=0, delta_column=0):
        row = self.selected_index // self.columns
        column = self.selected_index % self.columns
        target_row = row + delta_row
        target_column = column + delta_column
        row_count = (len(LEVEL_OPTIONS) + self.columns - 1) // self.columns

        if delta_column:
            current_row_count = min(self.columns, len(LEVEL_OPTIONS) - row * self.columns)
            target_column %= current_row_count

        if delta_row:
            target_row %= row_count
            target_row_count = min(self.columns, len(LEVEL_OPTIONS) - target_row * self.columns)
            target_column = min(column, target_row_count - 1)

        self.selected_index = target_row * self.columns + target_column
        play_effect("selectbutton", volume=0.65)

    def select_previous(self):
        self.move_selection(delta_column=-1)

    def select_next(self):
        self.move_selection(delta_column=1)

    def start_selected_level(self):
        play_effect("selectbutton", volume=0.78)
        from LoadMap1 import LoadMap1
        from LoadMap2 import LoadMap2
        from LoadMap3 import LoadMap3
        from LoadMap4 import LoadMap4
        from LoadMap5 import LoadMap5
        from LoadMap6 import LoadMap6
        from how_to_play_view import HowToPlayView

        level_classes = [LoadMap1, LoadMap2, LoadMap3, LoadMap4, LoadMap5, LoadMap6]
        selected_level_class = level_classes[self.selected_index]
        selected_label = LEVEL_OPTIONS[self.selected_index]["label"]
        next_view = HowToPlayView(
            character_folder=get_selected_character_folder(),
            level_class=selected_level_class,
            level_label=selected_label
        )
        self.window.show_view(next_view)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.select_previous()
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.select_next()
        elif key in (arcade.key.UP, arcade.key.W):
            self.move_selection(delta_row=-1)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_selection(delta_row=1)
        elif key == arcade.key.ENTER:
            self.start_selected_level()
        elif key == arcade.key.ESCAPE:
            play_effect("selectbutton", volume=0.7)
            from menu_view import MenuView
            self.window.show_view(MenuView())
