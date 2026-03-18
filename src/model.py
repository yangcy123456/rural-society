print("开始加载 src/model.py")

from mesa import Model
from src.agent import Villager
from src.network import RelationNetwork
from src.utils.yaml_loader import config
import numpy as np

PERSONALITY_DIMS = config["PERSONALITY_DIMS"]
NUM_VILLAGERS = config["NUM_VILLAGERS"]

class RuralVillageModel(Model):
    def __init__(self):
        super().__init__()
        self.num_villagers = NUM_VILLAGERS
        
        # 初始化网络
        self.network = RelationNetwork(self)
        
        # 初始化历史数据收集器
        self.history = {
            'mean_personality': [],
            'std_personality': [],
            'relation_count': []
        }
        
        # 初始化步数计数器 (用于图片命名和进度追踪)
        self.current_step = 0
        
        self._create_villagers()
        
        # 收集初始状态 (Step 0)
        self._collect_data()

    def _create_villagers(self):
        """初始化所有村民"""
        for i in range(self.num_villagers):
            family = f"家_{np.random.randint(0, 30)}"
            villager = Villager(
                unique_id=i,
                model=self,
                name=f"村民{i}",
                gender=np.random.choice(["男", "女"]),
                age=np.random.randint(0, 70),
                family=family
            )
            
            self.network.add_villager(villager)
            
            # 自动添加家族内部关系 (在 add_villager 中已部分处理，这里确保显式添加或补充)
            # 注意：add_villager 内部已经加了家族边，这里不需要重复加，除非逻辑分离
            # 为保险起见，依赖 network.py 中的 add_villager 逻辑即可
            
        # [重要] 所有村民添加完毕后，初始化随机邻居关系
        self.network.initialize_random_neighbors(probability=0.3)

    def get_community_norm(self):
        """获取全村平均人格"""
        mean_personality = {}
        all_values = {dim: [] for dim in PERSONALITY_DIMS}
        
        # Mesa 4.0 兼容：处理 agents 可能是 dict 或 list
        agents_list = list(self.agents.values()) if isinstance(self.agents, dict) else list(self.agents)
        
        for agent in agents_list:
            if hasattr(agent, 'personality'):
                for dim in PERSONALITY_DIMS:
                    val = agent.personality.get(dim, 0.0)
                    all_values[dim].append(val)
        
        for dim in PERSONALITY_DIMS:
            mean_personality[dim] = np.mean(all_values[dim]) if all_values[dim] else 0.0
        return mean_personality

    def _collect_data(self):
        """收集当前步的数据到 history"""
        current_norm = self.get_community_norm()
        mean_vec = [current_norm[dim] for dim in PERSONALITY_DIMS]
        
        std_vec = []
        agents_list = list(self.agents.values()) if isinstance(self.agents, dict) else list(self.agents)
        
        for dim in PERSONALITY_DIMS:
            values = [a.personality.get(dim, 0.0) for a in agents_list if hasattr(a, 'personality')]
            std_vec.append(np.std(values) if len(values) > 1 else 0.0)
        
        relation_count = len(self.network.G.edges()) if hasattr(self.network, 'G') else 0
            
        self.history['mean_personality'].append(mean_vec)
        self.history['std_personality'].append(std_vec)
        self.history['relation_count'].append(relation_count)

    def step(self):
        """
        模拟一步（一年）
        逻辑：执行Agent -> 收集数据 -> 计数器+1
        (绘图逻辑已移至 main.py 以控制频率)
        """
        # 1. 执行所有 Agent 的 step
        self.agents.do("step")
        
        # 2. 收集本步最新数据
        self._collect_data()
        
        # 3. 更新步数计数器
        self.current_step += 1

print("完成加载 src/model.py")