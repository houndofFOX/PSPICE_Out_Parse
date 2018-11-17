# This program parses a PSPICE output file and determines if all MOSFETS are in saturation

import sys
import logging
import os.path

LOG_LVL = logging.DEBUG

def main(Logger):
    mos_sec = 0
    found_v = [0, 0]

    VDS = []
    VDSAT = []
    for line in open(sys.argv[1], 'r'):
        # Get to the MOSFET parameters section
        if "**** MOSFETS" in line:
            Logger.debug("Found MOSFETS")
            mos_sec = 1
        # Process lines in the MOSFET section
        if mos_sec:
            # Find relevant lines
            (VDS, found_v[0]) = findLine("VDS ", found_v[0], line) if not found_v[0] else (VDS, found_v[0])
            (VDSAT, found_v[1]) = findLine("VDSAT ", found_v[1], line) if not found_v[1] else (VDSAT, found_v[1])

            # Calcualte VDS - VSAT
            if found_v[0] and found_v[1]:
                Logger.debug("{}, {}".format(len(VDS), len(VDSAT)))
                # Check that arrays VDS and VDSAT are the same length
                if not (len(VDS) == len(VDSAT)):
                    Logger.critical("VDS/VDSAT length mismatch")
                    sys.exit()
                found_v = [0, 0]
                VSAT = [round(abs(VDS_i) - abs(VDSAT_i), 5) for VDS_i, VDSAT_i in zip(VDS, VDSAT)]
                Logger.info("VDS - VDSAT")
                Logger.info("{}".format(VSAT))
                if any(VSAT_i < 0 for VSAT_i in VSAT):
                    Logger.info("VDS:   {}".format(VDS))
                    Logger.info("VDSAT: {}".format(VDSAT))
                    Logger.info("VSAT:  {}".format(VSAT))
                    Logger.info("Found MOSFET out of saturation")
                    sys.exit()
                print ""
    Logger.info("All MOSFETS are in saturation!")

# This function finds then parses the information in the appropriate
def findLine(name, found, line):
    if name in line:
        if found == 1:
            Logger.critical("Second {} found before other parameters".format(name.strip()))
            sys.exit()
        Logger.debug("Found {}".format(name.strip()))
        params = line.split()[1:]
        params = [float(param) for param in params]
        Logger.debug(params)
        return (params, 1)
    return ([], 0)

if __name__ ==   "__main__":
    #Logger.basicConfig(level=LOG_LVL, format = "[%(levelname -8s]: %(name)-15s: %(funcname)-15s: %(lineno)-4d >> %(message)s")
    #Logger.basicConfig(level=LOG_LVL)
    logging.basicConfig(format = "[%(levelname) -8s]: %(name)-15s: %(funcName)-10s: %(lineno)-4d >> %(message)s")
    Logger = logging.getLogger("PSPICE_Out_Parse")
    Logger.setLevel(LOG_LVL)
    if len(sys.argv) != 2:
        Logger.critical("Use as \"python proc_out_file.py <filename>\"")
        sys.exit()
    if not os.path.isfile(sys.argv[1]):
        Logger.critical("Invalid file name")
        sys.exit()
    main(Logger)
