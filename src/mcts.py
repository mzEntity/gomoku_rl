from constant import WIDTH, WIN_LEN
from constant import MCTS_HEURISTIC_WEIGHT, MCTS_ROLLOUT_WEIGHT, MCTS_SELECT_UCT, MCTS_SIMU_COUNT_PER_SEARCH

from constant import ROLLOUT_DEPTH, ROLLOUT_PER_SIMU, ROLLOUT_IMPORTANT_POS_WEIGHT, ROLLOUT_OTHER_POS_WEIGHT, ROLLOUT_USE_HEURISTIC_EPSILON
from constant import HEURISTIC_CFG


from game import GameAction, GameState, Game
from mcts_node import MCTSNode

from heuristic import Heuristic
from rollout import Rollout, get_next_state, get_terminal_value

from typing import List, Optional, Dict, Tuple
import random, math

import time
    
   
class MCTS:
    def __init__(self, n_simulations: int, c_uct: float, 
                rollout: Rollout, rollout_weight: float, 
                heuristic: Heuristic, heuristic_weight: float):
        self.n_simulations = n_simulations
        self.c_uct = c_uct
        
        self.rollout = rollout
        self.heuristic = heuristic
        
        self.rollout_weight = rollout_weight
        self.heuristic_weight = heuristic_weight
        
        
    def search(self, root_state: GameState):
        start = time.time()
        root_node = MCTSNode(root_state)
        if root_node.is_terminal():
            return None, dict()
        
        for i in range(self.n_simulations):
            break_early = self.simulation(root_node)
            if break_early:
                print(f"{i}/{self.n_simulations} break early")
                break
        
        max_visit_rate = -math.inf
        max_visit_action = None
        visit_rate_dict = root_node.get_visit_distribution()
        for action ,visit_rate in visit_rate_dict.items():
            if max_visit_rate < visit_rate:
                max_visit_rate   = visit_rate
                max_visit_action = action
                
        GameState.NEXT_STATE_MAP.clear()
        end = time.time()
        print(f"搜索时间: {end-start:.4f}s")
        return max_visit_action, visit_rate_dict
        
        
    def simulation(self, root_node: MCTSNode) -> bool:
        cur_node = root_node
        root_child = None
        # selection
        while not cur_node.is_terminal() and cur_node.is_fully_expanded():
            _, cur_node = cur_node.select_child(self.c_uct)
            if root_child is None:
                root_child = cur_node
        
        if not cur_node.is_terminal():
            # expansion
            action = cur_node.select_legal_unexpanded_action()
            next_state = get_next_state(cur_node.state, action)
            cur_node = cur_node.expand(action, next_state)
            if root_child is None:
                root_child = cur_node
            
        if cur_node.is_terminal():
            value = get_terminal_value(cur_node.state)
        else:
            value_rollout = self.rollout.estimate_value(cur_node.state)
            value_heuristic, _ = self.heuristic.estimate_value(cur_node.state)
            value = self.rollout_weight * value_rollout + self.heuristic_weight * value_heuristic
                
        cur_node.backup(value)
        
        if root_child is not None and root_child.is_dominate(self.n_simulations):
            return True
        return False


    
    
def print_visit_rate(visit_rate_dict: Dict[GameAction, float]):
    predict_board = [[0.0] * WIDTH for _ in range(WIDTH)]
    if visit_rate_dict is not None:
        for action, visit_rate in visit_rate_dict.items():
            predict_board[action.x][action.y] = visit_rate
    for row in predict_board:
        for cell in row:
            print(f"|{cell:.2f}", end="")
        print("|")
            
        
if __name__ == "__main__":
    game = Game()
    
    heuristic = Heuristic(HEURISTIC_CFG)
    agent = MCTS(
        MCTS_SIMU_COUNT_PER_SEARCH, MCTS_SELECT_UCT, 
        Rollout(ROLLOUT_PER_SIMU, ROLLOUT_DEPTH, heuristic, ROLLOUT_IMPORTANT_POS_WEIGHT, ROLLOUT_OTHER_POS_WEIGHT, ROLLOUT_USE_HEURISTIC_EPSILON), MCTS_ROLLOUT_WEIGHT, 
        heuristic, MCTS_HEURISTIC_WEIGHT
    )
    
    for i in range(10):
        cur_state = game.get_state()
        print(cur_state)
        if cur_state.done:
            print(f"finish")
            break
        action, visit_rate_dict = agent.search(cur_state)
        print_visit_rate(visit_rate_dict)
        if action is not None:
            print(f"choose action ({action.x}, {action.y})")
            ok = game.execute_action(action)
            if not ok:
                print("get illegal action")
                break
            else:
                game.check(action)
    cur_state = game.get_state()
    print(cur_state)