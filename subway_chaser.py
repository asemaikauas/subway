SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
LANE_COUNT = 3

# fixed on left-center
PLAYER_X = 250

LANE_POSITIONS_Y = [
    380,  # up
    518,  # mid
    645   # down
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
    def __init__(self, bg_city_img, lanes_img):
        self.scroll_speed = 4
        self.city_scroll_speed = 2

        self.city_segments = []
        self.track_segments = []

        self.bg_city = bg_city_img
        self.lanes = lanes_img

        self.reset()

    def reset(self):
        self.city_segments = [
            {"x": 0, "width": SCREEN_WIDTH},
            {"x": SCREEN_WIDTH, "width": SCREEN_WIDTH}
        ]
        self.track_segments = [
            {"x": 0, "width": SCREEN_WIDTH},
            {"x": SCREEN_WIDTH, "width": SCREEN_WIDTH}
        ]

    def update(self):
        if not player.is_moving:
            return

        for segment in self.city_segments:
            segment["x"] -= self.city_scroll_speed

        for segment in self.track_segments:
            segment["x"] -= self.scroll_speed

        self.city_segments = [s for s in self.city_segments if s["x"] + s["width"] > -50]
        self.track_segments = [s for s in self.track_segments if s["x"] + s["width"] > -50]

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
        
        if self.bg_city:
            for segment in self.city_segments:
                image(self.bg_city, segment["x"], 0)

        if self.lanes:
            for segment in self.track_segments:
                image(self.lanes, segment["x"], 0)



def setup():
    global player, bg
    global jack_img, bg_city_img, background_img, lanes_img
    
    size(SCREEN_WIDTH, SCREEN_HEIGHT)
    frameRate(60)
    
   
    jack_img = loadImage("jack.png")
    bg_city_img = loadImage("bg_city.png")
    background_img = loadImage("background.png")
    lanes_img = loadImage("lanes.png")
    
    player = Player(jack_img)
    bg = Background(bg_city_img, lanes_img)

def draw():
    global player, bg

    bg.update()
    player.update()

    bg.draw()
    player.draw()

 
def keyPressed():
    global player
    if key == CODED:
        if keyCode == UP:
            player.switch_lane("up")
        elif keyCode == DOWN:
            player.switch_lane("down")
    elif key == ' ':
        player.toggle_pause()