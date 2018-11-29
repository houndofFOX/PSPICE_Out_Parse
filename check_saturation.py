# This program utilizes Parse_PSPICE_Out.py to determine if all MOSFETS are in saturation

import sys
import logging
import os.path
import Parse_PSPICE_Out

DEFAULT_LOG_LVL = logging.INFO

class Check_Saturation():
    # Initialization
    def __init__(self, logger, params):
        # Assign Logger
        self.Logger = Logger
        self.remote = params[1].lower()
        self.filename = params[2]

    # Perform saturation check
    def process(self):
        # Setup Parse_PSPICE_Out Logger
        Parse_Logger = logging.getLogger("Parse_PSPICE_Out")
        # Create Parser object and Parse file
        Parser = Parse_PSPICE_Out.Parse_PSPICE_Out(Parse_Logger, self.remote, self.filename)
        MOS_List = Parser.parseFile()
        non_sat = []
        # Check if all MOSFETs are in saturation.
        for MOSFET in MOS_List:
            if MOSFET.VDS == None or MOSFET.VDSAT == None:
                self.Logger.critical("MOSFET {} has no VDS or VDSAT")
                sys.exit()
            if not abs(MOSFET.VDS) >= abs(MOSFET.VDSAT):
                non_sat.append(MOSFET.NAME)
        if len(non_sat) > 0:
            self.Logger.info("{} MOSFETS out of saturation: {}".format(len(non_sat), non_sat))
            

if __name__ == '__main__':
    # Setup Logging
    logging.basicConfig(format = "[%(levelname) -8s]: %(name)-15s: %(funcName)-10s: %(lineno)-4d >> %(message)s")
    Logger = logging.getLogger("check_saturation")
    Logger.setLevel(DEFAULT_LOG_LVL)
    # Check command line parameter requirements
    if len(sys.argv) != 3 and sys.argv[1].lower() not in ['l', 'r', 'local', 'remote']:
        Logger.critical("Use as \"python check_saturation.py\" <l>/<r> <filename>")
        sys.exit()
    if len(sys.argv) == 4 and sys.argv[3].lower() in ['v', 'verbose']:
        Logger.setLevel(logging.DEBUG)
    Check_Sat = Check_Saturation(Logger, sys.argv[:3])
    Check_Sat.process()

    