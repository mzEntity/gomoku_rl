from typing import List, Tuple, ClassVar

from constant import WIDTH, WIN_LEN, EMPTY, FIRST_PLAYER

class GameAction:
    EMPTY_ACTION: ClassVar["GameAction"]
    ALL_ACTIONS: ClassVar[List["GameAction"]]
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if not isinstance(other, GameAction):
            return False
        if self.x != other.x or self.y != other.y:
            return False
        return True
    
    def __hash__(self):
        return hash((self.x, self.y))


GameAction.EMPTY_ACTION = GameAction(-1, -1)
GameAction.ALL_ACTIONS = [GameAction(x, y) for x in range(WIDTH) for y in range(WIDTH)]


class GameState:
    EMPTY_STATE: ClassVar["GameState"]
    
    def __init__(
        self, 
        board: Tuple[Tuple[int, ...], ...], 
        next_player: int, 
        last_move: GameAction, 
        step: int, 
        done: bool, 
        winner: int
    ):
        self.board = board
        self.next_player = next_player
        self.last_move = last_move
        self.step = step
        
        self.done = done
        self.winner = winner
        self._init_next_legal_actions()
        
        
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        if self.board != other.board or self.next_player != other.next_player:
            return False
        return True


    def __hash__(self):
        return hash((self.board, self.next_player))

    
    def _init_next_legal_actions(self):
        if self.done:
            self.legal_actions = tuple()
        else:
            self.legal_actions = tuple([
                action 
                for action in GameAction.ALL_ACTIONS 
                if self.board[action.x][action.y] == EMPTY
            ])
            
    def __repr__(self):
        board = self.board
        s = ""
        for row in board:
            for cell in row:
                s += f"|{cell:2}"
            s += "|\n"
        s += f"last move: ({self.last_move.x}, {self.last_move.y}). next player: {self.next_player}. done: {self.done}. winner: {self.winner}."
        return s

    
GameState.EMPTY_STATE = GameState(
    tuple([tuple([EMPTY] * WIDTH) for _ in range(WIDTH)]), 
    FIRST_PLAYER, 
    GameAction.EMPTY_ACTION, 
    0, False, EMPTY
)


# execute_action -> check -> (get_state) -> execute_action ->... -> execute_action -> check -> get_result
class Game:
    def __init__(self, state: GameState=GameState.EMPTY_STATE):
        self._width: int = WIDTH
        self._win_len: int = WIN_LEN
        self._total_cell_count: int = WIDTH * WIDTH
        self.load(state)
        
        
    def reset(self):
        self.load(GameState.EMPTY_STATE)
        
    
    def load(self, state: GameState):
        self._board: List[List[int]] = [list(row) for row in state.board]
        self._player = state.next_player
        self._last_move = state.last_move
        self._step = state.step
        
        self._done = state.done
        self._winner = state.winner
        
        self._checked = True
        
    
    def get_current_player(self) -> int:
        return self._player
        
            
    def get_state(self) -> GameState:
        if not self._checked:
            raise ValueError("call get_state when game is not checked")
        board = tuple(tuple(row) for row in self._board)
        return GameState(board, self.get_current_player(), self._last_move, self._step, self._done, self._winner)
    
    
    def get_pos_state(self, x: int, y: int) -> int:
        return self._board[x][y]
            
    
    def is_action_legal(self, action: GameAction) -> bool:
        x, y = action.x, action.y
        return (not self._done) and self.get_pos_state(x, y) == EMPTY
    
    
    def execute_action(self, action: GameAction) -> bool:
        if not self.is_action_legal(action):
            return False
        x, y = action.x, action.y
        self._board[x][y] = self.get_current_player()
        self._last_move = action
        self._player *= -1
        self._step += 1
        self._checked = False
        
        return True
    
    
    def get_result(self):
        if not self._checked:
            raise ValueError("call get_result when game is not checked")
        return (self._done, self._winner)
        
    
    def check(self, last_action: GameAction) -> bool:
        x, y = last_action.x, last_action.y
        
        winner = self._check_win_based_on_idx(x, y)
        if winner != EMPTY:
            # somebody wins
            self._done = True
            self._winner = winner
        elif self._check_draw():
            # draw
            self._done = True
            self._winner = EMPTY
        else:
            # not done
            self._done = False
            self._winner = EMPTY
        self._checked = True
        return self._done
            
                    
    def _check_win_based_on_idx(self, x: int, y: int) -> int:
        player = self.get_pos_state(x, y)
        if player == EMPTY:
            return EMPTY
        # check 4 directions
        dirs = [(1,0),(0,1),(1,1),(1,-1)]
        for dx, dy in dirs:
            cnt = 1
            # forward
            i = 1
            while True:
                nx, ny = x + dx*i, y + dy*i
                if 0 <= nx < self._width and 0 <= ny < self._width and self.get_pos_state(nx, ny) == player:
                    cnt += 1
                    i += 1
                else:
                    break
            # backward
            i = 1
            while True:
                nx, ny = x - dx*i, y - dy*i
                if 0 <= nx < self._width and 0 <= ny < self._width and self.get_pos_state(nx, ny) == player:
                    cnt += 1
                    i += 1
                else:
                    break
            if cnt >= self._win_len:
                return player
        return EMPTY
    
    
    def _check_draw(self) -> bool:
        return self._step == self._total_cell_count