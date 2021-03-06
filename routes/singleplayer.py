import sys
from typing import List

import pygame

from player.local_player import LocalPlayer
from routes.route import Route
from utils.coin import Coin
from utils.level_bar import LevelBar
from utils.tile import Tile, TileImages


class Singleplayer(Route):

    def __init__(self, board_name: str = "../singleplayer_board"):
        self.is_builder_level = False if board_name == "../singleplayer_board" else True
        tile_images = TileImages(50).images
        self.grid: List[List[Tile]] = []
        self.danger_tiles: List[Tile] = []
        self.field_size = 50
        self.coins: List[Coin] = []
        self.grid_width, p_start, self.end_tile = self.make_grid(tile_images, board_name)
        self.level_camera_speed = 0
        self.player = LocalPlayer(1, *p_start)
        self.level_bar = LevelBar(self.field_size, tile_images)
        self.phase = 'game'
        self.font = pygame.font.Font("freesansbold.ttf", 100)
        self.background_image = pygame.image.load("res/tiles/background.png").convert_alpha()
        self.background_rects = []
        bg_counter = 0
        while bg_counter < self.grid_width:
            self.background_rects.append(
                self.background_image.get_rect(topleft=(bg_counter, 0))
            )
            bg_counter += self.background_image.get_width()
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def make_grid(self, tile_images, board_name):
        p_start = None
        end_tile = None
        with open(f'boards/builder_boards/{board_name}.txt') as file:
            x = file.readlines()
            grid_width = len(x[0]) * self.field_size - 1
            for i, line in enumerate(x):
                # add barrier field
                for k in range(6):
                    self.grid.append(
                        [Tile(-self.field_size * (k+1), (i + 1) * self.field_size,
                              self.field_size, tile_images, 'b', 'brick')])
                for j, c, in enumerate(line):
                    if c == '\n':
                        break
                    if c == 'c':
                        self.grid[i].append(
                            Tile(j * self.field_size, (i + 1) * self.field_size, self.field_size, tile_images))
                        self.coins.append(Coin(self.grid[i][j + 1].rect.centerx, self.grid[i][j + 1].rect.centery,
                                               tile_images['coin']))
                    elif c == '#':
                        filename = 'dirt'
                        if i != 0 and self.grid[i-1][j+1].type != '#':
                            filename = 'grass'
                        self.grid[i].append(
                            Tile(j * self.field_size, (i + 1) * self.field_size,
                                 self.field_size, tile_images, '#', filename))
                    elif c == 'A':
                        self.grid[i].append(
                            Tile(j * self.field_size, (i + 1) * self.field_size,
                                 self.field_size, tile_images, 'A', 'thorns'))
                        self.danger_tiles.append(self.grid[i][j + 1])
                    elif c == 'e':
                        # print(self.grid[i-1][j+1].img)
                        self.grid[i-1][j+1] = Tile(
                            j * self.field_size, i * self.field_size, self.field_size, tile_images, 'd', 'door_up'
                        )
                        # print(self.grid[i-1][j+1].img)
                        self.grid[i].append(
                            Tile(j * self.field_size, (i + 1) * self.field_size,
                                 self.field_size, tile_images, 'd', 'door_down'))
                        end_tile = self.grid[i][j+1]
                    else:
                        if c == 's':
                            p_start = (j * self.field_size, (i + 1) * self.field_size + self.field_size // 2)
                        self.grid[i].append(
                            Tile(j * self.field_size, (i + 1) * self.field_size, self.field_size, tile_images))
                # add barrier field
                for k in range(6):
                    self.grid[i].append(
                        Tile((j + k) * self.field_size, (i + 1) * self.field_size,
                             self.field_size, tile_images, 'b', 'brick'))
        return grid_width, p_start, end_tile

    def draw(self, win: pygame.Surface) -> None:
        for rect in self.background_rects:
            win.blit(self.background_image, rect)
        for row in self.grid:
            for tile in row:
                if tile.rect.colliderect(win.get_rect()):
                    tile.draw(win)
        for coin in self.coins:
            if coin.rect.colliderect(win.get_rect()):
                coin.draw(win)
        self.player.draw(win)
        self.level_bar.draw(win)

        if self.phase == 'lose':
            text_obj = self.font.render("YOU LOST", False, (200, 0, 0))
            win.blit(text_obj, text_obj.get_rect(midbottom=win.get_rect().center))
        elif self.phase == 'won':
            text_obj = self.font.render("YOU WON", False, (0, 200, 0))
            win.blit(text_obj, text_obj.get_rect(midbottom=win.get_rect().center))

    def update_state(self) -> 'Route':
        if self.phase == 'game':
            self.camera()
            self.update_tiles()
            self.player.update(self.grid, [])
            self.check_danger_fields()

        for row in self.grid:
            for tile in row:
                if tile.type != '.':
                    for arrow in self.player.bow.fly_arrows:
                        if (abs(arrow.angle) >= 90 and tile.rect.collidepoint(arrow.rect.midleft)) or (
                                abs(arrow.angle) < 90 and tile.rect.collidepoint(arrow.rect.midright)):
                            self.player.bow.fly_arrows.remove(arrow)

        for coin in self.coins:
            if self.player.rect.colliderect(coin.rect):
                self.coins.remove(coin)
                self.level_bar.increase_coin_counter()
            for arrow in self.player.bow.fly_arrows:
                # if (abs(arrow.angle) >= 90 and coin.rect.collidepoint(arrow.rect.midleft)) \
                #         or (abs(arrow.angle) < 90 and coin.rect.collidepoint(arrow.rect.midright)):
                if coin.rect.colliderect(arrow.rect):
                    self.coins.remove(coin)
                    self.level_bar.increase_coin_counter()
                    self.player.bow.fly_arrows.remove(arrow)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.USEREVENT and self.phase == 'game':
                self.level_bar.increase_time_counter()
            if self.level_bar.menu_button.is_mouse(event):
                if self.is_builder_level:
                    from routes.level_builder_menu import LevelBuilderMenu
                    return LevelBuilderMenu()
                else:
                    from routes.menu import Menu
                    return Menu((1000, 700))
        return self

    def camera(self):
        move = False
        if self.player.direction == "right" and self.player.is_moving:
            if self.player.rect.centerx >= 700:
                self.player.speed = 0
                self.level_camera_speed = -2
                move = True
        if self.player.direction == "left" and self.player.is_moving:
            if self.player.rect.centerx <= 300:
                self.player.speed = 0
                self.level_camera_speed = 2
                move = True
        if not move:
            self.player.speed = 2
            self.level_camera_speed = 0

    def update_tiles(self):
        if self.level_camera_speed != 0:
            player_blocks_state = self.player.is_on_block(self.grid)
            for field_list in self.grid:
                for tile in field_list:
                    if "left" not in player_blocks_state and "right" not in player_blocks_state:
                        tile.rect.x += self.level_camera_speed
            for coin in self.coins:
                if "left" not in player_blocks_state and "right" not in player_blocks_state:
                    coin.rect.x += self.level_camera_speed
            for rect in self.background_rects:
                if "left" not in player_blocks_state and "right" not in player_blocks_state:
                    rect.x += self.level_camera_speed

    def check_danger_fields(self):
        for tile in self.danger_tiles:
            if self.player.rect.collidepoint(tile.rect.center):
                pygame.mixer.music.load("res/thorns_hit.wav")
                pygame.mixer.music.play()
                self.phase = 'lose'
        if self.player.rect.collidepoint(self.end_tile.rect.topright):
            pygame.mixer.music.load("res/win.wav")
            pygame.mixer.music.play()
            self.phase = 'won'
