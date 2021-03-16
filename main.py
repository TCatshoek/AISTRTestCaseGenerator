from pathlib import Path
from rerssoconnector import RERSSOConnector
from utils import CorpusUtils
import re

# Reads the alphabet mapping from a file
def _read_alphabet_mapping(mapping_path):
    alphabet_mapping = {}
    try:
        with Path(mapping_path).open('r') as file:
            for line in file.readlines():
                j_symbol, c_symbol = line.split()
                alphabet_mapping[c_symbol] = j_symbol
        return alphabet_mapping
    except FileNotFoundError:
        return None

# Builds the alphabet mapping from the source when no file is available
# Kinda unnecessary since it is just a mapping from alphabet position to integers
def _build_alphabet_mapping(problem_path):
    problem = Path(problem_path).stem

    # Find the possible java inputs and outputs
    java_path = Path(problem_path).joinpath(f'{problem}.java')
    java_outputs = set()
    java_inputs = None
    c_path = Path(problem_path).joinpath(f'{problem}.c')
    c_outputs = set()
    c_inputs = None

    with open(java_path, 'r') as file:
        for line in file.readlines():
            # Inputs
            match = re.search(r'private String\[\] inputs = \{(.*)\};', line)
            if match:
                java_inputs = set(match.group(1).replace("\"", "").split(','))
            # Outputs
            match = re.search(r'System\.out\.println\(\"([A-Z])\"\);', line)
            if match:
                java_outputs.add(match.group(1))

    with open(c_path, 'r') as file:
        for line in file.readlines():
            # Inputs
            match = re.search(r'int inputs\[\] = {(.*)};', line)
            if match:
                c_inputs = set(match.group(1).replace("\"", "").split(','))
            # Outputs
            match = re.search(r'printf\(\"%d\\n\"\, ([0-9]+)\);', line)
            if match:
                c_outputs.add(match.group(1))

    java_symbols = list(sorted(java_inputs)) + list(sorted(java_outputs))
    c_symbols = list(sorted(c_inputs, key=int)) + list(sorted(c_outputs, key=int))

    print("C symbols: ", c_symbols)
    print("Java symbols: ", java_symbols)

    return {c_sym: j_sym for c_sym, j_sym in zip(c_symbols, java_symbols)}

def get_alphabet_mapping(problem_path):
    problem = Path(problem_path).stem
    assert "Problem" in problem, f"Not a problem path: {problem_path}"

    mapping = None

    # Try to find the mapping path
    mapping_path = None
    for subpath in Path(problem_path).iterdir():
        if "alphabet_mapping" in str(subpath):
            mapping = _read_alphabet_mapping(subpath)
            break

    # If not found, generate a mapping
    if mapping is None:
        mapping = _build_alphabet_mapping(problem_path)

    assert mapping is not None, "This should never happen"

    return mapping

def build_testcases(problem_path):
    alphabet_mapping = get_alphabet_mapping(problem_path)

    problem_path = Path(problem_path)
    problem = Path(problem_path).stem

    sul = RERSSOConnector(problem_path.joinpath(f'{problem}.so'))
    #sul = RERSConnectorV4(problem_path.joinpath(f'{problem}'))
    cutils = CorpusUtils(
        corpus_path=problem_path.joinpath('corpus'),
        fuzzer_path=problem_path.joinpath(f'{problem}_fuzz'),
        sul=sul
    )

    cutils.minimize_corpus()
    testcase_inputs = cutils.gather_testcases(return_time_date=False, minimized=True)
    testcase_inputs_ran = []
    testcase_outputs = []

    # Run the inputs
    for testcase_input in testcase_inputs:
        testcase_input_ran = []
        testcase_output = []
        sul.reset()
        for input_symbol in testcase_input:
            output_symbol = sul.process_input([int(input_symbol)])
            testcase_input_ran.append(input_symbol)
            #if output_symbol != "invalid_input" and "error" not in output_symbol:
            if 'error' in output_symbol:
                _, err_output = output_symbol.split('_')
                testcase_output.append(err_output)
                break
            else:
                testcase_output.append(output_symbol)

        testcase_outputs.append(testcase_output)
        testcase_inputs_ran.append(testcase_input_ran)

    traces = []
    # Create input output pairs, strip out invalid inputs and errors
    for inp, outp in zip(testcase_inputs_ran, testcase_outputs):
        #traces.append(list(filter(lambda x: x[1] != 'invalid_input' and 'error' not in x[1], zip(inp, outp))))
        traces.append(list(zip(inp, outp)))

    # Translate traces to java symbols and write to file
    to_write = set()
    to_write_c = set()
    for trace in traces:
        # Translate
        java_i = []
        java_o = []
        c_i = []
        c_o = []
        for (i, o) in trace:
            try:
                java_i.append(alphabet_mapping[i])
                c_i.append(i)
            except KeyError:
                print("Skipping", i)
            try:
                java_o.append(alphabet_mapping[o])
                c_o.append(o)
            except KeyError:
                print("Skipping", o)

        if len(java_i) > 0 and len(java_o) > 0:
            to_write.add(f'{",".join(java_i)}->{"".join(java_o)}\n')
            to_write_c.add(f'{",".join(c_i)}->{"".join(c_o)}\n')


    with open(f'testcases/{problem}Testcases.txt', 'w') as file:
        for line in sorted(to_write, key=lambda x: (len(x), x)):
            file.write(line)


if __name__=="__main__":
    # Make sure output dir exists
    Path("testcases").mkdir(exist_ok=True)

    # Helper functions to run in parallel
    def do_reachability(problem):
        build_testcases(f'libfuzzer/SeqReachabilityRers2020/{problem}')
    def do_ltl(problem):
        build_testcases(f'libfuzzer/SeqLtlRers2020/{problem}')

    # Create testcases for all problems
    import multiprocessing
    with multiprocessing.Pool(6) as pool:
        pool.map(do_reachability, [f"Problem{n}" for n in range(11,20)])
    with multiprocessing.Pool(6) as pool:
        pool.map(do_ltl, [f"Problem{n}" for n in range(1,10)])