import pygame
import os
import time
import random
import sys
pygame.font.init()
pygame.display.set_caption("Space Shooters")
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_2.png")), (WIDTH, HEIGHT))
SPEED_POWERUP = pygame.image.load(os.path.join("assets", "speed_powerup.png"))
EXPLOSION = pygame.image.load(os.path.join("assets", "explosion.png"))
clock = pygame.time.Clock()

#add in bomb sequence every 5 rounds, add in bomb weapon on player ship, shield powerup

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)
    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.COOLDOWN = 30

    def move_lasers(self, vel, objs, explosions):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        explosions.append(Explosion(obj.x, obj.y))
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

    def shoot(self):
        global ammo
        if self.cool_down_counter == 0 and ammo > 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            ammo -= 1

class Enemy(Ship):
    COLOR_MAP = {"red": (RED_SPACE_SHIP, RED_LASER), "green": (GREEN_SPACE_SHIP, GREEN_LASER), "blue": (BLUE_SPACE_SHIP, BLUE_LASER)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel
    def shoot(self):
    
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)

class Explosion:
    def __init__(self, x, y, timer=20):
        self.x = x
        self.y = y
        self.timer = timer
        self.img = EXPLOSION
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def update(self):
        self.timer -= 1
        return self.timer <= 0

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

class Powerup:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.img = SPEED_POWERUP
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return self.y > height

def pause():
    paused = True
    pause_font = pygame.font.SysFont("comicsans", 80)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
        WIN.blit(BG, (0, 0))
        pause_label = pause_font.render("Paused", 1, (255, 255, 255))
        WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, HEIGHT/2 - pause_label.get_height()/2))
        pygame.display.update()
        clock.tick(5)

def spin_wheel():
    spin_font = pygame.font.SysFont("comicsans", 40)
    prompt = spin_font.render("Spin the wheel for a power up? (Y/N)", 1, (255,255,255))
    WIN.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - prompt.get_height()//2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False

def show_spin_message(message, duration=2):
    message_font = pygame.font.SysFont("comicsans", 40)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration * 1000:
        WIN.blit(BG, (0, 0))
        msg_render = message_font.render(message, 1, (255,255,255))
        WIN.blit(msg_render, (WIDTH//2 - msg_render.get_width()//2, HEIGHT//2 - msg_render.get_height()//2))
        pygame.display.update()
        clock.tick(60)

def main():
    global ammo
    run = True
    FPS = 60
    level = 0
    lives = 5
    ammo = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    powerups = []
    enemies = []
    explosions = []
    enemy_vel = 1
    powerup_vel = 2
    player_vel = 5
    elaser_vel = 4
    wheel_multiplier = 1
    player = Player(300, 630)
    pickup_message = None
    pickup_message_end = 0
    lost = False
    lost_count = 0
    def redraw_window():
        WIN.blit(BG, (0, 0))
        if level == 2:
            WIN.blit(BG2, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,255))
        WIN.blit(lives_label, (10, 10))
        level_label = main_font.render(f"Level: {level}", 1, (0,0,255))
        WIN.blit(level_label, (WIDTH//2 - level_label.get_width()//2, 10))
        ammo_label = main_font.render(f"Ammo: {ammo}", 1, (0,0,255))
        WIN.blit(ammo_label, (WIDTH - ammo_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(WIN)
        for powerup in powerups:
            powerup.draw(WIN)
        player.draw(WIN)
        for explosion in explosions[:]:
            explosion.draw(WIN)
            if explosion.update():
                explosions.remove(explosion)
        if pickup_message and pygame.time.get_ticks() < pickup_message_end:
            msg_font = pygame.font.SysFont("comicsans", 40)
            msg_surface = msg_font.render(pickup_message, 1, (255,255,255))
            WIN.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, HEIGHT//2 - msg_surface.get_height()//2))
        if lost:
            lost_label = lost_font.render("YOU LOST!!", 1, (0,0,255))
            WIN.blit(lost_label, (WIDTH/3 - lost_label.get_width()/2, 350))
        pygame.display.update()
    while run:
        clock.tick(FPS)
        redraw_window()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause()
                if event.key == pygame.K_l:
                    if ammo >= 500:
                        ammo -= 500
                        lives += 1
                        pickup_message = "Extra Life Purchased"
                        pickup_message_end = pygame.time.get_ticks() + 2000
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            ammo += 50
            if spin_wheel():
                powerup_type = random.choice(["slower", "faster", "less lives", "more lives", "faster shots", "slower shots", "ammo"])
                multiplier_effect = 2 * wheel_multiplier
                if powerup_type == "faster":
                    player_vel = min(10, player_vel + 2 * multiplier_effect)
                    msg = f"Power Up: Faster x{multiplier_effect}"
                elif powerup_type == "slower":
                    player_vel = max(1, player_vel - 2 * multiplier_effect)
                    msg = f"Power Up: Slower x{multiplier_effect}"
                elif powerup_type == "more lives":
                    lives += 1 * multiplier_effect
                    msg = f"Power Up: More Lives x{multiplier_effect}"
                elif powerup_type == "less lives":
                    lives = max(0, lives - 1 * multiplier_effect)
                    msg = f"Power Up: Less Lives x{multiplier_effect}"
                elif powerup_type == "faster shots":
                    player.COOLDOWN = max(5, player.COOLDOWN - 10 * multiplier_effect)
                    msg = f"Power Up: Faster Shots x{multiplier_effect}"
                elif powerup_type == "slower shots":
                    player.COOLDOWN += 10 * multiplier_effect
                    msg = f"Power Up: Slower Shots x{multiplier_effect}"
                elif powerup_type == "ammo":
                    effect = random.choice([50, -50]) * multiplier_effect
                    if effect < 0:
                        if ammo + effect < 0:
                            ammo = 25
                            msg = "Power Up: Ammo Drain -> Awarded 25 Ammo"
                        else:
                            ammo += effect
                            msg = f"Power Up: Ammo Drain: {effect}"
                    else:
                        ammo += effect
                        msg = f"Power Up: Ammo Boost: +{effect}"
                show_spin_message(msg, 2)
                wheel_multiplier *= 2
            num_enemies = random.randint(25,40)
            for i in range(num_enemies):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        if random.randrange(0, 1000) == 1:
            powerup_type = random.choice(["slower", "faster", "less lives", "more lives", "faster shots", "slower shots"])
            powerup = Powerup(random.randrange(50, WIDTH-50), -50, powerup_type)
            powerups.append(powerup)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        for powerup in powerups[:]:
            powerup.move(powerup_vel)
            if powerup.off_screen(HEIGHT):
                powerups.remove(powerup)
            elif collide(player, powerup):
                if powerup.type == "faster":
                    player_vel = min(10, player_vel + 2)
                    pickup_message = "Power Up: Faster"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                elif powerup.type == "slower":
                    player_vel = max(1, player_vel - 2)
                    pickup_message = "Power Up: Slower"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                elif powerup.type == "more lives":
                    lives += 1
                    pickup_message = "Power Up: More Lives"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                elif powerup.type == "less lives":
                    lives = max(0, lives - 1)
                    pickup_message = "Power Up: Less Lives"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                elif powerup.type == "faster shots":
                    player.COOLDOWN = max(5, player.COOLDOWN - 10)
                    pickup_message = "Power Up: Faster Shots"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                elif powerup.type == "slower shots":
                    player.COOLDOWN += 10
                    pickup_message = "Power Up: Slower Shots"
                    pickup_message_end = pygame.time.get_ticks() + 2000
                powerups.remove(powerup)
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(elaser_vel, player)
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                explosions.append(Explosion(enemy.x, enemy.y))
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-4, enemies, explosions)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 80)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

num = input("Would you like to play space shooters:")
if num.lower() == "yes":
    print("""Welcome to Space Shooters
Your lives and level are located at the top.
Your healthbar is under your ship.
To move use the arrow keys or WASD.
To shoot use space.
Press L to purchase an extra life for 500 ammo.
Watch the game monitor for progress.
Click the screen on your left to begin.
Have fun and don't die!""")
else:
    print("Oh well")
    quit()

main_menu()
