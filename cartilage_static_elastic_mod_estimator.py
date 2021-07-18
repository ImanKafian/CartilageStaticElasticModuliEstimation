'''
About: Python script to estimate the static elastic moduli of cartilage: instantaneous and equilibrium
from the output files of the Biomomentum Mach 1 micromechanical testing system.
Author: Iman Kafian-Attari
Date: 18.07.2021
Licence: MIT
version: 0.1
=========================================================
How to use:
1. Select the output directory.
2. Select the input directory.
3. Input the radius of the indenter.
4. Input the Poisson's value at equilibrium.
5. Input the Poisson's value at instantaneous.
=========================================================
Notes:
1. This code is meant to estimate the elastic instantaneous and equilibrium moduli for articular cartilage.
2. It requires the following inputs from the user:
   - an output directory,
   - an input directory,
   - the radius of the used indenter,
   - Poisson's value for equilibrium modulus,
   - Poisson's value for instantaneous modulus.
3. It automatically estimates the instantaneous and equilibrium moduli each step.
4. It correctes the estimated values using the Hayes' formula.
4. It stores the following data per step:
   a) Equilibrium modulus:
   - Hayes ratio,
   - Equ kappa,
   - Equ stress,
   - Stepwise Equ mod,
   - fitted Equ mod,
   - Crt stepwise equ,
   - Crt fitted equ
   b) Instantaneous modulus:
   - Hayes ratio,
   - Inst kappa,
   - Inst stress,
   - Stepwise Inst mod,
   - Fitted Inst mod,
   - Crt stepwise inst,
   - Crt fitted inst.
5. The output files are saved as an Excel file
=========================================================
TODO for version O.2
1. Modify the code in a functional form.
2. Store the files as Pandas dataframes.
=========================================================
'''

print(__doc__)

import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import shutil
import math
from openpyxl import Workbook
from scipy import interpolate
from numpy import polyfit as fit
import xlrd, xlwt

# Setting up some mechanical parameters for Hayes' correction formula
points = np.array([0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2], dtype='float')
poisson_inst_vals = np.array([1.281, 1.683, 2.211, 2.855, 3.609, 4.469, 5.441, 6.528, 7.735, 9.069], dtype='float')
poisson_equ_vals = np.array([1.183, 1.434, 1.677, 1.963, 2.260, 2.564, 2.872, 3.181, 3.492, 3.804], dtype='float')
inst_k_interpolating = interpolate.interp1d(points, poisson_inst_vals, kind='cubic', fill_value='extrapolate')
equ_k_interpolating = interpolate.interp1d(points, poisson_equ_vals, kind='cubic', fill_value='extrapolate')

root = tk.Tk()
root.withdraw()

condition = True
while condition == True:

    # Reading the input and output directories
    output_dir = filedialog.askdirectory(parent=root, initialdir='C:\\', title='Select the output directory')
    input_dir = filedialog.askdirectory(parent=root, initialdir='C:\\', title='Select the input directory')

    # Listing all the input files ready for the estimator
    input_files = os.listdir(input_dir)
    file_list = sorted(input_files, key=lambda x: int("".join([i for i in x if i.isdigit()])))

    # Reading infromation required for estimating the elastic moduli
    radius = float(input('Inser the radius of the indenter (mm) --> ')) # The radius of the indenter
    poisson_eq = float(input('Inser the Poisson\'s value for equilibrium modulus --> ')) # The Poisson's value at equilibrium
    poisson_inst = float(input('Inser the Poisson\'s value for instantaneous modulus --> ')) # The Poisson's value at instantaneous

    for file in file_list:
        input_data = np.loadtxt(f'{input_dir}\\{file}')

        # Equilibrium Modulus
        equ_mod_data = np.zeros((7, input_data.shape[1]))

        # Preliminary data required for estimating the Hayes' corrected equilibrium modulus.
        for step in range(input_data.shape[1]):
            equ_mod_data[0][step] = radius/input_data[0][step] # Hayes' ratio (a/h), a = radius of indenter = 1/2
            equ_mod_data[1][step] = equ_k_interpolating(equ_mod_data[0][step]) # Equilibrium kappa for Hayes' correction
            equ_mod_data[2][step] = input_data[4][step]/ (math.pi*radius*radius) # Equilibrium stress
            equ_mod_data[3][step] = equ_mod_data[2][step]/input_data[2][step] # Step-wise init. Equilibrium mod.

        # Corrected equ.
        for step in range(input_data.shape[1]):
            # Init. equ. mod based on fitted line to equ. stresses and strains
            equ_mod_data[4][step] = fit(input_data[1, :], equ_mod_data[2, :], 1)[0]

            # Corrected step-wise equ. mod. for the step-wise init. equ. mod.
            equ_mod_data[5][step] = ((1 - pow(poisson_eq, 2)) * math.pi * equ_mod_data[0][step] * (
                    equ_mod_data[2][step]/input_data[1][step])) / (2 * equ_mod_data[1][step])

            equ_mod_data[6][step] = ((1 - pow(poisson_eq, 2)) * math.pi * equ_mod_data[0][0] * equ_mod_data[4][step]) / (
                    2 * equ_mod_data[1][0]) # Corrected fitted equ. mod. for the fitted init. equ. mod.

        # Instantaneous Modulus
        inst_mod_data = np.zeros((7, input_data.shape[1]))

        # Preliminary data required for estimating the Hayes' corrected instantaneous modulus.
        for step in range(input_data.shape[1]):
            inst_mod_data[0][step] = radius/input_data[0][step]  # Hayes' ratio (a/h)
            inst_mod_data[1][step] = inst_k_interpolating(inst_mod_data[0][step]) # Inst. kappa for Hayes' correction
            inst_mod_data[2][step] = input_data[7][step] / (math.pi * radius * radius)  # inst. stress
            inst_mod_data[3][step] = inst_mod_data[2][step] / input_data[2][step]  # Step-wise init. inst. mod.

        # Corrected Inst.
        for step in range(input_data.shape[1]):
            # Init. inst. mod based on fitted line to inst. stresses and strains
            inst_mod_data[4][step] = fit(input_data[1, :], inst_mod_data[2, :], 1)[0]

            # Corrected step-wise inst. mod. for the step-wise init. inst. mod.
            inst_mod_data[5][step] = ((1 - pow(poisson_inst, 2)) * math.pi * inst_mod_data[0][step] * (inst_mod_data[2][step]/input_data[1][step])) / (
                        2 * inst_mod_data[1][step])

            # Corrected fitted inst. mod. for the fitted init. inst. mod.
            inst_mod_data[6][step] = ((1 - pow(poisson_inst, 2)) * math.pi * inst_mod_data[0][0] * inst_mod_data[4][step]) / (
                        2 * inst_mod_data[1][0])

        # Building the output document into an excel file
        stat_mod = xlwt.Workbook()

        # Equ. :
        final_equ_data = stat_mod.add_sheet('Equ Mod.')
        final_equ_data.write(0, 0, 'Data')

        for i in range(input_data.shape[1]):
            final_equ_data.write(0, i+1, f'Step {i}')

        header = ['Hayes ratio', 'Equ kappa', 'Equ stress', 'Stepwise Equ mod', 'fitted Equ mod', 'Crt stepwise equ', 'Crt fitted equ']
        for label in range(len(header)):
            final_equ_data.write(label+1, 0, header[label])
        for i in range(input_data.shape[1]):
            for j in range(7):
                final_equ_data.write(j+1, i+1, equ_mod_data[j][i])

        # Inst. :
        final_inst_data = stat_mod.add_sheet('Inst Mod.')
        final_inst_data.write(0, 0, 'Data')
        for i in range(input_data.shape[1]):
            final_inst_data.write(0, i+1, f'Step {i}')

        header = ['Hayes ratio', 'Inst kappa', 'Inst stress', 'Stepwise Inst mod', 'fitted Inst mod', 'Crt stepwise Inst',
                  'Crt fitted Inst']
        for label in range(len(header)):
            final_inst_data.write(label + 1, 0, header[label])

        for i in range(input_data.shape[1]):
            for j in range(7):
                final_inst_data.write(j + 1, i + 1, inst_mod_data[j][i])

        stat_mod.save(f'{output_dir}\\{file[:-4]}-StaticElasticModuli.xls')

    check = input('Do you want to continue?(Y/N) --> ')
    if check == 'Y':
        condition = True
    elif check == 'N':
        condition = False
    else:
        print('Wrong input --> Exiting...')
        exit()
