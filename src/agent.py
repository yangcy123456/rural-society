import numpy as np
import random  # [修改] 新增导入 random
from mesa import Agent
from src.utils.yaml_loader import config

PERSONALITY_DIMS = config["PERSONALITY_DIMS"]
CHILD_PARENT_WEIGHT = config["CHILD_PARENT_WEIGHT"]
TEEN_COMMUNITY_WEIGHT = config["TEEN_COMMUNITY_WEIGHT"]
ADULT_STABLE_RATE = config["ADULT_STABLE_RATE"]

class Villager(Agent):
    def __init__(self, unique_id, model, name, gender, age, family):
        super().__init__(model)
        self.unique_id = unique_id
        
        # 基础身份
        self.name = name
        self.gender = gender
        self.age = age
        self.family = family
        
        # [修改] 初始化人格：先初始化为0 (保持兼容)，然后立即覆盖为随机值
        self.personality = {dim: 0.0 for dim in PERSONALITY_DIMS}
        
        # [修复点1] 人格初始化改为随机 (-0.7 到 0.7)，解决全0且不变的问题
        for dim in PERSONALITY_DIMS:
            self.personality[dim] = random.uniform(-0.7, 0.7)

    def step(self):
        """
        [修复点2] 每年执行一次：年龄增长 + 人格更新 + 行动
        原逻辑被重构以确保数据每帧都在变化，从而驱动可视化
        """
        # 1. 年龄增长
        self.age += 1
        
        # 2. 人格更新 (调用新写的 update_personality)
        self.update_personality()
        
        # 3. 采取行动 (调用新写的 take_action，修改社会关系)
        self.take_action()

    # [修复点3] 新增函数：根据年龄阶段微调人格
    def update_personality(self):
        """根据年龄阶段微调人格，家族/社区影响，最后 clamp 在 [-1,1]"""
        if self.age <= 12:
            # 儿童期：受家庭影响较大
            if hasattr(self.model, 'get_family_personality'):
                parent_personality = self.model.get_family_personality(self.family)
                for dim in PERSONALITY_DIMS:
                    # 混合当前人格与父母人格 (避免完全覆盖，保留一点自我)
                    mix_rate = 0.1 
                    target_val = CHILD_PARENT_WEIGHT * parent_personality[dim]
                    self.personality[dim] = (1 - mix_rate) * self.personality[dim] + mix_rate * target_val
                    self.personality[dim] = np.clip(self.personality[dim], -1, 1)
                    
        elif 12 < self.age <= 18:
            # 青少年：受社区规范影响
            if hasattr(self.model, 'get_community_norm'):
                community_norm = self.model.get_community_norm()
                for dim in PERSONALITY_DIMS:
                    # 向社区规范微调
                    shift = TEEN_COMMUNITY_WEIGHT * community_norm[dim] * 0.1
                    self.personality[dim] += shift
                    self.personality[dim] = np.clip(self.personality[dim], -1, 1)
                    
        else:
            # 成年：趋于稳定，但加入微小随机扰动防止“死锁”不变
            for dim in PERSONALITY_DIMS:
                # 原有稳定逻辑
                self.personality[dim] *= (1 - ADULT_STABLE_RATE * 0.1)
                # [关键] 加入微小随机波动，确保数值一直在变，可视化才会动
                self.personality[dim] += random.uniform(-0.005, 0.005)
                self.personality[dim] = np.clip(self.personality[dim], -1, 1)

    # [修复点4] 新增函数：随机行动，修改社会关系网络
    def take_action(self):
        """随机选择 交流/帮助/疏远，修改对应村民的关系权重"""
        # 获取除自己外的所有村民
        other_agents = [a for a in self.model.schedule.agents if a.unique_id != self.unique_id]
        if not other_agents:
            return
            
        # 随机选择一个目标
        target = random.choice(other_agents)
        
        # 随机选择行动类型
        action_type = random.choice(['help', 'talk', 'avoid'])
        
        # 确定权重变化量
        delta = 0.0
        if action_type == 'help':
            delta = 0.05
        elif action_type == 'talk':
            delta = 0.02
        elif action_type == 'avoid':
            delta = -0.05
            
        # 更新关系权重
        # 假设 model 中有 social_network 字典，键为 (id1, id2) 元组 (排序后)
        if hasattr(self.model, 'social_network'):
            # 确保键的顺序一致 (小ID, 大ID)
            key = (min(self.unique_id, target.unique_id), max(self.unique_id, target.unique_id))
            
            # 获取当前权重，若无则默认为中性值 0.5
            current_weight = self.model.social_network.get(key, 0.5)
            new_weight = current_weight + delta
            
            # 限制权重在 [0, 1]
            new_weight = max(0.0, min(1.0, new_weight))
            
            # [关键] 写入新值，触发社会网络变化
            self.model.social_network[key] = new_weight
            
        # 备用方案：如果 model 有专门的方法
        elif hasattr(self.model, 'update_relationship'):
            self.model.update_relationship(self.unique_id, target.unique_id, delta)

    # --- 原有函数保留 (如果需要被其他外部模块调用)，但 step 中已不再直接调用它们 ---
    def _update_personality(self):
        """保留原有签名以防外部调用，内部委托给新逻辑或留空"""
        # 为了防止逻辑重复执行，建议此处留空或仅作为兼容层
        pass 

    def _childhood_update(self):
        pass

    def _teenage_update(self):
        pass

    def _adult_update(self):
        pass