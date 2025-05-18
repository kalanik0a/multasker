import argparse
from multasker.util import Arguments

class ArgumentsNoClose(Arguments):
    def __init__(self, args:dict):
        super().__init__(args)

    def exit(self, status=0, message=None):
        if message:
            print(message)
        print("Continuing execution...")  # Your custom logic here