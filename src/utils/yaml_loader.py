import yaml
import os

def load_config(config_name="config.yaml"):
    """
    加载 YAML 配置文件。
    自动定位到项目根目录的 config 文件。
    """
    # 1. 获取当前文件所在的目录 (src/utils/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 向上两级找到项目根目录 (src/utils/ -> src/ -> root)
    # 假设目录结构是: root/src/utils/yaml_loader.py
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    
    # 3. 构建配置文件的绝对路径
    config_path = os.path.join(project_root, config_name)
    
    # 4. [文件不存在时报错]
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"配置文件未找到！\n"
            f"期望路径: {config_path}\n"
            f"请确保 {config_name} 位于项目根目录下。"
        )
    
    # 5. 加载配置
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                raise ValueError("配置文件为空或格式不正确")
            return data
    except yaml.YAMLError as e:
        raise RuntimeError(f"YAML 解析失败: {e}")

# [配置只加载一次]
# 模块导入时立即执行，后续所有 import config 的地方都共享这个内存对象
try:
    config = load_config()
except Exception as e:
    # 如果是导入阶段出错，打印错误并重新抛出，阻止程序继续运行
    print(f"[严重错误] 初始化配置失败: {e}")
    raise