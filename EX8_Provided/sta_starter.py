import json
import argparse
import copy
from os import PathLike, curdir
from pprint import pprint

# Avoid modifying these values for your initial implementation
# Once your implementation is completed and tested, you may subsequently
# find it interesting to mess with these numbers to see what happens

# Holds the delays of each cell type in a dictionary.
DELAY_DICT = {"$_NOT_" : 5, "$_AND_" : 9, "$_OR_" : 9, "$_XOR_" : 12,
              "$_NAND_" : 13, "$_NOR_" : 12, "$_XNOR_" : 12, "$_DFF_P_": None}

# Constants determining timing
# characteristics of circuit
CLOCK_PERIOD = 50
SETUP_TIME   = 8 # time that DFF input needs to be stable before the clock edge
HOLD_TIME    = 4 # time that DFF input needs to be stable after the clock edge
CLK2Q_MIN    = 1 # fastest time between clock edge and DFF output changing
CLK2Q_MAX    = 5 # slowest time between clock edge and DFF output changing

CLK_SKEW_MAX = 3 # worst case skew


# main entry point
def main():
    # Get arguments from commandline
    # and parse the JSON file
    # you shouldn't need to change this bit
    parser = argparse.ArgumentParser()
    parser.add_argument('json_filename', type=str)
    args = parser.parse_args()
    asic = ASIC(args.json_filename)

    # display the stats initially (before calculating paths)
    asic.display_asic()

    # calculate paths and display asic again
    asic.paths = get_paths(asic)
    asic.display_asic()

    analyze_path(asic.paths, asic)

    # TODO: you'll probably want to call into your other functions here to test them


def get_paths(asic):
    paths = []
    # TODO: you will implement this function

    endpoints = []
    for output in asic.outputs:
        for cell in asic.cell_list:
            if output in cell.outputs:
                endpoints.extend(cell.inputs)
    working_paths = []

    for endpoint in endpoints:
        path = []
        working_paths.append(path)

        while len(working_paths) != 0:
            p = working_paths.pop()

            if len(p) == 0:
                current_net = endpoint
            else:
                current_net = p[-1].input_net

            for cell in asic.cell_list:
                if current_net in cell.outputs:
                    if cell.type == '$_DFF_P_':
                        paths.append(list(reversed(p)))
                    else:
                        for inputs in cell.inputs:
                            temp = p.copy()
                            temp.append(PathHop(cell, inputs, current_net))
                            working_paths.append(temp)

    # Don't remove this, it verifies path correctness
    check_paths(paths)
    print("Number of paths", len(paths))
    return paths

def get_longest_paths(path_list, n):
    paths = []
    for path in path_list:
        total_delay = 0
        for hop in path:
            total_delay += hop.cell.delay
        paths.append((total_delay, path))
    return [item[1] for item in sorted(paths, key=lambda e: e[0], reverse=True)[:n]], [item[0] for item in sorted(paths, key=lambda e: e[0], reverse=True)[:n]]

def get_shortest_paths(path_list, n):
    paths = []
    for path in path_list:
        total_delay = 0
        for hop in path:
            total_delay += hop.cell.delay
        paths.append((total_delay, path))
    return [item[1] for item in sorted(paths, key=lambda e: e[0])[:n]], [item[0] for item in sorted(paths, key=lambda e: e[0])[:n]]

def analyze_path(path_list, asic):
    paths = []
    t_prop = []
    for i in range(5, 1, -1):
        try:
            paths, t_prop = get_longest_paths(path_list, i)
            break
        except:
            ...

    if len(paths) == 0:
        print("no paths")

    for i in range(len(paths)):
        print_path(asic, paths[i])
        if CLK2Q_MAX + t_prop[i] <= CLOCK_PERIOD - CLK_SKEW_MAX:
            print("within timing")
        else:
            print("fails timing")
        print("slack:", CLOCK_PERIOD - CLK_SKEW_MAX - t_prop[i] - CLK2Q_MAX)


######## You shouldn't need to modify anything below this line, but you may find it useful for reference

# prints a path
def print_path(asic, path):
    print("Start path:")
    print(f" - DFF output")
    if len(path):
        print(f" -> Net {path[0].input_net} ({asic.net_dict[path[0].input_net]})")
    for hop in path:
        print(f" -> Cell {hop.cell}")
        print(f" -> Net {hop.output_net} ({asic.net_dict[hop.output_net]})")
    print(f" -> DFF input (end path)")
    print()

# Holds information about a single hop in a path
## DO NOT MODIFY
class PathHop:
    def __init__(self, cell, input_net, output_net):
        if not isinstance(input_net, int):
            raise Exception(f"Net must be of type int. Provided '{input_net}' is of type {type(net)}")

        if input_net not in cell.inputs:
            raise Exception(f"The 'input_net' in a PathHop must be an input of the given cell. Net {input_net} is not an input to cell {cell}")

        if not isinstance(output_net, int):
            raise Exception(f"Net must be of type int. Provided '{output_net}' is of type {type(net)}")

        if output_net not in cell.outputs:
            raise Exception(f"The 'output_net' in a PathHop must be an output of the given cell. Net {output_net} is not an output of cell {cell}")

        self.cell = cell
        self.input_net = input_net
        self.output_net = output_net

    def __repr__(self):
        return f"<PathHop input_net={self.input_net} output_net={self.output_net} cell={self.cell}>"

# helper function to check validity of a list of paths
def check_paths(paths):
    for path in paths:
        if not all(isinstance(x, PathHop) for x in path):
            raise Exception(f"Path {path} is not of type list[PathHop]. This is not allowed.")

        if any(x.cell.type == "$_DFF_P" for x in path):
            raise Exception(f"Path {path} contains a DFF cell. This is not allowed - paths should only be combinational logic, and are assumed to start/end with a DFF.")

        if len(path) == 0:
            continue

        last = path[0]
        for hop in path[1:]:
            if last.output_net != hop.input_net:
                raise Exception(f"Path {path} is not contiguous. All paths must be contiguous (the output of each hop should be the input of the next hop)")

            last = hop

# Cell Class!!!
# Holds information about a specific cell in your circuit

# DO NOT MODIFY
class Cell:
    def __init__(self, cell_type, inputs, outputs) -> None:
        self.type = cell_type              # Name of cell, as seen in DELAY_DICT 
        self.inputs = inputs               # List of input net numbers 
        self.outputs = outputs             # List of output net numbers

        if cell_type not in DELAY_DICT:
            raise Exception(f"Cell type '{cell_type}' is unknown. This may be caused by a synthesis issue.")

        self.delay = DELAY_DICT[cell_type] # Delay of cell. Don't modify

    def __repr__(self):
        return f"<Cell '{self.type}' in={self.inputs} out={self.outputs} delay={self.delay}>"


# ASIC Class!!!
# Holds information abou your entire circuit

# DO NOT MODIFY
class ASIC:
    def __init__(self, file_name) -> None:
        self.cell_list = None      # List of all cells in the circuit
        self.inputs = None        # List of all inputs wires 
        self.outputs = None        # List of all output wires
        self.net_dict = None        # Dictionary of all wires in the circuit
        self.paths = None        # List of all logic paths. You'll fill this in get_paths()


        self.cell_list, self.inputs, self.outputs, self.net_dict =  parse_json(file_name)

    def display_asic(self):
        print("-----------")
        print("ASIC INFO")
        print("-----------")

        print("\n-------CELL LIST-------")
        for cell in self.cell_list:
            print("Type: " + str(cell.type) + " Inputs: " + str(cell.inputs) + " Outputs: " + str(cell.outputs))

        print()
        print("\n-------I/O LIST-------")
        print("Inputs: " + str(self.inputs))
        print("Outputs: " + str(self.outputs))

        print()
        print("\n-------Net Mappings-------")
        for bit in self.net_dict:
            print(f"[{bit}] -> {self.net_dict[bit]}")

        print()
        print("\n-------Paths-------")

        if self.paths is None or len(self.paths) == 0:
            print("(no paths found)")
        else:
            for path in self.paths:
                print_path(self, path)

        print("\n-------End ASIC Info-------")
        print()


# Function to initialize the ASIC object
# DO NOT MODIFY
def parse_json(filename):
    # Load json File
    with open(filename) as f:
         netlist_dict = json.load(f)

    # Used to remove the clock input from FFs
    # We should use clock in any paths :)
    clock_bit = -1

    # Parse through every cell and store its type, inputs and outputs
    for top_name in netlist_dict['modules']:
        cell_dict = netlist_dict['modules'][top_name]['cells']
        netlist = list()

        for cell in cell_dict:
            cell_type = cell_dict[cell]['type']
            inputs = list()
            outputs = list()

            for connection in cell_dict[cell]['connections']:
                if cell_dict[cell]['port_directions'][connection] == "input":
                    for bit in cell_dict[cell]['connections'][connection]:
                        if (cell_type != "$_DFF_P_" or connection != "C"):
                            inputs.append(bit)
                        else: clock_bit = bit
                else:
                    for bit in cell_dict[cell]['connections'][connection]:
                        outputs.append(bit)

            new_cell = Cell(cell_type, inputs, outputs)
            netlist.append(new_cell)

        # Parse through every port connection of the module and store 
        # the port as either an input or an output
        port_dict = netlist_dict['modules'][top_name]['ports']
        asic_in = list()
        asic_out = list()

        for port in port_dict:

            if port_dict[port]['direction'] == "input":
                for bit in port_dict[port]['bits']:
                    if bit != clock_bit:
                        asic_in.append(bit)

            else:
                for bit in port_dict[port]['bits']:
                    asic_out.append(bit)

        net_names = netlist_dict['modules'][top_name]['netnames']
        net_dict = dict()

        for name in net_names:
            bit_list = net_names[name]['bits']
            if len(bit_list) == 1:
                net_dict[bit_list[0]] = name
            else:
                for i in range(len(bit_list)):
                    net_dict[bit_list[i]] = (str(name) + f'[{i}]')

    return netlist, asic_in, asic_out, net_dict


if __name__ == '__main__':
    main()



