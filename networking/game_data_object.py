from typing import List, Dict

from networking.player_data_object import PlayerDataObject
from utils.field import Field


class GameDataObject:

    def __init__(self):
        self.players: Dict[int, PlayerDataObject] = {}
        self.grid: List[List[Field]] = []
        self.field_size = 50
        self.alive = 0
        self.time_to_start = 10
        self.winner = None
        self.make_grid()

    def make_grid(self):
        for i in range(0, 1000, self.field_size):
            self.grid.append([])
            for j in range(0, 700, self.field_size):
                self.grid[i // self.field_size].append(Field(i, j, self.field_size))
        with open("boards/multiplayer_board.txt") as file:
            x = file.readlines()
            for i, line in enumerate(x):
                for j, c in enumerate(line):
                    if c == '\n':
                        break
                    if c == '#':
                        self.grid[j][i].color = (0, 0, 0)
                        self.grid[j][i].type = '#'

    def add_player(self, player_id: int, x: int):
        self.players.setdefault(player_id, PlayerDataObject(player_id, x, 10))
        self.alive += 1

    def remove_player(self, player_id: int):
        self.players.pop(player_id)
        self.alive -= 1

    def update(self, player: PlayerDataObject):

        if len(player.hit_players_ids) > 0:
            for p_hit_tuple in player.hit_players_ids:
                self.players[p_hit_tuple[0]].is_hit = True
                self.players[p_hit_tuple[0]].hit_direction = p_hit_tuple[1]
            player.hit_players_ids = None

        if player.y < 650:
            self.players[player.id].x = player.x
            self.players[player.id].y = player.y
            self.players[player.id].is_moving = player.is_moving
            self.players[player.id].direction = player.direction
            self.players[player.id].arm_up = player.arm_up
        elif player.id in self.players:
            self.remove_player(player.id)

        if player.updated_hit:
            self.players[player.id].is_hit = False
            self.players[player.id].hit_direction = None
