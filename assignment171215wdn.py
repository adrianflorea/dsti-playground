import collections
from enum import Enum


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        pass
    return False


Edge = collections.namedtuple("Edge" , "id junctions type valve_status")


class ValveStatus(Enum):
    Open = 1
    Closed = 2


class EdgeType(Enum):
    Pipe = 1
    Valve = 2

class ParsingSection(Enum):
    Junctions = 1
    Pipes = 2
    Valves = 3


class WaterDistributionNetwork:
    def __init__(self):
        self._adjacency_list = {}
        self._edges = {}

    def _add_edge(self, edge_id, junction_id_1, junction_id_2, edge_type = EdgeType.Pipe, valve_status = None):
        edge = Edge(
            id=edge_id,
            junctions=[junction_id_1, junction_id_2],
            type=edge_type,
            valve_status=valve_status)
        self._adjacency_list[junction_id_1].append(edge)
        self._adjacency_list[junction_id_2].append(edge)
        self._edges[edge_id] = edge

    def _get_opposite_node_id(self, node_id, edge_id):
        edge = self._edges[edge_id]
        if edge.junctions[0] == node_id:
            return edge.junctions[0]
        elif edge.junctions[1] == node_id:
            return edge.junctions[0]
        else:
            raise ValueError("%s is not an endpoint of the edge %s!" % (node_id, edge_id))

    def _parse_junction(self, text):
        junction_id = text.split(sep=None, maxsplit=1)[0]
        return junction_id

    def _parse_pipe(self, text):
        pipe_id, junction_id_1, junction_id_2, _ = text.split(sep=None, maxsplit=3)
        return pipe_id, junction_id_1, junction_id_2

    def _parse_valve(self, text):
        valve_id, junction_id_1, junction_id_2, _, _, setting, _ = text.split(sep=None, maxsplit=6)
        valve_status = ValveStatus.Open
        if is_number(setting) and not bool(float(setting)):
            valve_status = ValveStatus.Closed
        # consider all valves open anyway
        return valve_id, junction_id_1, junction_id_2, ValveStatus.Open

    def _get_text_with_comment_removed(self, text):
        if text is not None and text.find(";") >= 0:
            return text.split(sep=";", maxsplit=1)[0]
        else:
            return text

    def _is_header(self, text):
        is_header = False
        if text is not None:
            text = text.lstrip()
            if len(text) > 0 and text[0] is ";":
                is_header = True
        return is_header

    def _is_empty(self, text):
        return text is None or len(text.strip()) is 0

    def add_junction(self, junction_id):
        self._adjacency_list[junction_id] = []

    def add_pipe(self, pipe_id, junction_id_1, junction_id_2):
        self._add_edge(
            edge_id=pipe_id,
            junction_id_1=junction_id_1, 
            junction_id_2=junction_id_2, 
            edge_type = EdgeType.Pipe, 
            valve_status = None)

    def add_valve(self, valve_id, junction_id_1, junction_id_2, valve_status=ValveStatus.Open):
        self._add_edge(
            edge_id=valve_id,
            junction_id_1=junction_id_1, 
            junction_id_2=junction_id_2, 
            edge_type = EdgeType.Valve, 
            valve_status = valve_status)

    def load_from_epanet_file(self, file_name):
        file = open(file_name, mode="r")
        parsing = False
        parsing_section = None
        for line_in_file in file:
            if self._is_header(line_in_file):
                continue
            elif self._is_empty(line_in_file):
                parsing = False
            # for simplification, tanks and reservoirs 
            # are considered junctions (nodes)
            elif line_in_file.strip() in ["[JUNCTIONS]", "[TANKS]", "[RESERVOIRS]"]:
                parsing = True
                parsing_section = ParsingSection.Junctions
                continue
            elif line_in_file.strip() == "[PIPES]":
                parsing = True
                parsing_section = ParsingSection.Pipes
                continue
            elif line_in_file.strip() == "[VALVES]":
                parsing = True
                parsing_section = ParsingSection.Valves
            elif parsing and parsing_section is ParsingSection.Junctions:
                junction_id = self._parse_junction(line_in_file)
                self.add_junction(junction_id)
                continue
            elif parsing and parsing_section is ParsingSection.Pipes:
                pipe_id, junction_id_1, junction_id_2 = self._parse_pipe(line_in_file)
                self.add_pipe(pipe_id, junction_id_1, junction_id_2)
                continue
            elif parsing and parsing_section is ParsingSection.Valves:
                valve_id, junction_id_1, junction_id_2, valve_status = self._parse_valve(line_in_file)
                self.add_valve(valve_id, junction_id, junction_id_2, valve_status)
                continue
            else:
                continue

    # BFS-like limited traversal
    def _get_valves_to_isolate(self, node_id, discovered_nodes):
        valves_to_isolate = set([])
        level = [node_id]
        while len(level) > 0:
            next_level = []
            for node in level:
                for edge in self._adjacency_list[node]:
                    # for simplification, we assume all valves are open
                    if edge.type == EdgeType.Valve:
                        valves_to_isolate.add(edge.id)
                    # continue the graph traversal in this edge "direction"
                    # only if the edge wasn't a valve
                    else:
                        # in a classic BFS this branch block would substitute the if
                        opposite_node_id = self._get_opposite_node_id(node, edge.id)
                        if opposite_node_id not in discovered_nodes:
                            discovered_nodes[opposite_node_id] = edge
                            next_level.append(opposite_node_id)
            level = next_level
        return valves_to_isolate, discovered_nodes

    def get_valves_to_isolate(self, pipe_id):
        pipe = self._edges[pipe_id]
        pipe_endpoint_1 = pipe.junctions[0]
        pipe_endpoint_2 = pipe.junctions[1]
        # for the both endpoints of the pipe
        valves_to_isolate_1, discovered_nodes_1 = self._get_valves_to_isolate(pipe_endpoint_1, {})
        valves_to_isolate_2, discovered_nodes_2 = self._get_valves_to_isolate(pipe_endpoint_2, discovered_nodes_1)
        # union
        return valves_to_isolate_1 | valves_to_isolate_2

"""
Course:  Algorithmics for Data Science - Optimisation - A17 @ DSTI
Instructor: Dr. Amir Nakib
Student: Adrian Florea

Assignment: 2 - Drinking network
Due date: December 15th, 2017, 12:00 AM CET

Propose an algorithm that allows to provide a list of valves to close to isolate each pipe
"""

def main():
    wdn = WaterDistributionNetwork()
    wdn.load_from_epanet_file("./network.inp")
    pipe_id = input("Which pipe do you want to isolate? Please enter its pipe ID: ")
    valves_to_isolate = wdn.get_valves_to_isolate(pipe_id)
    if len(valves_to_isolate) == 0:
        print("Pipe %s cannot be isolated!" % pipe_id)
    else:
        print("You need to close the following %d valves in order to isolate the pipe %s:"\
              % (len(valves_to_isolate), pipe_id))
        print(valves_to_isolate)
    pass

if __name__ == "__main__":
    main()