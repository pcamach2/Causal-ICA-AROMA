# Causal-ICA-AROMA

Causal-ICA-AROMA is a data-driven method designed to enhance [ICA-AROMA](https://github.com/maartenmennes/ICA-AROMA) in the identification and removal of motion-related independent components in fMRI data [1]. Causal-ICA-AROMA requires the output from ICA-AROMA as input. After ICA-AROMA is completed, Causal-ICA-AROMA identifies additional motion-related independent components that were not detected by ICA-AROMA. It achieves this by leveraging LiNGAM (Linear Non-Gaussian Acyclic Models) to learn a causal graph of the time courses of the spatially independent components of the fMRI data, obtained via Independent Component Analysis (ICA) [2]. Causal-ICA-AROMA then applies a simple criterion to reclassify motion components: any component that is strictly caused by ICA-AROMA-identified motion components is reclassified as a motion component.

## CLI Usage

```sh
python graph_AROMA.py -o <output_directory> [options]
```

#### Required Arguments

    -o, -out: Specify the output directory.

#### Optional Arguments

    --overwrite, --ow: Overwrite the existing output directory.
    --cdAlgorithm: Causal discovery algorithm to use (default: LiNGAM). Choices: LiNGAM.
    -c, --criteria: Selection criteria for noise components (default: pred). Choices: pred.
    --fsldir: Path to the FSL directory (default: $FSLDIR/bin).
    --group: Run in group mode.

#### AROMA Arguments (for fmriprep + AROMA mode)

    -i, -in: Input file.
    -m, -mix: Input mixing matrix file.
    -n, -noise: Input noise components file.
    -j, -noise_json: Input noise components JSON file.
    -t, -confound_tsv: Input confound TSV file.

#### Example Command

```sh
python graph_AROMA.py -o /path/to/output --overwrite --cdAlgorithm LiNGAM -i /path/to/input_file -m /path/to/mix_file -n /path/to/noise_file -j /path/to/noise_json -t /path/to/confound_tsv
```

## Requirements

This package requires Python, FSL, and the Causal Discover Toolbox (cdt) [3-4]. Make sure to first install all required Python packages: `python -m pip install -r requirements.txt`.

It may also be helpful to take a look at the pages of the required tools listed below.

## References
[1] Pruim, Raimon HR, et al. "ICA-AROMA: A robust ICA-based strategy for removing motion artifacts from fMRI data." Neuroimage 112 (2015): 267-277.<br>
[2] Shimizu, Shohei. "LiNGAM: Non-Gaussian methods for estimating causal structures." Behaviormetrika 41.1 (2014): 65-98.<br>
[3] Kalainathan, Diviyan, Olivier Goudet, and Ritik Dutta. "Causal discovery toolbox: Uncovering causal relationships in python." Journal of Machine Learning Research 21.37 (2020): 1-5.<br>
[4] Jenkinson, Mark, et al. "Fsl." Neuroimage 62.2 (2012): 782-790.


## Required Tools
https://github.com/maartenmennes/ICA-AROMA<br>
https://fentechsolutions.github.io/CausalDiscoveryToolbox/html/index.html<br>
https://fsl.fmrib.ox.ac.uk/fsl/docs/#/<br>


