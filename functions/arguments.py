import argparse
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import messagebox as mb
from calib.globals import METHOD

def cli_args():

    parser=argparse.ArgumentParser(
        prog='almaty_calibration',
        description='Determinate CG-6 Calibration Parameters',
        epilog='''
            Describe the program here.
        ''',
        exit_on_error=False
    )

    parser.add_argument(
        '--relative',
        nargs='+',
        help='Input data files'
    )

    parser.add_argument(
        '--absolute',
        metavar='in-file',
        type=argparse.FileType('r'),
        help='Input absolute file'
    )

    parser.add_argument(
        '--output',
        metavar='out-file',
        type=argparse.FileType('w'),
        default='output.xlsx',
        help='Name for the output file'
    )

    parser.add_argument(
        '--logs',
        metavar='out-file',
        type=argparse.FileType('w'),
        help='Report to log file'
    )
  
    parser.add_argument(
        '--method',
        default=METHOD,
        help='''
            The method of estimate params:
            RLM (Robust Linear Models) or OLM (ordinary least squares).
            Default is "RLM"
        '''
    )
    
    return parser.parse_args()

def gui_args():

    '''
    Define the namespace object for argument by CLI
    '''
    
    relative=list(
        fd.askopenfilenames(
            defaultextension='.dat',
            filetypes=[
                ('CG-6 format files', '*.dat'),
            ],
            title='Choose measured data file'
        )
    )

    absolute=fd.askopenfilename(
            defaultextension='.xlsx',
            filetypes=[
                ('Excel files', '*.xlsx'),
                ('All files', '*'),
            ],
            title='Choose absolute file'
        )

    output = fd.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[
            ('ASCII text file', '*.xlsx'),
            ('Comma separated files', '*.csv'),
            ('All files', '*')
        ],
        initialfile='output.xlsx',
        title='Save Output'
    )

    logs_mode = mb.askyesno(
        title='Log file',
        message='Want to create a log file?',
    )

    if logs_mode:
        logs = fd.asksaveasfilename(
            defaultextension=".log",
            initialfile='report.log',
            title='Log file',
        )
   
    method = sd.askstring(
        title='Solution method',
        initialvalue='RLM',
        prompt='Enter method (RLM or OLS):'
    )

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

    parser.add_argument('--logs', type=argparse.FileType('w'))
    if logs_mode:
        arguments.append('--logs')
        arguments.append(logs)

    parser.add_argument('--method', type=str)
    arguments.append('--method')
    arguments.append(method)

    return parser.parse_args(arguments)