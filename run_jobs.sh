#!/usr/bin/bash
python3 submit_crab.py -n 9000 -t 8 -s ttbar0PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 1000 -t 8 -s ttbar200PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 9000 -t 8 -s ttbar0PU -algo HYBRID_SIM_DISPLACED
python3 submit_crab.py -n 1000 -t 8 -s ttbar200PU -algo HYBRID_SIM_DISPLACED




