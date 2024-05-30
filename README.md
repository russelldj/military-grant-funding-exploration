# Military Grant Funding Exploration
The goal of this project is to explore the impacts of military funding for academic research. At this stage, the project is focused on analyzing publicly-available data about grant funding.

# Structure
This project contains both code and data for experiments on this topic. The `code` folder currently only contains `webscraping` but we could consider others such as `derived_attributes` for extracting other information from the scraped data and `analysis` for conducting experiments. The data is currently broken up by funding source, and then contains the `01_scraped` for data that was directly obtained from the web and `02_derived_attributes` for data where additional derived fields were added.

# Installation
Currently, this project has the following dependencies.
* `pandas`
* `selenium`

If you do not already have these dependencies installed, it's recommended that you first create a virtual environment, so you can seperate the dependencies for this project from other projects. This can be done with options such as `venv` or `conda`.