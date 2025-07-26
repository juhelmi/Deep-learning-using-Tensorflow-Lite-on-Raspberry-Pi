# Purpose of additional notes
Original README.md is as is. Mainly things works as they have been working. Target is to get same or nearly same done with current tools. 

Python module versions have about same features or they could be newer.

Local run for jupyter notebook was used. Virtual environment handling is some how simpler. First run things is Ubuntu and later in Raspberry Pi. Pyenv works in bosth cases.

# Some using hints
Dig IP address for Raspberry Pi

`nmap -sn 192.168.1.0/24`

# Python virtual environment

Get pyenv install instructions from https://github.com/pyenv/pyenv or other tutorial.

```
pyenv install 3.9.23
pyenv virtualenv 3.9.23 course_env
pyenv activate course_env
note: use this environment also in vs code
```


- python -m pip install --upgrade pip
- pip install numpy==1.26
- pip install opencv-python==4.9.0.80
- pip install keras

- pip install tensorflow
- pip install tflite
- pip install tflite-runtime
- pip install matplotlib keras scipy

If tensorflow will not work then try ```tensorflow==2.19.0``` also not any more supported runtime is ```tflite-runtime==2.14.0```.

Some needed modules might be missing. Check errors and install what is missing.

# Visual studio code

Install jupyter notebook to running as local data can be then easily used.

Install first pyenv to handle multiple virtual environments. Python 3.9.18 is used in my case. Numpy is 1.26 (older than 2.0) and opencv-python 4.9.0.88

This might require
- pip install notebook
- pip install jupyterlab
- pip install ipykernel

# Python audio modules

- pip install sounddevice
- pip install seaborn


# Migration to newer version

https://ai.google.dev/edge/litert/migration

New module can be istalled with

`python3 -m pip install ai-edge-litert`

`from ai_edge_litert.interpreter import Interpreter`

`interpreter = Interpreter(model_path=args.model_file`