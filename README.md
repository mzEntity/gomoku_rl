# gomoku_rl

基于强化学习的五子棋Agent

## 运行方法

```bash
gradio src/app.py
```

## 文件说明

- `constant.py`: 常量定义
- `game.py`: 五子棋状态、动作、环境定义
- `mcts_node.py`: 蒙特卡洛搜索节点定义
- `mcts.py`: 蒙特卡洛搜索算法
- `rollout.py`: 蒙特卡洛展开
- `heuristic.py`: 基于经验的盘面评估
- `app.py`: gradio界面