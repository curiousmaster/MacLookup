#! /usr/bin/python3
import sys
import csv
import csv, sqlite3
import argparse
from os.path import expanduser



# ======================================================================
# Path to csv file containing mac to vendor CSV # This file can be
# obtained by running the macupdate.py command
# ======================================================================
HOME = expanduser("~")
VendorCSV = HOME+"/.cache/mac-vendors.txt"
MACFILE = "mac-address-lookup.txt"


# ======================================================================
# Initiate the SQLITE3 database
# ======================================================================
con = sqlite3.connect(":memory:")
cur = con.cursor()


def parseArgs():
    # =================================================
    # NAME
    #   parseArgs()
    #
    # DESCRIPTION
    #   Parse command line options
    # =================================================
    global ARGS
    global QUERY
    global MACFILE
    global VendorCSV

    ap = argparse.ArgumentParser(description="maclookup configuration parser")
    ap.add_argument("-f", "--file", required=True, help="Specify input file")
    ap.add_argument("-d", "--database", required=False, help="Specify MAC lookup database")

    ARGS = vars(ap.parse_args())

    if ARGS['file']:
        MACFILE = ARGS['file']
        
    if ARGS['database']:
        VendorCSV = ARGS['database']

    return ARGS


# ======================================================================
# Create and populate SQLITE3 database
# ======================================================================
def genVendorDB(file):

    cur.execute("CREATE TABLE vendor (vmac, vendor);") # use your column names here

    with open(file,'r') as fin:
        dr = csv.DictReader(fin, delimiter=":",fieldnames=['vmac', 'vendor'])
        to_db = [(i['vmac'].upper(), i['vendor']) for i in dr]

    cur.executemany("INSERT INTO vendor (vmac, vendor) VALUES (?, ?);", to_db)

    con.commit()


# ======================================================================
# Query database for vendor
# ======================================================================
def macLookup(mac):

    vmac = mac[0:6] # only use the first 6 characters of the mac address

    cur.execute("SELECT vendor FROM vendor WHERE vmac=\"{}\";".format(vmac))

    rows = cur.fetchall()

    try:
        vendor = rows[0][0]
    except:
        vendor = ""

    return vendor


# ======================================================================
# Load file to convert. This file should be a list of mac addresses,
# one per line
# ======================================================================
def loadFile(file, delim):
    try:
        with open(file,"r") as data_file:
            reader = csv.reader(data_file, delimiter=delim, quotechar='"')
            results = list(reader)
    except IOError:
        print("unable to open file ({})".format(MACFILE))
        sys.exit(1)

    return results


# ======================================================================
# Main
# ======================================================================
def main():
    global MACFILE
    global VendorCSV

    ARGS = parseArgs()

    # Populate databse
    genVendorDB(VendorCSV)

    # Load indata
    MAC = loadFile(MACFILE,"#")


    # Loop through indata and lookup vendor
    for m in MAC:
        macOrig = m[0]
        mac = m[0].upper().replace(" ","").replace(":","").replace(".","").replace("-","")
        vendor = macLookup(mac)

        print("{},\"{}\"".format(macOrig,vendor))


if __name__ == "__main__":
	main()

