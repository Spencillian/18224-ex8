Following are the included example designs (each one comes with a .sv file, a .png rendering, and a .json file for your code to use). All designs have registers on their inputs / outputs so that all relevant paths are between DFFs rather than being input/output paths.

- simple: Computes the XOR of two inputs. Contains 2 paths.
- shortpath: Contains a path directly between two DFFs. May cause hold violations.
- longpath: Takes 8 inputs and ANDs them together in a chained fashion.
- balanced: Similar to 'longpath' but the ANDing is balanced in a tree. Compare against 'longpath' for longest-path delays and setup-time.
- adder: Just a 3-bit adder
- reconvergent: A design with logic that splits off and then re-converges. Try tracing ALL the paths by hand and compare it to your path-finder implementation.
- multiout: A design with more outputs than inputs.
- mult: A 4-bit multiplier synthesized to gates (focus on general trends here)
- bigadder: A 16-bit adder (focus on the general trends here: which input-output pairs have the best and worst timing?). This one doesn't have a PNG because it was too big (use your imagination + your knowledge of adder architectures!)




----------------------

To synthesize new designs:

yosys -p 'read_verilog -sv THE_DESIGN.sv; synth -flatten; abc -fast -g AND,OR,XOR,NAND,NOR,XNOR; dffunmap; write_json THE_DESIGN.json'
