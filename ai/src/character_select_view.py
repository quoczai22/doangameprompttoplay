import arcade

from Settings import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_MAIN_TEXT_COLOR,
    UI_MUTED_TEXT_COLOR,
    UI_PANEL_COLOR,
    UI_PANEL_SELECTED_COLOR,
    UI_SECONDARY_TEXT_COLOR,
    UI_SELECTED_COLOR,
    UI_TITLE_COLOR,
)
from game_settings import get_selected_character_folder, set_selected_character_folder
from pixel_text import PixelText
from pink_man import PinkMan


CHARACTER_OPTIONS = [
    {"label": "PINK MAN", "folder": "Pink Man"},
    {"label": "NINJA FROG", "folder": "Ninja Frog"},
]


class CharacterSelectView(arcade.View):
    def __init__(self):
        super().__init__()
        current_character = get_selected_character_folder()
        self.selected_index = next(
            (
                index for index, option in enumerate(CHARACTER_OPTIONS)
                if option["folder"] == current_character
            ),
            0
        )
        self.preview_sprites = arcade.SpriteList()
        self.card_centers = []

        spacing = 260
        start_x = SCREEN_WIDTH / 2 - spacing / 2
        y = SCREEN_HEIGHT / 2 + 20

        for index, option in enumerate(CHARACTER_OPTIONS):
            sprite = PinkMan(option["folder"])
            sprite.center_x = start_x + spacing * index
            sprite.center_y = y
            sprite.scale = 3.2
            self.preview_sprites.append(sprite)
            self.card_centers.append((sprite.center_x, sprite.center_y))

        self.title_text = PixelText(
            "CHỌN NHÂN VẬT",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 95,
            UI_TITLE_COLOR,
            size=34,
            anchor_x="center",
            bold=True
        )
        self.help_text = PixelText(
            "A/D hoặc ←/→ để đổi  |  ENTER để lưu  |  ESC để quay lại",
            SCREEN_WIDTH / 2,
            70,
            UI_MAIN_TEXT_COLOR,
            size=13,
            anchor_x="center"
        )

    def on_show_view(self):
        arcade.set_background_color((18, 20, 30))
        self.window.set_mouse_visible(False)

    def on_update(self, delta_time):
        self.preview_sprites.update_animation(delta_time)

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        for index, option in enumerate(CHARACTER_OPTIONS):
            center_x, center_y = self.card_centers[index]
            is_selected = index == self.selected_index
            border_color = UI_SELECTED_COLOR if is_selected else UI_MUTED_TEXT_COLOR
            fill_color = UI_PANEL_SELECTED_COLOR if is_selected else UI_PANEL_COLOR

            arcade.draw_rect_filled(
                arcade.XYWH(center_x, center_y - 5, 190, 230),
                fill_color
            )
            arcade.draw_rect_outline(
                arcade.XYWH(center_x, center_y - 5, 190, 230),
                border_color,
                4 if is_selected else 2
            )

            label = PixelText(
                option["label"],
                center_x,
                center_y - 105,
                UI_TITLE_COLOR if is_selected else UI_SECONDARY_TEXT_COLOR,
                size=16,
                anchor_x="center",
                bold=is_selected
            )
            label.draw()

        self.preview_sprites.draw()
        self.help_text.draw()

    def select_previous(self):
        self.selected_index = (self.selected_index - 1) % len(CHARACTER_OPTIONS)

    def select_next(self):
        self.selected_index = (self.selected_index + 1) % len(CHARACTER_OPTIONS)

    def save_selection(self):
        selected_folder = CHARACTER_OPTIONS[self.selected_index]["folder"]
        set_selected_character_folder(selected_folder)
        from settings_view import SettingsView
        self.window.show_view(SettingsView())

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.select_previous()
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.select_next()
        elif key == arcade.key.ENTER:
            self.save_selection()
        elif key == arcade.key.ESCAPE:
            from settings_view import SettingsView
            self.window.show_view(SettingsView())
