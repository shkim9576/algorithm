import time
import sys
import cPickle

startTime = time.time()
inf = float('inf')

##########################
###### State        ######
##########################
class State:
    def __init__(self, graph, player, name, color, depth, value, alpha, beta):
        self.graph = graph
        self.player = player
        self.name = name
        self.color = color
        self.depth = depth
        self.value = value
        self.alpha = alpha
        self.beta = beta


##########################
######   Input MGR  ######
##########################
class InputManager:
    def __init__(self):
        lines = []
        with open(sys.argv[2]) as f:
            lines.extend(f.read().splitlines())

        # Parse Input File
        # set domains
        self.domain = lines[0].split(",")  # R, G, B
        self.domain = map(str.strip, self.domain)

        # set max depth
        self.max_depth = lines[2]  # root is 0

        # set player preference
        player_1_preference = lines[3].split(",")  # R: 10, G: 5, B: 0
        player_1_preference = map(str.strip, player_1_preference)
        self.player_1_pref_dict = {}
        for pref in player_1_preference:
            player_1_pref_splits = pref.split(":")
            self.player_1_pref_dict.update({player_1_pref_splits[0]: player_1_pref_splits[1]})

        player_2_preference = lines[4].split(",")  # R: 0, G: 2, B: 8
        player_2_preference = map(str.strip, player_2_preference)
        self.player_2_pref_dict = {}
        for pref in player_2_preference:
            player_2_pref_splits = pref.split(":")
            self.player_2_pref_dict.update({player_2_pref_splits[0]: player_2_pref_splits[1]})

        # set graph
        graph = {}
        for line in lines[5:]:
            node_adj = line.split(':')
            adjacents = node_adj[1].split(',')
            adjacents = map(str.strip, adjacents)
            node = {"adjacent_nodes": adjacents, "name": node_adj[0], "color": None, "player": None}
            graph.update({node_adj[0]: node})  # name, node

        # set initial map
        init_colors = lines[1].split(",")  # WA: R-1, SA: G-2
        init_colors = map(str.strip, init_colors)

        root_node = self.update_color_player(graph, init_colors)
        self.state = State(graph, root_node.get("player"), root_node.get("name"), root_node.get("color"), 0, -inf, -inf, inf)

    def update_color_player(self, graph, init_colors):
        for elem in init_colors:   # WA: R-1, SA: G-2
            node_color = elem.split(":")  # WA: R-1
            node_color = map(str.strip, node_color)
            color_player = node_color[1].split("-")  # R-1
            color_player = map(str.strip, color_player)
            graph.get(node_color[0])["color"] = color_player[0]
            graph.get(node_color[0])["player"] = color_player[1]

            adjacents = graph.get(node_color[0])
            root_node = {"adjacent_nodes": adjacents, "name": node_color[0], "color": color_player[0], "player": color_player[1]}
        return root_node

ginput = InputManager()


##########################
######   Output MGR ######
##########################
report = []
class OutputManager:
    def __init__(self):
        self.last_r = ""

    def write_report(self, name, color, depth, value, alpha, beta, d):
        if d <= int(ginput.max_depth):
            r_list = [name, color, depth, value, alpha, beta]
            r = ", ".join(r_list)
            if r != self.last_r:
                report.append(r)
                self.last_r = r

    def write_to_file(self):
        fo = open("output.txt", "wb")
        fo.write("\n".join(report))
        fo.close()

goutput = OutputManager()


##########################
###### Game         ######
##########################
successors_cache = {}
class Game:

    def pass_con_1(self, graph, node):
        adjacent_nodes = node.get("adjacent_nodes")
        for anode in adjacent_nodes:
            if graph.get(anode).get("color") is not None:
                return True
        return False

    def pass_con_2(self, graph, node):
        adjacent_nodes = node.get("adjacent_nodes")
        for anode in adjacent_nodes:
            anode_obj = graph.get(anode)
            if (anode_obj.get("color") is node.get("color")) and (anode_obj.get("color") is not None) and (node.get("color") is not None):
                return False
        return True

    def successors(self, state):
        state_hash = self.get_state_hash(state)
        if state_hash in successors_cache:
            return successors_cache.get(state_hash)

        successors = []
        for name, node in state.graph.iteritems():
            if (node.get("color") is None) and self.pass_con_1(state.graph, node) and self.pass_con_2(state.graph, node):

                for color in ginput.domain:
                        if state.player is "1":
                            player = "2"
                        else:
                            player = "1"

                        new_graph = cPickle.loads(cPickle.dumps(state.graph, -1))
                        new_graph_node = new_graph.get(name)
                        new_graph_node["color"] = color
                        new_graph_node["name"] = name
                        new_graph_node["player"] = player
                        new_state = State(new_graph, player, name, color, state.depth + 1, -inf, -inf, inf)

                        if self.pass_constraint_1(new_state) and self.pass_constraint_2(new_state):
                            successors.append(new_state)

        successors.sort(key=lambda child_state: (child_state.name, child_state.color))
        successors_cache[state_hash] = successors
        return successors

    def get_state_hash(self, state):
        #return id(state)
        key = ""
        for name, node in state.graph.iteritems():
            color = node.get("color")
            player = node.get("player")
            if color is None:
                color = "None"
            if player is None:
                player = "None"
            key = "-".join([key, name, color, player])
        return key

    # constraints - 1 (The players can only color neighbors of nodes that have already been colored in the map)
    def pass_constraint_1(self, state):
        graph = state.graph
        adjacent_nodes = graph.get(state.name).get("adjacent_nodes")
        for anode in adjacent_nodes:
            if graph.get(anode).get("color") is not None:
                return True
        return False

    # constraints - 2 (Adjacent nodes could not have the same color)
    def pass_constraint_2(self, state):
        graph = state.graph
        adjacent_nodes = graph.get(state.name).get("adjacent_nodes")
        for anode in adjacent_nodes:
            anode_obj = graph.get(anode)
            if (anode_obj.get("color") is state.color) and (anode_obj.get("color") is not None) and (state.color is not None):
                return False
        return True

    def utility(self, state):
        player_1_score = 0
        player_2_score = 0
        for name, node in state.graph.iteritems():
            if node.get("player") is "1":
                player_1_score = player_1_score + int(ginput.player_1_pref_dict.get(node.get("color")))
            elif node.get("player") is "2":
                player_2_score = player_2_score + int(ginput.player_2_pref_dict.get(node.get("color")))
        return player_1_score - player_2_score

    def terminal_test(self, state):
        child_list = self.successors(state)
        for child in child_list:
            if self.pass_constraint_1(child) and self.pass_constraint_2(child):
                return False
        goutput.write_report(state.name, state.color, str(state.depth), str(self.utility(state)), str(state.alpha), str(state.beta), state.depth)
        return True

    def cutoff_test(self, state, depth):
        if depth > int(ginput.max_depth) or self.terminal_test(state):
            return True
        return False


##########################
######   Solution   ######
##########################
class Solution:
    def solve(self):
        game = Game()
        self.alphabeta_search(ginput.state, game)

    def alphabeta_search(self, state, game):

        def max_value(state, alpha, beta, depth):
            if game.cutoff_test(state, depth + 1):
                utility = game.utility(state)
                goutput.write_report(state.name, state.color, str(depth), str(utility), str(alpha), str(beta), depth)
                return utility

            v = -inf
            goutput.write_report(state.name, state.color, str(state.depth), str(v), str(alpha), str(beta), depth)

            for s in game.successors(state):
                s.alpha = alpha
                s.beta = beta
                v = max(v, min_value(s, alpha, beta, depth + 1))

                if v >= beta:
                    goutput.write_report(state.name, state.color, str(state.depth), str(v), str(alpha), str(beta), depth)
                    return v

                alpha = max(alpha, v)
                goutput.write_report(state.name, state.color, str(state.depth), str(v), str(alpha), str(beta), depth)
            return v


        def min_value(state, alpha, beta, depth):
            if game.cutoff_test(state, depth + 1):
                utility = game.utility(state)
                goutput.write_report(state.name, state.color, str(depth), str(utility), str(alpha), str(beta), depth)
                return utility

            v = inf
            goutput.write_report(state.name, state.color, str(depth), str(v), str(alpha), str(beta), depth)

            for s in game.successors(state):
                s.alpha = alpha
                s.beta = beta
                v = min(v, max_value(s, alpha, beta, depth + 1))

                if v <= alpha:
                    goutput.write_report(state.name, state.color, str(depth), str(v), str(alpha), str(beta), depth)
                    return v

                beta = min(beta, v)
                goutput.write_report(state.name, state.color, str(depth), str(v), str(alpha), str(beta), depth)
            return v

        # Start alpha beta search here!!!
        goutput.write_report(state.name, state.color, str(0), str(state.value), str(state.alpha), str(state.beta), 0)
        root_value = -inf
        root_alpha = -inf
        root_beta = inf
        best_color = ""
        best_node_name = ""
        best_value = -inf

        for child in game.successors(state):
            mv = min_value(child, root_alpha, root_beta, 1)
            if mv > best_value:
                best_value = mv
                best_color = child.color
                best_node_name = child.name

            root_value = max(root_value, mv)
            root_alpha = max(root_alpha, root_value)
            goutput.write_report(state.name, state.color, str(0), str(root_value), str(root_alpha), str(root_beta), 0)

        report.append(best_node_name + ", " + best_color + ", " + str(best_value))

##########################
######     Main     ######
##########################
def main():
    solution = Solution()
    solution.solve()
    goutput.write_to_file()
main()

endTime = time.time()
print "performance took: ", (endTime - startTime)
