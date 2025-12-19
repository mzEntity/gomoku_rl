from constant import WIDTH, WIN_LEN
from constant import MCTS_HEURISTIC_WEIGHT, MCTS_ROLLOUT_WEIGHT, MCTS_SELECT_UCT, MCTS_SIMU_COUNT_PER_SEARCH

from constant import ROLLOUT_DEPTH, ROLLOUT_PER_SIMU
from constant import HEURISTIC_CFG


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
    def __init__(self, env: GomokuEnv, n_simulations: int, c_uct: float, 
                rollout: Rollout, rollout_weight: float, 
                heuristic: Heuristic, heuristic_weight: float):
        self.env = env
        
        self.n_simulations = n_simulations
        self.c_uct = c_uct
        
        self.rollout = rollout
        self.heuristic = heuristic
        
        self.rollout_weight = rollout_weight
        self.heuristic_weight = heuristic_weight
        
        
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
            value_rollout = self.rollout.estimate_value(cur_node.state)
            value_heuristic = self.heuristic.estimate_value(cur_node.state)

            value = self.rollout_weight * value_rollout + self.heuristic_weight * value_heuristic
                
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
    agent = MCTS(
        GomokuEnv(), MCTS_SIMU_COUNT_PER_SEARCH, MCTS_SELECT_UCT, 
        Rollout(ROLLOUT_PER_SIMU, ROLLOUT_DEPTH), MCTS_ROLLOUT_WEIGHT, 
        Heuristic(HEURISTIC_CFG), MCTS_HEURISTIC_WEIGHT
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