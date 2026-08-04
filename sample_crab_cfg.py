from CRABClient.UserUtilities import config
config = config()
# import argparse
# import sys
#
# parser = argparse.ArgumentParser()
# parser.add_argument("-n", "--maxEvents", help="Number of events to run", type=int, default=1000)
# parser.add_argument("-s", "--sample", help="Sample to use", choices=["SUSY200PU", "SUSY0PU"], default="SUSY200PU")
# parser.add_argument("-t", "--nThreads", help="Number of cores/threads", type=int, default=1)
# parser.add_argument("-algo", "--algo", help="Algorithm to use", 
#                     choices=["HYBRID", "HYBRID_DISPLACED", "HYBRID_NEWKF", "HYBRID_SIM_DISPLACED", "HYBRID_SIM"], default="HYBRID")
# args = parser.parse_args()
#
samples = {
            "SUSY200PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_pre1-PU_150X_mcRun4_realistic_v1_STD_D121_RegeneratedGS_PU-v1/GEN-SIM-DIGI-RAW",
            "SUSY0PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_pre1-150X_mcRun4_realistic_v1_STD_RegeneratedGS_D121_noPU-v1/GEN-SIM-DIGI-RAW",
            "ttbar200PU":"/RelValTTbar_14TeV/CMSSW_20_0_0_pre1-PU_150X_mcRun4_realistic_v1_STD_D121_RegeneratedGS_PU-v1/GEN-SIM-DIGI-RAW",
            "ttbar0PU":"/RelValTTbar_14TeV/CMSSW_20_0_0_pre1-150X_mcRun4_realistic_v1_STD_RegeneratedGS_D121_noPU-v1/GEN-SIM-DIGI-RAW",
          }

# input arguments
# make sure nThreads = numCores (doesnt make sense but is necessary?)
# ew this is ugly 
# cli_params = [x for tup in [[f"-{x}",y] for x,y in list(vars(args).items())] for x in tup]
config.JobType.pyCfgParams = ["-n", "10", "-s", "SUSY200PU", "-t", "1", "-algo", "HYBRID_DISPLACED"]


config.General.requestName = "cli_test" #f"{args.algo}_{args.sample}_{args.maxEvents}"
config.General.workArea = 'crab_CMSSW_20_1_0_pre1'
config.General.transferOutputs = True
config.JobType.psetName = 'custom-L1TrackNtupleMaker_cfg.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.maxJobRuntimeMin = 30
config.JobType.maxMemoryMB = 3000
config.JobType.numCores = 1 #args.nThreads

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = 1
config.Data.publication = False

config.Data.outLFNDirBase = '/store/user/nwhittin/crab_CMSSW_20_1_0_pre1/'
config.Data.inputDataset = samples["SUSY200PU"]#[args.sample]

config.Site.storageSite = 'T3_CH_CERNBOX'

