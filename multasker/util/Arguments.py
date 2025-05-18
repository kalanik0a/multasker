import argparse
from email.policy import default
from sys import deactivate_stack_trampoline


class Arguments(argparse.ArgumentParser):
    def __init__(self, args:dict):
        self.args = args
        self.parser = None
        x = self.option_or_default
        super().__init__(prog=x(collection=self.args, name='prog'),
                          usage=x(collection=self.args, name='usage'),
                          description=x(collection=self.args, name='description'),
                          epilog=x(collection=self.args, name='epilog'),
                          parents=x(collection=self.args, name='parents', default=[]),
                          formatter_class=x(collection=self.args, name='formatter_class', default=argparse.HelpFormatter),
                          prefix_chars=x(collection=self.args, name='prefix_chars', default='-'),
                          fromfile_prefix_chars=x(collection=self.args, name='fromfile_prefix_chars'),
                          argument_default=x(collection=self.args, name='argument_default'),
                          conflict_handler=x(collection=self.args, name='conflict_handler', default='error'),
                          add_help=x(collection=self.args, name='add_help', default=True),
                          allow_abbrev=x(collection=self.args, name='allow_abbrev', default=True),
                          exit_on_error=x(collection=self.args, name='exit_on_error', default=True))

    @staticmethod
    def option_or_default(collection:dict, name:str, default=None):
        if name in collection.keys():
            return collection[name]
        else:
            return default