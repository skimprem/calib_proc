#!/usr/bin/env python
u'''
Read CG-x data file and calculate calibration parameters
'''

import sys
import argparse
import pandas as pd
from tkinter import filedialog as fd
from functions.arguments import cli_args, gui_args
from functions.loading import load_relative, load_absolute
from functions.processing import proc

def main():

    try:
        if len(sys.argv) == 1:
            args = gui_args()
            gui_mode = True
        else:
            args = cli_args()
            gui_mode = False

        data_files = []
        for data_file_name in args.relative:
            try:
                data_files.append(open(data_file_name, 'r', encoding='utf-8'))
            except FileNotFoundError:
                print(f"[ERROR] Relative data file not found: {data_file_name}")
                sys.exit(1)

        relative = load_relative(data_files)

        try:
            absolute = load_absolute(
                args.absolute.name,
                reduce_height=args.meter_height
            )
        except FileNotFoundError:
            print(f"[ERROR] Absolute file not found: {args.absolute.name}")
            sys.exit(1)
        
        params, ties = proc(
            relative=relative,
            absolute=absolute,
            model_type=args.method,
            drift_degree=args.drift_degree,
            calib_degree=args.calib_degree,
        )

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

    except argparse.ArgumentError as e:
        print(f"[ARGUMENT ERROR] {e}")
        print("Use --help to see available options.")
        sys.exit(2)

    # except Exception as e:
    #     print(f"[UNEXPECTED ERROR] {e}")
    #     sys.exit(99)


# run main program
if __name__ == '__main__':
    main()