#!/usr/bin/env python

# Functions for ICA-AROMA v0.1 beta
# Based on the design of https://github.com/maartenmennes/ICA-AROMA/blob/master/ICA_AROMA_functions.py

import os
import json

import cdt

import numpy as np
import pandas as pd
import networkx as nx

def runCausalDiscovery(inMix, cdAlgorithm, out, prepend=''):
  mix = pd.read_csv(inMix, sep='\t', header=None)
  mix.columns = [i+1 for i in range(mix.shape[1])]
  if cdAlgorithm == 'LiNGAM':
    model = cdt.causality.graph.LiNGAM()
  else:
    raise NotImplementedError()
  G = model.predict(mix)

  if out:
    outFile = os.path.join(out, "{}{}_graph.gpickle".format(prepend, cdAlgorithm))
    nx.write_gpickle(G, outFile)
    return outFile

def graphReclassification(graphFile, motionFile, mixTSV, motionJSON, confoundTSV, criteria, out, filename='AROMAnoiseICs.csv'):
  mix = pd.read_csv(mixTSV, sep='\t', header=None)
  mix.columns = [i+1 for i in range(mix.shape[1])]

  def reclassify(pred, succ, criteria, motion):
    if criteria == 'pred':
      if len(pred) == 0:
        return False
      return all([i in motion for i in pred])
    elif criteria == 'succ':
      if len(succ) == 0:
        return False
      return all([i in motion for i in succ])
    elif criteria == 'adj':
      if len(pred) == 0 and len(succ) == 0:
        return False
      return all([i in motion for i in pred]) \
                  and all([i in motion for i in succ])
    else:
      raise ValueError("criteria must be one of ['pred', 'succ', 'adj']")

  G = nx.read_gpickle(graphFile) # Read graph
  # Read nuissance ICs
  new_motion, motion = [], []
  with open(motionFile, 'r') as f:
    for line in f:
      line = line.rstrip().split(',')
      motion = [int(i) for i in line]

  for n in G.nodes():
    if n in motion:
      new_motion.append(n)
      continue
    pred, succ = list(G.predecessors(n)), list(G.successors(n))
    if reclassify(pred, succ, criteria, motion):
      new_motion.append(n)

  new_motion.sort()
  edit_motion_json(new_motion, mix, motionJSON, confoundTSV, out)
  new_motion = pd.DataFrame(data=new_motion).T
  if out:
    outFile = os.path.join(out,
      filename)

    new_motion.to_csv(outFile, header=False, index=False)

    return outFile

def edit_motion_json(new_motion, mix, motionJSON,  confoundTSV, out):
  new_motion.sort()
  confounds = pd.read_csv(confoundTSV, sep='\t')

  x = json.load(open(motionJSON, 'r'))
  cols = []
  for n in new_motion:
    x[f'aroma_motion_{n}']['MotionNoise'] = True
    col = "aroma_motion_{:02d}".format(n)
    cols.append(col)
    if col in confounds.columns:
      assert all(np.abs(confounds[col].values - mix[n].values) < 1e-6)
    else:
      confounds[col] = mix[n].values

  temp = confounds[cols]
  confounds = confounds.drop(cols, axis=1)
  confounds = pd.concat([confounds, temp], axis=1)

  json.dump(x, open(os.path.join(out, os.path.basename(motionJSON)), 'w'), indent=2)
  confounds.to_csv(open(os.path.join(out, os.path.basename(confoundTSV)), 'w'), sep='\t', index=False)

# def denoising(fslDir, inFile, outDir, melmix, denType, denIdx):
def regressOutNuissance(fslDir, inFile, outDir, melmix, name, denType='nonaggr', denIdx=[]):
  """ This function classifies the ICs based on the four features;
  maximum RP correlation, high-frequency content, edge-fraction and CSF-fraction

  Parameters
  ---------------------------------------------------------------------------------
  fslDir:   Full path of the bin-directory of FSL
  inFile:   Full path to the data file (nii.gz) which has to be denoised
  outDir:   Full path of the output directory
  melmix:   Full path of the melodic_mix text file
  denType:  Type of requested denoising ('aggr': aggressive, 'nonaggr': non-aggressive, 'both': both aggressive and non-aggressive
  denIdx:   Indices of the components that should be regressed out

  Output (within the requested output directory)
  ---------------------------------------------------------------------------------
  denoised_func_data_<denType>.nii.gz:    A nii.gz file of the denoised fMRI data"""

  # Import required modules
  import os
  import numpy as np

  # Check if denoising is needed (i.e. are there components classified as motion)
  check = denIdx.size > 0

  if check == 1:
    # Put IC indices into a char array
    if denIdx.size == 1:
      denIdxStrJoin = "%d"%(denIdx + 1)
    else:
      denIdxStr = np.char.mod('%i', (denIdx + 1))
      denIdxStrJoin = ','.join(denIdxStr)

    # Non-aggressive denoising of the data using fsl_regfilt (partial regression), if requested
    if (denType == 'nonaggr') or (denType == 'both'):
      os.system(' '.join([os.path.join(fslDir, 'fsl_regfilt'),
                '--in=' + inFile,
                '--design=' + melmix,
                '--filter="' + denIdxStrJoin + '"',
                '--out=' + os.path.join(outDir,
                name)]))

    # Aggressive denoising of the data using fsl_regfilt (full regression)
    if (denType == 'aggr') or (denType == 'both'):
      os.system(' '.join([os.path.join(fslDir, 'fsl_regfilt'),
                '--in=' + inFile,
                '--design=' + melmix,
                '--filter="' + denIdxStrJoin + '"',
                '--out=' + os.path.join(outDir,
                name),
                '-a']))
  else:
    print("  - None of the components were classified as motion, so no denoising is applied (a symbolic link to the input file will be created).")
    if (denType == 'nonaggr') or (denType == 'both'):
      os.symlink(inFile, os.path.join(outDir,
      name))
    if (denType == 'aggr') or (denType == 'both'):
      os.symlink(inFile, os.path.join(outDir,
      name))
