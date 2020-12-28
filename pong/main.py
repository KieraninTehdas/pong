import math
import random
import time
from typing import Tuple, Sequence, List

import pygame
from pygame.constants import K_UP, K_DOWN


class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_velocity_vector: Sequence[int],
        world_dimensions: Sequence[int],
        speed: int = 10,
    ):
        super().__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(int(world_dimensions[0] / 2), int(world_dimensions[1] / 2) - 10)
        )
        self.speed = speed
        self.velocity: List[int] = self._normalise_velocity(
            initial_velocity_vector, self.speed
        )
        self.containing_world_dimensions = world_dimensions

    @staticmethod
    def _normalise_velocity(velocity: Sequence[int], speed: int) -> List:
        norm_factor = int(
            speed
            / math.sqrt(
                sum([velocity_component ** 2 for velocity_component in velocity])
            )
        )
        return [norm_factor * velocity_component for velocity_component in velocity]

    def draw(self, surface: pygame.surface.Surface) -> None:
        surface.blit(self.surf, self.rect)

    def update(self) -> None:
        # Handle ball going beyond the world in a single step
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.containing_world_dimensions[1]:
            self.rect.bottom = self.containing_world_dimensions[1]

        if (
            self.rect.top == 0
            or self.rect.bottom == self.containing_world_dimensions[1]
        ):
            self.velocity[1] = -self.velocity[1]

        self.rect.move_ip((self.velocity[0], self.velocity[1]))

    def on_collision(self) -> None:
        self.velocity[0] = -self.velocity[0]

    def is_out_of_bounds(self) -> bool:
        return (
            self.rect.right <= 0
            or self.rect.left >= self.containing_world_dimensions[0]
        )

    def get_player_point(self) -> int:
        if self.rect.right <= 0:
            return -1
        elif self.rect.left >= self.containing_world_dimensions[0]:
            return 1
        else:
            return 0

    def reset(self, initial_velocity_vector: Sequence[int]):
        self.velocity = self._normalise_velocity(
            initial_velocity_vector, self.speed
        )
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
    pygame.init()

    def __init__(self):
        self.font_small = pygame.font.SysFont("Verdana", 20)
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
            initial_velocity_vector=self._get_random_vector(),
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

        self.player1_score = 0
        self.player2_score = 0
        self.winning_player = None

    def _display_winner(self):
        self._display_surf.blit(
            self.font_small.render(
                f"{self.winning_player} is the winner!", True, (255, 255, 255)
            ),
            ((self.width / 2) - 30, self.height / 2),
        )
        pygame.display.update()
        time.sleep(2)

    @staticmethod
    def _get_random_vector(min: int = -5, max: int = 5, dimensions: int = 2):
        return [
            random.choice([x for x in range(min, max + 1) if x != 0])
            for _ in range(dimensions)
        ]

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self._is_running = False

    def on_loop(self):
        if self.ball.is_out_of_bounds():
            if self.ball.get_player_point() > 0:
                self.player1_score += 1
            elif self.ball.get_player_point() < 0:
                self.player2_score += 1
            self.ball.reset(self._get_random_vector())
            return

        if self.player1_score == 10:
            self.winning_player = "Player 1"
        elif self.player2_score == 10:
            self.winning_player = "Player 2"

        if self.winning_player:
            self._is_running = False

        if pygame.sprite.spritecollideany(self.ball, self.bats):
            self.ball.on_collision()
        for sprite in self.all_sprites:
            sprite.update()

    def on_render(self):
        self._display_surf.fill((0, 0, 0))

        player1_score = self.font_small.render(
            str(self.player1_score), True, (255, 255, 255)
        )
        player2_score = self.font_small.render(
            str(self.player2_score), True, (255, 255, 255)
        )
        self._display_surf.blit(player1_score, (10, 10))
        self._display_surf.blit(player2_score, (self.width - 20, 10))

        for sprite in self.all_sprites:
            self._display_surf.blit(sprite.surf, sprite.rect)

        pygame.display.update()

    @staticmethod
    def teardown():
        pygame.quit()

    def run(self):
        while self._is_running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.game_clock.tick(self._fps)

        if self.winning_player:
            self._display_winner()

        self.teardown()


if __name__ == "__main__":
    game = Game()
    game.run()
