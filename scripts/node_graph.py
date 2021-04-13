import math
import itertools
import time

class Node():
    def __init__(self, state, length) -> None:
        super().__init__()
        self.state = state
        self.len = length
        self.val = math.inf
        self.parent = None


class NodeGraph():
    def __init__(self, node_states, group_ids, path_distances) -> None:
        super().__init__()
        self.distance_table = self.set_distance_table(node_states, group_ids)
        self.path_distances = path_distances
        self.node_states = node_states

    def get_exact_solution(self,areas_nodes, sample_count):
        multiple_seq = list(itertools.permutations(areas_nodes,sample_count))
        val_g = math.inf
        val_max = 0
        seq_g = None
        start = time.time()
        for item in multiple_seq:
            seq, val = self.get_value(item)
            if val < val_g:
                seq_g = seq
                val_g = val
            if val > val_max:
                val_max = val
        end = time.time()
        # print(f'Time needed to find exact solution: {end-start}')
        time_needed = end - start
        return seq_g, val_g, val_max, time_needed

    def set_distance_table(self, node_states, group_ids):
        distance_table = []
        
        for i in range(len(node_states)):
            column = []
            for j in range(len(node_states)):
                if group_ids[i] == group_ids[j]:
                    column.append(None)
                else:
                    column.append(self.get_distance(node_states[i], node_states[j]))
            distance_table.append(column)

        return distance_table

    def get_distance(self, state1, state2):
        p1_end = state1[1]
        p2_start = state2[0]
        # print(f"p1_end: {p1_end}")
        # print(f'p2_start: {p2_start}')
        # print(5*'----')

        x1, y1 = p1_end[0], p1_end[1]
        x2, y2 = p2_start[0], p2_start[1]

        x_diff = x2 - x1
        y_diff = y2 - y1

        dist = math.sqrt(x_diff*x_diff + y_diff*y_diff)
        # dist = math.sqrt(0)
        return dist

    def create_nodes(self, areas_nodes):
        graph_nodes = []
        for item in areas_nodes:
            nodes = []
            for node in item.node_states:
                len = self.path_distances[self.node_states.index(node)]
                nodes.append(Node(node, len))
                # print(f"len of this area: {self.path_distances[self.node_states.index(node)]}")
            graph_nodes.append(nodes)
        self.nodes = graph_nodes
        # print(graph_nodes[0])

    def get_distance_from_table(self, state1, state2):
        ind1 = self.node_states.index(state1)
        ind2 = self.node_states.index(state2)
        return self.distance_table[ind1][ind2]

    def assign_values(self):
        node_groups = self.nodes

        for i in range(len(node_groups[0])):
            node = node_groups[0][i]
            node.val = node.len

        for i in range(len(node_groups)-1):
            nodes_current = node_groups[i]
            nodes_next = node_groups[i+1]

            for j in range(len(nodes_next)):
                node_next_iter = nodes_next[j]
                for k in range(len(nodes_current)):
                    node_current_iter = nodes_current[k]
                    val_iter = node_current_iter.val + node_next_iter.len + self.get_distance_from_table(node_current_iter.state, node_next_iter.state)
                    # print(f'current value of distance and previous state: {val_iter}')
                    if val_iter < node_next_iter.val:
                        node_next_iter.val = val_iter
                        node_next_iter.parent = node_current_iter
            #             print(f'will set this as parent')
            #     print(10*'-')
            # print(10*'**')

    def get_shortest_path(self):
        value = math.inf
        min_val_node = None
        # print(f"last item of self.nodes {self.nodes[-1]}")
        for i in range(len(self.nodes[-1])):
            node_item = self.nodes[-1][i]
            # print(f'node_item: {node_item.val}')
            if node_item.val < value:
                min_val_node = node_item
                value = node_item.val
                # print(f'chosen index: {i}')

        node_sequence = [min_val_node]
        node_next = min_val_node

        while node_next.parent:
            node_sequence.append(node_next.parent)
            node_next = node_next.parent
            
        return node_sequence[::-1], min_val_node.val

    def get_value(self, seq):
        # seq = [self.areas[i] for i in seq]
        self.create_nodes(seq)
        self.assign_values()
        sequence, val = self.get_shortest_path()
        # print(f'sequence {sequence}, val: {val}')
        return sequence, val

    def set_areas(self, area):
        self.areas = area

    def get_value_fitness(self, seq):
        seq = [self.areas[i] for i in seq]
        self.create_nodes(seq)
        self.assign_values()
        sequence, val = self.get_shortest_path()
        # print(f'sequence {sequence}, val: {val}')
        return val

    

        




