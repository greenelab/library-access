# Data on Library Access to Scholarly Literature

[![Build Status](https://travis-ci.org/greenelab/library-access.svg?branch=master)](https://travis-ci.org/greenelab/library-access)

This repository is cataloging University Library access to scholarly literature.
Scholarly articles are identified using their DOIs.
The impetus for this project was [this discussion](https://github.com/greenelab/scihub-manuscript/issues/21 "Potential followup: comparison to authorized access") on the Sci-Hub Coverage Study.

## Environment

This repository uses [conda](http://conda.pydata.org/docs/) to manage its environment as specified in [`environment.yml`](environment.yml).
Install the environment with:

```sh
conda env create --file=environment.yml
```

Then use `source activate library-access` and `source deactivate` to activate or deactivate the environment.
On windows, use `activate library-access` and `deactivate` instead.

## Using the Code

The code files in this repository assume that your working directory is set to the top-level directory of this repository.

## License

The files in this repository are released under the CC0 1.0 public domain dedication ([`LICENSE-CC0.md`](LICENSE-CC0.md)), excepting those that match the glob patterns listed below.
Files matching the following glob patters are instead released under a BSD 3-Claue license ([`LICENSE-BSD-3-Clause.md`](LICENSE-BSD-3-Clause.md)):

- `*.py`
- `*.md`
- `.gitignore`
- `*.r`
- `*.sh`
