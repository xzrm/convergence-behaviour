﻿# Convergence behaviour plotter


## Overview
The tool was created to automate parsing and interaction with output files from FEM analyses.

__Instructions__: to open a file click on _File_ and open the outfile. A sample file is in "./sample outline" dir. The program will parse the file and display available analysis phases in the _Analysis settings_ tab. Select for which norm should the results be plotted and the line indicating the convergence tolerance (horizontal red line). To add tags to individual steps, select the _Add step_ tab, add the step number. The step should appear in the list and be available for deletion. To create a draggable line (see the vertical red line), select the _Add line_ tab and insert the number corresponding to any value in the axis.

Hover over the markers to display results in the plot.

Last modification: sometime in 2019

![Architecture](./pic/UI.png)

## Installation

On MacOs run

 ```bash
brew install python-tk
```

Create a virtualenv and source it

 ```bash
 virtualenv venv -p python3 && source venv/bin/activate
 ```

Install requirements

 ```bash
 pip install -r requirements.txt
 ```
