from typing import Tuple

import pygame
from pygame.constants import K_UP, K_DOWN


class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_x_velocity: int,
        initial_y_velocity: int,
        world_dimensions: Tuple[int, int],
    ):
        super().__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(int(world_dimensions[0] / 2), int(world_dimensions[1] / 2) - 10)
        )
        # TODO: normalise velocity to given speed
        # TODO: Don't use a tuple
        self.velocity = (initial_x_velocity, initial_y_velocity)
        self.containing_world_dimensions = world_dimensions

    def draw(self, surface: pygame.surface.Surface) -> None:
        surface.blit(self.surf, self.rect)

    def update(self) -> None:
        if (
            self.rect.top == 0
            or self.rect.bottom == self.containing_world_dimensions[1]
        ):
            self.velocity = (self.velocity[0], -self.velocity[1])

        self.rect.move_ip(self.velocity)

    def on_collision(self) -> None:
        self.velocity = (-self.velocity[0], self.velocity[1])

    def is_out_of_bounds(self) -> bool:
        return (
            self.rect.right < 0 or self.rect.left >= self.containing_world_dimensions[0]
        )

    def reset(self, initial_x_velocity: int, initial_y_velocity: int):
        self.velocity = (initial_x_velocity, initial_y_velocity)
        self.rect = self.surf.get_rect()
        self.rect = self.surf.get_rect(
            center=(
                int(self.containing_world_dimensions[0] / 2),
                int(self.containing_world_dimensions[1] / 2) - 10,
            )
        )


class Bat(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_position: Tuple[int, int],
        world_dimensions: Tuple[int, int],
        key_up: pygame.constants = K_UP,
        key_down: pygame.constants = K_DOWN,
    ):
        super().__init__()
        self.surf = pygame.Surface((10, 30))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(initial_position[0], initial_position[1])
        )
        self.world_dimensions = world_dimensions
        self.key_up = key_up
        self.key_down = key_down

    def update(self) -> None:
        pressed_keys = pygame.key.get_pressed()

        if self.rect.top > 0:
            if pressed_keys[self.key_up]:
                self.rect.move_ip(0, -5)
        if self.rect.bottom < self.world_dimensions[1]:
            if pressed_keys[self.key_down]:
                self.rect.move_ip(0, 5)


class ComputerBat(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_position: Tuple[int, int],
        world_dimensions: Tuple[int, int],
    ):
        super().__init__()
        self.surf = pygame.Surface((10, 30))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(initial_position[0], initial_position[1])
        )
        self.world_dimensions = world_dimensions

    def update(self) -> None:
        pass


class Game:
    def __init__(self):
        pygame.init()
        self.width = 640
        self.height = 480
        self.size = self.width, self.height
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._is_running = True
        self._fps = 30
        self.game_clock = pygame.time.Clock()

        self.bats = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.ball = Ball(
            initial_x_velocity=1,
            initial_y_velocity=5,
            world_dimensions=(self.width, self.height),
        )

        player1_bat = Bat(
            initial_position=(0, int(self.height / 2)),
            world_dimensions=(self.width, self.height),
        )

        player2_bat = Bat(
            initial_position=(self.width, int(self.height / 2)),
            world_dimensions=(self.width, self.height),
            key_up=pygame.constants.K_w,
            key_down=pygame.constants.K_s,
        )

        self.all_sprites.add([self.ball, player1_bat, player2_bat])
        self.balls.add(self.ball)
        self.bats.add([player1_bat, player2_bat])

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self._is_running = False

    def on_loop(self):
        if True in {ball.is_out_of_bounds() for ball in self.balls}:
            print("Ball went out")
            self.ball.reset(10, 5)
            return

        if pygame.sprite.spritecollideany(self.ball, self.bats):
            self.ball.on_collision()
        for sprite in self.all_sprites:
            sprite.update()

    def on_render(self):
        self._display_surf.fill((0, 0, 0))

        for sprite in self.all_sprites:
            self._display_surf.blit(sprite.surf, sprite.rect)

        pygame.display.update()

    def teardown(self):
        pygame.quit()

    def run(self):
        while self._is_running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.game_clock.tick(self._fps)
        self.teardown()


if __name__ == "__main__":
    game = Game()
    game.run()
