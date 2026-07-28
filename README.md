# Crab Job Helper for TrackFinder
Creates a crab_cfg.py file and submits it to crab job manager

## Options
- `-n` Number of Events
- `-t` Number of parallel threads
- `-s` Sample to use (from dictionary inside submit_crab.py and (must?) match the same dict in N tuple maker)
- `-algo` Algorithm to use (must be valid for the N tuple Maker)
- `--test` Create config but do not submit

## Usage
`python3 submit_crab.py -n 1000 -t 4 -s SUSY200PU -algo HYBRID_DISPLACED`
