# Data on Library Access to Scholarly Literature

[![Build Status](https://travis-ci.org/greenelab/library-access.svg?branch=master)](https://travis-ci.org/greenelab/library-access)

This repository is cataloging University Library access to scholarly literature.
Scholarly articles are identified using their DOIs.
The impetus for this project was [this discussion](https://github.com/greenelab/scihub-manuscript/issues/21 "Potential followup: comparison to authorized access") on the Sci-Hub Coverage Study.

The code in this repository facilitates fetching indicators of full-text availability for a list of DOIs from an OpenURL resolver. In this way, it enables large-scale analysis of bibliographic holdings / availability.

## Using the Code

**The code files in this repository assume that your working directory is set to the top-level directory of this repository.**

### Contents of this Repository, and the Order of Their Use

- `LICENSE-*.md`: License text to accompany the [License](#License) section of this Readme below.
- `environment.yml`: Conda environment file (see [Environment](#environment) below).
- `.gitattributes`: File with information for tracking files using [Git Large File Storage (LFS)](https://git-lfs.github.com/).
- `library_management_system_downloader` contains the following scripts, to be used in the following order:
	1. `downloader_configuration_file_TEMPLATE.py` should be copied to `downloader_configuration_file.py` and edited for your own institution's OpenURL resolver (These scripts were specifically tested using the OpenURL resolver that comes with Ex Libris' Alma management software).
	1. `run_api_download_and_parse_results.py`
	1. `copy_and_compress_database_and_extract_tsv.py`
- `evaluate_library_access_from_output_tsv` contains the following scripts, to be used in the following order:
	1. `create_stratefied_sample_of_dois.R`
	1. `join_doi-200_dates_to_doi-500.R`
	1. \[Run `facilitate_going_through_dois_manually.R` to help fill in the `.tsv` files created by the scripts above\]
	1. `penntext-accuracy-200.ipynb`
	1. `penntext-accuracy-500.ipynb`

- `data`: \[This is where datasets will be saved by the above scripts.\]

### Environment

This repository uses [conda](http://conda.pydata.org/docs/) to manage its environment as specified in [`environment.yml`](environment.yml).
Install the environment with:

```sh
conda env create --file=environment.yml
```

Then use `source activate library-access` and `source deactivate` to activate or deactivate the environment.
On windows, use `activate library-access` and `deactivate` instead.

## License

The files in this repository are released under the CC0 1.0 public domain dedication ([`LICENSE-CC0.md`](LICENSE-CC0.md)), excepting those that match the glob patterns listed below.
Files matching the following glob patters are instead released under a BSD 3-Clause license ([`LICENSE-BSD-3-Clause.md`](LICENSE-BSD-3-Clause.md)):

- `*.py`
- `*.md`
- `.gitignore`
- `*.r`
- `*.sh`
