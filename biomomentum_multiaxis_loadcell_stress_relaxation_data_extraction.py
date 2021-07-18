'''
About: Python script to run the extract the stress-relaxation dataset
from the output files of the Biomomentum Mach 1 micromechanical testing system.
Author: Iman Kafian-Attari
Date: 18.07.2021
Licence: MIT
version: 0.1
=========================================================
How to use:
1. Select the folder containing the input files.
2. Repeat the process for the remaining samples, if needed.
=========================================================
Notes:
1. This code is meant to extract the stress-relaxation dataset when a multiaxis loadcell is used.
2. Since the direction of exerted force is negative,
   the code takes the absolute value of the force for simplifying the later calculation
3. For stepwise stress-relaxation, it only considers the forces compressing the tissue.
4. The stepwise stress-relaxation output files are in the form of multiple rows x 3 columns:
-  The 1st column is the absolute position Z (mm), the 2nd column is force (n), and the 3rd column is time (s).
5. The bulk stress-relaxation output files are in the form of multiple rows x 10 columns:
-  Col 1: time (s), Col 2: Position z (mm), Col 3: Position x (mm), Col 4: Position y (mm)
-  Col 5: Fx (n), Col 6: Fy (n), Col 7: Fz (n), Col 8: Tx (n-mm), Col 9: Fy (n-mm), Col 10: Tz (n-mm).
6. The output files are saved as 2D numpy arrays
=========================================================
TODO for version O.2
1. Read the data for other axes.
2. Modify the code in a functional form.
3. Store the files as Pandas dataframes.
=========================================================
'''

print(__doc__)

import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import shutil

root = tk.Tk()
root.withdraw()

condition = True
while condition == True:

    # Selecting the folder containing input dataset
    input_directory = filedialog.askdirectory(parent=root, initialdir='C:\\', title='Choose the input directory')

    # Listing all the inputs
    input_files = sorted(os.listdir(input_directory), key=lambda x: int("".join([i for i in x if i.isdigit()])))

    # Creating a folder to store the input files after processing
    if not os.path.exists(f'{input_directory}\\Input'):
        os.mkdir(f'{input_directory}\\Input')

    # Creating a folder for the output files
    if not os.path.exists(f'{input_directory}\\Output'):
        os.mkdir(f'{input_directory}\\Output')

    # Reading each file and extracting its stress relaxation data
    for file in input_files:

        # Creating a folder specific to Stress Relaxation output files:
        if not os.path.exists(f'{input_directory}\\Output\\Stress-Relaxation'):
            os.mkdir(f'{input_directory}\\Output\\Stress-Relaxation')

        # Creating placeholders for the stress-relaxation data per file
        stress_relaxation = []
        stress_relaxation_flag = 0

        # Extracting the stress relaxation bulk data
        # <--> Reading everyting between <Stress Relaxation> and <End Data>
        with open(f'{input_directory}\\{file}') as f:
            for line in f:
                if line.strip() == '<Stress Relaxation>':
                    stress_relaxation_flag = 1
                if stress_relaxation_flag == 1:
                    stress_relaxation.append(line.strip())
                if stress_relaxation_flag == 1 and line.strip() == '<END DATA>':
                    stress_relaxation_flag = 0
        # Cleansing the extracted data from its metadata information
        tmp_sr_data = stress_relaxation[12:len(stress_relaxation)-1]

        # Reading the stress relaxation data per its steps
        step_count = 0 # creating a flag for steps
        tmp_step_data = [] # Creating a placeholder for stepwise stress relaxation data
        clean_comp_sr_data = [] # A placeholder for the bulk stress-relaxation data cleansed from in-line tags

        for line in tmp_sr_data:

            if line.strip() != '<divider>':
                stripped_line = line.strip() # Reading the data
                inner_list = stripped_line.split('\t')
                tmp_step_data.append(inner_list) # appending the data to stepwise placeholder
                clean_comp_sr_data.append(inner_list) # appending the data to the bulk placeholder
            else:
                step_count += 1 # Finishing the step
                # Preparing the data to store as a numpy array
                step_data = np.zeros((len(tmp_step_data), 3))
                for i in range(len(tmp_step_data)):
                    step_data[i][0] = float(tmp_step_data[i][1]) # Position x, mm
                    step_data[i][1] = np.abs(float(tmp_step_data[i][6])) # Force, n
                    step_data[i][2] = float(tmp_step_data[i][0]) # Time, s
                np.savetxt(f'{input_directory}\\Output\\Stress-Relaxation\\{file[:-4]}-StressRelax-step{step_count}-MultiAxisLoadCell.txt',
                           step_data, delimiter='\t')
                # Emptying the placeholder for the next step
                tmp_step_data = []
        # Storing the bulk stress-relaxation data for the sample
        np.savetxt(f'{input_directory}\\Output\\Stress-Relaxation\\{file[:-4]}-StressRelaxation-MultiAxisLoadCell.txt',
                   np.array(clean_comp_sr_data, dtype='float'), delimiter='\t')
        # Relocating the sample to the input folder
        shutil.move(f'{input_directory}\\{file}', f'{input_directory}\\Input\\{file}')

#   SETTING THE CONDITION FOR CONTINUING THE PROGRAM FOR OTHER PATELLAS
    check = input('Do you want to continue?(Y/N) --> ')
    if check == 'Y':
        condition = True
    elif check == 'N':
        condition = False
    else:
        print('Wrong input --> Exiting...')
        exit()
