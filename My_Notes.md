

# Some using hints
Dig ip address for Raspberry Pi

`nmap -sn 192.168.1.0/24`

# Migration to newer version

https://ai.google.dev/edge/litert/migration

New module can be istalled with

`python3 -m pip install ai-edge-litert`

`from ai_edge_litert.interpreter import Interpreter`

`interpreter = Interpreter(model_path=args.model_file`