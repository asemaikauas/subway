import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
LANE_COUNT = 3
PATH = os.getcwd()

# fixed on left-center
PLAYER_X = 250

LANE_POSITIONS_Y = [
    390,  # up
    518,  # mid
    635   # down
]

class AnimationConfig:

    
    SPRITE_IDLE = 0      
    SPRITE_SLIDE = 1     
    SPRITE_RUN = 2       
    SPRITE_JUMP = 3     
    SPRITE_FLY = 4    


    JUMP_DURATION = 40        
    SLIDE_DURATION = 40      
    
    JUMP_HEIGHT = 80          # vertical jump distance in pixels
    
    #  ADDD multiple frames
    # for example a list of [2, 2, 3, 3]  
    RUN_ANIMATION_FRAMES = [SPRITE_RUN]  
    
    RUN_ANIMATION_SPEED = 10   # higher = slower animation, lower = faster
                               # 10 frames = sprite changes every 0.16 seconds
    
    CHARACTER_WIDTH = 51       # character width in pxs
    CHARACTER_HEIGHT = 60      # character height in pxs


class State:
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    JUMPING = "JUMPING"
    SLIDING = "SLIDING"

class Player:
    def __init__(self, sprite_img):
        self.x = PLAYER_X
        self.y = LANE_POSITIONS_Y[1]
        self.base_y = LANE_POSITIONS_Y[1]  # for jump calculations
        self.target_lane = 1
        self.current_lane = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed_y = 15
        
        self.game_started = False  
        self.is_moving = False     
        
        self.sprite_sheet = sprite_img
        self.sprite_width = 32
        self.sprite_height = 32
        
        self.state = State.IDLE
        self.current_sprite_index = AnimationConfig.SPRITE_IDLE
        
        self.state_timer = 0         
        self.animation_counter = 0     
        self.run_frame_index = 0       
        
        self.jump_start_y = 0
        self.is_jumping = False
        
        self.is_sliding = False
    
    def start_game(self):
        if not self.game_started:
            self.game_started = True
            self.is_moving = True
            self.change_state(State.RUNNING)

    
    def change_state(self, new_state):
        if self.state == new_state:
            return False
        
        if new_state == State.JUMPING:
            if self.state != State.RUNNING:
                return False  
        
        if new_state == State.SLIDING:
            if self.state != State.RUNNING:
                return False  
        
        if self.state == State.JUMPING:
            self.is_jumping = False
        elif self.state == State.SLIDING:
            self.is_sliding = False
        
        self.state = new_state
        self.state_timer = 0
        
        if new_state == State.IDLE:
            self.current_sprite_index = AnimationConfig.SPRITE_IDLE
        elif new_state == State.RUNNING:
            self.current_sprite_index = AnimationConfig.SPRITE_RUN
            self.run_frame_index = 0
        elif new_state == State.JUMPING:
            self.current_sprite_index = AnimationConfig.SPRITE_JUMP
            self.is_jumping = True
            self.jump_start_y = self.base_y
        elif new_state == State.SLIDING:
            self.current_sprite_index = AnimationConfig.SPRITE_SLIDE
            self.is_sliding = True
        
        return True
    
    def jump(self):
        return self.change_state(State.JUMPING)
    
    def slide(self):
        return self.change_state(State.SLIDING)
    
    def update(self):
        self.state_timer += 1
        
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
    
    def _update_idle(self):
        pass
    
    def _update_running(self):
        # please Update logic for running state"""
        if len(AnimationConfig.RUN_ANIMATION_FRAMES) > 1:
            self.animation_counter += 1
            if self.animation_counter >= AnimationConfig.RUN_ANIMATION_SPEED:
                self.animation_counter = 0
                self.run_frame_index = (self.run_frame_index + 1) % len(AnimationConfig.RUN_ANIMATION_FRAMES)
                self.current_sprite_index = AnimationConfig.RUN_ANIMATION_FRAMES[self.run_frame_index]
    
    def _update_jumping(self):
        progress = float(self.state_timer) / AnimationConfig.JUMP_DURATION
        
        if progress >= 1.0:
            self.y = self.base_y
            self.change_state(State.RUNNING)
            return
        
        jump_offset = sin(progress * PI) * AnimationConfig.JUMP_HEIGHT
        
        self.y = self.base_y - jump_offset
    
    def _update_sliding(self):
        if self.state_timer >= AnimationConfig.SLIDE_DURATION:
            self.change_state(State.RUNNING)
    
    def _update_lane_movement(self):
        target_y = LANE_POSITIONS_Y[self.target_lane]
        distance = target_y - self.base_y
        
        if abs(distance) > 2:
            self.velocity_y = distance * 0.3
            self.base_y += self.velocity_y
        else:
            self.base_y = target_y
            self.velocity_y = 0
            self.current_lane = self.target_lane
        
        # If not jumping, sync display Y with base Y
        if self.state != State.JUMPING:
            self.y = self.base_y
    
    def draw(self):
        if self.sprite_sheet:
            sheet_width = self.sprite_sheet.width
            sheet_height = self.sprite_sheet.height
            frame_width = sheet_width / 5
            
            frame_x = self.current_sprite_index * frame_width
            
            pushMatrix()
            imageMode(CENTER)
            translate(self.x, self.y)
            
            img_copy = self.sprite_sheet.get(int(frame_x), 0, int(frame_width), int(sheet_height))
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
        self.track_scroll_speed = 4     

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

class Game:
    def __init__(self):
        jack_img = loadImage(PATH + "/jack.png")
        background_img = loadImage(PATH + "/background.png")
        bg_city_img = loadImage(PATH + "/bg_city.png")
        lanes_img = loadImage(PATH + "/lanes.png")
        
        self.player = Player(jack_img)
        self.background = Background(background_img, bg_city_img, lanes_img)
    
    def update(self):
        self.background.update(self.player.is_moving)
        self.player.update()
    
    def display(self):
        self.background.draw()
        self.player.draw()
    
    def mouse_click(self):
        self.player.start_game()
    
    def key_press(self):
        if key == CODED:
            if keyCode == UP:
                self.player.switch_lane("up")
            elif keyCode == DOWN:
                self.player.switch_lane("down")
            # Slide (Control key)
            elif keyCode == CONTROL:
                if self.player.game_started:
                    self.player.slide()
        
        elif key == ' ':
            if self.player.game_started:
                self.player.jump()

def setup():
    global game
    size(SCREEN_WIDTH, SCREEN_HEIGHT)
    frameRate(60)
    game = Game()

def draw():
    game.update()
    game.display()

def keyPressed():
    game.key_press()

def mousePressed():
    game.mouse_click()
