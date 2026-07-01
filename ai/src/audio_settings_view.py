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
from game_settings import (
    get_effects_volume,
    get_music_volume,
    is_effects_enabled,
    is_music_enabled,
    set_effects_volume,
    set_effects_enabled,
    set_music_volume,
    set_music_enabled,
)
from pixel_text import PixelText
from sound_manager import play_effect, play_menu_music, refresh_effects, refresh_menu_music


AUDIO_OPTIONS = [
    "NHẠC NỀN",
    "HIỆU ỨNG",
]


class AudioSettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.title_text = PixelText(
            "CÀI ĐẶT ÂM THANH",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 105,
            UI_TITLE_COLOR,
            size=32,
            anchor_x="center",
            bold=True
        )
        self.help_text = PixelText(
            "W/S hoặc ↑/↓ để chọn  |  A/D hoặc ←/→ để chỉnh  |  ENTER bật/tắt",
            SCREEN_WIDTH / 2,
            70,
            UI_MAIN_TEXT_COLOR,
            size=13,
            anchor_x="center"
        )

    def on_show_view(self):
        arcade.set_background_color((18, 20, 30))
        self.window.set_mouse_visible(False)
        play_menu_music()

    def on_draw(self):
        self.clear()
        self.title_text.draw()

        start_y = SCREEN_HEIGHT / 2 + 55
        for index, label in enumerate(AUDIO_OPTIONS):
            enabled = is_music_enabled() if index == 0 else is_effects_enabled()
            volume = get_music_volume() if index == 0 else get_effects_volume()
            status = "BẬT" if enabled else "TẮT"
            display_label = f"{label}: {status}  {int(volume * 100):3d}%"

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

            self.draw_volume_bar(SCREEN_WIDTH / 2, y - 33, volume, enabled, is_selected)

        self.help_text.draw()

    def draw_volume_bar(self, center_x, center_y, volume, enabled, is_selected):
        bar_width = 260
        bar_height = 10
        filled_width = bar_width * volume
        fill_color = UI_SELECTED_COLOR if enabled else UI_MUTED_TEXT_COLOR
        border_color = UI_TITLE_COLOR if is_selected else UI_MUTED_TEXT_COLOR

        arcade.draw_rect_outline(
            arcade.XYWH(center_x, center_y, bar_width, bar_height),
            border_color,
            2
        )
        if filled_width > 0:
            arcade.draw_rect_filled(
                arcade.XYWH(
                    center_x - bar_width / 2 + filled_width / 2,
                    center_y,
                    filled_width,
                    bar_height - 3
                ),
                fill_color
            )

    def move_selection(self, direction):
        self.selected_index = (self.selected_index + direction) % len(AUDIO_OPTIONS)
        play_effect("selectbutton", volume=0.65)

    def toggle_selected(self):
        play_effect("selectbutton", volume=0.78)
        if self.selected_index == 0:
            set_music_enabled(not is_music_enabled())
            refresh_menu_music()
        else:
            set_effects_enabled(not is_effects_enabled())
            refresh_effects()

    def adjust_selected_volume(self, direction):
        step = 0.1
        if self.selected_index == 0:
            set_music_volume(get_music_volume() + direction * step)
            refresh_menu_music()
        else:
            set_effects_volume(get_effects_volume() + direction * step)
            play_effect("selectbutton", volume=0.65)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.move_selection(-1)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_selection(1)
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.adjust_selected_volume(-1)
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.adjust_selected_volume(1)
        elif key == arcade.key.ENTER:
            self.toggle_selected()
        elif key == arcade.key.ESCAPE:
            play_effect("selectbutton", volume=0.7)
            from settings_view import SettingsView
            self.window.show_view(SettingsView())
