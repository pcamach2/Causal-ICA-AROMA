#!/usr/bin/env python

# Based on the design of ICA-AROMA https://github.com/maartenmennes/ICA-AROMA/blob/master/ICA_AROMA.py

import os
import argparse
import json

import numpy as np

from graph_AROMA_functions import *

# Change to script dir
cwd = os.path.realpath(os.path.curdir)
scriptDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(scriptDir)

####################################### PARSER #######################################

parser = argparse.ArgumentParser(description="Script to run graph ICA-AROMA")

# Required options
reqoptions = parser.add_argument_group('Required arguments')
reqoptions.add_argument('-o', '-out', dest='out')

# non-Required options
nonreqoptions = parser.add_argument_group('non-Required arguments')
nonreqoptions.add_argument('--overwrite', '--ow', dest='ow', required=False,
action='store_true')
nonreqoptions.add_argument('--cdAlgorithm', dest='cdAlgorithm', required=False,
default='LiNGAM', choices=['LiNGAM'])
nonreqoptions.add_argument('-c', '--criteria', dest='criteria',
required=False, default='pred', choices=['pred'])
nonreqoptions.add_argument('--fsldir', dest='fsldir',
required=False, default=os.path.join(os.environ['FSLDIR'], 'bin'))
nonreqoptions.add_argument('--group', dest='group', required=False, action='store_true')

# fmriprep + AROMA mode
fmripreparomaoptions = parser.add_argument_group('Aroma Arguments')
fmripreparomaoptions.add_argument('-i', '-in', dest='inFile', required=False)
fmripreparomaoptions.add_argument('-m', '-mix', dest='inMix', required=False)
fmripreparomaoptions.add_argument('-n', '-noise', dest='inNoise', required=False)
fmripreparomaoptions.add_argument('-j', '-noise_json', dest='inNoiseJSON', required=False)
fmripreparomaoptions.add_argument('-t', '-confound_tsv', dest='inConfoundTSV', required=False)


####################################### PARSE ARGUMENTS #######################################
args = parser.parse_args()

if args.inMix:
  inMix = args.inMix
  inNoise = args.inNoise
  inNoiseJSON = args.inNoiseJSON
  inConfoundTSV = args.inConfoundTSV
  inFile = args.inFile
  out = args.out

  assert os.path.exists(inFile), f"{inFile} does not exist"
  assert os.path.exists(inMix), f"{inMix} does not exist"
  assert os.path.exists(inNoise), f"{inNoise} does not exist"
  assert os.path.exists(inNoiseJSON), f"{inNoiseJSON} does not exist"
  assert os.path.exists(inConfoundTSV), f"{inConfoundTSV} does not exist"

  if out and (not os.path.isdir(out)):
    os.mkdir(out)
  elif os.path.isdir(out) and not args.ow:
    print("{} exists and --overwrite not selected.".format(out))
    exit()

  descr = {'cdAlgorithm': args.cdAlgorithm, 'criteria': args.criteria}

  with open(os.path.join(out, 'description.json'), 'w') as f:
    json.dump(descr, f)


  prepend = args.inNoise.split('/')[-1]
  prepend = prepend.split('.')[0]
  prepend = '_'.join(prepend.split('_')[:-1]) + '_'

  # Causal Discovery
  print("#"*10 + " Running Causal Discovery " + "#"*10)
  mixGraphFile = runCausalDiscovery(inMix, args.cdAlgorithm, out, prepend)

  # Reclassification
  print("#"*10 + " Reclassifying noiseICs based on Graph " + "#"*10)
  if args.inNoise:
    newMotionFile = graphReclassification(mixGraphFile, args.inNoise, args.inMix,
      args.inNoiseJSON, args.inConfoundTSV, args.criteria, out, os.path.basename(args.inNoise))
  else:
    newMotionFile = graphReclassification(mixGraphFile, args.inNoise, args.inMix,
      args.inNoiseJSON, args.inConfoundTSV, args.criteria, out)

  newMotion = []
  with open(newMotionFile) as f:
    for line in f:
      line = line.rstrip().split(',')
      newMotion += [int(i) for i in line]

  newMotion = np.asarray(newMotion)

  if args.group:
    name = "causal-discovery_{}_{}_group_".format(args.cdAlgorithm, args.criteria)
  else:
    name = "causal-discovery_{}_{}_".format(args.cdAlgorithm, args.criteria)

  with open(os.path.join(out, 'README'), 'w') as f:
    f.write(name)

  # Confound Regression
  print("#"*10 + " Regressing out new noiseICs " + "#"*10)
  regressOutNuissance(args.fsldir, args.inFile, out, inMix, name=args.inFile.split('/')[-1],
  denIdx=newMotion)
