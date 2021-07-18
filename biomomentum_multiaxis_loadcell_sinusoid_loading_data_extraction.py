'''
About: Python script to run the extract the sinusoid loading dataset
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
1. This code is meant to extract the sinusoid loading dataset when a multiaxis loadcell is used.
2. Since the direction of exerted force is negative,
   the code takes the absolute value of the force for simplifying the later calculation.
3. It only considers the forces exerted on the vertical axis, that is forces compressing the tissue.
4. The sinusoid loading output files are in the form of multiple rows x 3 columns:
-  The 1st column is the absolute position Z (mm), the 2nd column is force (n), and the 3rd column is time (s).
5. It automatically finds the used frequency and stores it in the label of the output file.
=========================================================
TODO for version O.2
1. Read the data for other axes.
2. Store the sinusoid loading data for all the frequencies combined
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

        # Creating a folder specific to Sinusoid Loading output files:
        if not os.path.exists(f'{input_directory}\\Output\\Sinuosoid-Loading'):
            os.mkdir(f'{input_directory}\\Output\\Sinuosoid-Loading')

        sinusoid = [] # A placeholder for the sinusoid data
        sinusoid_flag = 0 # A flag for sinusoid data in the raw input file
        frequency_count = 0 # a flag for each sinusoid frequency  in the raw input file

        # Extracting the sinusoid bulk data
        # <--> Reading all the dataset with <Sinusoid> and <End Data> tags
        with open(f'{input_directory}\\{file}') as f:
            for line in f:
                # Looking for Sinusoid tags
                if line.strip() == '<Sinusoid>':
                    sinusoid_flag = 1 # Upon finding, set the sinusoid and frequency flags
                    frequency_count += 1

                # Reading the sinusoid data
                if sinusoid_flag == 1 and line.strip() != '<END DATA>':
                    stripped_line = line.strip()
                    inner_list = stripped_line.split('\t')
                    sinusoid.append(inner_list)

                # Completing and storing the sinusoid data for the flagged freqency
                if sinusoid_flag == 1 and line.strip() == '<END DATA>':
                    sinusoid_flag = 0 # Turning off the frequency flag for the next sinusoid loading data

                    # Finding the frequency in metadata
                    frequency = '\t'.split(sinusoid[3])[1]

                    # Cleansing the data from its metadata information
                    tmp_sinusoid = sinusoid[7:]

                    # Storing the sinusoid loading data per frequency as a numpy 2D array
                    np_sinusoid = np.zeros((len(tmp_sinusoid), 3))
                    for i in range(len(tmp_sinusoid)):
                        np_sinusoid[i][0] = float(tmp_sinusoid[i][1]) # Position z (mm)
                        np_sinusoid[i][1] = np.abs(float(tmp_sinusoid[i][6])) # Fz (n)
                        np_sinusoid[i][2] = float(tmp_sinusoid[i][0]) # Time (s)

                    np.savetxt(f'{input_directory}\\Output\\Sinusoid-Loading\\'
                               f'{file[:-4]}-SinusoidLoading-{frequency}Hz-MultiAxisLoadCell.txt', np_sinusoid, delimiter='\t')

                    # Emptying the placeholders for the next frequency
                    sinusoid = []
                    tmp_sinusoid = []

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
