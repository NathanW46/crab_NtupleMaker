#!/usr/bin/bash
python3 submit_crab.py -n 10000 -t 8 -s DMuGun200PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 10000 -t 8 -s DMuGun200PU -algo HYBRID_SIM_DISPLACED
python3 submit_crab.py -n 1000 -t 8 -s SUSY200PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 1000 -t 8 -s SUSY200PU -algo HYBRID_SIM_DISPLACED




