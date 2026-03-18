import os
import sys

# 确保 src 目录在路径中 (如果在某些 IDE 运行需要)
if 'src' not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.model import RuralVillageModel
from src.utils.yaml_loader import config
# 导入可视化模块 (对应 src/visualize.py)
import src.visualize as visualize

def run_simulation():
    print("=== 乡土社会多智能体模拟器启动 ===")
    
    # [1. 开头自动建 outputs 文件夹]
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录已确认: ./{output_dir}/")

    model = RuralVillageModel()
    steps = config["SIMULATION_STEPS"]

    print(f"开始模拟，共 {steps} 年...")

    # [2. 主循环]
    for step in range(steps):
        # 执行模拟一步
        model.step()
        
        # 每 10 步保存一次可视化快照
        if step % 10 == 0:
            current_step_num = model.current_step
            print(f"年份：{current_step_num:3d} | 正在保存可视化快照...")
            
            # 调用具体的绘图函数
            visualize.draw_network(model, current_step_num)
            visualize.draw_personality_distribution(model, current_step_num)
            visualize.draw_social_indices(model, current_step_num)
            
            # 打印简要进度
            norm = model.get_community_norm()
            c_score = norm.get('尽责性C', 0.0)
            rel_count = model.history['relation_count'][-1]
            print(f"       -> 平均尽责性: {c_score:.2f}, 当前关系数: {rel_count}")

    # [3. 最后画：人格演化趋势图]
    print("正在生成全程人格演化趋势图...")
    visualize.draw_personality_trend(model)
    
    print("=== 模拟完成 ===")
    print(f"所有结果已保存至 ./{output_dir}/ 目录")
    print("文件列表:")
    print("  - network_step_X.png      (社会网络快照)")
    print("  - personality_dist_step_X.png (人格分布快照)")
    print("  - social_indices_step_X.png   (社会指标快照)")
    print("  - personality_trend.png   (全程演化趋势)")

if __name__ == "__main__":
    run_simulation()