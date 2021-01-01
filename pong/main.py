import math
import random
import time
from typing import Tuple, Sequence, List, Union

import pygame
import pygame_menu
from pygame.constants import K_UP, K_DOWN, K_ESCAPE


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


class Bat(pygame.sprite.Sprite):
    def __init__(
        self,
        initial_position: Tuple[int, int],
        world_dimensions: Tuple[int, int],
        key_up: pygame.constants = K_UP,
        key_down: pygame.constants = K_DOWN,
        speed: Union[float, int] = 5
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


class Game:
    ball_speeds = sorted(
        [("slow", 5), ("medium", 10), ("fast", 15)], key=lambda element: element[1]
    )
    bat_speeds = sorted(
        [("slow", 5), ("medium", 10), ("fast", 15)], key=lambda element: element[1]
    )

    pygame.init()

    def __init__(self):
        # Initialise basic py game stuff
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

        # Initialise the bats and ball(s) and associated sprite groups
        self.bats = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.ball = Ball(
            initial_velocity_vector=self._get_random_vector(),
            world_dimensions=(self.width, self.height),
            speed=self.ball_speeds[1][1],
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

        # Initialise player state
        self.player1_score = 0
        self.player2_score = 0
        self.winning_player = None

        # Setup the game menu
        self.menu = pygame_menu.menu.Menu(
            300, 400, "Main Menu", theme=pygame_menu.themes.THEME_BLUE
        )
        self.menu.add_selector(
            "Ball Speed: ",
            self.ball_speeds,
            onchange=lambda _, speed: self.ball.update_speed(speed),
            default=1,
        )
        self.menu.add_selector(
            "Bat Speed: ",
            self.ball_speeds,
            onchange=lambda _, speed: self._update_bat_speeds(speed),
            default=1,
        )

        self.menu.add_button("Play", lambda: self.menu.disable())
        self.menu.add_button(
            "Quit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        )

    def _update_bat_speeds(self, new_speed):
        for bat in self.bats:
            bat.speed = new_speed

    def _display_winner(self):
        winner_text = self.font_small.render(
            f"{self.winning_player} is the winner!", True, (255, 255, 255)
        )
        text_width = winner_text.get_rect().width
        text_height = winner_text.get_rect().height
        self._display_surf.blit(
            winner_text,
            ((self.width - text_width) / 2, (self.height - text_height) / 2),
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
            return

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_ESCAPE]:
            self.menu.enable()

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
            events = pygame.event.get()
            if self.menu.is_enabled():
                self.menu.draw(self._display_surf)
                self.menu.update(events)
                pygame.display.update()
            else:
                for event in events:
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
