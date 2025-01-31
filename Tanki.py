import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Танки")

TANK_IMAGE = pygame.image.load('tank.png').convert_alpha()
TANK_IMAGE = pygame.transform.scale(TANK_IMAGE, (50, 50))
BULLET_IMAGE = pygame.image.load('bullet.png').convert_alpha()
BULLET_IMAGE = pygame.transform.scale(BULLET_IMAGE, (15, 15))
BACKGROUND_IMAGE = pygame.image.load('backgr.png')

RED_HEART_IMAGE = pygame.image.load('redhp.png').convert_alpha()
BLUE_HEART_IMAGE = pygame.image.load('bluehp.png').convert_alpha()

BORDER_LEFT = 20
BORDER_RIGHT = 780
BORDER_TOP = 20
BORDER_BOTTOM = 580

TILE_WIDTH = BACKGROUND_IMAGE.get_width()
TILE_HEIGHT = BACKGROUND_IMAGE.get_height()


def generate_background(surface, tile_image):
    width, height = surface.get_size()
    num_tiles_x = 8
    num_tiles_y = 8
    for i in range(num_tiles_x):
        for j in range(num_tiles_y):
            surface.blit(tile_image, (i * TILE_WIDTH, j * TILE_HEIGHT))


class Tank(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, heart_color, start_angle=0, speed=2):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.angle = start_angle
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.health = 3
        self.heart_color = heart_color

    def rotate(self, delta_angle):
        self.angle += delta_angle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def move_forward(self):
        move_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.pos += move_direction * self.speed
        self.rect.center = self.pos

    def move_backward(self):
        move_direction = -pygame.math.Vector2(1, 0).rotate(-self.angle)
        self.pos += move_direction * self.speed
        self.rect.center = self.pos

    def shoot(self):
        self.bullets.add(Bullet(self.pos, self.angle))

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
    def __init__(self, position, angle, speed=10):
        super().__init__()
        self.image = BULLET_IMAGE
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


Tank1 = Tank(TANK_IMAGE, (200, 300), heart_color='red')
Tank2 = Tank(TANK_IMAGE, (500, 300), heart_color='blue')

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
        Tank1.pos -= Tank1.direction * Tank1.speed
    if not (BORDER_LEFT < Tank2.pos.x < BORDER_RIGHT and BORDER_TOP < Tank2.pos.y < BORDER_BOTTOM):
        Tank2.pos -= Tank2.direction * Tank1.speed

    Hit_tan1 = pygame.sprite.spritecollide(Tank1, Tank2.bullets, True)
    Hit_tank2 = pygame.sprite.spritecollide(Tank2, Tank1.bullets, True)

    if Hit_tan1:
        Tank1.health -= 1
        print(f"Попали в первый танк! Здоровье: {Tank1.health}")
    if Hit_tank2:
        Tank2.health -= 1
        print(f"Попали во второй танк! Здоровье: {Tank2.health}")

    if Tank1.rect.colliderect(Tank2.rect):
        collision_normal = pygame.math.Vector2(Tank1.pos - Tank2.pos)
        collision_angle = math.atan2(collision_normal.y, collision_normal.x)

        Tank1.move_backward()
        Tank2.move_backward()

        Tank1.angle = (Tank1.angle + collision_angle) % 360
        Tank2.angle = (Tank2.angle - collision_angle) % 360

    generate_background(screen, BACKGROUND_IMAGE)

    Tank1.draw(screen)
    Tank2.draw(screen)

    Tank1.update_bullets(screen)
    Tank2.update_bullets(screen)

    Tank1.draw_health_bar(screen)
    Tank2.draw_health_bar(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
