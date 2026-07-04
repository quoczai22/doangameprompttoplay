import arcade
import os
from Settings import *
from ai_algorithms import (
    astar_platform_path,
    bfs_local_search_targets,
    dijkstra_safe_path,
    hill_climbing_path,
    BotState,
)
from bresenham_utils import bresenham_line_of_sight

RIGHT_FACING = 0
LEFT_FACING = 1


class Bot(arcade.Sprite):
    def __init__(self, character_folder):
        super().__init__(scale=TILE_SCALING * 1.2)

        self.base_path = os.path.join(ASSETS_PATH, "Free", "Main Characters", character_folder)
        self.character_face_direction = RIGHT_FACING
        self.cur_texture_index = 0
        self.time_counter = 0.0

        self.idle_textures = []
        self.run_textures = []
        self.jump_textures = []
        self.fall_textures = []
        self.dead_textures = []

        self.patrol_speed = 1.0
        self.chase_speed = 2.0
        self.vision_radius = 300
        self.attack_radius = 1.2 * (32 * TILE_SCALING)

        self.is_dead = False
        self.change_x = -self.patrol_speed

        self.avoid_ledges = True
        self.hit_box_algorithm = "Simple"
        self.use_spatial_hash = True

        self.ai_timer = 0.0
        self.ai_interval = 0.08
        self.turn_cooldown = 0.0
        self.turn_lock_time = 0.18

        self.max_safe_drop_tiles = BOT_MAX_SAFE_DROP_TILES
        self.enable_platform_drop = ENABLE_BOT_PLATFORM_DROP_TEST
        self.is_dropping_from_platform = False
        self.use_pathfinding_support = ENABLE_PATHFINDING_SUPPORT

        # FSM
        self.state = BotState.PATROL
        self.previous_state = None
        self.last_seen_player_grid = None
        self.search_timer = 0.0
        self.max_search_time = 2.5
        self.bfs_search_targets = []
        self.current_search_goal = None

        # Bresenham cache
        self.last_los_start = None
        self.last_los_goal = None
        self.last_los_result = False
        self.last_los_cells = []
        self.last_los_blocked_cell = None

    def load_sprite_sheet(self, filename, columns, rows, frame_count):
        textures = []
        file_path = os.path.join(self.base_path, filename)
        if not os.path.exists(file_path):
            return textures

        sprite_sheet = arcade.load_spritesheet(file_path)
        frames = sprite_sheet.get_texture_grid(size=(32, 32), columns=columns, count=columns * rows)

        for i in range(frame_count):
            tex_r = frames[i]
            tex_l = tex_r.flip_left_right()
            textures.append([tex_r, tex_l])
        return textures

    def set_state(self, new_state, reason=""):
        if self.state != new_state:
            self.previous_state = self.state
            self.state = new_state
            if new_state == BotState.SEARCH:
                self.search_timer = 0.0
                self.bfs_search_targets = []
                self.current_search_goal = None

    def forget_player_and_patrol(self, reason=""):
        self.last_seen_player_grid = None
        self.search_timer = 0.0
        self.bfs_search_targets = []
        self.current_search_goal = None
        self.set_state(BotState.PATROL, reason)
        self.change_x = self.patrol_speed if self.character_face_direction == RIGHT_FACING else -self.patrol_speed

    def is_blocked_ahead(self, wall_lists=None, hazard_lists=None):
        hit_wall = self.check_wall(wall_lists)
        avoid_edge = self.avoid_ledges and self.should_avoid_edge(wall_lists, hazard_lists)
        return hit_wall or avoid_edge

    def forget_player_if_blocked(self, wall_lists=None, hazard_lists=None):
        if self.is_blocked_ahead(wall_lists, hazard_lists):
            self.flip_direction()
            self.forget_player_and_patrol("Bot bị chặn khi đuổi mục tiêu")
            return True

        return False

    def flip_direction(self):
        self.character_face_direction = (
            LEFT_FACING if self.character_face_direction == RIGHT_FACING else RIGHT_FACING
        )
        self.turn_cooldown = self.turn_lock_time

    def check_wall(self, wall_lists):
        if not wall_lists:
            return False

        look_ahead = 10
        check_x = self.right + look_ahead if self.character_face_direction == RIGHT_FACING else self.left - look_ahead

        sample_y_positions = [self.bottom + 8, self.center_y]

        for y in sample_y_positions:
            for w_list in wall_lists:
                if arcade.get_sprites_at_point((check_x, y), w_list):
                    return True
        return False

    def _get_front_probe_x(self):
        look_ahead = 10
        return self.right + look_ahead if self.character_face_direction == RIGHT_FACING else self.left - look_ahead

    def _get_front_edge_probe_x(self):
        edge_offset = 1
        return self.right + edge_offset if self.character_face_direction == RIGHT_FACING else self.left - edge_offset

    def _get_edge_probe_x_toward(self, target_x):
        edge_offset = 1
        return self.right + edge_offset if target_x >= self.center_x else self.left - edge_offset

    def _has_hazard_at(self, x, y, hazard_lists):
        if not hazard_lists:
            return False
        for h_list in hazard_lists:
            if arcade.get_sprites_at_point((x, y), h_list):
                return True
        return False

    def _has_support_at(self, x, y, wall_lists):
        if not wall_lists:
            return False
        for w_list in wall_lists:
            if arcade.get_sprites_at_point((x, y), w_list):
                return True
        return False

    def _get_safe_drop_distance(self, wall_lists, hazard_lists):
        if not wall_lists:
            return None

        front_x = self._get_front_edge_probe_x()
        tile_h = 32 * TILE_SCALING

        for level in range(0, self.max_safe_drop_tiles + 1):
            probe_y = self.bottom - 4 - (level * tile_h)

            if self._has_hazard_at(front_x, probe_y, hazard_lists):
                return None

            if self._has_support_at(front_x, probe_y, wall_lists):
                return level

        return None

    def _get_immediate_front_support(self, wall_lists):
        front_x = self._get_front_edge_probe_x()
        return self._has_support_at(front_x, self.bottom - 4, wall_lists)

    def _has_front_support_toward(self, target_x, wall_lists):
        front_x = self._get_edge_probe_x_toward(target_x)
        return self._has_support_at(front_x, self.bottom - 4, wall_lists)

    def should_avoid_edge(self, wall_lists, hazard_lists):
        if abs(self.change_y) > 0.1:
            return False

        safe_drop = self._get_safe_drop_distance(wall_lists, hazard_lists)
        return safe_drop is None

    def should_drop_from_platform(self, wall_lists, hazard_lists):
        if not self.enable_platform_drop or abs(self.change_y) > 0.1:
            return False

        has_front_support = self._get_immediate_front_support(wall_lists)
        if has_front_support:
            return False

        safe_drop = self._get_safe_drop_distance(wall_lists, hazard_lists)
        return safe_drop is not None and safe_drop > 0

    def _trace_bresenham_cells(self, start, end, walls):
        x0, y0 = start
        x1, y1 = end

        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        visited = []
        blocked_cell = None

        while True:
            current = (x0, y0)
            visited.append(current)

            if current != start and current != end and current in walls:
                blocked_cell = current
                break

            if current == end:
                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

        return visited, blocked_cell

    def _is_player_on_same_platform(self, player, walls, grid_unit):
        if abs(self.bottom - player.bottom) > grid_unit * 0.65:
            return False

        if not walls:
            return True

        bot_support_y = int((self.bottom - 4) // grid_unit)
        player_support_y = int((player.bottom - 4) // grid_unit)
        if bot_support_y != player_support_y:
            return False

        bot_grid_x = int(self.center_x // grid_unit)
        player_grid_x = int(player.center_x // grid_unit)
        left_x, right_x = sorted((bot_grid_x, player_grid_x))

        for grid_x in range(left_x, right_x + 1):
            if (grid_x, bot_support_y) not in walls:
                return False

        return True

    def update_ai(
        self,
        player,
        wall_lists=None,
        hazard_lists=None,
        grid_walls=None,
        grid_hazards=None,
        delta_time=1 / 60
    ):
        if self.is_dead:
            self.set_state(BotState.DEAD, "Bot đã chết")
            return

        if self.turn_cooldown > 0:
            self.turn_cooldown -= delta_time

        if abs(self.change_y) > 0.1:
            self.is_dropping_from_platform = True
            return
        self.is_dropping_from_platform = False

        self.ai_timer += delta_time
        if self.ai_timer < self.ai_interval:
            return
        self.ai_timer = 0.0

        grid_unit = 32 * TILE_SCALING
        start_grid = (int(self.center_x // grid_unit), int(self.center_y // grid_unit))
        goal_grid = (int(player.center_x // grid_unit), int(player.center_y // grid_unit))
        distance = arcade.get_distance_between_sprites(self, player)

        safe_walls = grid_walls if grid_walls is not None else set()
        self.grid_walls = safe_walls
        self.grid_hazards = grid_hazards if grid_hazards is not None else set()

        if start_grid == self.last_los_start and goal_grid == self.last_los_goal:
            has_line_of_sight = self.last_los_result
        else:
            has_line_of_sight = bresenham_line_of_sight(start_grid, goal_grid, safe_walls)
            los_cells, blocked_cell = self._trace_bresenham_cells(start_grid, goal_grid, safe_walls)
            self.last_los_start = start_grid
            self.last_los_goal = goal_grid
            self.last_los_result = has_line_of_sight
            self.last_los_cells = los_cells
            self.last_los_blocked_cell = blocked_cell

        same_platform = self._is_player_on_same_platform(player, safe_walls, grid_unit)
        has_front_support_to_player = (
            self._has_front_support_toward(player.center_x, wall_lists)
            if wall_lists
            else same_platform
        )
        can_engage_player = has_line_of_sight and same_platform and has_front_support_to_player

        if can_engage_player and distance <= self.attack_radius:
            self.last_seen_player_grid = goal_grid
            self.set_state(BotState.ATTACK, "Bot đã ở rất gần mục tiêu")
        elif can_engage_player and distance < self.vision_radius:
            self.last_seen_player_grid = goal_grid
            self.set_state(BotState.CHASE, "Bot phát hiện mục tiêu trong tầm nhìn")
        elif self.last_seen_player_grid is not None and same_platform:
            self.set_state(BotState.SEARCH, "Mất tầm nhìn trực tiếp nhưng còn nhớ vị trí cuối cùng của người chơi")
        else:
            self.last_seen_player_grid = None
            self.bfs_search_targets = []
            self.current_search_goal = None
            self.set_state(BotState.PATROL, "Không phát hiện mục tiêu")

        # FSM thi hành hành vi
        if self.state == BotState.PATROL:
            self.patrol(wall_lists, hazard_lists)

        elif self.state == BotState.CHASE:
            self.chase_player(player, wall_lists, hazard_lists)

        elif self.state == BotState.ATTACK:
            if player.center_x > self.center_x:
                self.change_x = self.chase_speed
                self.character_face_direction = RIGHT_FACING
            else:
                self.change_x = -self.chase_speed
                self.character_face_direction = LEFT_FACING

            self.forget_player_if_blocked(wall_lists, hazard_lists)

        elif self.state == BotState.SEARCH:
            self.search_last_seen_position(wall_lists, hazard_lists, delta_time)

    def patrol(self, wall_lists=None, hazard_lists=None):
        if self.turn_cooldown > 0:
            self.change_x = self.patrol_speed if self.character_face_direction == RIGHT_FACING else -self.patrol_speed
            return

        if abs(self.change_y) > 0.1:
            return

        hit_wall = self.check_wall(wall_lists)
        can_drop = self.should_drop_from_platform(wall_lists, hazard_lists)
        avoid_edge = self.avoid_ledges and (not can_drop) and self.should_avoid_edge(wall_lists, hazard_lists)

        if hit_wall or avoid_edge:
            self.flip_direction()

        self.change_x = self.patrol_speed if self.character_face_direction == RIGHT_FACING else -self.patrol_speed

    def chase_player(self, player, wall_lists=None, hazard_lists=None):
        grid_unit = 32 * TILE_SCALING
        start_grid = (int(self.center_x // grid_unit), int(self.center_y // grid_unit))
        goal_grid = (int(player.center_x // grid_unit), int(player.center_y // grid_unit))

        path = hill_climbing_path(start_grid, goal_grid)

        if len(path) > 1:
            next_step_grid_x = path[1][0]
            next_step_pixel_x = (next_step_grid_x * grid_unit) + (grid_unit / 2)

            if self.center_x < next_step_pixel_x:
                self.change_x = self.chase_speed
                self.character_face_direction = RIGHT_FACING
            elif self.center_x > next_step_pixel_x:
                self.change_x = -self.chase_speed
                self.character_face_direction = LEFT_FACING
            else:
                self.change_x = 0

            if self.is_blocked_ahead(wall_lists, hazard_lists):
                recovered = self.try_path_recovery(start_grid, goal_grid, grid_unit)
                if not recovered:
                    self.forget_player_if_blocked(wall_lists, hazard_lists)

    def search_last_seen_position(self, wall_lists=None, hazard_lists=None, delta_time=1 / 60):
        if self.last_seen_player_grid is None:
            self.set_state(BotState.PATROL, "Không còn vị trí mục tiêu để tìm")
            return

        self.search_timer += delta_time
        if self.search_timer >= self.max_search_time:
            self.forget_player_and_patrol("Tìm quá lâu nhưng không thấy lại người chơi")
            return

        grid_unit = 32 * TILE_SCALING
        start_grid = (int(self.center_x // grid_unit), int(self.center_y // grid_unit))
        goal_grid = self.get_bfs_search_goal(start_grid)
        if goal_grid is None:
            self.forget_player_and_patrol("BFS không còn điểm tìm kiếm hợp lệ")
            return

        goal_pixel_x = (goal_grid[0] * grid_unit) + (grid_unit / 2)

        if start_grid == goal_grid or abs(self.center_x - goal_pixel_x) <= grid_unit * 0.35:
            self.advance_bfs_search_goal()
            return

        path = hill_climbing_path(start_grid, goal_grid)
        if self.use_pathfinding_support:
            safe_path = dijkstra_safe_path(
                start_grid,
                goal_grid,
                getattr(self, "grid_walls", set()),
                getattr(self, "grid_hazards", set())
            )
            if safe_path:
                path = safe_path

        if len(path) > 1:
            next_step_grid_x = path[1][0]
            next_step_pixel_x = (next_step_grid_x * grid_unit) + (grid_unit / 2)

            if self.center_x < next_step_pixel_x:
                self.change_x = self.patrol_speed
                self.character_face_direction = RIGHT_FACING
            elif self.center_x > next_step_pixel_x:
                self.change_x = -self.patrol_speed
                self.character_face_direction = LEFT_FACING
            else:
                self.forget_player_and_patrol("Không còn hướng tìm hợp lệ")
                return

            self.forget_player_if_blocked(wall_lists, hazard_lists)

    def get_bfs_search_goal(self, start_grid):
        if self.current_search_goal is not None:
            return self.current_search_goal

        walls = getattr(self, "grid_walls", set())
        hazards = getattr(self, "grid_hazards", set())
        targets = bfs_local_search_targets(
            self.last_seen_player_grid,
            walls,
            hazards,
            max_depth=4,
            max_targets=5,
        )

        self.bfs_search_targets = [self.last_seen_player_grid] + targets
        self.current_search_goal = self.bfs_search_targets.pop(0) if self.bfs_search_targets else None

        return self.current_search_goal

    def advance_bfs_search_goal(self):
        if self.bfs_search_targets:
            self.current_search_goal = self.bfs_search_targets.pop(0)
            return

        self.forget_player_and_patrol("BFS đã kiểm tra xong khu vực mất dấu")

    def try_path_recovery(self, start_grid, goal_grid, grid_unit):
        if not self.use_pathfinding_support:
            return False

        walls = getattr(self, "grid_walls", set())
        hazards = getattr(self, "grid_hazards", set())
        path = dijkstra_safe_path(start_grid, goal_grid, walls, hazards)
        if not path:
            path = astar_platform_path(start_grid, goal_grid, walls)

        if len(path) <= 1:
            return False

        next_step_grid_x = path[1][0]
        next_step_pixel_x = (next_step_grid_x * grid_unit) + (grid_unit / 2)

        if self.center_x < next_step_pixel_x:
            self.change_x = self.chase_speed
            self.character_face_direction = RIGHT_FACING
            self.set_state(BotState.CHASE, "Dijkstra/A* hỗ trợ Hill Climbing khi đường thẳng bị chặn")
            return True
        if self.center_x > next_step_pixel_x:
            self.change_x = -self.chase_speed
            self.character_face_direction = LEFT_FACING
            self.set_state(BotState.CHASE, "Dijkstra/A* hỗ trợ Hill Climbing khi đường thẳng bị chặn")
            return True

        return False

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_counter += delta_time

        if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING

        if self.is_dead and self.dead_textures:
            if self.time_counter > 0.05:
                self.time_counter = 0
                self.cur_texture_index += 1
                if self.cur_texture_index >= len(self.dead_textures):
                    self.remove_from_sprite_lists()
                    return
                else:
                    self.texture = self.dead_textures[self.cur_texture_index][self.character_face_direction]
            return

        if self.change_y > 0 and self.jump_textures:
            self.texture = self.jump_textures[0][self.character_face_direction]
            return

        if self.change_y < 0 and self.fall_textures:
            self.texture = self.fall_textures[0][self.character_face_direction]
            return

        if abs(self.change_x) > 0.1 and self.run_textures:
            anim_speed = 0.08 if self.state in (BotState.CHASE, BotState.SEARCH) else 0.15
            if self.time_counter > anim_speed:
                self.time_counter = 0
                self.cur_texture_index = (self.cur_texture_index + 1) % len(self.run_textures)
                self.texture = self.run_textures[self.cur_texture_index][self.character_face_direction]
            return

        if self.idle_textures:
            if self.time_counter > 0.15:
                self.time_counter = 0
                self.cur_texture_index = (self.cur_texture_index + 1) % len(self.idle_textures)
                self.texture = self.idle_textures[self.cur_texture_index][self.character_face_direction]

    def play_death(self):
        if not self.is_dead:
            self.is_dead = True
            self.set_state(BotState.DEAD, "Bot bị tiêu diệt")
            self.cur_texture_index = 0
            self.time_counter = 0
            self.change_x = 0
            self.change_y = 0
