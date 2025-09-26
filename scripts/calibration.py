#!/usr/bin/env python
u'''
Read CG-x data file and calculate calibration parameters
'''

import sys
import argparse
import pandas as pd
import logging
from tkinter import filedialog as fd
from functions.arguments import cli_args, gui_args
from functions.loading import load_relative, load_absolute
from functions.processing import proc
from functions.logging import setup_logging


def main():

    try:

        # Setup logging
        logger = setup_logging()
        logger = logging.getLogger('calib_proc.main')

        if len(sys.argv) == 1:
            logger.info('No command line arguments provided, switching to GUI mode')
            args = gui_args()
            gui_mode = True
        else:
            logger.info('Command line arguments detected, switching to CLI mode')
            args = cli_args()
            gui_mode = False
        
        if args.logging:
            logger = setup_logging(enable_file_logging=True)
            logger = logging.getLogger('calib_proc.main')

        for key, value in vars(args).items():
            match key:
                case 'relative':
                    logger.info('Arguments: %s %s', key, ' '.join(value))
                case 'absolute' | 'output':
                    logger.info('Arguments: %s %s', key, value.name if hasattr(value, 'name') else value)
                case _:
                    logger.info('Arguments: %s %s', key, value)

        data_files = []
        for data_file_name in args.relative:
            try:
                logger.info('Opening CG-6 data file: %s', data_file_name)
                data_files.append(open(data_file_name, 'r', encoding='utf-8'))
            except FileNotFoundError:
                logger.error('CG-6 data file not found: "%s"', data_file_name)
                sys.exit(1)

        logger.info('Loading %d CG-6 data files', len(data_files))
        relative = load_relative(data_files)
        logger.info('Loaded %d CG-6 readings', len(relative))

        try:
            logger.debug('Loading reference data from: %s', args.absolute.name)
            absolute = load_absolute(
                args.absolute.name,
                reduce_height=args.meter_height
            )
            logger.info('Loaded %d reference gravity', len(absolute))
        except FileNotFoundError:
            logger.error('Reference file not found: "%s"', args.absolute.name)
            sys.exit(1)

        logger.info('Starting calibration processing')
        logger.debug('Processing parameters: method=%s, drift_degree=%d, calib_degree=%d', 
                    args.method, args.drift_degree, args.calib_degree)
        
        params, ties = proc(
            relative=relative,
            absolute=absolute,
            model_type=args.method,
            drift_degree=args.drift_degree,
            calib_degree=args.calib_degree,
        )

        logger.info('Processing complete. Generated %d calibration parameters and %d ties', 
                   len(params), len(ties))
        logger.info('Saving results to: %s', args.output.name)

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

        logger.info('Results saved successfully')

    except argparse.ArgumentError as e:
        logger = logging.getLogger('calib_proc')
        logger.error('Argument error: %s', e)
        logger.error('Use --help to see available options.')
        sys.exit(2)

    except Exception as e:
        logger = logging.getLogger('calib_proc')
        logger.error('Unexpected error: %s', e)
        logger.exception('Full traceback:')
        sys.exit(99)
    
    except KeyboardInterrupt:
        logger = logging.getLogger('calib_proc')
        logger.warning('Process interrupted by user')
        sys.exit(130)
        
    except SystemExit as e:
        if e.code != 0:
            logger = logging.getLogger('calib_proc')
            logger.warning('Exiting with code %d', e.code)
        raise

# run main program
if __name__ == '__main__':
    main()