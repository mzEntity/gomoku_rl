from constant import EMPTY, WIDTH, WIN_LEN
from game import GameState


class Heuristic:
    def __init__(self, heuristic_config):
        self.width = WIDTH
        self.win_len = WIN_LEN
        self.directions = [(0,1), (1,0), (1,1), (-1,1)]
        
        self.advantage_weight = heuristic_config['advantage_weight']
        self.empty_advantage_weight = heuristic_config['empty_advantage_weight']
        
        self.advantage_weight_dict = heuristic_config['advantage_weight_dict']
        self.empty_advantage_weight_dict = heuristic_config['empty_advantage_weight_dict']
        
    
    def cal_left_to_right(self, board, player):
        ans_2 = [[0] * self.width for _ in range(self.width)]
        ans_1 = [[0] * self.width for _ in range(self.width)]
        for x in range(self.width):
            cur_length = 0
            for y in range(self.width):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                
            cur_length = 0
            for y in range(self.width-1, -1, -1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length  
        return ans_1, ans_2
    
    def cal_top_to_bottom(self, board, player):
        ans_2 = [[0] * self.width for _ in range(self.width)]
        ans_1 = [[0] * self.width for _ in range(self.width)]
        for y in range(self.width):
            cur_length = 0
            for x in range(self.width):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                
            cur_length = 0
            for x in range(self.width-1, -1, -1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length
        return ans_1, ans_2
    
    def cal_left_top_to_right_bottom(self, board, player):
        ans_2 = [[0] * self.width for _ in range(self.width)]
        ans_1 = [[0] * self.width for _ in range(self.width)]
        
        for start_y in range(self.width):
            cur_length = 0
            y = start_y
            x = 0
            for i in range(self.width-start_y):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                x += 1
                y += 1
            
            cur_length = 0
            y = start_y
            x = self.width-1
            for i in range(start_y+1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length
                x -= 1
                y -= 1
                
        for start_x in range(self.width):
            cur_length = 0
            x = start_x
            y = 0
            for _ in range(self.width-start_x):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                x += 1
                y += 1
            
            cur_length = 0
            x = start_x
            y = self.width-1
            for _ in range(start_x+1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length
                x -= 1
                y -= 1
                
        return ans_1, ans_2
                
    def cal_left_bottom_to_right_top(self, board, player):
        ans_2 = [[0] * self.width for _ in range(self.width)]
        ans_1 = [[0] * self.width for _ in range(self.width)]
        
        for start_y in range(self.width):
            cur_length = 0
            y = start_y
            x = 0
            for _ in range(start_y+1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length
                x += 1
                y -= 1
            
            cur_length = 0
            y = start_y
            x = self.width-1
            for _ in range(self.width-start_y):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                x -= 1
                y += 1
                
        for start_x in range(self.width):
            cur_length = 0
            x = start_x
            y = 0
            for _ in range(start_x+1):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_2[x][y] = cur_length
                x -= 1
                y += 1
            
            cur_length = 0
            x = start_x
            y = self.width-1
            for _ in range(self.width-start_x):
                if board[x][y] == player:
                    cur_length += 1
                else:
                    cur_length = 0
                ans_1[x][y] = cur_length
                x += 1
                y -= 1
                
        return ans_1, ans_2
    
    def cal_all_length(self, board, player):
        d = {}
        ans_1, ans_2 = self.cal_left_to_right(board, player)
        d[(0, 1)] = [ans_1, ans_2]
        ans_1, ans_2 = self.cal_top_to_bottom(board, player)
        d[(1, 0)] = [ans_1, ans_2]
        ans_1, ans_2 = self.cal_left_top_to_right_bottom(board, player)
        d[(1, 1)] = [ans_1, ans_2]
        ans_1, ans_2 = self.cal_left_bottom_to_right_top(board, player)
        d[(-1, 1)] = [ans_1, ans_2]
        return d
        

    def is_empty(self, board, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.width:
            return False
        return board[x][y] == EMPTY
      
    def cal_open_dict(self, board, all_length_dict):
        open_dict = {i: {'both': 0, 'half': 0, 'close': 0}for i in range(2, self.win_len+1)}
        for dir in self.directions:
            dx, dy = dir
            ans1, ans2 = all_length_dict[dir]
            for x in range(self.width):
                for y in range(self.width):                   
                    length1, length2 = ans1[x][y], ans2[x][y]
                    if length2 != 1:
                        continue
                    
                    total_length = length1 + length2 - 1
                    if total_length <= 1:
                        continue
                    
                    next_x, next_y = x + length1 * dx, y + length1 * dy
                    prev_x, prev_y = x - length2 * dx, y - length2 * dy
                    prev_empty = self.is_empty(board, prev_x, prev_y)
                    next_empty = self.is_empty(board, next_x, next_y)
                    
                    if total_length >= self.win_len:
                        total_length = self.win_len
                        
                    if prev_empty and next_empty:
                        open_dict[total_length]['both'] += 1
                    elif prev_empty or next_empty:
                        open_dict[total_length]['half'] += 1
                    else:
                        open_dict[total_length]['close'] += 1
        return open_dict
     
    def cal_empty_open_dict(self, board, all_length_dict):
        all_empty_open_dict = {}
        for x in range(self.width):
            for y in range(self.width):
                if board[x][y] != EMPTY:
                    continue
                
                new_open_dict = {i: {'both': 0, 'half': 0, 'close': 0}for i in range(2, self.win_len+1)}
                for dir in self.directions:
                    dx, dy = dir
                    ans1, ans2 = all_length_dict[dir]
                    prev_x, prev_y = x - dx, y - dy
                    next_x, next_y = x + dx, y + dy
                    prev_length, next_length = 0, 0
                    if prev_x >= 0 and prev_x < self.width and prev_y >= 0 and prev_y < self.width:
                        prev_length = ans2[prev_x][prev_y]
                    if next_x >= 0 and next_x < self.width and next_y >= 0 and next_y < self.width:
                        next_length = ans1[next_x][next_y]
                        
                    new_length = prev_length + next_length + 1
                    if new_length <= 1:
                        continue
                    
                    prev_end_x, prev_end_y = prev_x - dx * prev_length, prev_y - dy * prev_length
                    next_end_x, next_end_y = next_x + dx * next_length, next_y + dx * next_length
                    
                    prev_empty = self.is_empty(board, prev_end_x, prev_end_y)
                    next_empty = self.is_empty(board, next_end_x, next_end_y)
                    
                    if new_length >= self.win_len:
                        new_length = self.win_len
                    
                    if prev_empty and next_empty:
                        new_open_dict[new_length]['both'] += 1
                    elif prev_empty or next_empty:
                        new_open_dict[new_length]['half'] += 1
                    else:
                        new_open_dict[new_length]['close'] += 1
                
                all_empty_open_dict[(x, y)] = new_open_dict
        return all_empty_open_dict
    
    
    def opponent_is_already_win(self, open_dict) -> bool:
        win_len = self.win_len
        #  .ooooo. & .oooooX & XoooooX
        if open_dict[win_len]['both'] >= 1 or open_dict[win_len]['half'] >= 1 or open_dict[win_len]['close'] >= 1:
            return True
        
        # .oooo.
        if open_dict[win_len-1]['both'] >= 1:
            return True
        
        return False
                    
    def player_is_already_win(self, open_dict, empty_open_dict) -> bool:
        win_len = self.win_len
        #  .ooooo. & .oooooX & XoooooX
        if open_dict[win_len]['both'] >= 1 or open_dict[win_len]['half'] >= 1 or open_dict[win_len]['close'] >= 1:
            return True
        
        # .oooo. & .ooooX
        if open_dict[win_len-1]['both'] >= 1 or open_dict[win_len-1]['half'] >= 1:
            return True
    
        # .ooo.
        if open_dict[win_len-2]['both'] >= 1:
            return True
        
        for empty_point, cur_empty_open_dict in empty_open_dict.items():
            # .ooooo. & .oooooX & XoooooX
            if cur_empty_open_dict[win_len]['both'] >= 1 or cur_empty_open_dict[win_len]['half'] >= 1 or cur_empty_open_dict[win_len]['close'] >= 1:
                return True
            
            # .oooo.
            if cur_empty_open_dict[win_len-1]['both'] >= 1:
                return True
            
            # (.ooooX, .ooooX)
            if cur_empty_open_dict[win_len-1]['half'] >= 2:
                return True
            
            # (.ooo., .ooo.)
            if cur_empty_open_dict[win_len-2]['both'] >= 2:
                return True
            
        return False
    
    def cal_advantage_value(self, open_dict) -> float:
        win_len = self.win_len
        
        d = {
            "both_n2": 0,
            "half_n1": 0,
            "both_n3": 0,
            "half_n2": 0,
            "half_n3": 0
        }
        
        d['both_n2'] += open_dict[win_len-2]['both']
        d['half_n1'] += open_dict[win_len-1]['half']
        d['both_n3'] += open_dict[win_len-3]['both']
        d['half_n2'] += open_dict[win_len-2]['half']
        d['half_n3'] += open_dict[win_len-3]['half']
        
        value = 0.0
        for title, occur_count in d.items():
            if title in self.advantage_weight_dict:
                value += occur_count * self.advantage_weight_dict[title]
        
        return value
    
    def cal_empty_advantage_value(self,empty_open_dict) -> float:
        win_len = self.win_len
        
        d = {
            "both_n2": 0,
            "half_n1": 0,
            "both_n3": 0,
            "half_n2": 0,
            "half_n3": 0
        }
        for start_point, cur_empty_open_dict in empty_open_dict.items():
            d['both_n2'] += cur_empty_open_dict[win_len-2]['both']
            d['half_n1'] += cur_empty_open_dict[win_len-1]['half']
            d['both_n3'] += cur_empty_open_dict[win_len-3]['both']
            d['half_n2'] += cur_empty_open_dict[win_len-2]['half']
            d['half_n3'] += cur_empty_open_dict[win_len-3]['half']
        
        value = 0.0
        for title, occur_count in d.items():
            if title in self.empty_advantage_weight_dict:
                value += occur_count * self.empty_advantage_weight_dict[title]
        
        return value
        

    def estimate_value(self, state: GameState) -> float:      
        if state.done:
            return 0.0
        
        board = state.board
        player = state.next_player
    # def estimate_value(self, board, player) -> float:        
        
        opponent = player * -1
        
        player_all_length_dict = self.cal_all_length(board, player)
        player_open_dict = self.cal_open_dict(board, player_all_length_dict)
        player_empty_open_dict = self.cal_empty_open_dict(board, player_all_length_dict)
        
        if self.player_is_already_win(player_open_dict, player_empty_open_dict):
            return 1.0
        
        opponent_all_length_dict = self.cal_all_length(board, opponent)
        opponent_open_dict = self.cal_open_dict(board, opponent_all_length_dict)
        opponent_empty_open_dict = self.cal_empty_open_dict(board, opponent_all_length_dict)
        
        if self.opponent_is_already_win(opponent_open_dict):
            return -1.0
        
        player_ad_value = self.cal_advantage_value(player_open_dict)
        opponent_ad_value = self.cal_advantage_value(opponent_open_dict)
        ad_value = 0
        if player_ad_value + opponent_ad_value != 0:
            ad_value = (player_ad_value - opponent_ad_value) / (player_ad_value + opponent_ad_value)
        
        player_empty_ad_value = self.cal_empty_advantage_value(player_empty_open_dict)
        opponent_empty_ad_value = self.cal_empty_advantage_value(opponent_empty_open_dict)
        empty_ad_value = 0
        if player_empty_ad_value + opponent_empty_ad_value != 0:
            empty_ad_value = (player_empty_ad_value - opponent_empty_ad_value) / (player_empty_ad_value + opponent_empty_ad_value)
        
        return ad_value * self.advantage_weight + empty_ad_value * self.empty_advantage_weight
    

def print_matrix(matrix):
    print("--------------------------------")
    for row in matrix:
        for cell in row:
            print(f"| {cell:2} ", end="")
        print("|")