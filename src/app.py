import gradio as gr
import os
from constant import WIDTH, BLACK, WHITE, EMPTY
from mcts import MCTS, GomokuEnv
from game import GameAction, GameState, Game


class GomokuGUI:
    def __init__(self, game: Game, agent: MCTS):
        self.game = game
        self.agent = agent
        
        self.reset()
        self.demo = self._init_interface()
        
        
    def reset(self):
        self.game.reset()
        self.update_state()
        
        self.search_result = None
        self.predict_result = None
        
    
    def search(self):
        state = self.game.get_state()
        player = state.next_player
        color = "黑" if player == BLACK else "白"
        best_action, visit_rate_dict = self.agent.search(state)
        
        self.predict_result = best_action
        self.search_result = visit_rate_dict
        if best_action is not None:
            return f"Agent认为{color}棋的最佳选择是：({best_action.x}, {best_action.y})", best_action.x, best_action.y
        return "游戏已经结束", 0, 0
        

    def place(self, row_idx, col_idx):
        cur_player = self.game.get_current_player()
        color = "黑" if cur_player == BLACK else "白"
        
        action = GameAction(row_idx, col_idx)
        ok = self.game.execute_action(action)
        if not ok:
            return "行为不合法"
        self.game.check(action)        
        return f"在({row_idx},{col_idx})处放置{color}棋"
    
    
    def update_state(self):
        self.state = self.game.get_state()

        
    def render_game_info(self):
        """
        将 List[List[int]] 转换为 HTML 格式的棋盘展示。
        - {EMPTY}: 空白
        - {BLACK}: 黑子 (●)
        - {WHITE}: 白子 (○)
        """
        html = """
        <style>
            .chess-board {
                border-collapse: collapse;
                margin: 10px auto;
                background-color: white !important;
            }
            .chess-cell {
                width: 30px;
                height: 30px;
                border: 1px solid black !important;
                padding: 0 !important;
                box-sizing: border-box;
            }
            .chess-cell-inner {
                width: 100%;
                height: 100%;

                display: flex;
                align-items: center;
                justify-content: center;

                background-color: white !important;
                color: black !important;
                font-size: 18px;
            }
        </style>
        <table class="chess-board">
    """
        board = self.state.board
        for row in board:
            html += "<tr>"
            for cell in row:
                symbol = "●" if cell == BLACK else "○" if cell == WHITE else " "
                html += f'<td class="chess-cell"><div class="chess-cell-inner">{symbol}</div></td>'
            html += "</tr>"

        html += "</table>"
        return html
    
    
    def render_predict_info(self):
        """
        将 List[List[float]] 转换为 HTML 格式的棋盘展示。
        """
        html = """
        <style>
            .predict-board {
                border-collapse: collapse;
                margin: 10px auto;
                background-color: white !important;
            }
            .predict-cell {
                width: 30px;
                height: 30px;
                border: 1px solid black !important;
                padding: 0 !important;
                box-sizing: border-box;
            }
            .predict-cell-inner {
                width: 100%;
                height: 100%;

                display: flex;
                align-items: center;
                justify-content: center;

                background-color: white !important;
                color: black !important;
                font-size: 15px;
            }
        </style>
        <table class="predict-board">
    """
        predict_board = [[0.0] * WIDTH for _ in range(WIDTH)]
        if self.search_result is not None:
            for action, visit_rate in self.search_result.items():
                predict_board[action.x][action.y] = visit_rate
                
        for row in predict_board:
            html += "<tr>"
            for cell in row:
                html += f'<td class="predict-cell"><div class="predict-cell-inner">{cell:.2f}</div></td>'
            html += "</tr>"

        html += "</table>"
        return html
    

    def _init_interface(self):
        with gr.Blocks() as demo:
            with gr.Row():
                with gr.Column():
                    game_render = gr.HTML()
                    predict_render = gr.HTML()
                with gr.Column():
                    with gr.Row():
                        row_idx = gr.Number(label=f"Row(0-{WIDTH-1})")
                        col_idx = gr.Number(label=f"Col(0-{WIDTH-1})")
                        
                    with gr.Row():
                        reset_btn = gr.Button("Reset")
                        place_btn = gr.Button("Place")
                        search_btn = gr.Button("Search")
                    msg_output = gr.Textbox(label="", container=False)
            
            demo.load(
                self.update_state, inputs=[], outputs=[]
            ).then(
                self.render_game_info, inputs=[], outputs=[game_render]
            ).then(
                self.render_predict_info, inputs=[], outputs=[predict_render]
            )
            
            place_btn.click(
                self.place, inputs=[row_idx, col_idx], outputs=[msg_output]
            ).then(
                self.update_state, inputs=[], outputs=[]
            ).then(
                self.render_game_info, inputs=[], outputs=[game_render]
            )
            
            search_btn.click(
                self.search, inputs=[], outputs=[msg_output, row_idx, col_idx]
            ).then(
                self.render_predict_info, inputs=[], outputs=[predict_render]
            )
            
            reset_btn.click(
                self.reset, inputs=[], outputs=[]
            ).then(
                self.update_state, inputs=[], outputs=[]
            ).then(
                self.render_game_info, inputs=[], outputs=[game_render]
            ).then(
                self.render_predict_info, inputs=[], outputs=[predict_render]
            )
        return demo


if __name__ == "__main__":
    os.environ["NO_PROXY"] = "localhost,127.0.0.1,192.168.0.*"
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    
    n_simulations = 100
    c_uct = 1
    
    game = Game()
    agent = MCTS(GomokuEnv(), use_rollout=False, use_heuristic=True)

    gui = GomokuGUI(game, agent)
    demo = gui.demo
    demo.launch()