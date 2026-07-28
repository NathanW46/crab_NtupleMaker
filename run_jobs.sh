#!/usr/bin/bash
python3 submit_crab.py -n 9000 -t 4 -s SUSY0PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 9000 -t 4 -s SUSY200PU -algo HYBRID_DISPLACED
python3 submit_crab.py -n 9000 -t 4 -s SUSY0PU -algo HYBRID_SIM
python3 submit_crab.py -n 9000 -t 4 -s SUSY200PU -algo HYBRID_NEWKF




