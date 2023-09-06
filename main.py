#!/bin/python3
# 
# Flappy bird

import pygame
from pygame.locals import *
import os
import random


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60


def load_image(name: str) -> tuple[pygame.Surface, pygame.Rect]:
    image = pygame.image.load(os.path.join("data", name)).convert_alpha()
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    
    return image, image.get_rect()


def load_font(name: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(os.path.join("data", name), size)


class Player:

    def __init__(self) -> None:
        self.image, self.rect = load_image("flappy.png")
        self.rect = self.rect.inflate(-8, -8)
        self.start()
    
    def start(self) -> None:
        self.gravity = 6
        self.rect.midleft = (40, SCREEN_HEIGHT // 2)
        self.jump = 0
    
    def update(self) -> None:
        self.rect.move_ip(0, self.gravity - self.jump)
        self.jump = max(self.jump - 1, -self.gravity)

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        elif self.rect.top <= 0:
            self.rect.top = 1
            self.jump = self.gravity
    
    def dojump(self) -> None:
        self.jump = 23


class Obstacle(pygame.sprite.Sprite):

    @classmethod
    def new(cls, hole_height: int):
        width = 80
        hole_top = random.randint(21, SCREEN_HEIGHT - 20 - hole_height)

        surf_top = pygame.Surface((width, hole_top - 1))
        surf_top.fill("green2")
        rect_top = surf_top.get_rect()
        surf_bot = pygame.Surface((width, SCREEN_HEIGHT - hole_top - hole_height))
        surf_bot.fill("green2")
        rect_bot = surf_bot.get_rect(bottom=(SCREEN_HEIGHT))

        return [Obstacle(surf_top, rect_top), Obstacle(surf_bot, rect_bot)]

    def __init__(self, image: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.rect = rect
        self.rect.right = SCREEN_WIDTH
        self.image = image
    
    def update(self) -> int:
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
            return 1
        return 0    


class Game:

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background = self.screen
        pygame.display.set_caption("flappy")
        self.clock = pygame.time.Clock()
        self.heading = load_font("upheavtt.ttf", 80)
        self.font = load_font("upheavtt.ttf", 50)
        self.score = 0
        self.score_rect = pygame.rect.Rect(0, 0, 80, 80)
        self.score_rect.topright = (SCREEN_WIDTH - 10, 10)


    def start(self):
        title = self.heading.render("flappy bird", False, "white")
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 300))
        play = (self.font.render("play!", False, "white"), self.font.render("Play!", True, "red"))
        play_rect = play[0].get_rect(center=(SCREEN_WIDTH // 2, 400))
        play_i = 0
        highscore = self.font.render(f"highscore: {self.read_score()}", False, "white")
        highscore_rect = highscore.get_rect(bottomleft=(10, SCREEN_HEIGHT - 10))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            mouse_pos = pygame.mouse.get_pos()
            if play_rect.collidepoint(mouse_pos):
                play_i = 1
                if pygame.mouse.get_pressed()[0]:
                    break
            else:
                play_i = 0
            
            self.screen.fill("deepskyblue")
            self.background.blit(title, title_rect)
            self.background.blit(play[play_i], play_rect)
            self.background.blit(highscore, highscore_rect)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            self.clock.tick(FPS)

        self.play()

    def play(self):
        self.score = 0
        hole_size = 250
        obstacle_count = 0
        player = Player()
        obstacles = pygame.sprite.Group([Obstacle.new(hole_size)])
        NEW_OBSTACLE = pygame.USEREVENT
        pygame.time.set_timer(NEW_OBSTACLE, 1000)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_q or event.key == K_ESCAPE:
                        return
                    if event.key == K_SPACE:
                        player.dojump()
                elif event.type == NEW_OBSTACLE:
                    obstacles.add(Obstacle.new(hole_size))
                    obstacle_count += 1
                    if obstacle_count % 5 == 0 and hole_size > 150:
                        hole_size -= 10

            # Do logical updates here.
            player.update()
            for i, obstacle in enumerate(obstacles):
                plus = obstacle.update()
                if i % 2 == 0:
                    self.score += plus

            # Fill the display with a solid color
            self.screen.fill("deepskyblue")  

            # Render the graphics here.
            self.screen.blit(player.image, player.rect)
            obstacles.draw(self.screen)

            score_image = self.heading.render(str(self.score), False, "white")
            self.screen.blit(score_image, self.score_rect)

            if pygame.sprite.spritecollideany(player, obstacles):
                self.background = self.screen.copy()
                break

            pygame.display.flip()  # Refresh on-screen display
            self.clock.tick(FPS)

        self.write_score()
        self.start()
    
    def write_score(self) -> None:
        num = int(self.read_score())
        if num < self.score:
            with open("highscore", "w", encoding="utf-8") as file:
                file.write(str(self.score))

    def read_score(self) -> str:
        with open("highscore", "r", encoding="utf-8") as file:
            text = file.read(3)
            if len(text) == 0:
                return "0"
            return text


if __name__ == "__main__":
    g = Game()
    g.start()
