'''
Global variables for calibration processing
'''

METHOD = 'RLM'

REL_HEADER = 'Station	Date	Time	CorrGrav	Line	StdDev	StdErr	RawGrav	X	Y	SensorTemp	TideCorr	TiltCorr	TempCorr	DriftCorr	MeasurDur	InstrHeight	LatUser	LonUser	ElevUser	LatGPS	LonGPS	ElevGPS	Corrections[drift-temp-na-tide-tilt]'

# Titles of the '/'-prefixed section headers found in Scintrex CG-5 files.
# These carry no key/value data and are skipped during parsing.
CG5_SECTION_TITLES = (
    'CG-5 SURVEY',
    'CG-5 SETUP PARAMETERS',
    'CG-5 OPTIONS',
)

# Maps the raw column tokens found in a CG-5 file's
# '/----LINE----STATION----...' header row to the column names used
# internally, aligned as closely as possible with the CG-6 naming
# (REL_HEADER above) so downstream processing does not need to care
# which instrument produced the data.
CG5_COLUMNS = {
    'LINE': 'Line',
    'STATION': 'Station',
    'ALT.': 'Alt',
    'GRAV.': 'CorrGrav',
    'SD.': 'StdErr',
    'TILTX': 'TiltX',
    'TILTY': 'TiltY',
    'TEMP': 'SensorTemp',
    'TIDE': 'TideCorr',
    'DUR': 'MeasurDur',
    'REJ': 'Reject',
    'TIME': 'Time',
    'DEC.TIME+DATE': 'DecTimeDate',
    'TERRAIN': 'TerrainCorr',
    'DATE': 'Date',
}

# Maps CG-5 header key/value metadata to the equivalent CG-6 header key,
# so that fields referenced elsewhere (e.g. 'Instrument Serial Number' used
# to group readings by meter in functions.processing.proc) line up
# regardless of instrument format.
CG5_HEADER_KEY_MAP = {
    'Instrument S/N': 'Instrument Serial Number',
}

TOTAL_UNCERT = 0.005