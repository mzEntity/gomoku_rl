from __future__ import annotations

from game import GameAction, GameState

from typing import Tuple, Optional, Dict, List

import math
import random


class MCTSNode:
    def __init__(self, state: GameState, parent: Optional[MCTSNode]=None):
        self.state: GameState = state
        
        self._parent: Optional[MCTSNode] = parent
        self._children: Dict[GameAction, MCTSNode] = dict()
        
        self._visit_count: int = 0      # N
        self._total_value: float = 0.0  # W
        
        
    def is_leaf(self) -> bool:
        return len(self._children) == 0
    
    
    def is_root(self) -> bool:
        return self._parent is None
    
    
    def is_terminal(self) -> bool:
        return self.state.done
    
    
    def is_fully_expanded(self) -> bool:
        return len(self._children) == len(self.state.legal_actions)
    
        
    def select_child(self, scalar: float) -> Tuple[GameAction, MCTSNode]:
        if self.is_leaf():
            raise ValueError("select_child cannot called by leaf node.")
        best_score = -math.inf
        best_action_list = []
        for a, c in self._children.items():
            if c._visit_count != 0:
                exploit = c._total_value / c._visit_count
                explore = math.sqrt(2.0 * math.log(self._visit_count) / float(c._visit_count))
                # print(f"{exploit:.4f}, {explore:.4f}")
                score = -exploit + scalar * explore
            else:
                score = math.inf
            
            if score == best_score:
                best_action_list.append(a)
            elif score > best_score:
                best_action_list = [a]
                best_score = score
        
        best_action = random.choice(best_action_list)
        return (best_action, self._children[best_action])
    
    
    def get_child_action_list(self) -> List[GameAction]:
        return list(self._children.keys())
    

    def select_legal_unexpanded_action(self) -> GameAction:
        legal_unexpanded_candidates = [action for action in self.state.legal_actions if action not in self._children]
        return random.choice(legal_unexpanded_candidates)
    

    def expand(self, action: GameAction, next_state: GameState) -> MCTSNode:
        if action in self._children:
            raise ValueError("Action already exists in child node list.")
        new_node = MCTSNode(next_state, self)
        self._children[action] = new_node
        return new_node
    
    
    def update(self, value: float) -> None:
        self._visit_count += 1
        self._total_value += value
        
        
    def backup(self, value: float) -> None:
        self.update(value)
        if self._parent is not None:
            self._parent.backup(-value)
            
    
    def get_visit_distribution(self) -> Dict[GameAction, float]:
        if self._visit_count == 0:
            return {}
        visit_distribution = {}
        for a, c in self._children.items():
            visit_distribution[a] = c._visit_count / self._visit_count
        return visit_distribution
    
    