import pygame
import sys


pygame.init()


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Машины")


car1_image = pygame.image.load('tank.png').convert_alpha()
car1_image = pygame.transform.scale(car1_image, (50, 50))
car2_image = pygame.image.load('tank.png').convert_alpha()
car2_image = pygame.transform.scale(car2_image, (50, 50))
bullet_image = pygame.image.load('bullet.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (15, 15))


class Car:
    def __init__(self, image, start_pos, start_angle=0, speed=2):
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

    def update_bullets(self):
        self.bullets.update()
        self.bullets.draw(screen)


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

        # Удаляем снаряд, если он выходит за пределы экрана
        if not screen.get_rect().contains(self.rect):
            self.kill()



car1 = Car(car1_image, (200, 300))
car2 = Car(car2_image, (500, 300))


border_left = 20
border_right = 780
border_top = 20
border_bottom = 580


clock = pygame.time.Clock()
running = True
while running:
    pygame.event.pump()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                car1.shoot()
            if event.key == pygame.K_RCTRL:
                car2.shoot()


    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        car1.rotate(3)
    if keys[pygame.K_d]:
        car1.rotate(-3)
    if keys[pygame.K_w]:
        car1.move_forward()
    if keys[pygame.K_s]:
        car1.move_backward()

    if keys[pygame.K_LEFT]:
        car2.rotate(3)
    if keys[pygame.K_RIGHT]:
        car2.rotate(-3)
    if keys[pygame.K_UP]:
        car2.move_forward()
    if keys[pygame.K_DOWN]:
        car2.move_backward()


    if not (border_left < car1.pos.x < border_right and border_top < car1.pos.y < border_bottom):
        car1.pos -= car1.direction * car1.speed
    if not (border_left < car2.pos.x < border_right and border_top < car2.pos.y < border_bottom):
        car2.pos -= car2.direction * car2.speed

    screen.fill((30, 30, 30))

    car1.draw(screen)
    car2.draw(screen)

    car1.update_bullets()
    car2.update_bullets()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()