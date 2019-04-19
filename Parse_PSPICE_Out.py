# This program parses all values in a PSPICE output file, returning MOSFETs objects containing MOSFET parameters

import os
import sys
import logging
import platform
#import os.path

LOG_LVL = logging.INFO
USERNAME = "sugimots"

# PSPICE output file parser
class Parse_PSPICE_Out():
    # Initialization
    def __init__(self, Logger, remote, filename):
        # Assign Logger
        self.Logger = Logger
        # Get remote file over SSH
        if remote.lower() in ['r', 'remote']:
            if platform.system() == 'Linux':
                os.system("scp {}@athena.ecs.csus.edu:{} .".format(USERNAME, filename))
            else:
                Logger.warning("Automatic remote file retrieval only supported on Linux")
                Logger.warning("Setting retrieval type to \"local\"")
                remote = 'l'
        # Check that requested file is available locally
        self.filename = filename if remote.lower() in ['l', 'local'] else filename.split('/')[-1]
        if not os.path.isfile(self.filename):
            Logger.critical("Invalid file name: {}".format(self.filename))
            sys.exit()
    
    # Parses PSPICE out file, generates list of MOSFET objects and returns them sorted by name
    def parseFile(self):
        mos_sec = 0  # Flag for when to begin parsing lines
        MOS_list = []
        short_MOS_list = []
        # Read file line at a time
        for line in open(self.filename, 'r'):
            # Toggle mos_sec when upon reaching MOSFET section
            if '**** MOSFETS'  in line:
                self.Logger.debug("Found MOSFETS")
                mos_sec = 1
            # Fills in MOSFET parameters when in MOSFET section.  Assumes "NAME" parameters comes first
            if mos_sec:
                # Create MOSFET objects when "NAME" parameter is encountered
                if "NAME " in line:
                    for name in line.split()[1:]:
                        MOSFET = MOSFET_Params()
                        MOSFET.NAME = name.strip()
                        short_MOS_list.append(MOSFET)
                # TODO: Funtionalize this shit
                # Add ID values to MOSFETs in short_MOS_list
                if "ID "  in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.ID = float(param)
                # Add VGS values to MOSFETs in short_MOS_list
                if "VGS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VGS = float(param)
                if "VDS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VDS = float(param)
                if "VBS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VBS = float(param)
                if "VTH " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VTH = float(param)
                if "VDSAT " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.VDSAT = float(param)
                if "Lin0/Sat1 " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.Lin0_Sat1 = float(param)
                if "if " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.IF = float(param)
                if "ir " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.IR = float(param)
                if "TAU " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.TAU = float(param)
                if "GM " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.GM = float(param)
                if "GDS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.GDS = float(param)
                if "GMB " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.GMB = float(param)
                if "CBD " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.CBD = float(param)
                if "CBS " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.CBS = float(param)
                if "CGSOV " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.CGSOV = float(param)
                if "CGDOV " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.CGDOV = float(param)
                if "CGBOV " in line:
                    for MOSFET, param in zip(short_MOS_list, line.split()[1:]):
                        MOSFET.CGBOV = float(param)
                # Add short_MOS_list to MOS_list
                if "Derivatives of gate " in line:
                    self.Logger.debug("MOSFET parameters added")
                    self.Logger.debug("len(short_MOS_list): {}".format(len(short_MOS_list)))
                    MOS_list.extend(short_MOS_list)
                    self.Logger.debug("len(MOS_list): {}".format(len(MOS_list)))
                    short_MOS_list = []
        # End for line in open(self.filename, 'r')
        self.Logger.debug("len(MOS_List): {}".format(len(MOS_list)))
        sorted_MOS_list = sorted(MOS_list, key=lambda MOSFET: MOSFET.NAME)
        return sorted_MOS_list



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
    Parser = Parse_PSPICE_Out(Logger, params[1], params[2])
    MOS_List = Parser.parseFile()
    # Print MOSFET List
    for MOSFET in MOS_List:
        Logger.info(MOSFET.NAME)
        Logger.info("ID:        {}".format(MOSFET.ID))
        Logger.info("VGS:       {}".format(MOSFET.VGS))
        Logger.info("VDS:       {}".format(MOSFET.VDS))
        Logger.info("VBS:       {}".format(MOSFET.VBS))
        Logger.info("VTH:       {}".format(MOSFET.VTH))
        Logger.info("VDSAT:     {}".format(MOSFET.VDSAT))
        Logger.info("Lin0/Sat1: {}".format(MOSFET.Lin0_Sat1))
        Logger.info("if:        {}".format(MOSFET.IF))
        Logger.info("ir:        {}".format(MOSFET.IR))
        Logger.info("TAU:       {}".format(MOSFET.TAU))
        Logger.info("GM:        {}".format(MOSFET.GM))
        Logger.info("GDS:       {}".format(MOSFET.GDS))
        Logger.info("GMB:       {}".format(MOSFET.GMB))
        Logger.info("CBD:       {}".format(MOSFET.CBD))
        Logger.info("CBS:       {}".format(MOSFET.CBS))
        Logger.info("CGSOV:     {}".format(MOSFET.CGSOV))
        Logger.info("CGDOV:     {}".format(MOSFET.CGDOV))
        Logger.info("CGBOV:     {}".format(MOSFET.CGBOV))
        Logger.info("")

# For running internal parsing test
if __name__ == '__main__':
    # Setup Logging
    logging.basicConfig(format = "[%(levelname) -8s]: %(name)-15s: %(funcName)-10s: %(lineno)-4d >> %(message)s")
    Logger = logging.getLogger("Parse_PSPICE_Out")
    Logger.setLevel(LOG_LVL)
    # Check command line parameter requirements
    if len(sys.argv) != 3 and sys.argv[1] not in ['l', 'r', 'L', 'R']:
        Logger.critical("Use as \"python Parse_PSPICE_Out.py \'l\'/\'r\' <filename>\"")
        sys.exit()
    testParser(Logger, sys.argv)
