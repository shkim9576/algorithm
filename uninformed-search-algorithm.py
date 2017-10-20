import time
import sys
from Queue import PriorityQueue
start = time.time()

# open input file
lines = []
with open(sys.argv[2]) as f:
    lines.extend(f.read().splitlines())

class Element(object):
    def __init__(self, path, remained_fuel):
        self.path = path
        self.remained_fuel = remained_fuel
        return
    def __cmp__(self, other):
        return -cmp(self.remained_fuel, other.remained_fuel)

def compareOrder(old_list, new_list):
    old_str = ''.join(old_list)
    new_str = ''.join(new_list)
    list_result = [old_str, new_str]
    list_result.sort()
    if list_result[0] == new_str:
        return True
    else:
        return False

# BFS ------------------------------------
def bfs(graph, initFule, start, end):
    visited_nodes = []
    queue = []
    queue.append({"path": [start], "remained_fuel": initFule})

    while queue:
        queue_element = queue.pop(0)
        path = queue_element["path"]
        remained_fuel = queue_element["remained_fuel"]
        node = path[-1]
        visited_nodes.append(node)

        # found path
        if node == end and remained_fuel >= 0:
            return {"path": path, "remained_fuel": remained_fuel}

        # append all child nodes and sort
        child_nodes = graph.get(node, [])
        child_nodes.sort()

        # put all child nodes into queues if it is neither visited nor already in the queue
        for child_node in child_nodes:
            child_splits = child_node.split('-')
            cn = child_splits[0].strip()
            cost = int(child_splits[1].strip())

            if cn not in visited_nodes:
                new_path = list(path)
                new_path.append(cn)
                new_remained_fuel = int(remained_fuel) - cost
                queue.append({"path": new_path, "remained_fuel": new_remained_fuel})
    return {}


# DFS ------------------------------------
def dfs(graph, initFule, start, end):
    visited_nodes = []
    stack = []
    stack.insert(0, {"path": [start], "remained_fuel": initFule})

    while stack:
        queue_element = stack.pop(0)
        path = queue_element["path"]
        remained_fuel = queue_element["remained_fuel"]
        node = path[-1]
        visited_nodes.append(node)

        # found path
        if node == end and remained_fuel >= 0:
            return {"path": path, "remained_fuel": remained_fuel}

        # append all child nodes and sort
        child_nodes = graph.get(node, [])
        child_nodes.sort(reverse=True)

        # put all child nodes into queues if it is neither visited nor already in the queue
        for child_node in child_nodes:
            child_splits = child_node.split('-')
            cn = child_splits[0].strip()
            cost = int(child_splits[1].strip())

            if cn not in visited_nodes:
                new_path = list(path)
                new_path.append(cn)
                new_remained_fuel = int(remained_fuel) - cost
                stack.insert(0, {"path": new_path, "remained_fuel": new_remained_fuel})
    return {}


# UCS ------------------------------------
def ucs(graph, initFule, start, end):
    visited_nodes = []
    priority_queue = PriorityQueue()
    priority_queue.put(Element([start], initFule))
    result = Element([], -1)

    while not priority_queue.empty():
        queue_element = priority_queue.get()
        path = queue_element.path
        remained_fuel = queue_element.remained_fuel
        node = path[-1]
        visited_nodes.append(node)

        # found path
        if node == end and remained_fuel >= 0:
            if (result.remained_fuel < remained_fuel) or (result.remained_fuel == remained_fuel and compareOrder(result.path, path)):
                result.remained_fuel = remained_fuel
                result.path = path

        # append all child nodes and sort
        child_nodes = graph.get(node, [])

        # put all child nodes into queues if it is neither visited nor already in the queue
        for child_node in child_nodes:
            child_splits = child_node.split('-')
            cn = child_splits[0].strip()
            cost = int(child_splits[1].strip())

            if cn not in visited_nodes:
                new_path = list(path)
                new_path.append(cn)
                new_remained_fuel = int(remained_fuel) - cost
                priority_queue.put(Element(new_path, new_remained_fuel))

    if result.remained_fuel < 0:
        return {}
    else:
        return {"path": result.path, "remained_fuel": result.remained_fuel}

def writeResultToFile (result):
    fo = open("output.txt", "wb")

    if not result:
        fo.write("No Path")
    else:
        result_path = result["path"]
        path_str = '-'.join(result_path)
        remained_fuel_str = str(result['remained_fuel'])
        fo.write(path_str)
        fo.write(' ')
        fo.write(remained_fuel_str)

    fo.close()

# Build graph
graph = {}
for line in lines[4:]:
    splits = line.split(':')
    child_list = splits[1].split(',')
    graph.update({splits[0]:child_list})

# Run algorithm
if lines[0] == "BFS":
    result = bfs(graph, lines[1], lines[2], lines[3])
elif lines[0] == "DFS":
    result = dfs(graph, lines[1], lines[2], lines[3])
elif lines[0] == "UCS":
    result = ucs(graph, lines[1], lines[2], lines[3])
else:
    print "Incorrect input file: Unknown Algorithm"

writeResultToFile(result)
end = time.time()
print(end-start)

