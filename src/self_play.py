from constant import WIDTH, WIN_LEN
from constant import MCTS_HEURISTIC_WEIGHT, MCTS_ROLLOUT_WEIGHT, MCTS_SELECT_UCT, MCTS_SIMU_COUNT_PER_SEARCH

from constant import ROLLOUT_DEPTH, ROLLOUT_PER_SIMU, ROLLOUT_IMPORTANT_POS_WEIGHT, ROLLOUT_OTHER_POS_WEIGHT, ROLLOUT_USE_HEURISTIC_EPSILON
from constant import HEURISTIC_CFG

from mcts_config import MCTSConfig


from game import GameAction, GameState, Game
from mcts_node import MCTSNode

from heuristic import Heuristic
from rollout import Rollout, get_next_state, get_terminal_value

from typing import List, Optional, Dict, Tuple
import random, math

import time

from mcts import MCTS

from utils import save_dict_to_file

def one_self_play():
    mcts_cfg1 = MCTSConfig(
        MCTS_SIMU_COUNT_PER_SEARCH, MCTS_SELECT_UCT, 
        ROLLOUT_PER_SIMU, ROLLOUT_DEPTH, HEURISTIC_CFG, 
        ROLLOUT_IMPORTANT_POS_WEIGHT, ROLLOUT_OTHER_POS_WEIGHT, ROLLOUT_USE_HEURISTIC_EPSILON, 
        HEURISTIC_CFG,
        MCTS_ROLLOUT_WEIGHT, MCTS_HEURISTIC_WEIGHT
    )
    
    mcts_cfg2 = MCTSConfig(
        MCTS_SIMU_COUNT_PER_SEARCH, MCTS_SELECT_UCT, 
        ROLLOUT_PER_SIMU, ROLLOUT_DEPTH, HEURISTIC_CFG, 
        ROLLOUT_IMPORTANT_POS_WEIGHT, ROLLOUT_OTHER_POS_WEIGHT, ROLLOUT_USE_HEURISTIC_EPSILON, 
        HEURISTIC_CFG,
        MCTS_ROLLOUT_WEIGHT, MCTS_HEURISTIC_WEIGHT
    )
    
    agent1 = MCTS(mcts_cfg1)
    agent2 = MCTS(mcts_cfg2)
    
    game = Game()
    
    search_history_list = []
    
    step_idx = 0
    while True:
        step_idx += 1
        cur_state = game.get_state()
        # print(cur_state)
        if cur_state.done:
            break
        print(f"start search {step_idx}/{WIDTH * WIDTH}")
        action1, visit_rate_dict1 = agent1.search(cur_state)
        if action1 is not None:
            # print(f"{cur_state.next_player} choose action ({action1.x}, {action1.y})")
            ok = game.execute_action(action1)
            if not ok:
                print("get illegal action")
                break
            else:
                search_history_list.append((cur_state, visit_rate_dict1))
                game.check(action1)
        
        step_idx += 1
        cur_state = game.get_state()
        # print(cur_state)
        if cur_state.done:
            break
        print(f"start search {step_idx}/{WIDTH * WIDTH}")
        action2, visit_rate_dict2 = agent2.search(cur_state)
        if action2 is not None:
            # print(f"{cur_state.next_player} choose action ({action2.x}, {action2.y})")
            ok = game.execute_action(action2)
            if not ok:
                print("get illegal action")
                break
            else:
                search_history_list.append((cur_state, visit_rate_dict2))
                game.check(action2)
                
                
    if not cur_state.done:
        print("not done but break")
    
    self_play_exp_list = []
    for search_ret in search_history_list:
        self_play_exp_list.append((search_ret[0], search_ret[1], cur_state.winner))
    
    # print(cur_state)
    return self_play_exp_list

def self_play(n_self_play):
    total_exp_list = []
    for i in range(n_self_play):
        self_play_exp_list = one_self_play()
        total_exp_list.extend(self_play_exp_list)
    
    useful_exp_list = []
    for exp in total_exp_list:
        state = exp[0]
        visit_rate_dict = exp[1]
        result = exp[2]
        
        policy = [[0.0] * WIDTH for _ in range(WIDTH)]
        for action, visit_rate in visit_rate_dict.items():
            policy[action.x][action.y] = visit_rate
        
        useful_exp_list.append({
            "state": {
                "board": state.board,
                "next_player": state.next_player
            },
            "policy": policy,
            "result": result
        })
    
    return useful_exp_list


if __name__ == "__main__":
    base = 20
    self_play_count = 10
    for i in range(self_play_count):
        print(f"self play {i+base+1}/{self_play_count+base}")
        result = self_play(1)
        save_dict_to_file(result, f"storage/{(i+base):04}.json")
        print(f"save to storage/{(i+base):04}.json")