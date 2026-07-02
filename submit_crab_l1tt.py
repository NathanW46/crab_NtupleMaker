#!/bin/env python
"""
CRAB submission script for the L1 Track NtupleMaker.

Usage:
  python3 submit_crab_l1tt.py HYBRID DispSUSY_PU200 \
      -o outputHLT.root -a mytag -c 2 -s 8000 -n 10 -d ntuples

Inputs (most to least important):
  algorithm  L1 tracking algorithm  (positional, restricted to known list)
  mcsample   sample key             (positional, must match sample_dict)
  -o/--outfile   output ROOT file name
  -a/--tag       tag for output dir / CRAB request
  -c/--cores     cores per job
  -s/--storage   memory (maxMemoryMB, RAM) per job
  -t/--test      generate config but do NOT submit

What it does:
  1. Generates a CRAB config (crab_cfg_<sample>.py) under <outdir>/<tag>/
  2. Forwards <algorithm> and <outfile> to the remote pset via pyCfgParams
  3. Submits via `crab submit` (skip with -t / --test)

MUST CHANGE 
L1TRKALGO line in L1NtupleMaker_cfg.py to:
L1TRKALGO = os.environ.get('L1TRKALGO', 'HYBRID')
"""

import os
import datetime
from argparse import ArgumentParser

username = "nwhittin"
initial  = username[0]

# Valid L1 tracking algorithms (see L1TrackNtupleMaker_cfg.py).
VALID_ALGOS = [
    'HYBRID', 'HYBRID_DISPLACED', 'HYBRID_NEWKF', 'HYBRID_REDUCED',
    'HYBRID_SIM', 'HYBRID_SIM_DISPLACED', 'TMTT', 'TRACKLET',
]

parser = ArgumentParser()
parser.add_argument("algorithm", choices=VALID_ALGOS,
                    help="TF tracking algorithm")
parser.add_argument("mcsample", help="sample key (must match sample_dict)")
parser.add_argument("-o", "--outfile", dest="outfile",
                    help="output ROOT file name", default="outputHLT.root")
parser.add_argument("-a", "--tag", dest="tag",
                    help="tag for output dir / CRAB request", default="ntuples")
parser.add_argument("-c", "--cores", dest="cores", type=int,
                    help="number of cores per job", default=1)
parser.add_argument("-s", "--storage", dest="storage", type=int,
                    help="memory per job in MB (maxMemoryMB); "
                         "default = cores * 2500", default=0)
parser.add_argument("-e", "--events", dest="events", type=int,
                    help="max events processed per job/file", default=1000)
parser.add_argument("-n", "--njobs", dest="njobs", type=int,
                    help="number of input files to process", default=1)
parser.add_argument("-d", "--outdir", dest="outdir",
                    help="output sub-directory label", default="ntuples")
parser.add_argument("-t", "--test", dest="test", action="store_true",
                    help="generate config but do NOT submit", default=False)
args = parser.parse_args()



# sample dictionary 
sample_dict = {
    'DispSUSY_PU200': '/DisplacedSUSY_stopToBottom_M-800_50mm_TuneCP5_14TeV-pythia8'
                      '/Phase2Spring24DIGIRECOMiniAOD-PU200_AllTP_140X_mcRun4_realistic_v4-v1'
                      '/GEN-SIM-DIGI-RAW-MINIAOD',
    'TTbar':          '/RelValTTbar_14TeV'
                      '/CMSSW_14_0_0_pre2-PU_133X_mcRun4_realistic_v1_STD_2026D98_PU200_RV229-v1'
                      '/GEN-SIM-DIGI-RAW',
    'DoubleMu_PU0':   '/RelValDoubleMuFlatPt1To100Dxy100GunProducer'
                       '/CMSSW_15_1_0_pre5-150X_mcRun4_realistic_v1_RV269_Run4D110_noPU-v1'
                       '/GEN-SIM-DIGI-RAW',
}

if args.mcsample not in sample_dict:
    parser.error("unknown sample '%s'; choose from: %s"
                 % (args.mcsample, ', '.join(sample_dict)))


# derived quantities
ds_name   = sample_dict[args.mcsample]
pset      = os.path.realpath(args.pset)
base_out  = '%s/%s' % (args.outdir, args.tag)
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# CRAB requestName
request_name = '%s_%s_%s_%s' % (args.algorithm, args.mcsample, args.tag, timestamp)
request_name = request_name.replace('-', '_').replace(' ', '_')[:100]

# Output goes to personal directory based on
# compute location. i.e. T2_CERN_CH
eos_lfn_base = '/store/user/%s/%s/' % (username, base_out)

# # totalUnits limits files processed (same role as -n in condor script)
# total_units_line = ''
# if args.njobs > 0:
#     total_units_line = 'config.Data.totalUnits          = %d' % args.njobs

# resources: memory defaults to 2500 MB/core
ncores    = args.cores
memory_mb = args.storage if args.storage > 0 else 2500 * ncores

# pyCfgParams: forward algorithm + output file name 
# The pset (customise_L1TrackNtupleMaker.py) reads these via VarParsing.
py_cfg_params = "['algo=%s', 'outputFile=%s', 'maxEvents=%d']" % (
    args.algorithm, args.outfile, args.events)

# create output directory & write CRAB config 
os.makedirs(base_out, exist_ok=True)
cfg_path = os.path.join(base_out, 'crab_cfg_%s.py' % args.mcsample)

crab_cfg = """\
from CRABClient.UserUtilities import config
config = config()

# ── General ──────────────────────────────────────────────────────────────
config.General.requestName          = '{request_name}'
config.General.workArea             = '{base_out}/crab_projects'
config.General.transferOutputs      = True
config.General.transferLogs         = True

# ── JobType ──────────────────────────────────────────────────────────────
config.JobType.pluginName           = 'Analysis'
config.JobType.psetName             = 'L1NtupleMaker_cfg.py'
# Forward the L1 tracking algorithm + output file name to the pset.
config.JobType.pyCfgParams          = {py_cfg_params}
# The pset uses TFileService -> {outfile}; CRAB needs this declared
config.JobType.outputFiles          = ['{outfile}']
config.JobType.maxMemoryMB          = {memory_mb}
config.JobType.numCores             = {ncores}
# condor +JobFlavour "tomorrow" ~ 24 h
config.JobType.maxJobRuntimeMin     = 1440

# ── Data ─────────────────────────────────────────────────────────────────
config.Data.inputDataset            = '{dataset}'
config.Data.inputDBS                = 'global'
config.Data.splitting               = 'FileBased'
config.Data.unitsPerJob             = 1          # one file per job (same as condor)
config.Data.outLFNDirBase           = '{eos_lfn_base}'
config.Data.outputDatasetTag        = '{tag}'
config.Data.publication             = False
# Allow jobs to run at ANY site (read input via XRootD) -- faster scheduling
config.Data.ignoreLocality          = True

config.Site.storageSite             = 'T2_CERN_CH'
# Open up scheduling to all T1/T2/T3 sites
config.Site.whitelist               = ['T1_*', 'T2_*', 'T3_*']
""".format(
    request_name     = request_name,
    base_out         = base_out,
    pset             = pset,
    py_cfg_params    = py_cfg_params,
    outfile          = args.outfile,
    dataset          = ds_name,
    eos_lfn_base     = eos_lfn_base,
    tag              = args.tag,
    memory_mb        = memory_mb,
    ncores           = ncores,
)

with open(cfg_path, 'w') as f:
    f.write(crab_cfg)

# ── summary ─────────────────────────────────────────────────────────────
njobs_str = str(args.njobs) if args.njobs > 0 else 'ALL'
print('──────────────────────────────────────────────')
print('CRAB config written to : %s' % cfg_path)
print('Request name           : %s' % request_name)
print('Algorithm              : %s' % args.algorithm)
print('Dataset                : %s' % ds_name)
print('Output file            : %s' % args.outfile)
print('Max events per job     : %s' % ('ALL' if args.events < 0 else str(args.events)))
print('Files to process       : %s' % njobs_str)
print('Cores / Memory per job : %d / %d MB' % (ncores, memory_mb))
print('Ignore locality        : True')
print('Output LFN base        : %s' % eos_lfn_base)
print('Storage site           : T3_CH_CERNBOX')
print('  -> /eos/user/%s/%s/%s/' % (initial, username, base_out))
print('──────────────────────────────────────────────')

if not args.test:
    cmd = 'crab submit -c %s' % cfg_path
    print('Submitting: %s' % cmd)
    os.system(cmd)
else:
    print('[TEST MODE] To submit manually run:')
    print('  crab submit -c %s' % cfg_path)
