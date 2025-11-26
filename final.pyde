import os
import random

PATH = os.getcwd()

#coins: generate randomly on lanes -- MUST NOT collide with other objects
#self.OBSTACLES: genrate randomly and not too close to each other:
#trains can be one after another but at least one lane should be free
#self.OBSTACLES jump: add some space between
#self.OBSTACLES slide: can't be one after another
#not a single obstacle can be right after or right before the train


#assume game_shift is game_shift
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
LANE_COUNT = 3
PATH = os.getcwd()

# fixed on left-center
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


class Player:
    def __init__(self, sprite_img):
        self.sprite_sheet = sprite_img
        self.sprite_width = 32
        self.sprite_height = 32
        self.current_frame = 1
        self.animation_counter = 0
        self.animation_speed = 5
        
        self.x = PLAYER_X
        self.y = LANE_POSITIONS_Y_JACK[1] - self.sprite_height
        self.target_lane = 1
        self.current_lane = 1
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed_y = 15
        self.is_moving = True

        

    def update(self):
        if not self.is_moving:
            return

        target_y = LANE_POSITIONS_Y_JACK[self.target_lane]
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

class Obstacle:
    def __init__(self, x, game):
        self.game = game
        self.x = x
        # pick sprite frame
        self.num = random.randint(0, 2)
        self.sprite = self.game.OBSTACLE_SPRITES[self.num]

        self.src_x = self.sprite["x"]
        self.w = self.sprite["w"]
        self.h = self.sprite["h"]
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.y = LANE_POSITIONS_Y[self.lane]-self.h

        

        # type rules
        if self.num == 0:
            self.type = "fence"
        elif self.num == 1:
            self.type = "bush"
        else:
            self.type = "slide"

        self.img = self.game.obs
        self.speed = game.background.track_scroll_speed
        
            
    def update(self):
        #move all objects with fixed speed, remove if are off screen already
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

        # pick sprite frame
        self.num = random.randint(0, 2)
        self.sprite = self.game.TRAIN_SPRITES[self.num]

        self.src_x = self.sprite["x"]
        self.w = self.sprite["w"]
        self.h = self.sprite["h"]

        self.lane = random.randint(0, LANE_COUNT - 1)
        self.y = LANE_POSITIONS_Y[self.lane] - self.h

        self.type = ["train1", "train2", "train3"][self.num]

        self.img = self.game.train
        self.speed = game.background.track_scroll_speed + 2

        

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
        #mario logic for constant animation
        #free_check from game to spawn so only spawn method is required + score tracking in UI
        
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
        self.count = random.randint(4, 10) # 4-10 coins
        self.space = 50 # distance between coins insid rows
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
        #if the row is fully off-screen --> remove
        if self.coins[-1].x + self.coins[-1].w < 0:
            if self.lane in self.game.taken_lanes:
               self.game.taken_lanes.remove(self.lane)
            self.game.COIN_ROWS.remove(self)

                
            
    def display(self):
        for c in self.coins:
            c.display()
            
            
class Game:
    def __init__(self):
        jack_img = loadImage(PATH + "/images/jack.png")
        background_img = loadImage(PATH + "/images/background.png")
        bg_city_img = loadImage(PATH + "/images/bg_city.png")
        lanes_img = loadImage(PATH + "/images/lanes.png")
        
        self.player = Player(jack_img)
        self.background = Background(background_img, bg_city_img, lanes_img)
        self.score = 0
        self.train = loadImage(PATH+'/images/trains.png')
        self.obs = loadImage(PATH+'/images/obstacles.png')
        self.coin_img = loadImage(PATH+'/images/coins.png')
        self.OBSTACLES = []
        self.COIN_ROWS = []
        self.taken_lanes = set()
        self.OBSTACLE_SPRITES = [
            {"x": 0,   "w": 107, "h": 100},  # fence
            {"x": 124, "w": 94,  "h": 100},  # bush
            {"x": 229, "w": 136, "h": 100}, # slide
        ]
        self.TRAIN_SPRITES = [
            {"x": 0,   "w": 307, "h": 149},   # train1
            {"x": 312, "w": 305, "h": 149},   # train2
            {"x": 620, "w": 314, "h": 149},   # train3
        ]


    def check_collision(self, rect1, rect2):
        # returns True if two rectangles (objects) touch
        return (rect1.x < rect2.x + rect2.w and
                rect1.x + rect1.w > rect2.x and
                rect1.y < rect2.y + rect2.h and
                rect1.y + rect1.h > rect2.y)

    def is_space_free(self, new_obj, other_list, is_coin_check=False):
        # check if enough space on the specific lane
        # Distances
        MIN_DIST = 200        # Standard gap
        TRAIN_BUFFER = 600    # Trains gap
        SLIDE_BUFFER = 350    # Slides need landing room
        COIN_BUFFER = 100     # Gap between coins and objects
        
        for other in other_list:
            # lane check
            if new_obj.lane != other.lane:
                continue

            # actual collision
            if self.check_collision(new_obj, other):
                return False

            # gap check according to distance rules
            #distance from the right edge of left obj to left edge of right obj

            if new_obj.x < other.x:
                left, right = new_obj, other
            else:
                left, right = other, new_obj
            
            distance = right.x - (left.x + left.w)

            # Determine required gap based on types
            required_gap = MIN_DIST

            # prevent spawn inside or too close to coins
            if is_coin_check or other.type == 'coinrow' or new_obj.type == 'coinrow':
                 required_gap = COIN_BUFFER

            # train gap
            elif "train" in new_obj.type or "train" in other.type:
                required_gap = TRAIN_BUFFER
                
                # speed check:
                # If the item on the LEFT is train, then need a bigger gap to prevent crash
                if left.speed > right.speed:
                    required_gap += 400 

            # slides gap
            elif new_obj.type == "slide" and other.type == "slide":
                required_gap = SLIDE_BUFFER

            if distance < required_gap:
                return False

        return True

    def spawn_obstacle(self):
        for _ in range(10): # try 10 times to find valid position
            start_x = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 800)
            
            # choose type
            if random.random() < 0.4: 
                new_obj = Train(start_x, self)
            else:
                new_obj = Obstacle(start_x, self)

            # check obs against obs
            if not self.is_space_free(new_obj, self.OBSTACLES):
                continue # Try loop again
            
            # check obs against coinrows
            if not self.is_space_free(new_obj, self.COIN_ROWS):
                continue 

            self.OBSTACLES.append(new_obj)
            self.taken_lanes.add(new_obj.lane)
            return

    def spawn_coinrow(self):
        for _ in range(6):
            lane = random.randint(0, LANE_COUNT - 1)
            start_x = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 800)
            
            new_row = CoinRow(start_x, lane, self)

            # check coinrow against obs
            if not self.is_space_free(new_row, self.OBSTACLES, is_coin_check=True):
                continue
            
            # check coinrow against coinrows
            if not self.is_space_free(new_row, self.COIN_ROWS, is_coin_check=True):
                continue

            self.COIN_ROWS.append(new_row)
            self.taken_lanes.add(new_row.lane)
            return
                
    def update(self):
        self.background.update(self.player.is_moving)
        self.player.update()
        # always have 6 obstacles
        if len(self.OBSTACLES) < 6:
            self.spawn_obstacle()
        for o in self.OBSTACLES:
            o.update()
        
        # always have 3 coin rows
        if len(self.COIN_ROWS) < 3:
            self.spawn_coinrow()
        for row in self.COIN_ROWS:
            row.update()
            
    def display(self):
        self.background.draw()
        self.player.draw()
        for row in self.COIN_ROWS:
            row.display()
        #objects should be higher than coins and if anything --> cover them
        self.OBSTACLES.sort(key=lambda obj: obj.y)
        for obj in self.OBSTACLES:
            obj.display()
        
        
        
    def handle_key(self, key_code, is_coded, is_space):
        if is_coded:
            if key_code == UP:
                self.player.switch_lane("up")
            elif key_code == DOWN:
                self.player.switch_lane("down")
        elif is_space:
            self.player.toggle_pause()
            
game = Game()

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
    
