import pygame
import os
import random
pygame.init()

DOCU_ROOT = 'C:\\Users\\Sasha\\Documents\\NCSS\\Trivia\\scoreboard'
SUPPORTED_AUDIO_FILES = ['.mp3', '.wav', '.ogg']
WIDTH = 920
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
NO_OF_TEAMS = 7 # teams from 1 to this number
PLACE_EXTENSIONS = ['st', 'nd', 'rd', 'th']
#pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

ITEM_NAMES = ["coin"] * 5 + ["banana"] * 3 + ["mushroom"] * 2 + ["greenshell"] * 3 + ["redshell"] * 2 + ["feather"] * 1 + ["lightning"] * 2 + ["star"] * 1

# some dimensions (paddingX, paddingY, startX, startY, [endX, endY])
class Area:
    def __init__(self, paddingX, paddingY, startX, startY, endX=None, endY=None):
        self.padding_x = paddingX
        self.padding_y = paddingY
        self.start_x = startX
        self.start_y = startY
        self.end_x = endX
        self.end_y = endY
       
RACE_AREA = Area(0, 40, 77, 195)
CONTAINER_AREA = Area(0, 0, 0, 185, WIDTH, 480)
TRACK_LENGTH = 736
MAX_SCORE = 200
#JUMP_SIZE = (float(TRACK_LENGTH) / MAX_SCORE) * 1
JUMP_SIZE = 1
SHAKING_MAGNITUDE = 3 # how wide the team numbers shake

def xload(img_name):
    """Loads an image with a transparent background."""
    image = pygame.image.load(DOCU_ROOT + os.sep + 'images' + os.sep + img_name).convert()
    image.set_colorkey(image.get_at((0, 0)))
    return image

def load(img_name):
    """Loads a regular image."""
    image = pygame.image.load(DOCU_ROOT + os.sep + 'images' + os.sep + img_name).convert()
    return image

def play(music_name):
    """Stops all music, and plays a given sound from the sfx folder."""
    pygame.mixer.music.load(sounds[music_name])
    pygame.mixer.music.play()

def fadeout():
    """Fades out the currently playing track."""
    pygame.mixer.music.fadeout(1000)
    
def stop():
    """Stops the currently playing track."""
    pygame.mixer.music.stop()
    
def xplay(music_name):
    """Stops all music, and plays a given sound from the sfx folder on loop."""
    pygame.mixer.music.load(sounds[music_name])
    pygame.mixer.music.play(-1)
    
def tile(image, start_x, start_y, end_x, end_y):
    y_gap = image.get_height()
    x_gap = image.get_width()
    
    for x in range(start_x, end_x, x_gap):
        for y in range(start_y, end_y, y_gap):
            screen.blit(image, (x, y))
    
def draw_bg(background_image):
    tile(background_image, 0, 0, WIDTH, HEIGHT)
    
def load_scores():
    scores_file = open("scores.txt")
    scores = {}
    for line in scores_file:
        try:
            parts = line.split()
            team_no = int(parts[0])
            team_name = parts[1]
            team_score = max(0, sum(int(x) for x in parts[2:]))
            
            # only load valid team numbers
            if team_no in range(1, NO_OF_TEAMS + 1):
                # load the image
                team_image = xload(team_name + ".png")
                team_no_image = xload("group_%s.png" % team_no)
                
                scores[team_no] = [team_name, team_image, team_no_image, team_score] # the last entry is the item
        except Exception, e:
            print "Error when loading scores: %s" % e
    return scores

def load_numbers():
    numbers = {}
    for i in range(10):
        numbers[i] = xload("group_%s.png" % i)
        
    for ext in PLACE_EXTENSIONS:
        numbers[ext] = xload(ext + '.png')
    return numbers
    
def load_items():
    items = []
    for item in ITEM_NAMES:
        items.append(xload("item_" + item + ".png"))
    return items
    
def load_music():
    """Loads all MP3 files in the music directory."""
    music = []
    for filename in [x for x in os.listdir(DOCU_ROOT + os.sep + 'music') if os.path.splitext(x)[1].lower() in SUPPORTED_AUDIO_FILES]:
        music.append(DOCU_ROOT + os.sep + 'music' + os.sep + filename)
    return music

def load_sfx():
    sounds = {}
    for filename in [x for x in os.listdir(DOCU_ROOT + os.sep + 'sfx') if os.path.splitext(x)[1].lower() in SUPPORTED_AUDIO_FILES]:
        sounds[os.path.splitext(filename)[0]] = DOCU_ROOT + os.sep + 'sfx' + os.sep + filename
    return sounds
    
def display_score(score, start_x, start_y):
    x = start_x
    y = start_y
    for digit in str(score):
        screen.blit(numbers[int(digit)], (x, y))
        x += numbers[int(digit)].get_width()
    
def get_extension(number):
    """Given a place, returns its extension."""
    if number <= 3:
        ext = PLACE_EXTENSIONS[number - 1]
    else:
        ext = PLACE_EXTENSIONS[-1]
    return ext
    
# load static images
track_image = load('track.png')
background_image = load('bg.png')
container_background = load('container_bg.png')
logo_image = load('logo.png')
flag_image = xload('flag.png')
number_bubble_image = xload('number_bubble.png')
star_image = xload('star.png')
numbers = load_numbers()

# window stuff
FRAMERATE = 10
clock = pygame.time.Clock()
pygame.display.set_caption("Super NCSS Trivia!")
pygame.display.set_icon(xload("item_banana.png"))

# load scores
scores = load_scores()
items = load_items()
music = load_music()
sounds = load_sfx()
team_items = [None] * NO_OF_TEAMS

# set animation data
team_current_offsets = [0] * NO_OF_TEAMS # how far down the track the teams are (actually)
buttons_shaking = [False] * NO_OF_TEAMS # False for normal, True for shaking
buttons_shaking_loc = [0] * NO_OF_TEAMS # 0 for normal, -1 for left, +1 for right
blank_screen = False # if True, loads nothing but the logo
final_scores_display = False # if true, displays the final scores instead
teams_to_print = 0 # the number of winning teams to print
star_location = 0 # the current location of the moving stars, between 0 and star_image.get_width()

quit = False
while quit != True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            quit = True

        if event.type == pygame.KEYDOWN:
            key = event.key
            
            if key == pygame.K_F12:
                # load scores
                scores = load_scores()
                # play moving sound
                play("engine_start")
            
            for team_key, team_f_key, team in [(pygame.K_1 + i, pygame.K_F1 + i, i + 1) for i in range(NO_OF_TEAMS)]:
                if key == team_key:
                    # item block
                    if team_items[team - 1]:
                        team_items[team - 1] = None
                    else:
                        # play music and freeze item
                        play("item_beep")
                        team_items[team - 1] = random.choice(items)
                if key == team_f_key:
                    # if they're all shaking, unshake all of them except this one (and stop the music)
                    if all(buttons_shaking):
                        [buttons_shaking.__setitem__(x, False) for x in range(NO_OF_TEAMS) if x != team - 1]
                        fadeout()
                    else:
                        buttons_shaking[team - 1] = not buttons_shaking[team - 1] # on and off
            
            if key == pygame.K_F11:
                # shake all
                [buttons_shaking.__setitem__(x, True) for x in range(NO_OF_TEAMS)]
                # randomise locations
                [buttons_shaking_loc.__setitem__(x, random.randint(-SHAKING_MAGNITUDE, SHAKING_MAGNITUDE)) for x in range(NO_OF_TEAMS)]
                # play shaking sound
                xplay("random_team")
                
            if key == pygame.K_F10:
                # stop all
                [buttons_shaking.__setitem__(x, False) for x in range(NO_OF_TEAMS)]
            
            if key == pygame.K_p:
                # play
                pygame.mixer.music.load(random.choice(music))
                pygame.mixer.music.play(-1)
                    
            if key == pygame.K_s:
                # stop all music
                fadeout()
            
            if key == pygame.K_RETURN or key == pygame.K_a:
                # start a round
                play("start_round")
                
            if key == pygame.K_f:
                # end a round
                play("end_round") # automatically stops other sounds
                
            if key == pygame.K_b:
                # clear the screen (or unclear it)
                blank_screen = not blank_screen
                
            if key == pygame.K_l:
                # display final scores
                final_scores_display = not final_scores_display
                if final_scores_display:
                    # play winning music
                    play('trivia_winners_announcements')
                
            if key == pygame.K_UP:
                # increase number of printed scores
                teams_to_print += 1
                
            if key == pygame.K_DOWN:
                # decrease number of printed scores
                teams_to_print -= 1

    # paint background
    draw_bg(background_image)
    tile(container_background, CONTAINER_AREA.start_x, CONTAINER_AREA.start_y, CONTAINER_AREA.end_x, CONTAINER_AREA.end_y)
    
    # paint logo
    screen.blit(logo_image, (225, 25))
    
    if not blank_screen and not final_scores_display:
        # paint tracks, characters and flags
        current_x = RACE_AREA.start_x
        current_y = RACE_AREA.start_y
        for (number, (name, image, no_image, score)) in scores.items():
            
            # shaking data
            if buttons_shaking[number - 1]:
                screen.blit(number_bubble_image, (current_x - 55 + buttons_shaking_loc[number - 1], current_y - 5)) # number bubble
                screen.blit(no_image, (current_x - 44 + buttons_shaking_loc[number - 1], current_y + 5)) # number
                if buttons_shaking_loc[number - 1] == 0:
                    buttons_shaking_loc[number - 1] = SHAKING_MAGNITUDE
                else:
                    buttons_shaking_loc[number - 1] *= -1
            else:
                screen.blit(number_bubble_image, (current_x - 55, current_y - 5)) # number bubble
                screen.blit(no_image, (current_x - 44, current_y + 5)) # number
            
            screen.blit(track_image, (current_x + 10, current_y + 3)) # track
            screen.blit(flag_image, (current_x + 744, current_y + 5)) # flag
            
            # update destination
            target_offset = int((float(score) / MAX_SCORE) * TRACK_LENGTH)
            
            # animate: keep moving them by 1 pixel until they reach their destination
            if (team_current_offsets[number - 1] < target_offset):
                #print "%s: Animating (%s < %s)" % (number, team_current_offsets[number - 1], target_offset)
                if (team_current_offsets[number - 1] + JUMP_SIZE > target_offset):
                    # jump_size is too large a jump
                    screen.blit(image, (current_x + target_offset, current_y)) # character
                    team_current_offsets[number - 1] = target_offset
                else:
                    screen.blit(image, (current_x + team_current_offsets[number - 1] + JUMP_SIZE, current_y)) # character
                    team_current_offsets[number - 1] += JUMP_SIZE
            elif (team_current_offsets[number - 1] > target_offset):
                #print "%s: Animating (%s > %s)" % (number, team_current_offsets[number - 1], target_offset)
                if (team_current_offsets[number - 1] - JUMP_SIZE < target_offset):
                    # jump_size is too large a jump
                    screen.blit(image, (current_x + target_offset, current_y)) # character
                    team_current_offsets[number - 1] = target_offset
                else:
                    screen.blit(image, (current_x + team_current_offsets[number - 1] - JUMP_SIZE, current_y)) # character
                    team_current_offsets[number - 1] -= JUMP_SIZE
            else:
                screen.blit(image, (current_x + target_offset, current_y)) # character
                #print "%s: Not animated" % number
            
            
            # item block
            item_loc = (current_x + 160, current_y + 7)
            if number == NO_OF_TEAMS:
                # tutor block: move it to always be in front of their character
                pushed_item_loc = (current_x + team_current_offsets[number - 1] + 45, current_y + 7)
                # check if they've reached it yet
                if pushed_item_loc[0] > item_loc[0]:
                    item_loc = pushed_item_loc
                
            if team_items[number - 1] == None:
                screen.blit(random.choice(items), item_loc) # question block
            else:
                screen.blit(team_items[number - 1], item_loc) # question block

            
            current_x += RACE_AREA.padding_x
            current_y += RACE_AREA.padding_y
        #print "finished scores!"
        
        #print "Song is playing? %s (volume %s)" % (pygame.mixer.music.get_busy(), pygame.mixer.music.get_volume())
    
    elif not blank_screen and final_scores_display:
        winning_scores = sorted(scores.items(), key=lambda x: x[1][-1]) # ascending order: loser is first
        teams_printed = 0
        
        # stars
        STAR_PADDING = 5
        STAR_SPEED = 3
        for x in range(CONTAINER_AREA.start_x - 50 + star_location, CONTAINER_AREA.end_x, star_image.get_width() + STAR_PADDING):
            for y in range(CONTAINER_AREA.start_y + 15, CONTAINER_AREA.end_y - 50, star_image.get_height() + STAR_PADDING):
                screen.blit(star_image, (x, y))
        star_location = (star_location + STAR_SPEED) % (star_image.get_width() + STAR_PADDING)
        
        # print teams in winning order
        current_x = RACE_AREA.start_x + 370
        current_y = RACE_AREA.start_y
        for (number, (name, image, no_image, score)) in winning_scores:
            if teams_printed >= teams_to_print:
                break
            
            place_image = numbers[NO_OF_TEAMS - teams_printed]
            screen.blit(place_image, (current_x - 125, current_y + 5)) # place number
            screen.blit(numbers[get_extension(NO_OF_TEAMS - teams_printed)], (current_x - 125 + place_image.get_width(), current_y + 5)) # place number extension
            
            screen.blit(number_bubble_image, (current_x - 55, current_y - 5)) # number bubble
            screen.blit(no_image, (current_x - 44, current_y + 5)) # number
            screen.blit(image, (current_x, current_y)) # character
            display_score(score, current_x + 100, current_y + 5) # score
            current_x += RACE_AREA.padding_x
            current_y += RACE_AREA.padding_y
            teams_printed += 1
    
    
    pygame.display.update()
    clock.tick(FRAMERATE)
        
