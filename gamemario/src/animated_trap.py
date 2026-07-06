import os
import arcade
from Settings import ROOT_DIR


class AnimatedTrap(arcade.Sprite):
    def __init__(self, x, y, original_texture, scale=1.0, trap_type="fan", frame_time=0.04):
        super().__init__(scale=scale)
        self.center_x = x
        self.center_y = y
        self.texture = original_texture
        self.textures = []
        self.current_frame = 0
        self.time_counter = 0.0
        self.frame_time = frame_time

        if trap_type == "fan":
            self._load_fan_animation()

    def _load_fan_animation(self):
        fan_sheet = os.path.join(ROOT_DIR, "Free", "Traps", "Fan", "On (24x8).png")
        if not os.path.exists(fan_sheet):
            return

        sheet = arcade.load_spritesheet(fan_sheet)
        self.textures = sheet.get_texture_grid(size=(24, 8), columns=4, count=4)
        if self.textures:
            self.texture = self.textures[0]

    def update_animation(self, delta_time: float = 1 / 60):
        if not self.textures:
            return

        self.time_counter += delta_time
        if self.time_counter < self.frame_time:
            return

        self.time_counter = 0.0
        self.current_frame = (self.current_frame + 1) % len(self.textures)
        self.texture = self.textures[self.current_frame]
