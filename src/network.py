import networkx as nx
import random
import numpy as np

class RelationNetwork:
    def __init__(self, model=None):
        """
        初始化关系网络
        :param model: 传入 model 引用 (可选)，方便反向调用或注册
        """
        self.G = nx.Graph()
        self.model = model

    def add_villager(self, villager):
        """
        [修改点 1] 添加村民节点
        存储 unique_id, name, family, age, personality
        并自动处理家族内部关系
        """
        uid = villager.unique_id
        
        # 1. 添加节点及其属性
        self.G.add_node(
            uid,
            name=villager.name,
            family=villager.family,
            age=villager.age,
            personality=villager.personality.copy() # 存储副本，防止外部修改影响图属性一致性
        )
        
        # 2. [修改点 2] 初始化时：自动检查同家族成员并加边 (权重 0.6 ~ 0.9)
        family_members = self.get_family_members(villager.family)
        for member_id in family_members:
            if member_id != uid:
                # 如果边不存在，则添加
                if not self.G.has_edge(uid, member_id):
                    weight = random.uniform(0.6, 0.9)
                    self.add_relation(uid, member_id, "家族", weight)

    def initialize_random_neighbors(self, probability=0.3):
        """
        [修改点 2 补充] 在所有村民添加完毕后调用此方法
        为随机邻居加边 (权重 0.2 ~ 0.5)
        建议在 Model._create_villagers 循环结束后调用一次
        """
        nodes = list(self.G.nodes())
        n = len(nodes)
        
        for i in range(n):
            for j in range(i + 1, n):
                # 如果已经存在边（如家族关系），跳过
                if self.G.has_edge(nodes[i], nodes[j]):
                    continue
                
                # 按概率建立随机邻居关系
                if random.random() < probability:
                    weight = random.uniform(0.2, 0.5)
                    self.add_relation(nodes[i], nodes[j], "邻居", weight)

    def add_relation(self, a_id, b_id, relation_type, weight):
        """
        添加或更新村民之间的关系
        """
        # 如果边已存在，可以选择更新类型或保留原类型，这里选择更新权重
        if self.G.has_edge(a_id, b_id):
            self.G[a_id][b_id]['weight'] = weight
            # 可选：保留原有的 type 或追加 type，这里简单覆盖或保留
            # self.G[a_id][b_id]['type'] = relation_type 
        else:
            self.G.add_edge(a_id, b_id, type=relation_type, weight=weight)

    def get_family_members(self, family):
        """获取同一家族的所有村民ID"""
        return [n for n, attr in self.G.nodes(data=True) if attr.get("family") == family]

    def update_weight(self, a_id, b_id, delta):
        """
        [修改点 3] 动态更新边权重
        weight += delta, 限制在 [0, 1]
        如果边不存在，则不操作或创建一条弱关系 (此处选择不操作，避免凭空产生关系)
        """
        if not self.G.has_edge(a_id, b_id):
            # 可选策略：如果互动足够多，可以在此处创建新边
            # 这里严格遵循“修改对应村民的关系权重”，假设关系需先存在
            return

        current_weight = self.G[a_id][b_id].get('weight', 0.5)
        new_weight = current_weight + delta
        
        # 限制范围 [0, 1]
        new_weight = max(0.0, min(1.0, new_weight))
        
        self.G[a_id][b_id]['weight'] = new_weight

    def get_network_stats(self):
        """
        [修改点 4] 返回网络统计指标
        用于 model.step() 收集数据
        """
        if self.G.number_of_nodes() == 0:
            return {
                'avg_degree': 0.0,
                'clustering_coefficient': 0.0,
                'connected_components': 0
            }
        
        # 1. 平均度
        avg_degree = np.mean([d for n, d in self.G.degree()]) if self.G.number_of_edges() > 0 else 0.0
        
        # 2. 平均聚类系数
        clustering_coefficient = nx.average_clustering(self.G)
        
        # 3. 连通分量数
        connected_components = nx.number_connected_components(self.G)
        
        return {
            'avg_degree': float(avg_degree),
            'clustering_coefficient': float(clustering_coefficient),
            'connected_components': int(connected_components)
        }

    def get_all_relations(self):
        """辅助函数：返回所有边的列表，用于计数"""
        return list(self.G.edges(data=True))