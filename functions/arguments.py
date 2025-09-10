import argparse
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import messagebox as mb
from functions.globals import METHOD
from tkinter import ttk, simpledialog


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
        '--logs',
        metavar='out-file',
        type=argparse.FileType('w'),
        default='report.log',
        help='Report to log file'
    )
  
    parser.add_argument(
        '--method',
        type=str,
        default=METHOD,
        help='''
            The method of estimate params:
            RLM (Robust Linear Models) or OLM (ordinary least squares).
            Default is "RLM"
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

    method = ask_option(
        title='Solution method',
        options=['WLS', 'OLS', 'RLM'],
        initial='WLS',
        text='Select the method to estimate parameters:'
    )

    drift_degree = ask_option(
        title='Drift degree',
        options=[1, 2],
        initial=2,
        text='Select the degree of drift fit:'
    )

    calib_degree = ask_option(
        title='Calibration degree',
        options=[1, 2],
        initial=1,
        text='Select the degree of calibration fit:'
    )

    meter_height = sd.askfloat(
        title='Meter height',
        prompt='Enter the height of the meter (m):',
        initialvalue=0.21,
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
