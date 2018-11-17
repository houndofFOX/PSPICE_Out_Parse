# This program parses a PSPICE output file and determines if all MOSFETS are in saturation

import sys
import logging
import os.path

LOG_LVL = logging.INFO

def main():
    mos_sec = 0
    found_v = [0, 0]

    VDS = []
    VDSAT = []
    for line in open(sys.argv[1], 'r'):
        # Get to the MOSFET parameters section
        if "**** MOSFETS" in line:
            logging.debug("Found MOSFETS")
            mos_sec = 1
        # Process lines in the MOSFET section
        if mos_sec:
            # Find relevant lines
            (VDS, found_v[0]) = findLine("VDS ", found_v[0], line) if not found_v[0] else (VDS, found_v[0])
            (VDSAT, found_v[1]) = findLine("VDSAT ", found_v[1], line) if not found_v[1] else (VDSAT, found_v[1])

            # Calcualte VDS - VSAT
            if found_v[0] and found_v[1]:
                logging.debug("{}, {}".format(len(VDS), len(VDSAT)))
                # Check that arrays VDS and VDSAT are the same length
                if not (len(VDS) == len(VDSAT)):
                    logging.critical("VDS/VDSAT length mismatch")
                    sys.exit()
                found_v = [0, 0]
                VSAT = [round(abs(VDS_i) - abs(VDSAT_i), 5) for VDS_i, VDSAT_i in zip(VDS, VDSAT)]
                logging.info("VDS - VDSAT")
                logging.info("{}".format(VSAT))
                if any(VSAT_i < 0 for VSAT_i in VSAT):
                    logging.info("VDS:   {}".format(VDS))
                    logging.info("VDSAT: {}".format(VDSAT))
                    logging.info("VSAT:  {}".format(VSAT))
                    logging.info("Found MOSFET out of saturation")
                    sys.exit()
                print ""
    logging.info("All MOSFETS are in saturation!")

# This function finds then parses the information in the appropriate
def findLine(name, found, line):
    if name in line:
        if found == 1:
            logging.critical("Second {} found before other parameters".format(name.strip()))
            sys.exit()
        logging.debug("Found {}".format(name.strip()))
        params = line.split()[1:]
        params = [float(param) for param in params]
        logging.debug(params)
        return (params, 1)
    return ([], 0)

if __name__ ==   "__main__":
    #logging.basicConfig(level=LOG_LVL, format = "%({0: <6})s - %(message)s".format(logging.getLevelName(LOG_LVL)))
    logging.basicConfig(level=LOG_LVL)
    if len(sys.argv) != 2:
        logging.critical("Use as \"python proc_out_file.py <filename>\"")
        sys.exit()
    if not os.path.isfile(sys.argv[1]):
        logging.critical("Invalid file name")
        sys.exit()
    main()
