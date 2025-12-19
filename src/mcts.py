from constant import WIDTH, WIN_LEN
from constant import MCTS_SIMU_COUNT_PER_SEARCH, MCTS_SELECT_UCT, MCTS_HEURISTIC_WEIGHT, MCTS_ROLLOUT_WEIGHT


from game import GameAction, GameState, Game
from mcts_node import MCTSNode

from heuristic import Heuristic
from rollout import Rollout

from typing import List, Optional, Dict, Tuple
import random, math

class GomokuEnv:
    def __init__(self):
        self.width = WIDTH
        self.win_len = WIN_LEN
        
                        
    def next_state(self, state: GameState, action: GameAction) -> GameState:
        game_inst = Game(state)
        ok = game_inst.execute_action(action)
        if not ok:
            raise ValueError("next_state: illegal action.")        
        game_inst.check(action)

        return game_inst.get_state()
    
    
    def get_value(self, state: GameState) -> float: 
        if not state.done:
            raise ValueError("get_value for a non terminated state.")
        if state.winner == 0:
            return 0
        return state.winner * state.next_player
        
        
class MCTS:
    def __init__(self, env: GomokuEnv, use_rollout: bool = False, use_heuristic: bool = True):
        self.env = env
        
        self.n_simulations = MCTS_SIMU_COUNT_PER_SEARCH
        self.c_uct = MCTS_SELECT_UCT
        
        self.rollout = None
        self.heuristic = None
        if use_rollout:
            self.rollout = Rollout()
        if use_heuristic:
            self.heuristic = Heuristic()
        
        
    def search(self, root_state: GameState):
        root_node = MCTSNode(root_state)
        if root_node.is_terminal():
            return None, dict()
        
        for _ in range(self.n_simulations):
            self.simulation(root_node)
        
        max_visit_rate = -math.inf
        max_visit_action = None
        visit_rate_dict = root_node.get_visit_distribution()
        for action ,visit_rate in visit_rate_dict.items():
            if max_visit_rate < visit_rate:
                max_visit_rate   = visit_rate
                max_visit_action = action
        return max_visit_action, visit_rate_dict
        
        
    def simulation(self, root_node: MCTSNode):
        cur_node = root_node
        # selection
        while not cur_node.is_terminal() and cur_node.is_fully_expanded():
            _, cur_node = cur_node.select_child(self.c_uct)
        
        if not cur_node.is_terminal():
            # expansion
            action = cur_node.select_legal_unexpanded_action()
            next_state = self.env.next_state(cur_node.state, action)
            cur_node = cur_node.expand(action, next_state)
            
        if cur_node.is_terminal():
            value = self.env.get_value(cur_node.state)
        else:
            value = 0
            if self.rollout is not None and MCTS_ROLLOUT_WEIGHT > 0:
                value_rollout = self.rollout.estimate_value(cur_node.state)
                value = value_rollout
                
            if self.heuristic is not None and MCTS_HEURISTIC_WEIGHT > 0:
                value_heuristic = self.heuristic.estimate_value(cur_node.state)
                value = value_heuristic
            
            if self.rollout is not None and self.heuristic is not None and 0 < MCTS_ROLLOUT_WEIGHT < 1.0:
                value = MCTS_ROLLOUT_WEIGHT * value_rollout + MCTS_HEURISTIC_WEIGHT * value_heuristic
                
        # print(value)
        cur_node.backup(value)


    
    
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
    agent = MCTS(GomokuEnv(), use_rollout=True, use_heuristic=True)
    
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