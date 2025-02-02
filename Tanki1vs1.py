import pygame
import sys
import random
import json

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
sound_played = False
SPAWN_OFFSET = 50
SPAWN_ROTATION = 180
pygame.display.set_caption("Танки")
RED_TANK_IMAGE = pygame.image.load('images/redtank.png').convert_alpha()
RED_TANK_IMAGE = pygame.transform.scale(RED_TANK_IMAGE, (50, 50))
BLUE_TANK_IMAGE = pygame.image.load('images/bluetank.png').convert_alpha()
BLUE_TANK_IMAGE = pygame.transform.scale(BLUE_TANK_IMAGE, (50, 50))
BULLET_IMAGE = pygame.image.load('images/bullet.png').convert_alpha()
BULLET_IMAGE = pygame.transform.scale(BULLET_IMAGE, (15, 15))
MENU_BACKGROUND_IMAGE = pygame.image.load('images/background.png')
GAME_BACKGROUND_IMAGE = pygame.image.load('images/desert_bg.png')
RED_HEART_IMAGE = pygame.image.load('images/redhp.png').convert_alpha()
BLUE_HEART_IMAGE = pygame.image.load('images/bluehp.png').convert_alpha()

BORDER_LEFT = 20
BORDER_RIGHT = SCREEN_WIDTH - 20
BORDER_TOP = 20
BORDER_BOTTOM = SCREEN_HEIGHT - 20

TILE_WIDTH = GAME_BACKGROUND_IMAGE.get_width()
TILE_HEIGHT = GAME_BACKGROUND_IMAGE.get_height()

MAPS_FILE = "maps.json"
CURRENT_MAP_KEY = "last_selected_map"


class MapManager:
    def __init__(self):
        self.maps = self.load_maps()
        self.current_map_index = 0

    def load_maps(self):
        try:
            with open(MAPS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_maps = [
                {
                    "name": "Пустыня",
                    "background": "images/desert_bg.png",
                    "obstacles": []
                },
                {
                    "name": "Город",
                    "background": "images/city_bg.png",
                    "obstacles": []
                },
                {
                    "name": "Лес",
                    "background": "images/forest_bg.png",
                    "obstacles": []
                }
            ]
            with open(MAPS_FILE, 'w') as f:
                json.dump(default_maps, f)
            return default_maps

    def get_current_map(self):
        return self.maps[self.current_map_index]

    def next_map(self):
        self.current_map_index = (self.current_map_index + 1) % len(self.maps)

    def prev_map(self):
        self.current_map_index = (self.current_map_index - 1) % len(self.maps)

    def save_current_map(self):
        settings = {CURRENT_MAP_KEY: self.get_current_map()["name"]}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)


def generate_background(surface, map_manager):
    try:
        tile_image = pygame.image.load(map_manager.get_current_map()["background"]).convert()
        width, height = surface.get_size()
        num_tiles_x = (width // tile_image.get_width()) + 1
        num_tiles_y = (height // tile_image.get_height()) + 1

        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                surface.blit(tile_image, (i * tile_image.get_width(), j * tile_image.get_height()))
    except Exception as e:
        print(f"ошибка загрузки фона: {e}")


def get_random_spawn_positions():
    if random.random() < 0.5:
        red_pos = (BORDER_RIGHT - SPAWN_OFFSET, BORDER_TOP + SPAWN_OFFSET)
        blue_pos = (BORDER_LEFT + SPAWN_OFFSET, BORDER_BOTTOM - SPAWN_OFFSET)
        red_angle = 180
        blue_angle = 0
    else:
        red_pos = (BORDER_LEFT + SPAWN_OFFSET, BORDER_TOP + SPAWN_OFFSET)
        blue_pos = (BORDER_RIGHT - SPAWN_OFFSET, BORDER_BOTTOM - SPAWN_OFFSET)
        red_angle = 0
        blue_angle = 180

    return red_pos, blue_pos, red_angle, blue_angle

class Tank(pygame.sprite.Sprite):
    def __init__(self, color, start_pos, heart_color, start_angle=0, speed=2):
        super().__init__()
        self.original_image = RED_TANK_IMAGE if color == 'red' else BLUE_TANK_IMAGE
        self.image = pygame.transform.rotate(self.original_image, start_angle)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.angle = start_angle
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.health = 3
        self.heart_color = heart_color
        self.shots_fired = 0
        self.hits = 0
        self.moving = False
        self.magazine_size = 5
        self.bullets_in_magazine = 5
        self.last_shot_time = 0
        self.reload_start_time = 0
        self.is_reloading = False
        self.reload_per_bullet = 3000
        self.shot_cooldown = 500

    def rotate(self, delta_angle):
        self.angle = (self.angle + delta_angle) % 360
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def move_backward(self):
        move_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.pos -= move_direction * self.speed
        self.rect.center = self.pos
        self.moving = True

    def move_forward(self):
        move_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.pos += move_direction * self.speed
        self.rect.center = self.pos
        self.moving = True

    def stop_moving(self):
        self.moving = False

    def shoot(self):
        current_time = pygame.time.get_ticks()

        if self.is_reloading:
            return

        if current_time - self.last_shot_time < self.shot_cooldown:
            return

        if self.bullets_in_magazine > 0:
            self.bullets.add(Bullet(self.pos, self.angle))
            self.bullets_in_magazine -= 1
            self.shots_fired += 1
            self.last_shot_time = current_time

            if self.bullets_in_magazine == 0:
                self.start_reload()
            else:
                self.is_reloading = False

    def start_reload(self):
        if not self.is_reloading and self.bullets_in_magazine < self.magazine_size:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()

    def update_reload(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            time_since_reload = current_time - self.reload_start_time
            bullets_reloaded = time_since_reload // self.reload_per_bullet
            new_bullets = min(self.magazine_size, bullets_reloaded + self.bullets_in_magazine)

            if new_bullets != self.bullets_in_magazine:
                self.bullets_in_magazine = new_bullets
                if self.bullets_in_magazine == self.magazine_size:
                    self.is_reloading = False

    def draw_ammo(self, surface):
        ammo_x = self.rect.centerx - 25
        ammo_y = self.rect.top - 20
        for i in range(self.bullets_in_magazine):
            pygame.draw.rect(surface, (255, 215, 0), (ammo_x + i * 8, ammo_y, 6, 15))

        if self.is_reloading:
            reload_text = font.render("Reloading...", True, (255, 0, 0))
            surface.blit(reload_text, (self.rect.centerx - 40, self.rect.top - 40))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_bullets(self, surface):
        self.bullets.update()
        self.bullets.draw(surface)

    def draw_health_bar(self, surface):
        heart_x = self.rect.left - 40
        heart_y = self.rect.bottom + 5
        for _ in range(self.health):
            if self.heart_color == 'red':
                surface.blit(RED_HEART_IMAGE, (heart_x, heart_y))
            elif self.heart_color == 'blue':
                surface.blit(BLUE_HEART_IMAGE, (heart_x, heart_y))
            heart_x += RED_HEART_IMAGE.get_width() + 5


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, tank_angle, speed=10):
        super().__init__()
        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2(1, 0).rotate(-tank_angle)
        self.speed = speed

    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = self.position
        if not screen.get_rect().contains(self.rect):
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, size, color=(128, 128, 128)):
        super().__init__()
        self.size = size
        self.color = color
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def set_position(self, pos):
        self.rect.topleft = pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MapSelector:
    def __init__(self, maps):
        self.maps = maps
        self.selected_map = None

    def display_maps(self, screen):
        for i, map_name in enumerate(self.maps):
            rect = pygame.Rect(100, 100 + i * 50, 150, 40)
            pygame.draw.rect(screen, (255, 255, 255), rect)
            text = font.render(map_name, True, (0, 0, 0))
            screen.blit(text, (rect.x + 5, rect.y + 5))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, map_name in enumerate(self.maps):
                    rect = pygame.Rect(100, 100 + i * 50, 150, 40)
                    if rect.collidepoint(x, y):
                        self.selected_map = map_name
                        break


def load_last_selected_map(map_manager):
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            if isinstance(settings, dict):
                current_map_name = settings.get(CURRENT_MAP_KEY)
                if current_map_name:
                    for i, map_data in enumerate(map_manager.maps):
                        if map_data["name"] == current_map_name:
                            map_manager.current_map_index = i
                            break
            else:
                raise ValueError
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        map_manager.current_map_index = 0
        save_last_selected_map(map_manager.get_current_map()["name"])


def save_last_selected_map(map_name):
    with open('settings.json', 'w') as file:
        json.dump({CURRENT_MAP_KEY: map_name}, file)

def rotate(self, delta_angle):
    self.angle = (self.angle + delta_angle) % 360
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.pos)

def check_collisions(tanks, bullets, obstacles):
    for tank in tanks:
        collided_obstacles = pygame.sprite.spritecollide(tank, obstacles, False)
        for obstacle in collided_obstacles:
            tank.stop_moving()

    groupcollide_dict = pygame.sprite.groupcollide(tanks, tanks, False, False)
    for tank, colliding_tanks in groupcollide_dict.items():
        for other_tank in colliding_tanks:
            if tank != other_tank:
                tank.stop_moving()
                other_tank.stop_moving()

    for bullet in bullets:
        collided_obstacles = pygame.sprite.spritecollide(bullet, obstacles, False)
        for obstacle in collided_obstacles:
            bullet.kill()


def show_end_screen(tank1, tank2):
    screen.fill((255, 255, 255))
    if tank1.health > 0:
        winner_text = "Первый танк победил!"
    else:
        winner_text = "Второй танк победил!"

    lines = [
        f"{winner_text}",
        "",
        f"Первый танк:",
        f"Выстрелы: {tank1.shots_fired}",
        f"Попадания: {tank1.hits}",
        f"HP: {tank1.health}",
        "",
        f"Второй танк:",
        f"Выстрелы: {tank2.shots_fired}",
        f"Попадания: {tank2.hits}",
        f"HP: {tank2.health}"
    ]

    y_offset = SCREEN_HEIGHT // 4
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        x_pos = (SCREEN_WIDTH - text_surface.get_width()) // 2
        screen.blit(text_surface, (x_pos, y_offset))
        y_offset += 40


def main_menu(map_manager):
    global start_button, exit_button, map_left_button, map_right_button

    start_button = pygame.Rect(350, 400, 200, 50)
    exit_button = pygame.Rect(350, 470, 200, 50)
    map_left_button = pygame.Rect(250, 300, 50, 50)
    map_right_button = pygame.Rect(600, 300, 50, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    map_manager.save_current_map()
                    start_sound.play()
                    return
                if exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                if map_left_button.collidepoint(mouse_pos):
                    map_manager.prev_map()
                if map_right_button.collidepoint(mouse_pos):
                    map_manager.next_map()

        screen.fill((0, 0, 0))
        screen.blit(MENU_BACKGROUND_IMAGE, (0, 0))

        current_map = map_manager.get_current_map()
        map_text = font.render(f"Выбранная карта: {current_map['name']}", True, (255, 255, 255))
        screen.blit(map_text, (300, 200))

        pygame.draw.rect(screen, (0, 255, 0), start_button)
        pygame.draw.rect(screen, (255, 0, 0), exit_button)
        pygame.draw.rect(screen, (200, 200, 200), map_left_button)
        pygame.draw.rect(screen, (200, 200, 200), map_right_button)

        screen.blit(font.render("Начать игру", True, (0, 0, 0)), (375, 415))
        screen.blit(font.render("Выход", True, (0, 0, 0)), (400, 485))
        screen.blit(font.render("<", True, (0, 0, 0)), (265, 310))
        screen.blit(font.render(">", True, (0, 0, 0)), (615, 310))

        pygame.display.flip()
        clock.tick(60)

map_manager = MapManager()
load_last_selected_map(map_manager)
red_pos, blue_pos, red_angle, blue_angle = get_random_spawn_positions()

Tank1 = Tank(color='red',start_pos=red_pos,heart_color='red',start_angle=red_angle)
Tank2 = Tank(color='blue',start_pos=blue_pos,heart_color='blue',start_angle=blue_angle)

obstacles = pygame.sprite.Group()

obstacle_size = 50
obstacle = Obstacle(obstacle_size)
random_x = random.randint(BORDER_LEFT, BORDER_RIGHT - obstacle_size)
random_y = random.randint(BORDER_TOP, BORDER_BOTTOM - obstacle_size)
obstacle.set_position((random_x, random_y))
obstacles.add(obstacle)

clock = pygame.time.Clock()
running = True
game_over = False
winner = None

font = pygame.font.Font(None, 32)

start_button = pygame.Rect(350, 250, 100, 50)
exit_button = pygame.Rect(350, 320, 100, 50)

pygame.mixer.init()
hit_sound = pygame.mixer.Sound('music/hit.wav')
start_sound = pygame.mixer.Sound('music/start.wav')
end_sound = pygame.mixer.Sound('music/end.wav')
ricochet_sound = pygame.mixer.Sound('music/ricochet.wav')

RICOCHET_CHANCE = 0.5

maps = ['Map1', 'Map2', 'Map3']
map_selector = MapSelector(maps)
selected_map = map_manager.get_current_map()["name"]

main_menu(map_manager)

while running:
    pygame.event.pump()
    Tank1.update_reload()
    Tank2.update_reload()

    Tank1.draw_ammo(screen)
    Tank2.draw_ammo(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Tank1.shoot()
            if event.key == pygame.K_RETURN:
                Tank2.shoot()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        Tank1.rotate(3)
    if keys[pygame.K_d]:
        Tank1.rotate(-3)
    if keys[pygame.K_w]:
        Tank1.move_forward()
    if keys[pygame.K_s]:
        Tank1.move_backward()

    if keys[pygame.K_LEFT]:
        Tank2.rotate(3)
    if keys[pygame.K_RIGHT]:
        Tank2.rotate(-3)
    if keys[pygame.K_UP]:
        Tank2.move_forward()
    if keys[pygame.K_DOWN]:
        Tank2.move_backward()

    if not (BORDER_LEFT < Tank1.pos.x < BORDER_RIGHT and BORDER_TOP < Tank1.pos.y < BORDER_BOTTOM):
        Tank1.stop_moving()
    if not (BORDER_LEFT < Tank2.pos.x < BORDER_RIGHT and BORDER_TOP < Tank2.pos.y < BORDER_BOTTOM):
        Tank2.stop_moving()

    Hit_tan1 = pygame.sprite.spritecollide(Tank1, Tank2.bullets, True)
    Hit_tank2 = pygame.sprite.spritecollide(Tank2, Tank1.bullets, True)

    if Hit_tan1:
        for bullet in Hit_tan1:
            if random.random() < 0.1:
                bullet.kill()
                ricochet_sound.play()
            else:
                Tank1.health -= 1
                Tank2.hits += 1
                hit_sound.play()

    if Hit_tank2:
        for bullet in Hit_tank2:
            if random.random() < 0.1:
                bullet.kill()
                ricochet_sound.play()
            else:
                Tank2.health -= 1
                Tank1.hits += 1
                hit_sound.play()

    if Tank1.rect.colliderect(Tank2.rect):
        Tank1.stop_moving()
        Tank2.stop_moving()

    for bullet in Tank1.bullets.sprites() + Tank2.bullets.sprites():
        if pygame.sprite.collide_rect(bullet, obstacle):
            bullet.kill()

    if pygame.sprite.collide_rect(Tank1, obstacle):
        Tank1.stop_moving()
    if pygame.sprite.collide_rect(Tank2, obstacle):
        Tank2.stop_moving()

    if Tank1.health <= 0 or Tank2.health <= 0:
        game_over = True
        if not sound_played:
            end_sound.play()
            sound_played = True

    if not game_over:
        generate_background(screen, map_manager)

        Tank1.draw(screen)
        Tank2.draw(screen)

        Tank1.update_bullets(screen)
        Tank2.update_bullets(screen)

        Tank1.draw_health_bar(screen)
        Tank2.draw_health_bar(screen)

        obstacles.draw(screen)

    else:
        show_end_screen(Tank1, Tank2)

    pygame.display.flip()
    clock.tick(60)

save_last_selected_map(selected_map)
pygame.quit()
sys.exit()