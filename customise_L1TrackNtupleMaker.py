import os
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ('analysis')

options.outputFile = 'output.root'
options.inputFiles = 'infile.root'
options.maxEvents  = 1000

# L1 tracking algorithm, forwarded to L1TrackNtupleMaker_cfg via the environment.
options.register('algo', 'HYBRID',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "L1 tracking algorithm")
# Number of threads, kept in sync with CRAB's config.JobType.numCores.
options.register('nThreads', 1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "number of threads / cores")
options.parseArguments()

os.environ['L1TRKALGO'] = options.algo
# os.environ['GEOMETRY']  = options.geometry

from L1TrackNtupleMaker_cfg import *

process.TFileService = cms.Service("TFileService", fileName = cms.string(options.outputFile), closeFileFast = cms.untracked.bool(True))

process.maxEvents.input = cms.untracked.int32(options.maxEvents)
process.source.fileNames = cms.untracked.vstring (options.inputFiles)

# Match CRAB's numCores; numberOfStreams=0 lets it follow numberOfThreads.
process.options.numberOfThreads = cms.untracked.uint32(options.nThreads)
process.options.numberOfStreams = cms.untracked.uint32(0)
