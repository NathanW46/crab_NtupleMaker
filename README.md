# L1 Track NtupleMaker — CRAB submission

A small wrapper for running the L1 Track NtupleMaker over a dataset on the grid.
You give it an algorithm and a sample, it writes a CRAB config and submits it.

## Usage 


```bash
python3 submit_crab_l1tt.py HYBRID_DISPLACED DispSUSY_PU200 \
    -o myntuple.root -a v1 -c 2 -e 500 -n 10
```

### Options

| Flag | What it does | Default |
|------|--------------|---------|
| `algorithm` | L1 tracking algorithm (positional) | — required |
| `mcsample`  | Sample key (positional) | — required |
| `-o` | Output ROOT file name | `outputHLT.root` |
| `-a` | Tag for the output dir / CRAB request | `ntuples` |
| `-c` | Cores per job | `1` |
| `-s` | Memory per job in MB (RAM); defaults to `2500 × cores` | auto |
| `-e` | Max events processed per job | `1000` |
| `-n` | Number of input files to run over | `1` |
| `-d` | Output sub-directory label | `ntuples` |
| `-t` | Write the config but **don't** submit | off |

The algorithm has to be one of:
`HYBRID`, `HYBRID_DISPLACED`, `HYBRID_NEWKF`, `HYBRID_REDUCED`, `HYBRID_SIM`,
`HYBRID_SIM_DISPLACED`, `TMTT`, `TRACKLET`.

Samples come from the `sample_dict` near the top of `submit_crab_l1tt.py` 
