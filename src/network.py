import networkx as nx

class RelationNetwork:
    def __init__(self):
        self.G = nx.Graph()

    def add_villager(self, villager):
        """添加村民节点"""
        self.G.add_node(
            villager.unique_id,
            name=villager.name,
            family=villager.family,
            personality=villager.personality
        )

    def add_relation(self, a_id, b_id, relation_type, weight):
        """添加村民之间的关系（血缘/地缘等）"""
        self.G.add_edge(a_id, b_id, type=relation_type, weight=weight)

    def get_family_members(self, family):
        """获取同一家族的所有村民ID"""
        return [n for n, attr in self.G.nodes(data=True) if attr.get("family") == family]