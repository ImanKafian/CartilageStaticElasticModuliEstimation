'''
About: Python script to make the input files for estimating the elastic moduli: instantaneous and equilibrium
from the output files of the Biomomentum Mach 1 micromechanical testing system.
Author: Iman Kafian-Attari
Date: 18.07.2021
Licence: MIT
version: 0.1
=========================================================
How to use:
1. Select ll the step-wise stress-relaxation files per sample.
2. Select the output directory.
3. Input the sample's label.
4. Input the sample's thickness in mm.
5. Input the list of strains used in the experiment, separate the values with comma.
6. Repeat the process for the remaining samples, if needed.
=========================================================
Notes:
1. This code is meant to prepare the input files from the extracted step-wise stress-relaxation dataset.
2. It requires the following inputs from the user:
   - input files,
   - an output directory,
   - an output label,
   - sample thickness
   - list of strains used  in the experiment, separated with comma (,).
3. It automatically reads the peak and equilibrium forces per each step.
4. It stores the following data per step:
   - remaining thickness per step
   - user-defined strain
   - estimated strain from the experimental data
   - accumulated estimated strain
   - equilibrium force
   - initial minimum force
   - peak force
   - delta peak force
5. The output files are saved as 2D numpy arrays
=========================================================
TODO for version O.2
1. Modify the code in a functional form.
2. Store the files as Pandas dataframes.
=========================================================
'''

print(__doc__)

import numpy as np
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()

condition = True
while condition == True:

    # Reading the stress-relaxation files per sample for all the steps
    input_files = filedialog.askopenfilenames(parent=root, initialdir='C:\\', title='Select the sample\'s stress-relaxation files for all the steps')

    # Selecting the output directory
    output_dir = filedialog.askdirectory(parent=root, initialdir='C:\\', title='Choose the output directory')

    # Reading the sample's label:
    label = input('Insert the sample\'s label --> ')

    # Reading the thickness of the sample
    thickness = float(input('Insert the sample\'s thickness (mm) --> '))

    # Reading the strains used per step
    strains = list(','.split(input('List the strains used in experiments, separate them with a comma (,) --> ')))

    # Building the input data file for estimating the inst. and eq. moduli.
    # The input data includes measured thickness at 3 steps, (thickness measured by microscope)
    # Assumed strain (0.05, 0. 10, 0.15)
    # Accumulated measured strain ((last pt - first pt)/first pt) at each step
    # Accumulated measured step
    # Initial minimum force before the peak (avg of first 20 pts)
    # Max force
    # Equ. force (avg og last 3000 pts.)
    mod_input_data = np.zeros((8, len(strains)))
    for step in range(len(strains)):
        file = np.loadtxt(input_files[step])
        if step > 0:
            mod_input_data[0][step] = mod_input_data[0][step-1]*(1-float(strains[step-1]))
        else:
            mod_input_data[0][step] = thickness

        mod_input_data[1][step] += float(strains[step]) # User-defined strain at each step
        mod_input_data[2][step] = (file[len(file)-1][0]-file[0][0])/thickness # Measured strain
        mod_input_data[3][step] = np.sum(mod_input_data[2, 0:step+1]) # accumulated measured strain
        mod_input_data[4][step] = np.nanmean(file[len(file)-101:, 1]) # equ. force as a man value of the last 100 points
        mod_input_data[5][step] = np.nanmean(file[0:20, 1]) # Initial minimum force
        mod_input_data[6][step] = np.amax(file[:, 1]) # peak forces
        if step > 0:
            mod_input_data[7][step] = mod_input_data[6][step]-mod_input_data[4][step-1] # delta peak frce <=> peak forces - (init or equ force)
        else:
            mod_input_data[7][step] = mod_input_data[6][step]-mod_input_data[5][step]

    np.savetxt(f'{output_dir}\\{label}-StaticElasticMod-Input.txt', mod_input_data, delimiter='\t')

    check = input('Do you want to continue?(Y/N) --> ')
    if check == 'Y':
        condition = True
    elif check == 'N':
        condition = False
    else:
        print('Wrong input --> Exiting...')
        exit()
