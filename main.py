import pygame
import pymunk
import pymunk.pygame_util
import math

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM_PANEL = 50

# game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pyool")

# pymunk space
space = pymunk.Space()
static_body = space.static_body # creates the effect of friction
draw_options = pymunk.pygame_util.DrawOptions(screen)

# clock
clock = pygame.time.Clock()
FPS = 120

# game variables
diameter = 36
pocket_diameter = 66
force = 0
max_force = 10000
force_direction = 1
taking_shot = True
powering_up = False
potted_balls = []
cue_ball_potted = False

# colors
bg = (50,50,50)
gray = (192,192,192)
white = (255, 255, 255)

# fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# load images
cue_image = pygame.image.load("assets/images/cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table.png").convert_alpha()
ball_images = []
for i in range(1, 17):
    ball_image = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)

# putting text on screen
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

#create balls
def create_ball(radius, position):
    body = pymunk.Body() #creates DYNAMIC pymunk body
    body.position = position

    shape = pymunk.Circle(body, radius) #shapes ball with body and radius
    shape.mass = 5
    shape.elasticity = 0.8
    # use pivot joint for friction
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000 # emulate friction

    space.add(body, shape, pivot) #add ball to space
    return shape

# setup balls
balls = []
rows = 5
# potting balls
for column in range(5):
    for row in range(rows):
        position = (250 + (column * (diameter + 1)), 267 + (row * (diameter + 1)) + (column * diameter / 2))
        new_ball = create_ball(diameter / 2, position)
        balls.append((new_ball, ball_number))
    rows -= 1
# cue ball
pos = (888, SCREEN_HEIGHT / 2)
cue_ball = create_ball(diameter / 2, pos)
balls.append(cue_ball)

# create pockets
pockets =[
    (55,63),
    (592,48),
    (1134,64),
    (55,616),
    (592,629),
    (1134,616)
]

# create cushions
cushions = [
    [(88, 56), (109, 77), (555, 77), (564, 56)],
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],
    [(89, 621), (110, 600), (556, 600), (564, 621)],
    [(622, 621), (630, 600), (1081, 600), (1102, 621)],
    [(56, 96), (77, 117), (77, 560), (56, 581)],
    [(1143, 96), (1122, 117), (1122, 560), (1143, 581)],
] # pixel coordinates of cushions on table image
def create_cushion(poly_dimensions):
    body = pymunk.Body(body_type = pymunk.Body.STATIC) #creates STATIC pymunk body
    body.position = ((0, 0))

    shape = pymunk.Poly(body, poly_dimensions)
    shape.elasticity = 0.8

    space.add(body, shape)
for c in cushions:
    create_cushion(c)

# create cue
class Cue():
    def __init__(self, position):
        # ensure cue rotates around cue ball
        self.original_image = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, 
         (self.rect.centerx - self.image.get_width() / 2,
          self.rect.centery - self.image.get_height() / 2)         
        )
cue = Cue(balls[-1].body.position) # grab position of the cue ball through list index

# power bars
power_bar = pygame.Surface((10, 20))
power_bar.fill(gray)

# maingame loop
run = True
while run:
    clock.tick(FPS)
    space.step(1 / FPS) # every gameloop, pymunk checks for updates

    # fill bg
    screen.fill(bg)

    # draw table
    screen.blit(table_image, (0, 0))

    # potted balls?
    for i, ball in enumerate(balls):
        for pocket in pockets:
            ball_x_distance = abs(ball.body.position[0] - pocket[0])
            ball_y_distance = abs(ball.body.position[1] - pocket[1])
            ball_distance = math.sqrt((ball_x_distance ** 2)+(ball_y_distance ** 2))
            if ball_distance <= pocket_diameter / 2:
                #check if potted = cue ball
                if i == len(balls) - 1:
                    cue_ball_potted = True
                    ball.body.position = (-100, -100)
                    ball.body.velocity = (0.0, 0.0)
                else:
                    space.remove(ball.body)
                    balls.remove(ball)
                    potted_balls.append(ball_images[i])
                    ball_images.pop(i)

    # draw balls
    for i, ball in enumerate(balls):
        screen.blit(ball_images[i], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

    # check if balls stopped moving
    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0: # if velocity (movement) != 0 (still moving), cue is gone
            taking_shot = False

    # draw cue
    if taking_shot == True:
        if cue_ball_potted == True:
            #reposition cue ball
            balls[-1].body.position = (888, SCREEN_HEIGHT / 2)
            cue_ball_potted = False
        # calc angle
        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_distance = balls[-1].body.position[0] - mouse_pos[0]
        y_distance = -(balls[-1].body.position[1] - mouse_pos[1])
        cue_angle = math.degrees(math.atan2(y_distance, x_distance)) # turn radius into degrees
        cue.update(cue_angle)
        cue.draw(screen)

        # power up cue
        if powering_up == True:
            force += 100 * force_direction
            if force >= max_force or force <= 0:
                force_direction *= -1
            #draw power bars - each bar 2000
            for bar in range(math.ceil(force / 2000)):
                screen.blit(power_bar, (balls[-1].body.position[0] - 30 + (bar * 15), balls[-1].body.position[1] + 30))
        elif powering_up == False and taking_shot == True:
            x_impulse = math.cos(math.radians(cue_angle))
            y_impulse = math.sin(math.radians(cue_angle))
            balls[-1].body.apply_impulse_at_local_point((force * -x_impulse, force * y_impulse), (0, 0))
            force = 0
            force_direction = 1

    # draw bottom panel
    pygame.draw.rect(screen, bg, (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))

    # draw potted balls
    for i, (ball, ball_number) in enumerate(potted_balls):
        screen.blit(ball, (20 + (i * 50), SCREEN_HEIGHT + 10))
        if ball_number == 8:
            eight_ball_potted = True

    # game over?
    eight_ball_potted = False
    if eight_ball_potted:
        if len(potted_balls) == 15:
            eight_ball_potted = True
            draw_text("YOU WIN")
        elif eight_ball_potted and cue_ball_potted: # scratching
            eight_ball_potted = True
            cue_ball_potted = True
            draw_text("GAME OVER")
        else:
            draw_text("GAME OVER")

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot == True:
            powering_up = True
        if event.type == pygame.MOUSEBUTTONUP and taking_shot == True:
            powering_up = False
        if event.type == pygame.QUIT:
            run = False

    # drawing debug        
    pygame.display.update()

pygame.quit()