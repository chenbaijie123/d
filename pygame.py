import pygame
import random
import sys

# Setup
WIDTH, HEIGHT = 640, 480
LITTERBOX_RECT = pygame.Rect(160, 250, 320, 120)
CAT_RECT = pygame.Rect(270, 180, 100, 80)
POOP_RADIUS = 15
ARM_POS = (150, 130)  # Arm anchor point

# Colors
BG = (210, 220, 235)
LITTER = (230, 222, 180)
POOP = (99, 73, 35)
CAT = (155, 124, 98)
ARM = (70, 70, 120)
PACKAGE = (245, 203, 167)
TEXT = (60, 60, 60)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto Cat Litter Shovel Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

def draw_litterbox(): pygame.draw.rect(screen, LITTER, LITTERBOX_RECT, border_radius=18)

def draw_cat(): pygame.draw.ellipse(screen, CAT, CAT_RECT)

def draw_poop(pos): pygame.draw.circle(screen, POOP, pos, POOP_RADIUS)

def draw_arm(end_pos):
    pygame.draw.line(screen, ARM, ARM_POS, end_pos, 18)
    pygame.draw.circle(screen, ARM, end_pos, 28, 0)

def draw_package(x, y): pygame.draw.rect(screen, PACKAGE, (x, y, 38, 28), border_radius=8)

def text(msg, pos): screen.blit(font.render(msg, True, TEXT), pos)

# Sim states
cat_in_box = False
poop_present = False
poop_pos = (0, 0)
arm_state = "idle"  # "to_poop", "scoop", "to_package", "release", "back"
arm_progress = 0
package_positions = []
cooldown = 0
cat_timer = random.randint(120, 240)

def random_poop_pos():
    x = random.randint(LITTERBOX_RECT.left+38, LITTERBOX_RECT.right-38)
    y = random.randint(LITTERBOX_RECT.top+32, LITTERBOX_RECT.bottom-18)
    return (x, y)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()

    screen.fill(BG)
    draw_litterbox()

    # Cat logic
    if cooldown <= 0 and not cat_in_box and random.random() < 0.003:
        cat_in_box = True
        cat_timer = random.randint(120, 240)
    if cat_in_box:
        draw_cat()
        cat_timer -= 1
        if cat_timer == 60 and not poop_present:
            poop_present = True
            poop_pos = random_poop_pos()
        if cat_timer <= 0:
            cat_in_box = False
            cooldown = random.randint(180, 350)  # wait before cat returns

    if not cat_in_box and cooldown > 0:
        cooldown -= 1

    # Draw Poop
    if poop_present:
        draw_poop(poop_pos)

    # Package
    for idx, (x, y, timer) in enumerate(package_positions):
        draw_package(x, y)
        package_positions[idx] = (x, y-2, timer-1)
    package_positions = [p for p in package_positions if p[2]>0]

    # Robotic Arm State Machine
    poop_detected = poop_present and not cat_in_box
    arm_base = ARM_POS
    arm_end = ARM_POS
    arm_text = "Idle"
    ARM_SPEED = 1.5

    if arm_state == "idle":
        if poop_detected:
            arm_state = "to_poop"
            arm_progress = 0
    elif arm_state == "to_poop":
        # Move arm towards poop
        px, py = poop_pos
        dx = (px - arm_base[0]) * (arm_progress / 100)
        dy = (py - arm_base[1]) * (arm_progress / 100)
        arm_end = (int(arm_base[0]+dx), int(arm_base[1]+dy))
        arm_text = "Moving to waste"
        arm_progress += ARM_SPEED*2
        if arm_progress >= 100:
            arm_progress = 0
            arm_state = "scoop"
    elif arm_state == "scoop":
        arm_end = poop_pos
        arm_text = "Scooping..."
        arm_progress += ARM_SPEED
        if arm_progress >= 45:
            arm_progress = 0
            arm_state = "to_package"
            poop_present = False  # Scooped up!
    elif arm_state == "to_package":
        px, py = 550, 90+25  # Packaging bin position
        ox, oy = poop_pos
        dx = (px - arm_base[0]) * (arm_progress / 100)
        dy = (py - arm_base[1]) * (arm_progress / 100)
        arm_end = (int(arm_base[0]+dx), int(arm_base[1]+dy))
        arm_text = "Moving to packaging"
        arm_progress += ARM_SPEED*2
        if arm_progress >= 100:
            arm_progress = 0
            arm_state = "release"
    elif arm_state == "release":
        arm_end = (550, 90+25)
        arm_text = "Packaging..."
        arm_progress += ARM_SPEED
        if arm_progress >= 35:
            arm_state = "back"
            package_positions.append((530, 90, 60))
    elif arm_state == "back":
        dx = (arm_base[0] - 550) * (arm_progress/100)
        dy = (arm_base[1] - (90+25)) * (arm_progress/100)
        arm_end = (int(550+dx), int(90+25+dy))
        arm_text = "Arm returning"
        arm_progress += ARM_SPEED*2.5
        if arm_progress >= 100:
            arm_state = "idle"
            arm_progress = 0
    else:
        arm_state = "idle"

    if arm_state != "idle":
        draw_arm(arm_end)
    else:
        # Draw arm at rest
        draw_arm((ARM_POS[0]+36, ARM_POS[1]+60))
    # Text/Status
    text(f"Cat in box: {'Yes' if cat_in_box else 'No'}", (24, 24))
    text(f"Poop detected: {'Yes' if poop_present else 'No'}", (24, 56))
    if arm_state != "idle": text(f"Robotic Arm: {arm_text}", (24, 400))
    else: text("Robotic Arm: Idle", (24, 400))
    text("Press [X] to Quit", (24, 440))

    pygame.display.flip()
    clock.tick(60)
