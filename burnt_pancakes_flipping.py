import sys
from operator import itemgetter
import copy

''' This program will allow user to input arbitrary number of pancakes, but user has to follow the format #C#C#C...#C#C-X to avoid unexpected behaviours from the program as there is no input format checking. X has to be 'a' indicating using A* searchh algorithm, or 'b' using BFS. This format follows the description of the burnt pancakes problem.'''

# get user input
input_pancakes, algo = itemgetter(0,1)(sys.argv[1].split('-'))
num_of_pancakes = int(len(input_pancakes)/2)

# Basic node unit for the search graph
class PancakesNode:
    
    def __init__(self, parent=None, children=[], cost=0, heuristic=0,current_pancakes=None, from_spatula=None):
        self.parent = parent
        self.children = children
        self.cost = cost
        self.heuristic = heuristic
        self.current_pancakes = current_pancakes
        # assign 1, 2, 3 or 4, indicating how were pancakes flipped to get to this state node
        self.from_spatula = from_spatula

    # check if the goal condition is met, i.e. pancakes in order
    def check_goal(self):
        for _ in range(len(self.current_pancakes)):
            if _ % 2 == 0:
                if int(self.current_pancakes[_]) != (_ + 2)/2:
                    return False
            else:
                if self.current_pancakes[_] != 'w':
                    return False
        return True

    # evaluate the heuristic for the current node, by identifying the largest pancake ID that is not in order
    def evaluate_heuristic(self, pancakes_seq):
        ids_not_in_order = []
        for pancake_id in range(1, num_of_pancakes + 1):
            if pancake_id != int(pancakes_seq[pancake_id * 2 - 2]):
                ids_not_in_order.append(pancake_id)
            else:
                if pancakes_seq[pancake_id * 2 - 1] == 'b':
                    ids_not_in_order.append(pancake_id)
        if len(ids_not_in_order) == 0:
            return 0
        else:
            return max(ids_not_in_order)

# Pancakes search graph class
class PancakesGraph:
    
    def __init__(self, root=None):
        self.root = root
        self.check_fringe = set() # only store pancakes string sequence to avoid visiting an expanded node
        self.nodes_fringe = [] # candidate nodes to be expanded
 
    # flip the pancakes(meaning to expand this node)
    def expand_flip(self, pancakes_node):
        pancakes_to_flip = list(pancakes_node.current_pancakes)
        # flip times based on the number of pancakes
        for flip_at in range(1, num_of_pancakes + 1):
            flipped_pancakes = copy.deepcopy(pancakes_to_flip)
            pancakes_to_be_flipped = []
            for j in range(flip_at):
                pancakes_to_be_flipped.append((flipped_pancakes[j * 2], flipped_pancakes[j * 2 + 1]))
            pancakes_to_be_flipped.reverse()
            for k in range(len(pancakes_to_be_flipped)):
                flipped_pancakes[2 * k] = pancakes_to_be_flipped[k][0]
                flipped_pancakes[2 * k + 1] = 'b' if pancakes_to_be_flipped[k][1] == 'w' else 'w'
            flipped_pancakes = "".join(flipped_pancakes)
            # if the newly flipped pancake sequence has not been seen before, a node will be formed with this sequence and added to the graph
            if flipped_pancakes not in self.check_fringe:
                expanded_node = PancakesNode(
                        parent=pancakes_node, 
                        children=[], 
                        cost=pancakes_node.cost+flip_at,
                        heuristic=pancakes_node.evaluate_heuristic(flipped_pancakes),
                        current_pancakes=flipped_pancakes,
                        from_spatula=flip_at
                        )
                pancakes_node.children.append(expanded_node)
                self.check_fringe.add(flipped_pancakes)
                self.nodes_fringe.append(expanded_node)
        # After this node is expanded, remove it from the fringe. And be careful to not remove this sequence from the check_fringe, which caused bug initially
        # self.check_fringe.remove(pancakes_node.current_pancakes)
        self.nodes_fringe.remove(pancakes_node)
    
    # traversely prints out the flipping order using a stack, based on the algorithm chosen
    def print_output(self, goal_node):
        print_stack = []
        tmp_node = goal_node
        # when this node is along the print path and not root(need to be treated saparately), added to the print stack
        while tmp_node.parent != None:
            print_stack.append(tmp_node)
            tmp_node = tmp_node.parent
        # add root
        print_stack.append(tmp_node)
        # the last print line, which prints the goal node sequence needs to be treated saparately
        while len(print_stack) != 1:
            curr_print_node = print_stack.pop()
            flipped_at = print_stack[-1].from_spatula
            flip_string = curr_print_node.current_pancakes[:2*flipped_at] + '|' + curr_print_node.current_pancakes[2*flipped_at:]
            if algo == 'a':
                print(f"{flip_string} g={curr_print_node.cost}, h={curr_print_node.heuristic}")
            else:
                print(flip_string)
        # print the goal node
        if algo == 'a':
                print(f"{goal_node.current_pancakes} g={goal_node.cost}, h={goal_node.heuristic}")
        else:
            print(goal_node.current_pancakes)

    # tie breaking mechanism by converting sequnce to 8-digit int and choose the maximum one
    def break_tie(self, fringe_to_check):
        if len(fringe_to_check) == 1:
            return fringe_to_check[0]
        else:
            eight_digits = []
            for node in fringe_to_check:
                eight_digit = []
                for char in node.current_pancakes:
                    if char == 'w':
                        eight_digit.append('1')
                    elif char == 'b':
                        eight_digit.append('0')
                    else:
                        eight_digit.append(str(char))
                eight_digits.append(int("".join(eight_digit)))
            return fringe_to_check[eight_digits.index(max(eight_digits))]

    # Starting point of BFS search
    def BFS(self):
        # first check if fringe still has nodes to expand
        while len(self.nodes_fringe) != 0:
            # expand the node by tie-breaking if there is more than one node in the fringe
            node_to_expand = self.break_tie(self.nodes_fringe)
            # Before expanding, check if this node is the goal node; print the path and end the program if this is the goal node
            if node_to_expand.check_goal() == False:
                self.expand_flip(node_to_expand)
            else:
                self.print_output(node_to_expand)
                return
        sys.exit('No solution found!') # may never execute

     # Starting point of A* search
    def A_star(self):
        while len(self.nodes_fringe) != 0:
            if len(self.nodes_fringe) == 1:
                node_to_expand = self.nodes_fringe[0]
            else:
                # Compared to BFS, A* chooses the node with the minimum g(n)+h(n) to expand rather than using a customized tie-breaking mechanism. However, if there is more than one node that has the same minimum of g(n)+h(n), then use the customized tie-breaking to choose a node to expand.
                candidate_nodes = []
                nodes_cost_heuristic_sum = []
                for node in self.nodes_fringe:
                    nodes_cost_heuristic_sum.append(node.cost + node.heuristic)
                min_sum = min(nodes_cost_heuristic_sum)
                for node_iter in range(len(nodes_cost_heuristic_sum)):
                    if min_sum == nodes_cost_heuristic_sum[node_iter]:
                        candidate_nodes.append(self.nodes_fringe[node_iter])
                node_to_expand = self.break_tie(candidate_nodes)
            if node_to_expand.check_goal() == False:
                self.expand_flip(node_to_expand)
            else:
                self.print_output(node_to_expand)
                return
        sys.exit('No solution found!') # may never execute

# Create the search graph
pancakes_graph = PancakesGraph()
# Add its root
pancakes_graph.root = PancakesNode(current_pancakes=input_pancakes)
# Evaluate the heuristic of the root node
pancakes_graph.root.heuristic = pancakes_graph.root.evaluate_heuristic(pancakes_graph.root.current_pancakes)
# Add root node to the fringe
pancakes_graph.check_fringe.add(pancakes_graph.root.current_pancakes)
pancakes_graph.nodes_fringe.append(pancakes_graph.root)

# Start the main program
if algo == 'b':
    print("Using BFS -")
    pancakes_graph.BFS()
elif algo == 'a':
    print("Using A* -")
    pancakes_graph.A_star()
else:
    sys.exit("Please input a valid algorithm indicator - 'a' or 'b'.")