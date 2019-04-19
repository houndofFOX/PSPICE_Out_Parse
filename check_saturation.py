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
        Parse_Logger.setLevel(self.Logger.getEffectiveLevel())
        # Create Parser object and Parse file
        Parser = Parse_PSPICE_Out.Parse_PSPICE_Out(Parse_Logger, self.remote, self.filename)
        MOS_List = Parser.parseFile()
        non_sat = []
        sat_margin = 100
        von_out = []
        von_margin = 100
        # Check parameters for all MOSFETs.
        for MOSFET in MOS_List:
            # Check if MOSFET is in saturation.
            if MOSFET.VDS == None or MOSFET.VDSAT == None:
                self.Logger.critical("MOSFET {} has no VDS or VDSAT".format(MOSFET.NAME))
                sys.exit()
            saturation = abs(MOSFET.VDS) - abs(MOSFET.VDSAT)
            if saturation < 0:
                non_sat.append(MOSFET.NAME)
            # Record saturation margin if necessary
            sat_margin = saturation if sat_margin > saturation else sat_margin
            # Check if Von requirement is met
            if MOSFET.VGS == None or MOSFET.VTH == None:
                self.Logger.critical("MOSFET {} has not VGS or VTH".format(MOSFET.NAME))
                sys.exit()
            von = abs(MOSFET.VGS) - abs(MOSFET.VTH)
            if von < 0.150:
                von_out.append(MOSFET.NAME)
            # Record Von margin if necessary
            von_margin = von if von_margin > von else von_margin
        # Print results to user
        if len(non_sat) > 0:
            self.Logger.info("{} MOSFETS out of saturation: {}".format(len(non_sat), non_sat))
        else:
            self.Logger.info("All MOSFETS are in saturation!")
        self.Logger.info("Saturation Margin: {}".format(sat_margin))
        if len(von_out) > 0:
            self.Logger.info("{} MOSFETS do not meet Von > 150mV: {}".format(len(von_out), von_out))
        else:
            self.Logger.info("All MOSFETS meet Von > 150mV")
        self.Logger.info("Von Margin: {}".format(von_margin))

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

    
