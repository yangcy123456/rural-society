from src.model import RuralVillageModel
from src.utils.yaml_loader import config
from src.visualize import plot_personality_distribution, plot_personality_evolution

def run_simulation():
    print("=== 乡土社会多智能体模拟器启动 ===")
    model = RuralVillageModel()
    history = []
    steps = config["SIMULATION_STEPS"]

    for step in range(steps):
        model.step()
        community_norm = model.get_community_norm()
        history.append(community_norm)
        if step % 20 == 0:
            print(f"年份：{step:2d} | 平均尽责性: {community_norm['尽责性C']:.2f}")

    # 可视化结果
    plot_personality_distribution(model, steps)
    plot_personality_evolution(history)
    print("=== 模拟完成 ===")

if __name__ == "__main__":
    run_simulation()