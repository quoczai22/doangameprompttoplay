import arcade


class MovingPlatform(arcade.Sprite):
    def __init__(
        self,
        x,
        y,
        texture,
        scale,
        boundary_left=None,
        boundary_right=None,
        change_x=0,
        boundary_bottom=None,
        boundary_top=None,
        change_y=0,
    ):
        super().__init__()

        self.texture = texture
        self.scale = scale
        self._float_x = float(x)
        self._float_y = float(y)
        self.center_x = round(self._float_x)
        self.center_y = round(self._float_y)

        self.boundary_left = round(boundary_left) if boundary_left is not None else self.center_x
        self.boundary_right = round(boundary_right) if boundary_right is not None else self.center_x
        self.boundary_bottom = round(boundary_bottom) if boundary_bottom is not None else self.center_y
        self.boundary_top = round(boundary_top) if boundary_top is not None else self.center_y
        self.speed_x = change_x * 60
        self.speed_y = change_y * 60
        self.change_x = change_x
        self.change_y = change_y

        self.delta_x = 0
        self.delta_y = 0

    def update(self, delta_time: float = 1 / 60):
        old_x = self.center_x
        old_y = self.center_y

        self._float_x += self.speed_x * delta_time
        self._float_y += self.speed_y * delta_time

        if self.speed_x > 0 and self._float_x >= self.boundary_right:
            self._float_x = self.boundary_right
            self.speed_x *= -1
            self.change_x *= -1
        elif self.speed_x < 0 and self._float_x <= self.boundary_left:
            self._float_x = self.boundary_left
            self.speed_x *= -1
            self.change_x *= -1

        if self.speed_y > 0 and self._float_y >= self.boundary_top:
            self._float_y = self.boundary_top
            self.speed_y *= -1
            self.change_y *= -1
        elif self.speed_y < 0 and self._float_y <= self.boundary_bottom:
            self._float_y = self.boundary_bottom
            self.speed_y *= -1
            self.change_y *= -1

        self.center_x = round(self._float_x)
        self.center_y = round(self._float_y)
        self.delta_x = self.center_x - old_x
        self.delta_y = self.center_y - old_y
