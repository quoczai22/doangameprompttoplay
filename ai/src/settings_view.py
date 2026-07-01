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
from game_settings import get_selected_character_label
from pixel_text import PixelText


SETTINGS_OPTIONS = [
    "CÀI ĐẶT ÂM THANH",
    "CÀI ĐẶT NHÂN VẬT",
]


class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.notice_message = ""
        self.title_text = PixelText(
            "CÀI ĐẶT",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 105,
            UI_TITLE_COLOR,
            size=36,
            anchor_x="center",
            bold=True
        )
        self.help_text = PixelText(
            "W/S hoặc ↑/↓ để chọn  |  ENTER để mở  |  ESC để quay lại",
            SCREEN_WIDTH / 2,
            70,
            UI_MAIN_TEXT_COLOR,
            size=13,
            anchor_x="center"
        )

    def on_show_view(self):
        arcade.set_background_color((18, 20, 30))
        self.window.set_mouse_visible(False)

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        start_y = SCREEN_HEIGHT / 2 + 60
        for index, label in enumerate(SETTINGS_OPTIONS):
            display_label = label
            if index == 1:
                display_label = f"{label}: {get_selected_character_label()}"

            y = start_y - index * 85
            is_selected = index == self.selected_index
            fill_color = UI_PANEL_SELECTED_COLOR if is_selected else UI_PANEL_COLOR
            border_color = UI_SELECTED_COLOR if is_selected else UI_MUTED_TEXT_COLOR
            text_color = UI_TITLE_COLOR if is_selected else UI_SECONDARY_TEXT_COLOR

            arcade.draw_rect_filled(
                arcade.XYWH(SCREEN_WIDTH / 2, y, 430, 58),
                fill_color
            )
            arcade.draw_rect_outline(
                arcade.XYWH(SCREEN_WIDTH / 2, y, 430, 58),
                border_color,
                3 if is_selected else 2
            )

            PixelText(
                display_label,
                SCREEN_WIDTH / 2,
                y - 8,
                text_color,
                size=18,
                anchor_x="center",
                bold=is_selected
            ).draw()

        if self.notice_message:
            PixelText(
                self.notice_message,
                SCREEN_WIDTH / 2,
                120,
                UI_MUTED_TEXT_COLOR,
                size=13,
                anchor_x="center"
            ).draw()

        self.help_text.draw()

    def move_selection(self, direction):
        self.selected_index = (self.selected_index + direction) % len(SETTINGS_OPTIONS)

    def open_selected(self):
        if self.selected_index == 0:
            self.notice_message = "Cài đặt âm thanh sẽ được thêm sau."
            return

        from character_select_view import CharacterSelectView
        self.window.show_view(CharacterSelectView())

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.move_selection(-1)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_selection(1)
        elif key == arcade.key.ENTER:
            self.open_selected()
        elif key == arcade.key.ESCAPE:
            from menu_view import MenuView
            self.window.show_view(MenuView())
