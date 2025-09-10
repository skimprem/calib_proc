#!/usr/bin/env python
u'''
Read CG-6 data file and calculate calibration parameters
'''

import pandas as pd
from tkinter import filedialog as fd
from functions.arguments import cli_args, gui_args
from functions.loading import load_relative, load_absolute
from functions.processing import params as calib_params

def main():

    gui_mode = False
    args = cli_args()

    if args.relative is None:
        gui_mode = True
        args = gui_args()

    data_files = []
    for data_file_name in args.relative:
        data_files.append(open(data_file_name, 'r', encoding='utf-8'))

    relative = load_relative(data_files)
    absolute = load_absolute(args.absolute.name)

    params, ties = calib_params(
        relative=relative,
        absolute=absolute,
    )

    print(params)
    print(ties)
    
    with pd.ExcelWriter(args.output.name) as writer:  

        params.to_excel(
            writer,
            index=False,
            sheet_name='calibration_parameters'
        )

        ties.to_excel(
            writer,
            index=False,
            sheet_name='fitted_ties'
            )


# run main program
if __name__ == '__main__':
    main()