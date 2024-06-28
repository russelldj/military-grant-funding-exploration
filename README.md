# Military Grant Funding Exploration
The goal of this project is to explore the impacts of military funding for academic research. At this stage, the project is focused on analyzing publicly-available data about grant funding.

# Structure
This project contains both code and data for experiments on this topic. The `military_grant_funding_exploration` folder contains the code in subfolders, but currently only has `webscraping`. But in the future we could consider others such as `derived_attributes` for extracting other information from the scraped data and `analysis` for conducting experiments. The data is currently broken up by funding source, and then contains the `01_scraped` for data that was directly obtained from the web and `02_derived_attributes` for data where additional derived fields were added.

# Installation
This project uses `poetry` to manage the dependencies and ensure that everyone is working with the same versions of the libraries. If you have not already, install it using the instructions [here](https://python-poetry.org/docs/#installation). It's best to install the dependencies for this project in a dedicated virtual environment. My preference is to use `conda`, but there are other examples such as `venv`, or letting `poetry` create its own virtual environment.

To use conda, first install it using the instructions [here](https://docs.anaconda.com/free/anaconda/install/). Then create and activate a conda environment for this project with Python 3.11.
```
conda create -n MGFE python=3.11 -y
conda activate MGFE
```

Now you have a dedicated environment for this project. You also need to download a copy of the code in this repository, which you can do by going to your directory of choice and running `git clone <git@github.com:russelldj/military-grant-funding-exploration.git>`. Now you have the project code downloaded and a conda environment `MGFE` to do your own tinkering, but none of the dependencies are installed. To do that, first make sure you are in the top level directory of this project (`/military-grant-funding-exploration`) and that your conda environment is active. Then run
```
poetry install
```
Now when you are in the conda environment, you will be able to import the dependencies (e.g. `selenium`, `pandas`) as well as import the `military_grant_funding_exploration` module. This is true no matter what directory you are currently in.

# Running
The recommended script to run for webscraping DoD data is `military_grant_funding_exploration/webscraping/DoD_DTIC_scraping.py`. You can provide which campuses you'd like to run using the `--campuses` flag, or by default it will run for all of them. This script produces `.json` data in the `data/DoD/01_scraped` folder for each campus.
