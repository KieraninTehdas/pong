import math
from typing import Sequence, List, Union

import pygame


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
        self.velocity: List[float] = self._normalise_velocity(
            initial_velocity_vector, self.speed
        )
        self.containing_world_dimensions = world_dimensions

    @staticmethod
    def _normalise_velocity(
        velocity: Sequence[Union[int, float]], speed: int
    ) -> List[float]:
        norm_factor = speed / math.sqrt(
            sum([velocity_component ** 2 for velocity_component in velocity])
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
        self.velocity = self._normalise_velocity(initial_velocity_vector, self.speed)
        self.rect = self.surf.get_rect()
        self.rect = self.surf.get_rect(
            center=(
                int(self.containing_world_dimensions[0] / 2),
                int(self.containing_world_dimensions[1] / 2) - 10,
            )
        )

    def update_speed(self, new_speed: int):
        self.speed = new_speed
        self.velocity = self._normalise_velocity(self.velocity, self.speed)
