

# Some using hints
Dig ip address for Raspberry Pi

`nmap -sn 192.168.1.0/24`

# Visual studio code

Install jupyter notebook to running as local data can be then easily used.

Install first pyenv to handle multiple virtual environments. Python 3.9.18 is used in my case. Numpy is 1.26 (older than 2.0) and opencv-python 4.9.0.88


This might require
- pip install notebook
- pip install jupyterlab
- pip install ipykernel

# Migration to newer version

https://ai.google.dev/edge/litert/migration

New module can be istalled with

`python3 -m pip install ai-edge-litert`

`from ai_edge_litert.interpreter import Interpreter`

`interpreter = Interpreter(model_path=args.model_file`