import random
import time

import pygame
import pygame_menu
from pygame.constants import K_ESCAPE

from pong.balls import Ball
from pong.bats import Bat, ComputerBat


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

        player2_bat = ComputerBat(
            initial_position=(self.width, int(self.height / 2)),
            world_dimensions=(self.width, self.height),
            game_ball=self.ball,
        )
        # player2_bat = Bat(
        #     initial_position=(self.width, int(self.height / 2)),
        #     world_dimensions=(self.width, self.height),
        #     key_up=pygame.constants.K_w,
        #     key_down=pygame.constants.K_s,
        # )

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
        self.menu.add_button("Play", lambda: self.menu.disable())
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
        self._display_surf.blit(
            player2_score, (self.width - player2_score.get_rect().width - 10, 10)
        )

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
