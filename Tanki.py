import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Танки")

Tank1_image = pygame.image.load('tank.png').convert_alpha()
Tank1_image = pygame.transform.scale(Tank1_image, (50, 50))
Tank2_image = pygame.image.load('tank.png').convert_alpha()
Tank2_image = pygame.transform.scale(Tank2_image, (50, 50))
bullet_image = pygame.image.load('bullet.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (15, 15))

BORDER_LEFT = 20
BORDER_RIGHT = 780
BORDER_TOP = 20
BORDER_BOTTOM = 580

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

clock = pygame.time.Clock()
running = True
while running:
    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                Tank1.shoot()
            if event.key == pygame.K_RCTRL:
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
        print("Попали в первый танк!")
    if Hit_tank2:
        print("Попали во второй танк!")

    screen.fill((30, 30, 30))

    Tank1.draw(screen)
    Tank2.draw(screen)

    Tank1.update_bullets(screen)
    Tank2.update_bullets(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
