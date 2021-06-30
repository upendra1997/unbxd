from itertools import count
from copy import deepcopy
from collections import namedtuple
import itertools
import os


class Symbol:

    def __init__(self, symbol) -> None:
        self.symbol = symbol

    def __str__(self):
        return self.symbol


class Empty(Symbol):
    def __init__(self) -> None:
        super().__init__("_")


class Player:
    id_iter = count()

    def __init__(self, symbol: Symbol):
        self.symbol = symbol

    def id(self):
        return id(self)


class DummyPlayer(Player):

    def __init__(self):
        super().__init__(" ")

    def id(self):
        return 0


class Board():
    def __init__(self, board_size: tuple[int, int]) -> None:
        self.rows = board_size[0]
        self.columns = board_size[1]
        self._board = [[Empty() for j in range(self.columns)]
                       for i in range(self.rows)]

    def __str__(self):
        s = [[str(e) for e in row] for row in self._board]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '|'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        return '\n'.join(table)

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board: list[list[Symbol]]):
        self._board = board


class GameAction:
    def __init__(self) -> None:
        pass

    def __str__(self):
        return "GameAction"

    def transform(state):
        return state


History = namedtuple("history", ["board", "action", "meta"])


class GameOverException(Exception):
    pass

class TieException(GameOverException):
    pass


class Game():
    def __init__(self, board: Board) -> None:
        self._players = []
        self.board = board
        self.history = [History(deepcopy(board), None, {})]
        self._current_player = None
        self._available_actions = []

    @property
    def player(self):
        return self._current_player or DummyPlayer()

    @property
    def players(self):
        return self._players

    @property
    def available_actions(self):
        return self._available_actions

    @player.setter
    def player(self, player: Player):
        self._current_player = player

    @players.setter
    def players(self, players: list[players]):
        self._players = players
        self._players_iterator = itertools.cycle(self._players)
        self.player = next(self._players_iterator)

    @available_actions.setter
    def available_actions(self, available_actions):
        self._available_actions = []
        for action in available_actions:
            action.game = self
            self._available_actions.append(action)

    def next_player(self):
        self.player = next(self._players_iterator)

    def __str__(self):
        history = "\n\n".join(
            map(lambda h: f'''{str(h.board)} {str(h.action)} {str(h.meta)}''', self.history))
        return f'''current player: {self.player.id()}, symbol: {self.player.symbol}''' \
            + '\n' \
            + f'''{self.board}''' \
            + '''\n\n''' \
            + '''Logs:''' \
            + '''\n''' \
            + f'''{history}''' \
            + '''\n'''

    def act(self, action: GameAction):
        self.history = []

    def turn(self, action: GameAction, meta: dict[any, any]):
        self.history.append(History(deepcopy(self.board), action, meta))
        self.next_player()

    def win(self):
        return True


class Place(GameAction):
    def __init__(self) -> None:
        super().__init__()
        self.game = None

    def apply(self, row, col):
        state = self.game.board
        new_board = Board((state.rows, state.columns))
        new_board._board = deepcopy(state._board)
        new_board._board[row][col] = self.game.player.symbol
        self.game.board = new_board
        self.game.turn(self, {})

    @staticmethod
    def string():
        return "Place"

    def __str__(self):
        return self.string()


def screen_clear():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')


class TicTacToe(Game):
    def __init__(self) -> None:
        board = Board((3, 3))
        super().__init__(board)
        player1 = Player(Symbol("X"))
        player2 = Player(Symbol("O"))
        self.players = [player1, player2]
        self.available_actions = [Place()]
        self.counter = 0

    def win(self):
        def win_indexes(n):
            # Rows
            for r in range(n):
                yield [(r, c) for c in range(n)]
            for c in range(n):
                yield [(r, c) for r in range(n)]
            yield [(i, i) for i in range(n)]
            yield [(i, n - 1 - i) for i in range(n)]

        n = 3
        for indexes in win_indexes(n):
            if all(self.board.board[r][c].symbol == "X" for r, c in indexes):
                return True
        for indexes in win_indexes(n):
            if all(self.board.board[r][c].symbol == "O" for r, c in indexes):
                return True
        return False
    
    def turn(self, action: GameAction, meta: dict[any, any]):
        m = {
            "palyer": self.player,
        }
        if self.win():
            m["win"] = self.player
        meta |= m
        super().turn(action, meta)
        if self.win():
            raise GameOverException("Game Over")
        self.counter+=1
        if self.counter > 9:
            raise TieException("Game Tie")



if __name__ == '__main__':
    game = TicTacToe()
    while True:
        try:
            print(game)
            action_input = input(
                f"Possible actions: [ {' '.join(map(str, game.available_actions))} ]\n",)
            game_action = None
            for action in game.available_actions:
                if str(action_input) == Place.string():
                    [x, y] = map(int, input(
                        "enter x and y coordinates: ").split(" "))
                    game_action = action.apply(x, y)
            print('-'*80)
        except IndexError:
            continue
        except GameOverException:
            print('-'*80)
            print(game.history[-1].board)
            print(f'{game.history[-1].meta["win"]} won')
            print("Game Over")
            break