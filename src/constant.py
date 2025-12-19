from typing import Dict

# game
BLACK: int = 1
WHITE: int = BLACK * -1
EMPTY: int = 0
FIRST_PLAYER: int = BLACK

WIDTH: int = 10
WIN_LEN: int = 5


# mcts
MCTS_SIMU_COUNT_PER_SEARCH = 1000
MCTS_SELECT_UCT = 0.1
MCTS_ROLLOUT_WEIGHT: float = 0.0
MCTS_HEURISTIC_WEIGHT: float = 1.0 - MCTS_ROLLOUT_WEIGHT


# rollout
ROLLOUT_PER_SIMU = 20
ROLLOUT_DEPTH = 20


# heuristic
HEURISTIC_ADVANTAGE_WEIGHT_DICT: Dict[str, int] = {
    "both_n2": 12,
    "half_n1": 10,
    "both_n3": 5,
    "half_n2": 6,
    "half_n3": 2
}

HEURISTIC_EMPTY_ADVANTAGE_WEIGHT_DICT: Dict[str, int] = {
    "both_n2": 8,
    "half_n1": 7,
    "both_n3": 3,
    "half_n2": 4,
    "half_n3": 1
}

HEURISTIC_ADVANTAGE_WEIGHT: float = 0.7
HEURISTIC_EMPTY_ADVANTAGE_WEIGHT: float = 1.0 - HEURISTIC_ADVANTAGE_WEIGHT