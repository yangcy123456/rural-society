print("开始加载 model.py") 

from mesa import Model
# Mesa 4.0 不再需要导入 RandomActivation 或任何 Scheduler
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
        
        # Mesa 4.0: 不需要创建 schedule 对象
        # 所有的 agent 会自动添加到 self.agents 集合中
        self.network = RelationNetwork()
        
        self._create_villagers()

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
            # Mesa 4.0: 实例化即自动注册到 self.agents，无需 schedule.add()
            
            self.network.add_villager(villager)
            
            # 自动添加家族内部关系
            # 注意：此时 villager 刚加入，可能需要确保 network 能正确获取最新列表
            family_members = self.network.get_family_members(family)
            for member_id in family_members:
                if member_id != i:
                    self.network.add_relation(i, member_id, "家族", 0.8)

    def get_family_personality(self, family):
        """获取某家族的平均人格（用于儿童期继承）"""
        # Mesa 4.0: 直接使用 self.agents
        # self.agents 是一个 AgentSet，可以直接迭代
        family_agents = [a for a in self.agents if a.family == family and a.age > 30]
        
        if not family_agents:
            return {dim: 0.0 for dim in PERSONALITY_DIMS}
        
        mean_personality = {}
        for dim in PERSONALITY_DIMS:
            mean_personality[dim] = np.mean([a.personality[dim] for a in family_agents])
        return mean_personality

    def get_community_norm(self):
        """获取全村平均人格（用于青少年期规范）"""
        # 直接使用 self.agents
        mean_personality = {}
        for dim in PERSONALITY_DIMS:
            # 确保 agent 有 personality 属性
            values = [a.personality[dim] for a in self.agents if hasattr(a, 'personality')]
            if values:
                mean_personality[dim] = np.mean(values)
            else:
                mean_personality[dim] = 0.0
        return mean_personality

    def step(self):
        """模拟一步（一年）"""
        # Mesa 4.0 核心变化：使用 agents.do("step") 替代 schedule.step()
        # 这会自动按随机顺序调用所有 agent 的 step() 方法
        self.agents.do("step")

print("完成加载 model.py")