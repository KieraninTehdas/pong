from typing import Tuple, Union

import pygame
from pygame.constants import K_UP, K_DOWN

from pong.balls import Ball


class Bat(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_position: Tuple[int, int],
        world_dimensions: Tuple[int, int],
        key_up: pygame.constants = K_UP,
        key_down: pygame.constants = K_DOWN,
        speed: Union[float, int] = 5,
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
        self.speed = speed

    def update(self) -> None:
        pressed_keys = pygame.key.get_pressed()

        if self.rect.top > 0:
            if pressed_keys[self.key_up]:
                self.rect.move_ip(0, -self.speed)
        if self.rect.bottom < self.world_dimensions[1]:
            if pressed_keys[self.key_down]:
                self.rect.move_ip(0, self.speed)


class ComputerBat(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_position: Tuple[int, int],
        world_dimensions: Tuple[int, int],
        game_ball,
        speed: Union[float, int] = 5,
    ):
        super().__init__()
        self.surf = pygame.Surface((10, 30))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(initial_position[0], initial_position[1])
        )
        self.world_dimensions = world_dimensions
        self.speed = speed
        self.game_ball: Ball = game_ball

    def update(self) -> None:
        n_projected_steps = 3

        # Move towards the centre if the ball is going away
        if self.game_ball.velocity[0] < 0:
            if self.rect.centery > self.world_dimensions[1] / 2:
                self.rect.move_ip(0, -self.speed)
            else:
                self.rect.move_ip(0, self.speed)

        projected_y_position = (
            self.game_ball.velocity[1] * n_projected_steps
        ) + self.game_ball.rect.centery

        if projected_y_position < 0:
            projected_y_position = -1 * projected_y_position
        elif projected_y_position > self.world_dimensions[1]:
            projected_y_position = (2 * self.world_dimensions[1]) - projected_y_position

        projected_x_position = (
            self.game_ball.velocity[0] * n_projected_steps
        ) + self.game_ball.rect.centerx

        if projected_x_position > self.world_dimensions[0]:
            steps_to_undo = int(
                (projected_x_position - self.world_dimensions[0]) / self.game_ball.speed
            )

            if self.game_ball.velocity[1] > 0:
                projected_y_position = projected_y_position - (
                    steps_to_undo * self.game_ball.velocity[1]
                )
            elif self.game_ball.velocity[1] < 0:
                projected_y_position = projected_y_position + (
                    steps_to_undo * self.game_ball.velocity[1]
                )

        if self.rect.top >= 0:
            if projected_y_position < self.rect.top:
                self.rect.move_ip(0, -self.speed)
        if self.rect.bottom <= self.world_dimensions[1]:
            if projected_y_position > self.rect.bottom:
                self.rect.move_ip(0, self.speed)
