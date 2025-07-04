"""
Author: Changbeom Choi (@cbchoi)
Copyright (c) 2014-2020 Handong Global University
Copyright (c) 2021-2024 Hanbat National University
License: MIT.  The full license text is available at:
https://github.com/eventsim/pyjevsim/blob/main/LICENSE
 
Simple GP example using Behavior Models.

PEG(process event generator) model generates events periodically.
Buffer model stores and forwards Events generated by the PEG.
MsgRecv handles the event messages generated by the PEG.

Usage:
From a terminal in the parent directory, run the following command.

   pytest -s ./tests/test_behavioral_model.py 
"""

import math
import time

from pyjevsim.definition import *
from pyjevsim.system_executor import SysExecutor
from .model_msg_recv import MsgRecv
from .model_peg import PEG

def execute_simulation(t_resol=1, execution_mode=ExecutionType.V_TIME):
    # System Executor Initialization
    se = SysExecutor(t_resol, ex_mode=execution_mode, snapshot_manager=None)
    se.insert_input_port("start")

    # Model Creation
    gen = PEG("Gen")
    proc = MsgRecv("Proc")

    # Register Model to Engine
    se.register_entity(gen)
    se.register_entity(proc)

    # Set up relation among models
    se.coupling_relation(se, "start", gen, "start")
    se.coupling_relation(gen, "process", proc, "recv")

    # Inject External Event to Engine
    se.insert_external_event("start", None)
    
    for _ in range(3):
        se.simulate(1)


# Test Suite
def test_casual_order1(capsys):
    execute_simulation(1, ExecutionType.V_TIME)
    
    captured = capsys.readouterr()
    
    desired_output = (
        "[Gen][IN]: started\n[Gen][OUT]: 0\n"
        + "[MsgRecv][IN]: 0\n[Gen][OUT]: 1\n[MsgRecv][IN]: 1\n"
    )
    assert captured.out == desired_output
    
def test_execution_mode():
    before = time.perf_counter()
    execute_simulation(1, ExecutionType.R_TIME)
    after = time.perf_counter()
    diff = after - before
    assert math.isclose(diff, 3, rel_tol=0.05)

def test_classical_devs(capsys):
    from .model_classic_peg import PEG as CPEG
    se = SysExecutor(1, ex_mode=ExecutionType.V_TIME, snapshot_manager=None)
    se.insert_input_port("start")

     # Model Creation
    gen = CPEG("Gen")
    proc = MsgRecv("Proc")

    # Register Model to Engine
    se.register_entity(gen)
    se.register_entity(proc)

    # Set up relation among models
    se.coupling_relation(se, "start", gen, "start")
    se.coupling_relation(gen, "process", proc, "recv")

    # Inject External Event to Engine
    se.insert_external_event("start", None)

    for _ in range(3):
        se.simulate(1)

    captured = capsys.readouterr()
    assert "classic" in captured.out