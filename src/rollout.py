from game import GameAction, GameState, Game

from typing import Tuple

from heuristic import Heuristic

import random

def get_next_state(state: GameState, action: GameAction) -> GameState:
    if state in GameState.NEXT_STATE_MAP and action in GameState.NEXT_STATE_MAP[state]:
        # print("hit")
        return GameState.NEXT_STATE_MAP[state][action]
    
    game_inst = Game(state)
    ok = game_inst.execute_action(action)
    if not ok:
        raise ValueError("next_state: illegal action.")        
    game_inst.check(action)
    
    next_state = game_inst.get_state()
    GameState.NEXT_STATE_MAP.setdefault(state, dict())
    GameState.NEXT_STATE_MAP[state][action] = next_state
    return next_state


def get_terminal_value(state: GameState) -> float: 
    if not state.done:
        raise ValueError("get_value for a non terminated state.")
    if state.winner == 0:
        return 0
    return state.winner * state.next_player


class Rollout:
    def __init__(self, n_rollout: int, depth: int, heuristic: Heuristic, important_pos_weight: int, other_pos_weight: int, epsilon: float):
        self.n_rollout = n_rollout
        self.depth = depth
        self.heuristic = heuristic
        # self.heuristic = None
        self.important_pos_weight = important_pos_weight
        self.other_pos_weight = other_pos_weight
        self.epsilon = epsilon
        
        
    def estimate_value(self, state: GameState) -> float:
        cur_player = state.next_player
        total_value = 0
        for i in range(self.n_rollout):
            # print(f"{i}/{self.n_rollout}")
            final_state, depth = self.roll_out(state)
            if self.heuristic:
                final_value, _ = self.heuristic.estimate_value(final_state)
                if final_state.next_player == cur_player:
                    total_value += final_value
                else:
                    total_value -= final_value
            else:
                total_value = final_state.winner * cur_player
            
        
        value = total_value / self.n_rollout
        # print(value, total_value)
        return value
    
    
    def roll_out(self, state: GameState) -> Tuple[GameState, int]:
        game_inst = Game(state)
        cur_depth = 0
        while not state.done and cur_depth < self.depth:
            legal_action_list = state.legal_actions
            if self.heuristic and random.random() < self.epsilon:
                _, important_pos_list = self.heuristic.estimate_value(state)
                # print(len(legal_action_list), len(important_pos_list))
                weights = []
                for action in legal_action_list:
                    if (action.x, action.y) in important_pos_list:
                        weights.append(self.important_pos_weight)
                    else:
                        weights.append(self.other_pos_weight)
                
                action = random.choices(legal_action_list, weights=weights, k=1)[0]
            else:
                action = random.choice(legal_action_list)
            ok = game_inst.execute_action(action)
            if not ok:
                return state, cur_depth
            game_inst.check(action)
            state = game_inst.get_state()
            cur_depth += 1
        return state, cur_depth
    
    
def print_matrix(matrix):
    print("--------------------------------")
    for row in matrix:
        for cell in row:
            print(f"| {cell:2} ", end="")
        print("|")