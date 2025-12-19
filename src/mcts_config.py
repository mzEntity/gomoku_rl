class MCTSConfig:
    def __init__(self, simu_count_per_search: int, c_uct: float, 
                 rollout_per_simu: int, rollout_depth: int, rollout_heuristic_config,
                 rollout_important_pos_weight: int, rollout_other_pos_weight: int, rollout_use_heuristic_epsilon: float, 
                 heuristic_config,
                 rollout_weight: float, heuristic_weight: float,
                 use_break_early: bool=False):
        self.simu_count_per_search = simu_count_per_search
        self.c_uct = c_uct
        
        self.rollout_per_simu = rollout_per_simu
        self.rollout_depth = rollout_depth
        self.rollout_heuristic_config = rollout_heuristic_config
        
        self.rollout_important_pos_weight = rollout_important_pos_weight
        self.rollout_other_pos_weight = rollout_other_pos_weight
        self.rollout_use_heuristic_epsilon = rollout_use_heuristic_epsilon
        
        self.heuristic_config = heuristic_config
        
        self.rollout_weight= rollout_weight
        self.heuristic_weight = heuristic_weight
        
        self.use_break_early = use_break_early