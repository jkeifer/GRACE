name: inverse
layout: true
class: center, middle, inverse
---
# GRACE Groundwater Exploration
### Jarrett Keifer

---
template: inverse
# Project Objectives
---
layout: false
## Project Objectives

1. Gain an understanding of available GRACE data and how to use them

1. Use GRACE data to visualize groundwater

1. Build tooling to produce such visualizations for Areas of Interest (AOIs)



---
template: inverse
# GRACE Data
---
## GRACE Data

- Gravity Recovery and Climate Experiment (GRACE)

- Measures Earth's gravity field

- Two satellites, distance between affected by gravity field anomalies

<center><img class="center" src="images/grace-fo.jpeg" height=350></center>
.footnote[Image: [NASA JPL GRACE-FO Mission Overview](https://gracefo.jpl.nasa.gov/mission/overview/)]
---
## GRACE Data

- Four levels of data available, 0 to 3, from least to most processed

    - Level 0: raw data from GRACE satellites

    - Levels 1A & 1B: unit conversions, resampling, and more useful formatting

    - Level 2: gravity field estimates

        - Processed using multiple, independent models by JPL, UTCSR, and GFZ

        - "Spherical harmonic coefficients of the 'geopotential'" [0]

        - The lowest degree spherical harmonic (60 deg) corresponds to about 330km
          of spatial resolution

.footnote[[0] [GRACE-FO Level 3 Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/gracefo/docs/GRACE-FO_L3_Handbook_JPL.pdf)]
---
## GRACE Data

- Four levels of data available, 0 to 3, from least to most processed

    - Level 3

        - Represent changes in mass throughout parts of the Earth gravity system

        - Each observation a "surface mass deviation for that month relative to a
          baseline temporal average" [0]

        - Filters tuned for domain-specific products

        - De-correlation filters and smoothing can remove N-S data anomalies

            - A static scaling factor dataset allows adding in some lost anomalies

.footnote[[0] [GRACE-FO Level 3 Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/gracefo/docs/GRACE-FO_L3_Handbook_JPL.pdf)]
---
## GRACE Data

- Four levels of data available, 0 to 3, from least to most processed

<center><img class="center" src="images/level3-processing.png" height=450></center>
.footnote[Image: [GRACE-FO Level 3 Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/gracefo/docs/GRACE-FO_L3_Handbook_JPL.pdf)]
---
## GRACE Data

- GRACE data selected for this project:

    - GRCTellus.JPL.200204_202103.GLO.RL06M.MSCNv02CRI.nc

        - Represents liquid water equivalent (LWE) in centimeters

        - 0.5 degree global grid

    - CLM4.SCALE_FACTOR.JPL.MSCNv02CRI.nc

        - Dimensionless



---
template: inverse
class: center, middle
# Data Scripts



---
template: inverse
class: center, middle
# Analysis Walkthrough



---
template: inverse
# The tool
---
## The tool

- Build tooling to produce such visualizations for Areas of Interest (AOIs)

    - Python cli tool called `ggw` to:

        - `map`

        - `animate`

        - `plot`

---
## The tool

Like this:
```
$ ggw map [ -d DATA_DIR ] AOI_FILE YYYY-MM OUTFILE
```

<center><img class="center" src="images/sac_2009-05.png" height=450></center>
---
## The tool

Like this:
```
$ ggw animate [ -d DATA_DIR ] [ --fps FPS ] AOI_FILE START_YYYY-MM END_YYYY-MM OUTFILE
```

<center><img class="center" src="images/sac_2004-01_2020-12.gif" height=450></center>
---
## The tool

Like this:
```
$ ggw plot [ -d DATA_DIR ] AOI_FILE START_YYYY-MM END_YYYY-MM OUTFILE
```

<br />
<br />
<br />
<center><img class="center" src="images/sac_2004-01_2020-12_plot.png" width=750></center>
---
template: inverse
class: center, middle
# ggw Demo
---
template: inverse
# Next Steps
---
## Next Steps

- Project AOI and calculate area to turn LWE thickness into water volume

- Allow trend line to accommodate missing dates

- Use other data to further isolate groundwater signal vs other mass transfer
  (snow water equivalent, surface water, soil moisture)

- Factor LWE uncertainties into reported quantities

- Better titles/labels

- Better performance

    - Main slowdown seems to be initialization/loading data not AOI size

    - Code has some places that need obvious improvement

- Incorporate user feedback
---
template: inverse
# Thank you!
## Questions?

<br />
<br />
<br />
.left[
### Selected Links

- [NASA JPL GRACE-FO Mission Overview](https://gracefo.jpl.nasa.gov/mission/overview/)
- [GRACE-FO Mission Documentation](https://podaac.jpl.nasa.gov/gravity/gracefo-documentation)
- [GRACE Level 1B Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/grace/docs/Handbook_1B_v1.3.pdf)
- [GRACE Level 2 Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/grace/docs/L2-UserHandbook_v4.0.pdf)
- [GRACE-FO Level 3 Handbook](https://podaac-tools.jpl.nasa.gov/drive/files/allData/gracefo/docs/GRACE-FO_L3_Handbook_JPL.pdf)
- [GRACE Tellus FAQs](https://grace.jpl.nasa.gov/about/faq/)
- [Rodell et al., Satellite-based estimates of groundwater depletion in India](https://escholarship.org/uc/item/22577805)
]
