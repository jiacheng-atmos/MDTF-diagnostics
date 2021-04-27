# Flow-Dependent, Cross-Timescale Model Diagnostics POD
#
# ================================================================================
#
# Last update: 4/27/2021
#
#   The flow-dependent model diagnostics compares daily atmospheric circulation patterns,
#   or weather types, characteristics in reanalyses and models to analyze misrepresented
#   physical processes related to spatiotemporal systematic errors in those models.
#   Relationships between these biases and climate teleconnections
#   (e.g., SST patterns, ENSO, MJO, etc.) can be explored in different models.
#
# Version and contact info
#
#   - Version/revision information: version 1 (4/27/2021)
#   - Developer/point of contact: Ángel G. Muñoz (agmunoz@iri.columbia.edu) and
#                                 Andrew W. Robertson (awr@iri.columbia.edu)
#   - Other contributors: Drew Resnick (drewr@iri.columbia.edu), James Doss-Gollin
#
# Open source copyright agreement
#
#   The MDTF framework is distributed under the LGPLv3 license (see LICENSE.txt).
#
# FUNCTIONALITY!!
#
#   In this section you should summarize the stages of the calculations your
#   diagnostic performs, and how they translate to the individual source code files
#   provided in your submission. This will, e.g., let maintainers fixing a bug or
#   people with questions about how your code works know where to look.
#
# Required programming language and libraries
#
#   This diagnostic runs on the most recent version of python3.
#   The required packages are as follows, and all should be the most updated version.
#   Python Libraries used: "netCDF4", "xarray", "numpy", "pandas", "sklearn",
#                          "cartopy", "matplotlib", "numba", "datetime", "typing"
#
# Required model output variables!!!!!!!!!!
#
#   This diagnostic assumes the data is structured on a time grid with no leap years.
#   It also assumes each variable is for a single ensemble member.
#
#   DESCRIBE EACH VARIBALE IN INPUT DATA
#
# References
#
#   Muñoz, Á. G., Yang, X., Vecchi, G. A., Robertson, A. W., & Cooke, W. F. (2017):
#       PA Weather-Type-Based Cross-Time-Scale Diagnostic Framework for Coupled Circulation
#       Models. Journal of Climate, 30 (22), 8951–8972, doi:10.1175/JCLI-D-17-0115.1.
#
# ================================================================================

#driver file
import os
import glob

missing_file=0
if len(glob.glob(os.environ["PRECT_FILE"]))==0:
    print("Required Precipitation data missing!")
    missing_file=1
if len(glob.glob(os.environ["Z250_FILE"]))==0:
    print("Required Geopotential height data missing!")
    missing_file=1
if len(glob.glob(os.environ["T250_FILE"]))==0:
    print("Required temperature data missing!")
    missing_file=1

if missing_file==1:
    print("Flow-Dependent, Cross-Timescale Model Diagnostics Package will NOT be executed!")
else:

    try:
        os.system("python3 "+os.environ["POD_HOME"]+"/"+"WeatherTypes.py")
    except OSError as e:
        print('WARNING',e.errno,e.strerror)
        print("**************************************************")
        print("Flow-Dependent, Cross-Timescale Model Diagnostics (WeatherTypes.py) is NOT Executed as Expected!")
        print("**************************************************")

    print("**************************************************")
    print("Flow-Dependent, Cross-Timescale Model Diagnostics (WeatherTypes.py) Executed!")
    print("**************************************************")