from boa.compiler import Compiler

Compiler.load_and_save('neospace.py')

# return the compiler object for inspection
compiler = Compiler.load('neospace.py')

# retrieve the default module for inpection
default_module = compiler.default

# retreive the default/entry method for the smart contract
entry_method = default_module.main
