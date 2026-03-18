import matplotlib.pyplot as plt
import numpy as np
from src.utils.yaml_loader import config

PERSONALITY_DIMS = config["PERSONALITY_DIMS"]

def plot_personality_distribution(model, step):
    """绘制全村人格维度均值柱状图 (适配 Mesa 4.0)"""
    data = {dim: [] for dim in PERSONALITY_DIMS}
    
    # ✅ 修改点：从 model.agents 获取智能体
    # Mesa 4.0 中 model.agents 通常是一个字典 {id: agent}，我们需要遍历 values()
    # 如果 model.agents 是集合或列表，则直接遍历
    agents = list(model.agents.values()) if isinstance(model.agents, dict) else list(model.agents)
    
    if not agents:
        print("警告：未找到任何智能体，无法绘制分布图。")
        return

    for agent in agents:
        for dim in PERSONALITY_DIMS:
            # 确保 agent 有 personality 属性
            if hasattr(agent, 'personality') and dim in agent.personality:
                data[dim].append(agent.personality[dim])
            else:
                data[dim].append(0.0) # 默认值
    
    # 计算均值，防止空列表报错
    means = [np.mean(data[dim]) if data[dim] else 0.0 for dim in PERSONALITY_DIMS]

    plt.figure(figsize=(10, 5)) # 稍微加宽一点
    plt.bar(PERSONALITY_DIMS, means, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    plt.ylim(-1, 1)
    plt.title(f"第 {step} 年 村民人格均值分布")
    plt.ylabel("平均得分 (-1 ~ 1)")
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_personality_evolution(history):
    """绘制人格随时间演化曲线"""
    if not history:
        print("警告：历史数据为空，无法绘制演化图。")
        return

    steps = list(range(len(history)))
    plt.figure(figsize=(12, 6))
    
    for dim in PERSONALITY_DIMS:
        # 安全提取数据，防止某个维度缺失
        values = [h.get(dim, 0.0) if isinstance(h, dict) else getattr(h, dim, 0.0) for h in history]
        plt.plot(steps, values, label=dim, linewidth=2)
        
    plt.title("村民人格随时间演化")
    plt.xlabel("模拟年份")
    plt.ylabel("维度平均值 (-1~1)")
    plt.legend(loc='best')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()