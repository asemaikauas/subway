add_library('minim')

import time
import os
import random


PATH = os.getcwd()
player = Minim(this)


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
LANE_COUNT = 3

PLAYER_X = 250

LANE_POSITIONS_Y_JACK = [
    390,  # up
    518,  # mid
    635   # down
]

LANE_POSITIONS_Y = [
    430,  # up
    550,  # mid
    665   # down
]

class AnimationConfig:
    SPRITE_IDLE = 0
    SPRITE_RUN1 = 1
    SPRITE_RUN2 = 2
    SPRITE_JUMP = 3
    SPRITE_SLIDE = 4
    SPRITE_FLY = 5

    SPRITE_COORDINATES = {
        0: (0, 0, 19, 40),     # idle
        1: (19, 0, 27, 40),    # run1
        2: (45, 0, 30, 40),    # run2 
        3: (75, 0, 24, 40),    # jump 
        4: (99, 0, 28, 40),    # slide 
        5: (128, 0, 36, 40),   # flying (for later)
    }

    SLIDE_DURATION = 70
    RUN_ANIMATION_FRAMES = [1, 2]  # cycle between run1 and run2
    RUN_ANIMATION_SPEED = 7
    CHARACTER_WIDTH = 60
    CHARACTER_HEIGHT = 60

class State:
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    JUMPING = "JUMPING"
    SLIDING = "SLIDING"

class Player:
    def __init__(self, sprite_img, game):
        # store game reference (important)
        self.game = game

        self.x = PLAYER_X
        self.y = LANE_POSITIONS_Y_JACK[1]
        self.base_y = LANE_POSITIONS_Y_JACK[1]
        self.target_lane = 1
        self.current_lane = 1

        self.velocity_x = 0
        self.velocity_y = 0
        
        self.NORMAL_JUMP_FORCE = -10
        self.SUPER_JUMP_FORCE = -14

        self.JUMP_FORCE = self.NORMAL_JUMP_FORCE
        self.GRAVITY = 0.5
        self.MAX_FALL_SPEED = 15
        
        self.powerup_active = False
        self.powerup_end_time = 0

        self.is_moving = True
        self.on_train = False

        # Use animation config sizes as collider sizes to avoid mismatch
        self.sprite_sheet = sprite_img
        self.sprite_width = AnimationConfig.CHARACTER_WIDTH
        self.sprite_height = AnimationConfig.CHARACTER_HEIGHT

        self.state = State.RUNNING
        self.current_sprite_index = AnimationConfig.SPRITE_RUN1

        self.state_timer = 0
        self.animation_counter = 0
        self.run_frame_index = 0

        self.is_jumping = False
        self.is_on_ground = True
        self.is_sliding = False

    def change_state(self, new_state):
        if self.state == new_state:
            return False

        if new_state == State.JUMPING:
            if self.state != State.RUNNING or (not self.is_on_ground and not self.on_train):
                return False

        if new_state == State.SLIDING:
            if self.state != State.RUNNING:
                return False

        # reset flags for old states
        if self.state == State.JUMPING:
            self.is_jumping = False
        elif self.state == State.SLIDING:
            self.is_sliding = False

        self.state = new_state
        self.state_timer = 0

        if new_state == State.IDLE:
            self.current_sprite_index = AnimationConfig.SPRITE_IDLE
        elif new_state == State.RUNNING:
            self.current_sprite_index = AnimationConfig.SPRITE_RUN1
            self.run_frame_index = 0
        elif new_state == State.JUMPING:
            self.current_sprite_index = AnimationConfig.SPRITE_JUMP
            self.is_jumping = True
            self.velocity_y = self.JUMP_FORCE
            self.is_on_ground = False
            self.on_train = False
        elif new_state == State.SLIDING:
            self.current_sprite_index = AnimationConfig.SPRITE_SLIDE
            self.is_sliding = True

        return True

    def jump(self):
        if self.on_train:
            # jump off train
            # ensure base_y set to lane ground to allow normal jump physics
            self.base_y = LANE_POSITIONS_Y_JACK[self.current_lane]
            
        return self.change_state(State.JUMPING)

    def slide(self):
        return self.change_state(State.SLIDING)

    def toggle_pause(self):
        self.is_moving = not self.is_moving

    def apply_gravity(self):
        if self.is_on_ground:
            self.velocity_y = 0
        else:
            self.velocity_y += self.GRAVITY
            if self.velocity_y > self.MAX_FALL_SPEED:
                self.velocity_y = self.MAX_FALL_SPEED

        self.y += self.velocity_y

        if self.y >= self.base_y:
            self.y = self.base_y
            self.velocity_y = 0
            self.is_on_ground = True
            if self.state == State.JUMPING:
                self.change_state(State.RUNNING)
                
    # activate super jump            
    def super_jump(self):
        self.powerup_active = True
        self.JUMP_FORCE = self.SUPER_JUMP_FORCE
        
        self.powerup_end_time = millis() + 10000 # 10 seconds
    

    def _update_lane_movement(self):
        # If on train, SKIP the logic that pulls us to the ground lane
        if self.on_train:
            # Check if we ran off the end of the train
            if getattr(self.game, "last_train", None) is not None:
                train = self.game.last_train
                px = self.x
                buffer = 20
                
                # If player X is outside train width
                if px < train.x - buffer or px > train.x + train.w + buffer:
                    self.on_train = False
                    # Reset floor to real ground so we fall
                    self.base_y = LANE_POSITIONS_Y_JACK[self.current_lane]
            return 

        # Normal lane switching logic (only runs if NOT on train)
        target_y = LANE_POSITIONS_Y_JACK[self.target_lane]
        distance = target_y - self.base_y

        if abs(distance) > 2:
            self.velocity_x = distance * 0.3
            self.base_y += self.velocity_x
        else:
            self.base_y = target_y
            self.velocity_x = 0
            self.current_lane = self.target_lane

        if self.is_on_ground:
            self.y = self.base_y

    def _update_idle(self):
        pass

    def _update_running(self):
            self.animation_counter += 1
            if self.animation_counter >= AnimationConfig.RUN_ANIMATION_SPEED:
                self.animation_counter = 0
                self.run_frame_index = (self.run_frame_index + 1) % len(AnimationConfig.RUN_ANIMATION_FRAMES)
                self.current_sprite_index = AnimationConfig.RUN_ANIMATION_FRAMES[self.run_frame_index]

    def _update_jumping(self):
        self.apply_gravity()
        if self.state == State.JUMPING:
            self.current_sprite_index = AnimationConfig.SPRITE_JUMP

    def _update_sliding(self):
        if self.state_timer >= AnimationConfig.SLIDE_DURATION:
            self.change_state(State.RUNNING)

    def update(self):
        if not self.is_moving:
            return
        
        if self.powerup_active and millis() > self.powerup_end_time:
            self.powerup_active = False
            
        if not self.powerup_active:
            self.JUMP_FORCE = self.NORMAL_JUMP_FORCE

        self.state_timer += 1

        # If on_train
        if self.on_train:
            self.y = self.base_y
            self.is_on_ground = True
            self.velocity_y = 0
        
        if self.state == State.IDLE:
            self._update_idle()
        elif self.state == State.RUNNING:
            self._update_running()
        elif self.state == State.JUMPING:
            self._update_jumping()
        elif self.state == State.SLIDING:
            self._update_sliding()

        if self.is_moving:
            self._update_lane_movement()

    def _update_lane_movement(self):
        # If on train, SKIP the logic that pulls us to the ground lane
        if self.on_train:
            # Check if we ran off the end of the train
            if getattr(self.game, "last_train", None) is not None:
                train = self.game.last_train
                px = self.x
                buffer = 20
                
                # If player X is outside train width
                if px < train.x - buffer or px > train.x + train.w + buffer:
                    self.on_train = False
                    # Reset floor to real ground so we fall
                    self.base_y = LANE_POSITIONS_Y_JACK[self.current_lane]
            return 

        # Normal lane switching logic (only runs if NOT on train)
        target_y = LANE_POSITIONS_Y_JACK[self.target_lane]
        distance = target_y - self.base_y

        if abs(distance) > 2:
            self.velocity_x = distance * 0.3
            self.base_y += self.velocity_x
        else:
            self.base_y = target_y
            self.velocity_x = 0
            self.current_lane = self.target_lane

        if self.is_on_ground:
            self.y = self.base_y

    def draw(self):
        # drawing uses CENTER translate style in your engine — leave as-is
        if self.sprite_sheet:
            sheet_width = self.sprite_sheet.width
            sheet_height = self.sprite_sheet.height

            if AnimationConfig.SPRITE_COORDINATES is not None:
                coords = AnimationConfig.SPRITE_COORDINATES[self.current_sprite_index]
                if len(coords) == 2:
                    frame_x, frame_width = coords
                    frame_y = 0
                    frame_height = sheet_height
                else:
                    frame_x, frame_y, frame_width, frame_height = coords
            else:
                frame_width = sheet_width // 5
                frame_x = self.current_sprite_index * frame_width
                frame_y = 0
                frame_height = sheet_height

            pushMatrix()
            imageMode(CENTER)
            translate(self.x, self.y)
            img_copy = self.sprite_sheet.get(frame_x, frame_y, frame_width, frame_height)
            image(img_copy, 0, 0, AnimationConfig.CHARACTER_WIDTH, AnimationConfig.CHARACTER_HEIGHT)
            imageMode(CORNER)
            popMatrix()
        else:
            fill(255, 100, 100)
            ellipse(self.x, self.y - 20, 40, 40)
            fill(100, 150, 255)
            rect(self.x - 10, self.y - 10, 20, 30)

    def switch_lane(self, direction):
        if not self.is_moving:
            return
        if direction == "up" and self.target_lane > 0:
            self.target_lane -= 1
        elif direction == "down" and self.target_lane < LANE_COUNT - 1:
            self.target_lane += 1

class Background:
    def __init__(self, background_img, bg_city_img, lanes_img):
        self.bg_scroll_speed = 1
        self.city_scroll_speed = 2
        self.track_scroll_speed = 5

        self.bg_segments = []
        self.city_segments = []
        self.track_segments = []

        self.background = background_img
        self.bg_city = bg_city_img
        self.lanes = lanes_img

        self.reset()

    def reset(self):
        self.bg_segments = [
            {"x": 0, "width": SCREEN_WIDTH},
            {"x": SCREEN_WIDTH, "width": SCREEN_WIDTH}
        ]
        self.city_segments = [
            {"x": 0, "width": SCREEN_WIDTH},
            {"x": SCREEN_WIDTH, "width": SCREEN_WIDTH}
        ]
        self.track_segments = [
            {"x": 0, "width": SCREEN_WIDTH},
            {"x": SCREEN_WIDTH, "width": SCREEN_WIDTH}
        ]

    def update(self, is_moving):
        if not is_moving:
            return

        for segment in self.bg_segments:
            segment["x"] -= self.bg_scroll_speed
        for segment in self.city_segments:
            segment["x"] -= self.city_scroll_speed
        for segment in self.track_segments:
            segment["x"] -= self.track_scroll_speed

        self.bg_segments = [s for s in self.bg_segments if s["x"] + s["width"] > -50]
        self.city_segments = [s for s in self.city_segments if s["x"] + s["width"] > -50]
        self.track_segments = [s for s in self.track_segments if s["x"] + s["width"] > -50]

        if len(self.bg_segments) > 0 and self.bg_segments[-1]["x"] + self.bg_segments[-1]["width"] < SCREEN_WIDTH + 50:
            self.bg_segments.append({
                "x": self.bg_segments[-1]["x"] + self.bg_segments[-1]["width"],
                "width": SCREEN_WIDTH
            })
        if len(self.city_segments) > 0 and self.city_segments[-1]["x"] + self.city_segments[-1]["width"] < SCREEN_WIDTH + 50:
            self.city_segments.append({
                "x": self.city_segments[-1]["x"] + self.city_segments[-1]["width"],
                "width": SCREEN_WIDTH
            })
        if len(self.track_segments) > 0 and self.track_segments[-1]["x"] + self.track_segments[-1]["width"] < SCREEN_WIDTH + 50:
            self.track_segments.append({
                "x": self.track_segments[-1]["x"] + self.track_segments[-1]["width"],
                "width": SCREEN_WIDTH
            })

    def draw(self):
        background(255)
        if self.background:
            for segment in self.bg_segments:
                image(self.background, segment["x"], 0)
        if self.bg_city:
            for segment in self.city_segments:
                image(self.bg_city, segment["x"], 0)
        if self.lanes:
            for segment in self.track_segments:
                image(self.lanes, segment["x"], 0)

class Obstacle:
    def __init__(self, x, game):
        self.game = game
        self.x = x
        self.num = random.randint(0, 2)
        self.sprite = self.game.OBSTACLE_SPRITES[self.num]

        self.src_x = self.sprite["x"]
        self.w = self.sprite["w"]
        self.h = self.sprite["h"]
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.y = LANE_POSITIONS_Y[self.lane] - self.h

        if self.num == 0:
            self.type = "fence"
        elif self.num == 1:
            self.type = "bush"
        else:
            self.type = "slide"

        self.img = self.game.obs
        self.speed = game.background.track_scroll_speed

    def update(self):
        self.x -= self.speed
        if self.x + self.w <= 0:
            if self.lane in self.game.taken_lanes:
                self.game.taken_lanes.remove(self.lane)
            if self in self.game.OBSTACLES:
                self.game.OBSTACLES.remove(self)

    def display(self):
        image(self.img, self.x, self.y, self.w, self.h, self.src_x, 0, self.src_x + self.w, self.h)

class Train:
    def __init__(self, x, game):
        self.game = game
        self.x = x
        self.num = random.randint(0, 2)
        self.sprite = self.game.TRAIN_SPRITES[self.num]

        self.src_x = self.sprite["x"]
        self.w = self.sprite["w"]
        self.h = self.sprite["h"]

        self.lane = random.randint(0, LANE_COUNT - 1)
        self.y = LANE_POSITIONS_Y[self.lane] - self.h

        self.type = ["train1", "train2", "train3"][self.num]

        self.img = self.game.train
        self.speed = game.background.track_scroll_speed + random.randint(1, 2)

    def update(self):
        self.x -= self.speed
        if self.x + self.w <= 0:
            if self.lane in self.game.taken_lanes:
                self.game.taken_lanes.remove(self.lane)
            if self in self.game.OBSTACLES:
                self.game.OBSTACLES.remove(self)

    def display(self):
        image(self.img, self.x, self.y, self.w, self.h,
              self.src_x + self.w, 0, self.src_x, self.h)

class Coin:
    def __init__(self, x, game):
        self.type = 'coin'
        self.x = x
        self.game = game
        self.img = self.game.coin_img
        self.slices = 4
        self.slice = 0
        self.speed = game.background.track_scroll_speed

        self.w = 30
        self.h = 30

        self.lane = random.randint(0, LANE_COUNT - 1)
        self.y = LANE_POSITIONS_Y[self.lane] - self.h

    def update_coin(self):
        self.x -= self.speed

    def display(self):
        if frameCount % 15 == 0:
            self.slice = (self.slice + 1) % self.slices
        src_x = self.slice * self.w
        image(self.img, self.x, self.y, self.w, self.h, src_x, 0, src_x + self.w, self.h)

class CoinRow:
    def __init__(self, x, lane, game):
        self.game = game
        self.x = x
        self.lane = lane
        self.coins = []
        self.coin_w = 30
        self.count = random.randint(4, 10)
        self.space = 50
        self.w = (self.count * self.coin_w) + (self.space * (self.count - 1))

        self.type = 'coinrow'
        self.speed = game.background.track_scroll_speed
        self.h = 30

        self.y = LANE_POSITIONS_Y[lane] - self.h

        for i in range(self.count):
            c = Coin(self.x + i * self.space, game)
            c.lane = lane
            c.y = self.y
            self.coins.append(c)

    def update(self):
        self.x -= self.speed
        for c in self.coins:
            c.update_coin()
            
        should_remove = False
        
        if len(self.coins) == 0:
            should_remove = True
        elif self.coins[-1].x + self.coins[-1].w < 0:
            should_remove = True
            
        if should_remove:      
            if self.lane in self.game.taken_lanes:
                self.game.taken_lanes.remove(self.lane)
            if self in self.game.COIN_ROWS:
                self.game.COIN_ROWS.remove(self)

    def display(self):
        for c in self.coins:
            c.display()


# CLASS POWER UPS: initializing, updating, displaying work for all powerups
# in order to implement flying has to work with other class and/or add it as function in this class
class PowerUP:
    def __init__(self, x, lane, game):
        self.game = game
        self.x = x
        self.lane = lane
        self.type = random.choice(['doublejump', 'flying'])
        if self.type == 'doublejump':
            self.sprite = self.game.POWERUPS_SPRITES[1]
        else:
            self.sprite = self.game.POWERUPS_SPRITES[0]
            
        self.img = self.game.powerups
        self.flag = False
        
        self.src_x = self.sprite["x"]
        self.w = self.sprite["w"]
        self.h = self.sprite["h"]
        
        self.speed = game.background.track_scroll_speed
        self.y = LANE_POSITIONS_Y[lane] - self.h
        
    def update(self):
        self.x -= self.speed
        
            
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h, self.src_x, 0, self.src_x + self.w, self.h)
            
        
class Game:
    def __init__(self):
        self.game_over = False
        self.score = 0

        # image loads
        
        jack_img = loadImage(PATH + "/images/jack_new.png") if os.path.exists(PATH + "/images/jack_new.png") else None
        background_img = loadImage(PATH + "/images/background.png") if os.path.exists(PATH + "/images/background.png") else None
        bg_city_img = loadImage(PATH + "/images/bg_city.png") if os.path.exists(PATH + "/images/bg_city.png") else None
        lanes_img = loadImage(PATH + "/images/lanes.png") if os.path.exists(PATH + "/images/lanes.png") else None

        self.player = Player(jack_img, self)
        self.background = Background(background_img, bg_city_img, lanes_img)

        self.train = loadImage(PATH + '/images/trains.png') if os.path.exists(PATH + '/images/trains.png') else None
        self.obs = loadImage(PATH + '/images/obstacles.png') if os.path.exists(PATH + '/images/obstacles.png') else None
        self.coin_img = loadImage(PATH + '/images/coins.png') if os.path.exists(PATH + '/images/coins.png') else None
        self.powerups = loadImage(PATH + '/images/powerups.png') 
        
        # sounds 
        self.bg_sound = player.loadFile(PATH + '/sounds/bg_sound.mp3') 
        self.death_sound = player.loadFile(PATH + '/sounds/death_sound.mp3') 
        self.coin_sound = player.loadFile(PATH + '/sounds/coin.mp3')
        self.power_sound = player.loadFile(PATH + '/sounds/powerUp.mp3') 
        self.bg_sound.loop()

        self.OBSTACLES = []
        self.COIN_ROWS = []
        self.POWER_UPS = []
        self.taken_lanes = set()

        self.last_train = None
        self.powerups_count = 0

        self.OBSTACLE_SPRITES = [
            {"x": 0,   "w": 107, "h": 100},  # fence
            {"x": 124, "w": 94,  "h": 100},  # bush
            {"x": 229, "w": 136, "h": 100},  # slide barrier
        ]

        self.TRAIN_SPRITES = [
            {"x": 0,   "w": 276, "h": 134},
            {"x": 284, "w": 275, "h": 134},
            {"x": 566, "w": 314, "h": 134},
        ]
        
        self.POWERUPS_SPRITES = [
            {"x": 0,   "w": 57, "h": 51},
            {"x": 57, "w": 43, "h": 51},
        ]

    def check_player(self, obj):
        # ignore different lanes
        if obj.lane not in (self.player.current_lane, self.player.target_lane):
            return False

        padding = 15
        p_left = self.player.x - self.player.sprite_width/2 + padding
        p_right = self.player.x + self.player.sprite_width/2 - padding
        p_top = self.player.y - self.player.sprite_height/2 + padding
        p_bottom = self.player.y + self.player.sprite_height/2 - padding

        # coins: collect, but not lethal
        if getattr(obj, "type", None) in ("coin", "coinrow"):
            return (p_left < obj.x + obj.w and
                    p_right > obj.x and
                    p_top < obj.y + obj.h and
                    p_bottom > obj.y)
        #powerups: collect and use
        if obj.type in ('flying', 'doublejump'):
            return (p_left < obj.x + obj.w and
                    p_right > obj.x and
                    p_top < obj.y + obj.h and
                    p_bottom > obj.y)
            
        # trains:
        if "train" in getattr(obj, "type", ""):
            feet = p_bottom
            train_top = obj.y
            train_left = obj.x
            train_right = obj.x + obj.w

            # 1. Check if we are jumping OUT of the train
            # If colliding but moving UP, we are jumping off. Safe.
            is_touching = (p_left < train_right and p_right > train_left and 
                           p_top < obj.y + obj.h and p_bottom > obj.y)
            
            if is_touching and self.player.velocity_y < 0:
                return False

            # 2. Check Landing
            horizontally_over = (p_right > train_left and p_left < train_right)
            falling_down = self.player.velocity_y >= 0
            # Allow feet to be slightly below top (tolerance)
            within_landing = (feet >= train_top - 5 and feet <= train_top + 5)

            if horizontally_over and falling_down and within_landing:
                self.player.on_train = True
                self.player.is_on_ground = True
                self.player.velocity_y = 0
                
                # --- VISUAL FIX ---
                # Lift base_y by half height (30px) so feet sit ON top, not waist.
                self.player.base_y = train_top - 30
                self.player.y = self.player.base_y 
                
                self.last_train = obj
                return False

            # If we are already riding this train, ignore collision
            if self.player.on_train:
                return False

        # --- GENERAL COLLISION (Death) ---
        is_colliding = (p_left < obj.x + obj.w and
                        p_right > obj.x and
                        p_top < obj.y + obj.h and
                        p_bottom > obj.y)

        if not is_colliding:
            return False

        # Avoidance logic
        if obj.type in ("fence", "bush"):
            if self.player.is_jumping and not self.player.is_on_ground:
                return False

        if obj.type == "slide":
            if self.player.is_sliding:
                return False

        return True

    def check_collision(self, rect1, rect2):
        return (rect1.x < rect2.x + rect2.w and
                rect1.x + rect1.w > rect2.x and
                rect1.y < rect2.y + rect2.h and
                rect1.y + rect1.h > rect2.y)

    def is_space_free(self, new_obj, other_list, is_coin_check=False):
        MIN_DIST = 200
        TRAIN_BUFFER = 800
        SLIDE_BUFFER = 350
        COIN_BUFFER = 100

        for other in other_list:
            if new_obj.lane != other.lane:
                continue

            # collision check
            if self.check_collision(new_obj, other):
                return False

            if new_obj.x < other.x:
                left, right = new_obj, other
            else:
                left, right = other, new_obj

            distance = right.x - (left.x + left.w)

            required_gap = MIN_DIST

            if is_coin_check or other.type == 'coinrow' or new_obj.type == 'coinrow':
                required_gap = COIN_BUFFER
            elif "train" in new_obj.type or "train" in other.type:
                required_gap = TRAIN_BUFFER
                if left.speed > right.speed:
                    required_gap += 600
            elif new_obj.type == "slide" and other.type == "slide":
                required_gap = SLIDE_BUFFER

            if distance < required_gap:
                return False

        return True

    def spawn_obstacle(self):
        blocked_lanes = set()
        for ob in self.OBSTACLES:
            if ob.x > SCREEN_WIDTH - 200:
                blocked_lanes.add(ob.lane)
        no_spawn_lane = len(blocked_lanes)>=2
        
        # Normal random spawner with safe checks
        attempts = 8
        for _ in range(attempts):
            start_x = random.randint(SCREEN_WIDTH + 200, SCREEN_WIDTH + 1000)
            #skip the lane if other lanes are already blocked
            if no_spawn_lane:
                return
            
            if random.random() < 0.4:
                new_obj = Train(start_x, self)
            else:
                new_obj = Obstacle(start_x, self)
                
            if new_obj.lane not in blocked_lanes and len(blocked_lanes)>=2:
                continue 

            if not self.is_space_free(new_obj, self.OBSTACLES):
                continue
            if not self.is_space_free(new_obj, self.COIN_ROWS):
                continue
            if not self.is_space_free(new_obj, self.POWER_UPS):
                continue


            self.OBSTACLES.append(new_obj)
            self.taken_lanes.add(new_obj.lane)
            return

        # if failed, do nothing this tick

    def spawn_coinrow(self):
        attempts = 6
        for _ in range(attempts):
            lane = random.randint(0, LANE_COUNT - 1)
            start_x = random.randint(SCREEN_WIDTH + 200, SCREEN_WIDTH + 800)

            new_row = CoinRow(start_x, lane, self)

            if not self.is_space_free(new_row, self.OBSTACLES, is_coin_check=True):
                continue
            if not self.is_space_free(new_row, self.COIN_ROWS, is_coin_check=True):
                continue
            if not self.is_space_free(new_row, self.POWER_UPS, is_coin_check=True):
                continue

            self.COIN_ROWS.append(new_row)
            self.taken_lanes.add(new_row.lane)
  
            return
        
    def spawn_powerup(self):
        if random.random() < 0.005: # 0.5% chance per frame
            attempts = 3
            for _ in range(attempts):
                lane = random.randint(0, LANE_COUNT - 1)
                start_x = random.randint(SCREEN_WIDTH + 200, SCREEN_WIDTH + 800)

                new_pu = PowerUP(start_x, lane, self)
                
                # Check against Obstacles Aand trains
                if not self.is_space_free(new_pu, self.OBSTACLES):
                    continue
                
                # Check against Coins
                if not self.is_space_free(new_pu, self.COIN_ROWS):
                    continue
                
                # Check against other Powerups
                if not self.is_space_free(new_pu, self.POWER_UPS):
                    continue

                self.POWER_UPS.append(new_pu)
                return

    def update(self):
        self.background.update(self.player.is_moving)
        self.player.update()

        # check obstacles near player
        for obs in list(self.OBSTACLES):  # iterate copy because may remove
            # optimize lane check
            if obs.lane != self.player.current_lane and obs.lane != self.player.target_lane and abs(self.player.target_lane - self.player.current_lane) != 1:
                continue
            if self.check_player(obs):
                self.game_over = True
                self.bg_sound.pause()
                self.death_sound.rewind()
                self.death_sound.play()
                break

        # coins collection
        for cr in list(self.COIN_ROWS):
            for co in list(cr.coins):
                if self.check_player(co):
                    try:
                        cr.coins.remove(co)
                    except ValueError:
                        pass
                    self.score += 1
                    self.coin_sound.rewind()
                    self.coin_sound.play()
                        
        # power-ups collection
        for pu in list(self.POWER_UPS):            
            if pu.x + pu.w <0:
                self.POWER_UPS.remove(pu)
                continue
            
            if self.check_player(pu):
                self.power_sound.rewind()
                self.power_sound.play()
                if pu.type == 'doublejump':
                    self.player.super_jump()
                if pu in self.POWER_UPS:
                    self.POWER_UPS.remove(pu)

        # spawn/maintain obstacles
        if len(self.OBSTACLES) < 6:
            self.spawn_obstacle()
        for o in list(self.OBSTACLES):
            o.update()

        # spawn/maintain coin rows
        if len(self.COIN_ROWS) < 3:
            self.spawn_coinrow()
        for row in list(self.COIN_ROWS):
            row.update()
        
        # spawn/maintain power ups    
        if len(self.POWER_UPS) < 1:
            self.spawn_powerup()
        for pu in list(self.POWER_UPS):
            pu.update()

    def display(self):
        self.background.draw()
        
        for row in self.COIN_ROWS:
            row.display()
        
        self.OBSTACLES.sort(key=lambda obj: obj.y)    
        self.POWER_UPS.sort(key=lambda pu: pu.y)       
        all_objects = self.POWER_UPS + self.OBSTACLES
        
        for smth in all_objects:
            if smth.lane <= self.player.current_lane:
                smth.display()
                
        self.player.draw()
        
        for smth in all_objects:
            if smth.lane > self.player.current_lane:
                smth.display()
            
        
        
        if self.game_over:
            noLoop()
            fill(0, 0, 0, 150)
            noStroke()
            rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            textSize(32)
            fill(255, 255, 255)
            textAlign(CENTER, CENTER)
            text('GAME OVER', SCREEN_WIDTH/2, SCREEN_HEIGHT/2-30)
            textSize(24)
            text('Score:' + ' ' + str(self.score), SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)
            textSize(16)
            text('Click to restart', SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 70)
        else:
            padding = 10
            box_width = 80 + 8 * len(str(self.score))
            box_height = 50
            box_x = SCREEN_WIDTH - box_width - 20
            box_y = 15
            
            # tint to see when the powerup is active
            if self.player.powerup_active:
                tint(0, 160, 50)
            else:
                noTint()
            fill(255, 255, 255, 200)
            noStroke()
            rect(box_x, box_y, box_width, box_height, 10)

            if self.coin_img:
                image(self.coin_img, box_x + 10, box_y + 10, 30, 30, 0, 0, 30, 30)

            fill(0)
            textSize(24)
            textAlign(LEFT, CENTER)
            text(str(self.score), box_x + 50, box_y + (box_height/2) - 3)

# global game
game = None

def setup():
    global game
    size(SCREEN_WIDTH, SCREEN_HEIGHT)
    frameRate(60)
    game = Game()

def draw():
    game.update()
    game.display()

def keyPressed():
    if key == CODED:
        if keyCode == UP:
            game.player.switch_lane("up")
        elif keyCode == DOWN:
            game.player.switch_lane("down")
        elif keyCode == CONTROL or keyCode == 17:
            game.player.slide()
    elif key == ' ':
        game.player.jump()

def mousePressed():
    global game
    if game.game_over:
        game.bg_sound.close()
        game.death_sound.close()
        game.coin_sound.close()
        game.power_sound.close()
        game = Game()
        loop()
