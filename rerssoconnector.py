from subprocess import check_output
import re

from ctypes import *

class RERSSOConnector():
    def __init__(self, path_to_so):
        self.path_to_so = path_to_so

        # Hook up the shared library
        self.dll = CDLL(path_to_so)

        # Set types
        self.dll.reset.restype = None
        self.dll.calculate_output.argtypes = [c_int]
        self.dll.calculate_output.restype = c_int

        # Be sure to initialize all variables in the RERS code
        self.dll.reset()

    def process_input(self, inputs):
        output = None
        for input in inputs:
            output = self.dll.calculate_output(int(input))
            if output < -1:
                return f'error_{str((output * -1))}'

        if output == -1:
            return "invalid_input"

        return str(output)

    def reset(self):
        self.dll.reset()

    def get_alphabet(self):
        # Grep the source file for the line defining the input alphabet
        tmp = check_output(["grep", "-o", "int inputs\[\] \= {\(.*\)};", f"{str(self.path_to_so).replace('.so', '')}.c"])
        # Extract it and put it into a list
        return re.search('{(.*)}', tmp.decode()).group(1).split(',')


