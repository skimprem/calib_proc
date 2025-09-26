import sys
import argparse
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import messagebox as mb
from functions.globals import METHOD
from tkinter import ttk, simpledialog
import logging


logger = logging.getLogger('calib_proc.arguments')
class ComboDialog(simpledialog.Dialog):
    def __init__(self, parent, title, options, text, initial=None):
        self.options = options
        self.text = text
        self.initial = initial or options[0]
        self.selection = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.text).pack(padx=5, pady=5)
        self.combo = ttk.Combobox(master, values=self.options, state="readonly")
        self.combo.pack(padx=5, pady=5)
        self.combo.set(self.initial)
        return self.combo  # чтобы фокус встал на поле

    def apply(self):
        self.selection = self.combo.get()

def ask_option(title, options, text, initial=None):
    root = tk.Tk()
    root.withdraw()
    dlg = ComboDialog(root, title, options, text, initial)
    return dlg.selection

def cli_args():

    logger.info('Starting CLI for argument input')

    parser=argparse.ArgumentParser(
        prog='calibration',
        description='Determinate CG-6 Calibration Parameters',
        epilog='''
            Describe the program here.
        ''',
        exit_on_error=False
    )

    parser.add_argument(
        '--relative',
        nargs='+',
        help='Input data files',
        required=True, 
    )

    parser.add_argument(
        '--absolute',
        metavar='in-file',
        type=argparse.FileType('r'),
        help='Input absolute file',
        required=True
    )

    parser.add_argument(
        '--output',
        metavar='out-file',
        type=argparse.FileType('w'),
        default='output.xlsx',
        help='Name for the output file'
    )

    parser.add_argument(
        '--logging',
        action='store_true',
        help='Enable logging to file'
    )
  
    parser.add_argument(
        '--method',
        type=str,
        default=METHOD,
        help='''
            The method of estimate params:
            RLM (Robust Linear Models) or
            OLS (ordinary least squares) or
            WLS (Weighted Least Squares).
            Default is "WLS"
        '''
    )

    parser.add_argument(
        '--drift_degree',
        type=int,
        default=2,
        help='''
            The degree of drift fitting.
            Default is 2.
        '''
    )

    parser.add_argument(
        '--calib_degree',
        type=int,
        default=1,
        help='''
            The degree of calibration fitting.
            Default is 1.
        '''
    )

    parser.add_argument(
        '--meter_height',
        type=float,
        default=0.21,
        help='''
            The height of the meter.
            Default is 0.21 m.
        '''
    )   

    return parser.parse_args()

def gui_args():

    '''
    Define the namespace object for argument by CLI
    '''

    logger.info('Starting GUI for argument input')

    logger.info('Logging mode selection')
    logging_mode = mb.askyesno(
        title='Logging',
        message='Enable logging to file?',
    )
   
    logger.info('Opening file selection dialog for relative measurements')
    relative=list(
        fd.askopenfilenames(
            defaultextension='.dat',
            filetypes=[
                ('CG-6 format files', '*.dat'),
            ],
            title='Choose measured data files'
        )
    )

    if not relative:
        logger.warning('User cancelled relative file selection, exiting')
        sys.exit(0)

    logger.info('Opening file selection dialog for absolute measurements')
    absolute=fd.askopenfilename(
            defaultextension='.xlsx',
            filetypes=[
                ('Excel files', '*.xlsx'),
                ('All files', '*'),
            ],
            title='Choose absolute file'
        )
    if not absolute:
        logger.warning('User cancelled absolute file selection, exiting')
        sys.exit(0)

    logger.info('Opening file selection dialog for output file')
    output = fd.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[
            ('ASCII text file', '*.xlsx'),
            ('Comma separated files', '*.csv'),
            ('All files', '*')
        ],
        initialfile='output.xlsx',
        title='Save Output',
    )

    if not output:
        logger.warning('User cancelled output file selection, exiting')
        sys.exit(0)

    logger.info('Selecting solution method')
    method = ask_option(
        title='Solution method',
        options=['WLS', 'OLS', 'RLM'],
        initial='WLS',
        text='Select the method to estimate parameters:'
    )

    if not method:
        logger.warning('User cancelled method selection, exiting')
        sys.exit(0)

    logger.info('Selecting drift degree')
    drift_degree = ask_option(
        title='Drift degree',
        options=[1, 2],
        initial=2,
        text='Select the degree of drift fit:'
    )

    if not drift_degree:
        logger.warning('User cancelled drift degree selection, exiting')
        sys.exit(0)

    logger.info('Selecting calibration degree')
    calib_degree = ask_option(
        title='Calibration degree',
        options=[1, 2],
        initial=1,
        text='Select the degree of calibration fit:'
    )

    if not calib_degree:
        logger.warning('User cancelled calibration degree selection, exiting')
        sys.exit(0)

    logger.info('Entering meter height')
    meter_height = sd.askfloat(
        title='Meter height',
        prompt='Enter the height of the meter (m):',
        initialvalue=0.21,
    )

    if not meter_height:
        logger.warning('User cancelled meter height input, exiting')
        sys.exit(0)

    arguments = []
    parser = argparse.ArgumentParser()

    parser.add_argument('--relative')
    arguments.append('--relative')
    arguments.append(relative)

    parser.add_argument('--absolute', type=argparse.FileType('r'))
    arguments.append('--absolute')
    arguments.append(absolute)

    parser.add_argument('--output', type=argparse.FileType('w'))
    arguments.append('--output')
    arguments.append(output)

    parser.add_argument('--logging', action='store_true')
    if logging_mode:
        arguments.append('--logging')

    parser.add_argument('--method', type=str)
    arguments.append('--method')
    arguments.append(method)

    parser.add_argument('--drift_degree', type=int)
    arguments.append('--drift_degree')
    arguments.append(str(drift_degree))

    parser.add_argument('--calib_degree', type=int)
    arguments.append('--calib_degree')
    arguments.append(str(calib_degree))

    parser.add_argument('--meter_height', type=float)
    arguments.append('--meter_height')
    arguments.append(str(meter_height))

    return parser.parse_args(arguments)
