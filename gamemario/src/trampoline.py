import os

import arcade

from Settings import ROOT_DIR


class Trampoline(arcade.Sprite):
    def __init__(self, x, y, original_texture, scale=1.0):
        super().__init__(scale=scale)
        self.center_x = x
        self.center_y = y
        self.texture = original_texture
        self.idle_texture = original_texture
        self.jump_textures = []
        self.current_frame = 0
        self.time_counter = 0.0
        self.is_bouncing = False
        self.bounce_speed = 24
        self.cooldown_duration = 2.0
        self.cooldown_timer = 0.0

        self._load_idle_texture()
        self._load_jump_animation()

    def _load_idle_texture(self):
        idle_file = os.path.join(ROOT_DIR, "Free", "Traps", "Trampoline", "Idle.png")
        if os.path.exists(idle_file):
            self.idle_texture = arcade.load_texture(idle_file)
            self.texture = self.idle_texture

    def _load_jump_animation(self):
        jump_sheet = os.path.join(ROOT_DIR, "Free", "Traps", "Trampoline", "Jump (28x28).png")
        if not os.path.exists(jump_sheet):
            return

        sheet = arcade.load_spritesheet(jump_sheet)
        self.jump_textures = sheet.get_texture_grid(size=(28, 28), columns=8, count=8)

    def bounce(self):
        if not self.can_bounce():
            return False

        self.is_bouncing = True
        self.current_frame = 0
        self.time_counter = 0.0
        self.cooldown_timer = self.cooldown_duration
        if self.jump_textures:
            self.texture = self.jump_textures[0]
        return True

    def can_bounce(self):
        return self.cooldown_timer <= 0

    def update_animation(self, delta_time: float = 1 / 60):
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0, self.cooldown_timer - delta_time)

        if not self.is_bouncing or not self.jump_textures:
            return

        self.time_counter += delta_time
        if self.time_counter < 0.04:
            return

        self.time_counter = 0.0
        self.current_frame += 1
        if self.current_frame >= len(self.jump_textures):
            self.is_bouncing = False
            self.texture = self.idle_texture
            return

        self.texture = self.jump_textures[self.current_frame]
