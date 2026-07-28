import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--maxEvents", help="Number of events to run", type=int, default=1000)
parser.add_argument("-s", "--sample", help="Sample to use", choices=["SUSY200PU", "SUSY0PU"], default="SUSY200PU")
parser.add_argument("-t", "--nThreads", help="Number of cores/threads", type=int, default=1)
parser.add_argument("-algo", "--algo", help="Algorithm to use", 
                    choices=["HYBRID", "HYBRID_DISPLACED", "HYBRID_NEWKF", "HYBRID_SIM_DISPLACED", "HYBRID_SIM"], default="HYBRID")
parser.add_argument("--test", help="Create cfg without submission", action="store_true") 
args = parser.parse_args()

request_name = f"CMSSW20_{args.algo}_{args.sample}_{args.maxEvents}"
base_out = 'crab_CMSSW_20_1_0_pre1'

os.makedirs(base_out, exist_ok=True)
cfg_path = os.path.join(base_out, 'crab_cfg.py')


maxMem = 2000*args.nThreads
# maxTime = 150


samples = {
            "SUSY200PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_pre1-PU_150X_mcRun4_realistic_v1_STD_D121_RegeneratedGS_PU-v1/GEN-SIM-DIGI-RAW",
            "SUSY0PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_pre1-150X_mcRun4_realistic_v1_STD_RegeneratedGS_D121_noPU-v1/GEN-SIM-DIGI-RAW"
          }

# cli_params = [x for tup in [[f"-{x}",y] for x,y in list(vars(args).items())] for x in tup]
py_cfg_params = ["-n", str(args.maxEvents), "-t", str(args.nThreads), "-s", args.sample, "-algo", args.algo]

crab_cfg = """\
from CRABClient.UserUtilities import config
config = config()

# input arguments
# make sure nThreads = numCores (doesnt make sense but is necessary?)
config.JobType.pyCfgParams = {py_cfg_params}


config.General.requestName = '{request_name}'
config.General.workArea = '{base_out}'
config.General.transferOutputs = True
config.JobType.psetName = 'custom-L1TrackNtupleMaker_cfg.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.numCores = {nThreads}
config.JobType.maxMemoryMB = {maxMem}

config.Data.splitting = 'Automatic'
# config.Data.unitsPerJob = 1
config.Data.totalUnits = {maxEvents}
config.Data.publication = False

config.Data.outLFNDirBase = '/store/user/nwhittin/crab_CMSSW_20_1_0_pre1/'
config.Data.inputDataset = '{sample}'

config.Site.storageSite = 'T3_CH_CERNBOX'
""".format(
    request_name     = request_name,
    py_cfg_params    = py_cfg_params,
    nThreads         = args.nThreads,
    sample           = samples[args.sample],
    maxEvents        = args.maxEvents,
    maxMem           = maxMem,
    # maxTime          = maxTime,
    base_out         = base_out,
)
# Other unused options:


with open(cfg_path, 'w') as f:
    f.write(crab_cfg)



if not args.test:
    cmd = 'crab submit -c %s' % cfg_path
    print('Submitting: %s' % cmd)
    os.system(cmd)
else:
    print('To submit, manually run:')
    print('  crab submit -c %s' % cfg_path)
