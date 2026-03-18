import numpy as np
from mesa import Agent
from src.utils.yaml_loader import config

PERSONALITY_DIMS = config["PERSONALITY_DIMS"]
CHILD_PARENT_WEIGHT = config["CHILD_PARENT_WEIGHT"]
TEEN_COMMUNITY_WEIGHT = config["TEEN_COMMUNITY_WEIGHT"]
ADULT_STABLE_RATE = config["ADULT_STABLE_RATE"]

class Villager(Agent):
    # ✅ 修改点 1: __init__ 只接收 model，移除 unique_id 参数传递
    # 注意：如果您的 model.py 在创建 agent 时仍然传了 unique_id，
    # 您也需要去 model.py 把那个参数去掉，或者在这里保留参数但不传给 super()
    def __init__(self, unique_id, model, name, gender, age, family):
        # Mesa 4.0: 只传 model
        super().__init__(model)
        
        # 手动保存 unique_id (如果后续代码用到 self.unique_id)
        # 在 Mesa 4.0 中，unique_id 可能不再是 Agent 的内置属性，需手动维护
        self.unique_id = unique_id
        
        # 基础身份
        self.name = name
        self.gender = gender
        self.age = age
        self.family = family
        
        # 空白人格初始化
        self.personality = {dim: 0.0 for dim in PERSONALITY_DIMS}

    def step(self):
        """每年执行一次：年龄增长 + 人格更新"""
        self.age += 1
        self._update_personality()

    def _update_personality(self):
        """无监督人格成长逻辑"""
        if self.age <= 12:
            self._childhood_update()
        elif 12 < self.age <= 18:
            self._teenage_update()
        else:
            self._adult_update()

    def _childhood_update(self):
        # 确保 model 中有此方法
        if hasattr(self.model, 'get_family_personality'):
            parent_personality = self.model.get_family_personality(self.family)
            for dim in PERSONALITY_DIMS:
                self.personality[dim] = CHILD_PARENT_WEIGHT * parent_personality[dim]
                self.personality[dim] = np.clip(self.personality[dim], -1, 1)

    def _teenage_update(self):
        # 确保 model 中有此方法
        if hasattr(self.model, 'get_community_norm'):
            community_norm = self.model.get_community_norm()
            for dim in PERSONALITY_DIMS:
                self.personality[dim] += TEEN_COMMUNITY_WEIGHT * community_norm[dim]
                self.personality[dim] = np.clip(self.personality[dim], -1, 1)

    def _adult_update(self):
        for dim in PERSONALITY_DIMS:
            self.personality[dim] *= (1 - ADULT_STABLE_RATE)
            self.personality[dim] = np.clip(self.personality[dim], -1, 1)