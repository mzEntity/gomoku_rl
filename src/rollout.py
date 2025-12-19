from constant import ROLLOUT_PER_SIMU, ROLLOUT_DEPTH
from game import GameAction, GameState, Game

from typing import Tuple

import random

class Rollout:
    def __init__(self):
        self.n_rollout = ROLLOUT_PER_SIMU
        self.depth = ROLLOUT_DEPTH
        
        
    def estimate_value(self, state: GameState) -> float:
        win_count = 0
        lose_count = 0
        draw_count = 0
        for _ in range(self.n_rollout):
            winner, depth = self.roll_out(state)
            if winner == state.next_player:
                win_count += 1
            elif winner == 0:
                draw_count += 1
            else:
                lose_count += 1
        value = (win_count - lose_count) / self.n_rollout
        return value
    
    
    def roll_out(self, state: GameState) -> Tuple[int, int]:
        game_inst = Game(state)
        cur_depth = 0
        while not state.done and cur_depth < self.depth:
            legal_action_list = state.legal_actions
            action = random.choice(legal_action_list)
            ok = game_inst.execute_action(action)
            if not ok:
                return 0, cur_depth
            game_inst.check(action)
            state = game_inst.get_state()
            cur_depth += 1
        return state.winner, cur_depth