import hashlib

def hash_key(key, m=8):
    h = int(hashlib.sha1(str(key).encode()).hexdigest(), 16)
    return h % (2**m)


class Node:
    def __init__(self, node_id, m=8):
        self.node_id = hash_key(node_id, m)
        self.m = m
        self.successor = self
        self.predecessor = None
        self.finger = [None] * m

    def __repr__(self):
        return f"Node({self.node_id})"

    def join(self, existing_node):
        if existing_node:
            self.init_finger_table(existing_node)
            self.update_others()
        else:
            for i in range(self.m):
                self.finger[i] = self
            self.predecessor = self

    def init_finger_table(self, existing_node):
        self.finger[0] = existing_node.find_successor(
            (self.node_id + 1) % (2**self.m)
        )
        self.successor = self.finger[0]
        self.predecessor = self.successor.predecessor
        self.successor.predecessor = self
        for i in range(self.m - 1):
            start = (self.node_id + 2**i) % (2**self.m)
            if self.in_interval(start, self.node_id, self.finger[i].node_id):
                self.finger[i+1] = self.finger[i]
            else:
                self.finger[i+1] = existing_node.find_successor(start)

    def update_others(self):
        for i in range(self.m):
            pred_id = (self.node_id - 2**i + 2**self.m) % (2**self.m)
            p = self.find_predecessor(pred_id)
            p.update_finger_table(self, i)

    def update_finger_table(self, s, i):
        start = (self.node_id + 2**i) % (2**self.m)
        if self.in_interval(s.node_id, self.node_id, self.finger[i].node_id, inclusive=True):
            self.finger[i] = s
            p = self.predecessor
            if p != self:
                p.update_finger_table(s, i)

    def find_successor(self, id_):
        pred = self.find_predecessor(id_)
        return pred.successor

    def find_predecessor(self, id_):
        node = self
        while not self.in_interval(id_, node.node_id, node.successor.node_id, inclusive=True):
            node = node.closest_preceding_finger(id_)
        return node

    def closest_preceding_finger(self, id_):
        for i in range(self.m-1, -1, -1):
            if self.in_interval(self.finger[i].node_id, self.node_id, id_):
                return self.finger[i]
        return self

    @staticmethod
    def in_interval(x, a, b, inclusive=False):
        if a < b:
            return a < x < b or (inclusive and (x == b))
        else:  
            return x > a or x < b or (inclusive and (x == b))


if __name__ == "__main__":
    m = 6  
    n1 = Node("node1", m)
    n1.join(None)

    n2 = Node("node2", m)
    n2.join(n1)

    n3 = Node("node3", m)
    n3.join(n1)

    print("===== Node Finger Tables =====")
    for n in [n1, n2, n3]:
        print(f"{n}: fingers -> {[f.node_id for f in n.finger]}")

    key = "my_file.txt"
    key_id = hash_key(key, m)
    owner = n1.find_successor(key_id)
    print(f"\nKey '{key}' (id={key_id}) duoc luu o Node {owner.node_id}")
