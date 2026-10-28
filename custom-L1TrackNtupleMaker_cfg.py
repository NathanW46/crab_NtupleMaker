
############################################################
# THIS JOB RUNS THE L1 TRACKING ALGORITHM.
# (Several alternative algorithms can be specified).
# It also runs an EDAnalyzer that makes a TTREE of
# track performance. (The script makeHists.csh can
# optionally then be used to create histograms from this).
############################################################

import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
from FWCore.ParameterSet.VarParsing import VarParsing
import os
process = cms.Process("L1TrackNtuple")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--maxEvents", help="Number of events to run", type=int, default=1000)
parser.add_argument("-s", "--sample", help="Sample to use", choices=["SUSY200PU", "SUSY0PU", "ttbar200PU", "ttbar0PU", 
                                                                     "dMuGun200PU", "dMuGun0PU", "deGun200PU", "deGun0PU"], default="SUSY200PU")
parser.add_argument("-t", "--nThreads", help="Number of cores/threads", type=int, default=1)
parser.add_argument("--algo", help="Algorithm to use", 
                    choices=["HYBRID", "HYBRID_DISPLACED", "HYBRID_NEWKF", "HYBRID_SIM_DISPLACED", "HYBRID_SIM"], default="HYBRID")
parser.add_argument("--tag", type=str, default=None, help="Optional filename tag")

args = parser.parse_args()

#copied from https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1TrackMC?extralog=-%20caching%20topic#CMSSW_20_1_0_pre1_or_very_simila
# as of 2026-10-26
samples = {
            "SUSY200PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_patch1-PU_150X_mcRun4_realistic_v1_STD_D121_RegeneratedGS_PU_20260904_125332_RV11-v1/GEN-SIM-DIGI-RAW",
     	    "SUSY0PU":"/RelValDisplacedSUSY_14TeV/CMSSW_20_0_0_patch1-150X_mcRun4_realistic_v1_Run4_D121_pp_noPU_STD_Reference_20260903_192421_RV19-v1/GEN-SIM-DIGI-RAW",
         	"ttbar200PU":"/RelValTTbar_14TeV/CMSSW_20_0_0_patch1-PU_150X_mcRun4_realistic_v1_STD_D121_RegeneratedGS_PU_20260904_125332_RV11-v1/GEN-SIM-DIGI-RAW",
            "ttbar0PU":"/RelValTTbar_14TeV/CMSSW_20_0_0_patch1-150X_mcRun4_realistic_v1_Run4_D121_pp_noPU_STD_Reference_20260903_192421_RV19-v1/GEN-SIM-DIGI-RAW",
            "dMuGun0PU":"/RelValDoubleMuFlatPt1To100Dxy100GunProducer/CMSSW_20_1_0_pre1-150X_mcRun4_realistic_v1_RV302_Run4D121_noPU-v1/GEN-SIM-DIGI-RAW",
            "dMuGun200PU":"/RelValDoubleMuFlatPt1To100Dxy100GunProducer/CMSSW_20_1_0_pre1-PU_150X_mcRun4_realistic_v1_RV302_Run4D121_PU200-v1/GEN-SIM-DIGI-RAW",
            "deGun0PU":"/RelValDoubleEFlatPt1To100Dxy100GunProducer/CMSSW_20_1_0_pre1-150X_mcRun4_realistic_v1_RV302_Run4D121_noPU-v1/GEN-SIM-DIGI-RAW",
            "deGun200PU":"/RelValDoubleEFlatPt1To100Dxy100GunProducer/CMSSW_20_1_0_pre1-PU_150X_mcRun4_realistic_v1_RV302_Run4D121_PU200-v1/GEN-SIM-DIGI-RAW",
          }
outfile = f"CMSSW20_{args.algo}_{args.sample}_{args.maxEvents}"
if args.tag:
    outfile += f"-{args.tag}"
outfile += ".root"
print(args)
############################################################
# edit options here
############################################################

# D121 MC recommended. D110 MC can only be used if made with CMSSW_20.
#GEOMETRY = "D110"
GEOMETRY = "D121"

# Set L1 tracking algorithm:
# 'HYBRID' (baseline, 4par fit) or 'HYBRID_DISPLACED' (extended, 5par fit).
# 'HYBRID_NEWKF' (baseline, 4par fit, with bit-accurate KF emulation),
# 'HYBRID_REDUCED' to use the "L5L6" seeding only reduced (NEWKF) cfg.
# 'HYBRID_SIM' prompt tracklet reco + (NEWKF) Track Processing simulation (4 param fit)
# 'HYBRID_SIM_DISPLACED' displaced tracklet reco + (NEWKF) Track Processing simulation (5 param fit)
# (Or legacy algos 'TMTT' or 'TRACKLET').
L1TRKALGO = args.algo
process.options.numberOfThreads = args.nThreads
# Write output dataset?
WRITE_DATA = False

############################################################
# import standard configurations
############################################################

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.L1track = dict(limit = -1)
process.MessageLogger.Tracklet = dict(limit = -1)
process.MessageLogger.cout.enableStatistics = True
process.MessageLogger.cerr.enableStatistics = True

print("using geometry " + GEOMETRY + " (tilted)")
process.load('Configuration.Geometry.GeometryExtendedRun4' + GEOMETRY + 'Reco_cff')
process.load('Configuration.Geometry.GeometryExtendedRun4' + GEOMETRY +'_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

############################################################
# input and output
############################################################

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(args.maxEvents))

#--- To use MCsamples scripts, defining functions get*data*() for easy MC access,
#--- follow instructions in https://github.com/cms-L1TK/MCsamples

from MCsamples.Scripts.getCMSdata_cfi import *
#from MCsamples.Scripts.getCMSlocaldata_cfi import *
inputMC = getCMSdata(samples[args.sample])

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(*inputMC))

# To avoid confusion, drop previously reconstructed L1 tracks + their truth association.
process.source.dropDescendantsOfDroppedBranches = cms.untracked.bool(False)
process.source.inputCommands = cms.untracked.vstring()
process.source.inputCommands.append('keep *_*_*_*')
process.source.inputCommands.append('drop  *_*TTTrack*_*_*')

# Use skipEvents to select particular single events for test vectors
#process.source.skipEvents = cms.untracked.uint32(11)

process.TFileService = cms.Service("TFileService", fileName = cms.string(outfile), closeFileFast = cms.untracked.bool(True))
process.Timing = cms.Service("Timing", summaryOnly = cms.untracked.bool(True))

############################################################
# L1 tracking: stubs / DTC emulation
############################################################

process.load('L1Trigger.TrackTrigger.TrackTrigger_cff')

# Load code to remake clusters + stubs + their truth association,
# in case user wants to remake them. 
process.load("SimTracker.TrackTriggerAssociation.TrackTriggerAssociator_cff")
process.TTClusterAssociatorFromPixelDigis.digiSimLinks = cms.InputTag("simSiPixelDigis","Tracker")

process.TTClusterStub = cms.Path(process.TrackTriggerClustersStubs)
process.TTClusterStubTruth = cms.Path(process.TrackTriggerAssociatorClustersStubs)

# load more code to associate stubs with mctruth
process.load( 'SimTracker.TrackTriggerAssociation.StubAssociator_cff' )
# load code that analyzes mc truth
process.load( 'L1Trigger.TrackTrigger.AnalyzerMC_cff' )
# DTC emulation
process.load('L1Trigger.TrackerDTC.DTC_cff')

# load code that analyzes DTCStubs
process.load('L1Trigger.TrackerDTC.Analyzer_cff')

# modify default cuts
#process.TrackTriggerSetup.FrontEnd.BendCut = 5.0
#process.TrackTriggerSetup.Hybrid.MinPt = 1.0

process.dtc = cms.Path(process.StubAssociator + process.AnalyzerMC + process.ProducerDTC + process.AnalyzerDTC)

############################################################
# L1 tracking
############################################################

process.load("L1Trigger.TrackFindingTracklet.L1HybridEmulationTracks_cff")

# HYBRID: prompt tracking
if (L1TRKALGO == 'HYBRID'):
    process.load( 'L1Trigger.TrackFindingTracklet.Analyzer_cff' )
    process.TTTracksEmulation = cms.Path(process.L1THybridTracks)
    process.TTTracksEmulationWithTruth = cms.Path(process.L1THybridTracksWithAssociators + process.AnalyzerTracklet)
    NHELIXPAR = 4
    L1TRK_NAME  = "l1tTTTracksFromTrackletEmulation"
    L1TRK_LABEL = "Level1TTTracks"
    L1TRUTH_NAME = "TTTrackAssociatorFromPixelDigis"

# HYBRID: extended tracking
elif (L1TRKALGO == 'HYBRID_DISPLACED'):
    NHELIXPAR = 5
    L1TRK_NAME  = "l1tTTTracksFromExtendedTrackletEmulation"
    L1TRK_LABEL = "Level1TTTracks"
    L1TRUTH_NAME = "TTTrackAssociatorFromPixelDigisExtended"
    process.load( 'L1Trigger.TrackFindingTracklet.Analyzer_cff' )
    process.AnalyzerTracklet.InputTag = cms.InputTag(L1TRK_NAME, L1TRK_LABEL)
    process.TTTracksEmulation = cms.Path(process.L1TExtendedHybridTracks)
    process.TTTracksEmulationWithTruth = cms.Path(process.L1TExtendedHybridTracksWithAssociators + process.AnalyzerTracklet)

# HYBRID_NEWKF: prompt tracking or reduced
elif (L1TRKALGO == 'HYBRID_NEWKF' or L1TRKALGO == 'HYBRID_REDUCED'):
    process.load( 'L1Trigger.TrackFindingTracklet.Producer_cff' )
    process.load( 'L1Trigger.TrackFindingTracklet.Analyzer_cff' )
    NHELIXPAR = 4
    L1TRK_NAME  = process.TrackFindingTrackletAnalyzer_params.OutputLabelTFP.value()
    L1TRK_LABEL = process.TrackFindingTrackletProducer_params.BranchTTTracks.value()
    L1TRUTH_NAME = "TTTrackAssociatorFromPixelDigis"
    process.TTTrackAssociatorFromPixelDigis.TTTracks = cms.VInputTag( cms.InputTag(L1TRK_NAME, L1TRK_LABEL) )
    process.HybridNewKF = cms.Sequence(process.L1THybridTracks + process.ProducerTM + process.ProducerDR + process.ProducerKF + process.ProducerTQ + process.ProducerTFP)
    process.TTTracksEmulation = cms.Path(process.HybridNewKF)
    # Optionally include code producing performance plots & end-of-job summary.
    process.TTTracksEmulationWithTruth = cms.Path(process.HybridNewKF + process.TrackTriggerAssociatorTracks + process.AnalyzerTracklet + process.AnalyzerTM + process.AnalyzerDR + process.AnalyzerKF + process.AnalyzerTFP )
    from L1Trigger.TrackFindingTracklet.Customize_cff import *
    if (L1TRKALGO == 'HYBRID_NEWKF'):
        fwConfig( process )
        # Cheat to improve z0 resolution (bypass issues in Tracklet digitisation by using TTStubs)
        process.TrackFindingTrackletSetup.DR.UseTTStubs = True
        # Cheat to investigate z0 resolution (after NEWKF's DR, do KF fit with OLDKF instead of NEWKF)
        # oldKFConfig( process )
    if (L1TRKALGO == 'HYBRID_REDUCED'):
        reducedConfig( process )
    # Needed by L1TrackNtupleMaker
    process.HitPatternHelperSetup.useNewKF = True

# prompt tracklet track finding followed by Track Processing simulation (4 param fit)
elif (L1TRKALGO == 'HYBRID_SIM'):
    process.load( 'L1Trigger.TrackFindingTracklet.Producer_cff' )
    process.load( 'L1Trigger.TrackFindingTracklet.Analyzer_cff' )
    process.load( 'SimTracker.TrackTriggerAssociation.StubAssociator_cff' )
    from L1Trigger.TrackFindingTracklet.Customize_cff import *
    NHELIXPAR = 4
    L1TRK_NAME  = "ProducerSim"
    L1TRK_LABEL = process.TrackFindingTrackletProducer_params.BranchTTTracks.value()
    L1TRUTH_NAME = "TTTrackAssociatorFromPixelDigis"
    process.TTTrackAssociatorFromPixelDigis.TTTracks = cms.VInputTag( cms.InputTag(L1TRK_NAME, L1TRK_LABEL) )
    from L1Trigger.TrackFindingTracklet.Customize_cff import *
    sim4Config( process )
    # uncomment for 5 par + prompt seeds
    # also set NHELIXPAR to 5 above
    # process.TrackFindingTrackletSetup.Sim.NPar = 5

    process.Sim = cms.Sequence(process.L1THybridTracks + process.ProducerSim)
    process.TTTracksEmulationWithTruth = cms.Path(process.Sim + process.TrackTriggerAssociatorTracks + process.AnalyzerTracklet + process.AnalyzerSim)
    process.TTTracksEmulation = cms.Path(process.Sim)

# displaced tracklet track finding followed Track Processing simulation (5 param fit)
elif (L1TRKALGO == 'HYBRID_SIM_DISPLACED'):
    process.load( 'L1Trigger.TrackFindingTracklet.Producer_cff' )
    process.load( 'L1Trigger.TrackFindingTracklet.Analyzer_cff' )
    process.load( 'SimTracker.TrackTriggerAssociation.StubAssociator_cff' )
    from L1Trigger.TrackFindingTracklet.Customize_cff import *
    NHELIXPAR = 5
    TRACKLET_NAME  = "l1tTTTracksFromExtendedTrackletEmulation"
    TRACKLET_LABEL = "Level1TTTracks"
    L1TRK_NAME  = "ProducerSim"
    L1TRK_LABEL = process.TrackFindingTrackletProducer_params.BranchTTTracks.value()
    L1TRUTH_NAME = "TTTrackAssociatorFromPixelDigisExtended"
    process.TTTrackAssociatorFromPixelDigisExtended.TTTracks = cms.VInputTag( cms.InputTag(L1TRK_NAME, L1TRK_LABEL) )
    process.AnalyzerTracklet.InputTag = cms.InputTag(TRACKLET_NAME, TRACKLET_LABEL)
    process.StubAssociator.MaxZ0 = 30.
    process.StubAssociator.MaxD0 = 10.
    process.StubAssociator.MaxVertR = 10.
    process.StubAssociator.MaxVertZ = 60.
    from L1Trigger.TrackFindingTracklet.Customize_cff import *
    sim5Config( process )
    process.Sim = cms.Sequence(process.L1TExtendedHybridTracks + process.ProducerSim)
    process.TTTracksEmulationWithTruth = cms.Path(process.Sim + process.L1TExtendedHybridTracksWithAssociators + process.AnalyzerTracklet + process.AnalyzerSim)
    process.TTTracksEmulation = cms.Path(process.Sim)


else:
    print("ERROR: Unknown L1TRKALGO option")
    exit(1)


# Define L1 track ntuple maker
from L1Trigger.TrackFindingTracklet.L1TrackNtupleMaker_cfi import *
process.L1TrackNtuple = L1TrackNtupleMaker.clone(
   L1Tk_nPar = NHELIXPAR, # use 4 or 5-parameter L1 tracking?
   L1TrackInputTag = (L1TRK_NAME, L1TRK_LABEL),         # TTTrack input
   MCTruthTrackInputTag = (L1TRUTH_NAME, L1TRK_LABEL),  # MCTruth input
)

process.ana = cms.Path(process.L1TrackNtuple)


############################################################
# final schedule of what is to be run
############################################################

# Run tracking + track associator
process.schedule = cms.Schedule(process.dtc,process.TTTracksEmulationWithTruth,process.ana)

# Use this to re-run the cluster+stub making + truth association
# (Not needed unless you want to change them)
# To avoid confusion, drop existing info if you are doing this. 
#process.source.inputCommands.append('drop  *_*TTCluster*_*_*')
#process.source.inputCommands.append('drop  *_*TTStub*_*_*')
#process.schedule = #cms.Schedule(process.TTClusterStub,process.TTClusterStubTruth,process.dtc,process.TTTracksEmulationWithTruth,process.ana)


############################################################
# write output dataset
############################################################

if (WRITE_DATA):
  process.writeDataset = cms.OutputModule("PoolOutputModule",
      splitLevel = cms.untracked.int32(0),
      eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
      outputCommands = process.RAWSIMEventContent.outputCommands,
      fileName = cms.untracked.string('output_dataset.root'), ## ADAPT IT ##
      dataset = cms.untracked.PSet(
          filterName = cms.untracked.string(''),
          dataTier = cms.untracked.string('GEN-SIM')
      )
  )
  process.writeDataset.outputCommands.append('keep  *TTTrack*_*_*_*')
  process.writeDataset.outputCommands.append('keep  *TTStub*_*_*_*')

  process.pd = cms.EndPath(process.writeDataset)
  process.schedule.append(process.pd)



