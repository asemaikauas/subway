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

class Player:
    def __init__(self, sprite_img):
        self.x = PLAYER_X
        self.y = LANE_POSITIONS_Y[1]
        self.target_lane = 1
        self.current_lane = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed_y = 15
        self.is_moving = True

        self.sprite_sheet = sprite_img
        self.sprite_width = 32
        self.sprite_height = 32
        self.current_frame = 1
        self.animation_counter = 0
        self.animation_speed = 5

    def update(self):
        if not self.is_moving:
            return

        target_y = LANE_POSITIONS_Y[self.target_lane]
        distance = target_y - self.y

        if abs(distance) > 2:
            self.velocity_y = distance * 0.3
            self.y += self.velocity_y
        else:
            self.y = target_y
            self.velocity_y = 0
            self.current_lane = self.target_lane

        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame += 1
            if self.current_frame > 3:
                self.current_frame = 1

    def draw(self):
        if self.sprite_sheet:
            sheet_width = self.sprite_sheet.width
            sheet_height = self.sprite_sheet.height
            frame_width = sheet_width / 5
            
            frame_x = self.current_frame * frame_width
            
            pushMatrix()
            imageMode(CENTER)
            translate(self.x, self.y)
            
            img_copy = self.sprite_sheet.get(int(frame_x), 0, int(frame_width), int(sheet_height))
            image(img_copy, 0, 0, 60, 60)
            
            imageMode(CORNER)
            popMatrix()
        else:
            fill(255, 100, 100)
            ellipse(self.x, self.y - 20, 40, 40)
            fill(100, 150, 255)
            rect(self.x - 10, self.y - 10, 20, 30)

    def switch_lane(self, direction):
        if direction == "up" and self.target_lane > 0:
            self.target_lane -= 1
        elif direction == "down" and self.target_lane < LANE_COUNT - 1:
            self.target_lane += 1

    def toggle_pause(self):
        self.is_moving = not self.is_moving

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

        # Update far background layer (slowest)
        for segment in self.bg_segments:
            segment["x"] -= self.bg_scroll_speed

        # Update city layer (medium speed)
        for segment in self.city_segments:
            segment["x"] -= self.city_scroll_speed

        # Update track layer (fastest)
        for segment in self.track_segments:
            segment["x"] -= self.track_scroll_speed

        # Remove off-screen segments and add new ones for seamless scrolling
        self.bg_segments = [s for s in self.bg_segments if s["x"] + s["width"] > -50]
        self.city_segments = [s for s in self.city_segments if s["x"] + s["width"] > -50]
        self.track_segments = [s for s in self.track_segments if s["x"] + s["width"] > -50]

        # Add new segments when needed
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
        
        # Draw layers from back to front for parallax effect
        # Layer 1: Far background (slowest)
        if self.background:
            for segment in self.bg_segments:
                image(self.background, segment["x"], 0)
        
        # Layer 2: City buildings (medium speed)
        if self.bg_city:
            for segment in self.city_segments:
                image(self.bg_city, segment["x"], 0)

        # Layer 3: Track/lanes (fastest)
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
    
    def handle_key(self, key_code, is_coded, is_space):
        if is_coded:
            if key_code == UP:
                self.player.switch_lane("up")
            elif key_code == DOWN:
                self.player.switch_lane("down")
        elif is_space:
            self.player.toggle_pause()

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
    elif key == ' ':
        game.player.toggle_pause()
