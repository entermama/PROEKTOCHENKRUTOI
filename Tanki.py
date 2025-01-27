import pygame
import sys

pygame.init()
pygame.display.init()


info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Танки")


Tank1_image = pygame.image.load('tank.png').convert_alpha()
Tank1_image = pygame.transform.scale(Tank1_image, (50, 50))
Tank2_image = pygame.image.load('tank.png').convert_alpha()
Tank2_image = pygame.transform.scale(Tank2_image, (50, 50))
bullet_image = pygame.image.load('bullet.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (15, 15))
wall_image = pygame.image.load('wall.png').convert()
wall_image = pygame.transform.scale(wall_image, (50, 50))
background_image = pygame.image.load('fon.jpg').convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

count = 0


class Button:
    def __init__(self, x, y, width, height, text, font_size, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color

    def draw(self, surface):
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Tank(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, start_angle=0, speed=2):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.angle = start_angle
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.direction = pygame.math.Vector2(1, 0)

    def rotate(self, delta_angle):
        self.angle += delta_angle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.direction = pygame.math.Vector2(1, 0).rotate(-self.angle)

    def move_forward(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

    def move_backward(self):
        self.pos -= self.direction * self.speed
        self.rect.center = self.pos

    def shoot(self):
        self.bullets.add(Bullet(self.pos, self.angle))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update_bullets(self, surface):
        self.bullets.update()
        self.bullets.draw(surface)


class MapSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, angle, speed=10):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect(center=position)
        self.angle = angle
        self.speed = speed
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2(1, 0).rotate(-self.angle)

    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = self.position

        if not screen.get_rect().contains(self.rect):
            self.kill()


Tank1 = Tank(Tank1_image, (200, 300))
Tank2 = Tank(Tank2_image, (500, 300))


map_sprites = pygame.sprite.Group()
tile_size = 50
BORDER_LEFT = tile_size
BORDER_RIGHT = screen_width - tile_size
BORDER_TOP = tile_size
BORDER_BOTTOM = screen_height - tile_size

for x in range(tile_size, screen_width - tile_size, tile_size):
    map_sprites.add(MapSprite(wall_image, x, tile_size))
    map_sprites.add(MapSprite(wall_image, x, screen_height - tile_size -tile_size))
for y in range(tile_size, screen_height - tile_size, tile_size):
    map_sprites.add(MapSprite(wall_image, tile_size, y))
    map_sprites.add(MapSprite(wall_image, screen_width - tile_size - tile_size, y))

map_sprites.add(MapSprite(wall_image, 100, 250))
map_sprites.add(MapSprite(wall_image, screen_width - 150, 250))
map_sprites.add(MapSprite(wall_image, 100, 400))
map_sprites.add(MapSprite(wall_image, screen_width - 150, 400))


start_button = Button(screen_width // 2 - 100, screen_height // 2 - 50, 200, 50, "Начать игру", 100, (255, 255, 255))
start_button_2 = Button(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50, "Настройки", 100, (255, 255, 255))
start_screen = True
while start_screen:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                start_screen = False
            if start_button_2.is_clicked(event.pos):
                pass

    screen.blit(background_image, (0, 0))
    start_button.draw(screen)
    start_button_2.draw(screen)
    pygame.display.flip()

clock = pygame.time.Clock()
running = True
while running:
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Tank1.shoot()
            if event.key == pygame.K_KP_ENTER:
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
        Tank1.pos -= Tank1.direction * Tank1.speed
    if not (BORDER_LEFT < Tank2.pos.x < BORDER_RIGHT and BORDER_TOP < Tank2.pos.y < BORDER_BOTTOM):
        Tank2.pos -= Tank2.direction * Tank2.speed

    collided_tank1 = pygame.sprite.spritecollide(Tank1, map_sprites, False)
    collided_tank2 = pygame.sprite.spritecollide(Tank2, map_sprites, False)

    if collided_tank1:
      Tank1.pos -= Tank1.direction * Tank1.speed

    if collided_tank2:
      Tank2.pos -= Tank2.direction * Tank2.speed
    #проверка попаданий
    Hit_tan1 = pygame.sprite.spritecollide(Tank1, Tank2.bullets, True)
    Hit_tank2 = pygame.sprite.spritecollide(Tank2, Tank1.bullets, True)

    if Hit_tan1:
        count +=1
        print("Попали в первый танк!")
        if count == 5:
            background_image = pygame.image.load('fon_2.jpg').convert()
            screen.blit(background_image, (0, 0))
            font = pygame.font.Font(None, 52)
            text = font.render("Победил второй танк!", True, (0, 0, 0))
            text_rect = text.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(100000)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            running = False
    if Hit_tank2:
        print("Попали во второй танк!")
        count += 1
        if count == 5:
            background_image = pygame.image.load('fon_2.jpg').convert()
            screen.blit(background_image, (0, 0))
            font = pygame.font.Font(None, 52)
            text = font.render("Победил первый танк!", True, (0, 0, 0))
            text_rect = text.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(100000)
            if event.type == pygame.QUIT:
                exit()
            running = False
    screen.fill((30, 30, 30))
    map_sprites.draw(screen)
    Tank1.draw(screen)
    Tank2.draw(screen)
    Tank1.update_bullets(screen)
    Tank2.update_bullets(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()