GRACE Groundwater Analysis Project
==================================

This is a simple project to make a python cli tool to view groundwater
accumulation over time via data from the GRACE gravity anomoly meaurements.

The basic workflow is modeled on the Appendix B analysis from the
[GRACE L-3 Product User Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/gracefo/docs/GRACE-FO_L3_Handbook_JPL.pdf)

An exploration of the analysis performed by the tool is included in the
analysis.ipynb Jupyter notebook.


Setting up the tool
-------------------

A handful of scripts are included to initialize/update the data used for
this project. To get the data you will need a earthdata.nasa.gov login with
the `NASA GESDISC DATA ARCHIVE` and `PODAAC_Drive_OPS` as authorized applications.
You will also need a PO.DAAC API token.

To get the data, run the `update-data` script. You will be prompted for your
login/API information as required.

To install the python tool, run `pip install setup.py`. A virtualenv is recommended.
GDAL is a required dependency, so you will need to make sure that is installed to
the system before attempting to run the pip install.


Using the tool
--------------

More to come on this front.
