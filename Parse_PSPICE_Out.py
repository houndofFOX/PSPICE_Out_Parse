# This program parses all values in a PSPICE output file, returning MOSFETs objects containing MOSFET parameters

import os
import sys
import logging
import platform
#import os.path

LOG_LVL = logging.DEBUG
USERNAME = "sugimots"

# PSPICE output file parser
class Parse_PSPICE_Out():
    # Initialization
    def __init__(self, Logger, params):
        # Assign Logger
        self.Logger = Logger
        # Get remote file over SSH
        if params[1] in ['r', 'R']:
            if platform.system() is 'Linux':
                os.system("scp {}@athena.ecs.csus.edu:{} .".format(USERNAME, params[2]))
            else:
                Logger.warning("Automatic remote file retrieval only supported on Linux")
                Logger.warning("Setting retrieval type to \"local\"")
                params[1] = 'l'
        # Check that requested file is available locally
        self.filename = params[2] if params[1].lower() is 'l' else params[2].split('/')[-1]
        if not os.path.isfile(self.filename):
            Logger.critical("Invalid file name: {}".format(params[2].split('/')[-1]))
            sys.exit()
    
    # Parses PSPICE out file, generates list of MOSFET objects
    def parseFile(self):
        mos_sec = 0  # Flag for when to begin parsing lines
        MOS_list = []
        short_MOS_list = []
        # Read file line at a time
        for line in open(self.filename, 'r'):
            # Toggle mos_sec when upon reaching MOSFET section
            if '**** MOSFETS'  in line:
                Logger.debug("Found MOSFETS")
                mos_sec = 1
            # Fills in MOSFET parameters when in MOSFET section.  Assumes "NAME" parameters comes first
            if mos_sec:
                # Create MOSFET objects when "NAME" parameter is encountered
                if "NAME " in line:
                    for name in line.split()[1:]:
                        MOSFET = MOSFET_Params()
                        MOSFET.NAME = name.strip()
                        short_MOS_list.append(MOSFET)
                # Add ID values to MOSFETs in short_MOS_list
                if "ID "  in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.ID = float(param)
                # Add VGS values to MOSFETs in short_MOS_list
                if "VGS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VGS = float(param)
                # Add short_MOS_list to MOS_list
                if "Derivatives of gate " in line:
                    Logger.debug("All MOSFET parameters added")
                    MOS_list.append(short_MOS_list)



# MOSFET object that is returned by the Parse class
class MOSFET_Params():
    def __init__(self):
        self.NAME = None    
        self.ID = None
        self.VGS = None
        self.VDS = None
        self.VBS = None
        self.VTH = None
        self.VDSAT = None
        self.Lin0_Sat1 = None
        self.IF = None
        self.IR = None
        self.TAU = None
        self.GM = None
        self.GDS = None
        self.GMB = None
        self.CBD = None
        self.CBS = None
        self.CGSOV = None
        self.CGDOV = None
        self.CGBOV = None

# PSPICE output file parser test function
def testParser(Logger, params):
    # Get "file pointer" for input file
    Parser = Parse_PSPICE_Out(Logger, params)
    MOS_List = Parser.parseFile()

# For running internal parsing test
if __name__ == '__main__':
    # Setup Logging
    logging.basicConfig(format = "[%(levelname) -8s]: %(name)-15s: %(funcName)-10s: %(lineno)-4d >> %(message)s")
    Logger = logging.getLogger("Parse_PSPICE_Out")
    Logger.setLevel(LOG_LVL)
    # Check command line parameters requirements
    if len(sys.argv) != 3 and sys.argv[1] not in ['l', 'r', 'L', 'R']:
        Logger.critical("Use as \"python Parse_PSPICE_Out.py 'l'/'r' <filename>\"")
        sys.exit()
    testParser(Logger, sys.argv)
