#!/usr/bin/python
import maidenhead as mh
import csv
#
#######################
##### csv2adif.py #####
#######################
# Input csv file from libreoffice Calc (or other spreadsheet software)
# QSO data fields: DATE TIME_ON TIME_OFF CALL MODE FREQ RST_SENT RST_RCVD NAME QTH QSL_SENT QSL_RCVD GRIDSQUARE QSL_VIA COMMENT
# Date format: YYYYMMDD
# Time format: HHMM
# Frequency: in kHz
# Name and QTH: only one word (no blank)
# QSL_Sent QSL_Rcvd: "Y" if QSL Sent / Received - "N" if not
# Comment: words separated by blank
# Enter "0" if no data in a field.
# ADIF output file to be used by cqrlog software
#
# This script uses maidenhead python package. Install it in an activated virtual environment with: pip install -r requirements.txt.
#
# F6HSV - November 2025
###############################################################################################################################################

# Converts a 5-character QTH locator to geographic coordinates (latitude, longitude).
# Param locator: 5-character QTH Locator code (e.g. BK58b)
# Return: (latitude, longitude) in decimal degrees
def locator_to_coordinates(locator):

    # Format verification
    if len(locator) != 5:
        raise ValueError("The locator must be 5 characters long.")

    # The letters are mapped from A=0 to Z=25
    def letter_to_number(letter):
        return ord(letter.upper()) - ord('A')

    # Extracting components from the locator
    letter1 = locator[0]        # First letter: from A to Z - Longitude - Large tile - Width 2 degrees
    letter2 = locator[1]        # Second letter: from A to Z - Latitude - Large tile - Height 1 degrees
    number1 = int(locator[2])   # First digit: from 0 to 7 - Latitude - Small square - Height 7 minutes 30 seconds
    number2 = int(locator[3])   # Second digit: from 1 to 9 then 0 - Longitude - Small square - Width 12 minutes
    letter3 = locator[4]        # Fifth character (letter): from a to j (except i) - subdivision - width 4 minutes, height 2 minutes and 30 seconds

    # 1. Define the base coordinates (the 2 degrees x 1 degrees large tile)
    # Each letter is converted into a number between 0 and 25 (A=0, Z=25)
    # Result in degrees
    # Base latitude (starting from 40 degrees North for large tile xA)
    base_lat = 40 + letter_to_number(letter2)

    # Base longitude (starting from 0 degree East for the square Ay)
    if letter_to_number(letter1) < 19: # letter from A to T - East longitude
        base_lon = letter_to_number(letter1) * 2
    else: # letter from U to Z - West longitude
        base_lon = (letter_to_number('Z') - letter_to_number(letter1) + 1) * (-2)
    #print ("base_lat :", base_lat)
    #print ("base_lon :", base_lon)

    # 2. Calculation of small squares
    # The large tile is divided into 80 small squares. We calculate the subcoordinates.
    # Latitude (in minutes of angle)
    ssq_lat = 60 - (7.5 * (number1 + 1))

    # Longitude (in minutes of angle)
    if number2 != 0:
        ssq_lon = (number2 - 1) * 12
    else:
        ssq_lon = 108
    #print ("ssq_lat :", ssq_lat)
    #print ("ssq_lon :", ssq_lon)

    # 3. Consideration of the subdivision letter in minutes of angle
    # The values correspond to the center of the subdivision
    if letter3.upper() == 'A':
        sub_lat = 6.25
        sub_lon = 6
    elif letter3.upper() == 'B':
        sub_lat = 6.25
        sub_lon = 10
    elif letter3.upper() == 'C':
        sub_lat = 3.75
        sub_lon = 10
    elif letter3.upper() == 'D':
        sub_lat = 1.25
        sub_lon = 10
    elif letter3.upper() == 'E':
        sub_lat = 1.25
        sub_lon = 6
    elif letter3.upper() == 'F':
        sub_lat = 1.25
        sub_lon = 2
    elif letter3.upper() == 'G':
        sub_lat = 3.75
        sub_lon = 2
    elif letter3.upper() == 'H':
        sub_lat = 6.25
        sub_lon = 2
    elif letter3.upper() == 'J':
        sub_lat = 3.75
        sub_lon = 6
    else:
        sub_lat = 0
        sub_lon = 0
    #print ("sub_lat :", sub_lat)
    #print ("sub_lon :", sub_lon)

    # 4. Final calculation of coordinates (latitude and longitude)
    lat = base_lat + (ssq_lat / 60.0) + (sub_lat / 60.0)  # Final Latitude
    lon = base_lon + (ssq_lon / 60.0) + (sub_lon / 60.0)  # Final Longitude

    return lat, lon

#
# Write the data to the output file
# Parameters:
# qso: dictionary from csv.DictReader
# f: adif file handle
#
# Frequency converted in MHz
# Name and QTH encoded with UTF-8 characters
#
def WriteToAdifFile(qso, f):
    for key, value in qso.items():
        if key == 'FREQ':
            f.write('<' + key + ':' + str(len(str(float(value)/1000))) + '>' + str(float(value)/1000) + ' ')
        elif key == 'NAME' or key == 'QTH':
            f.write('<' + key + '_INTL:' + str(len(value)) + '>' + value + ' ')
        elif key == 'COMMENT':
            f.write('<' + key + ':' + str(len(value)) + '>' + value + ' ')
        else:
            f.write('<' + key + ':' + str(len(value)) + '>' + value.upper() + ' ')
    f.write('<EOR>' + "\n")
    return

################
##### MAIN #####
################

# Input / output files
fileName = input("Enter the csv input file name, without extension: ")
CsvFileName = fileName + '.csv'
print("csv file name: ", CsvFileName)

AdifFileName = fileName + '.adi'
print("ADIF file name: ", AdifFileName)
adiffile = open(AdifFileName, mode = 'w')

with open(CsvFileName, "r", encoding="utf-8") as csvfile:
    csv_dict = csv.DictReader(csvfile, delimiter = " ")

    for qso in csv_dict:
        # Some adjustments before writing data in output file...
        # Case of blank field: Data "0" replaced by nothing
        for key, value in qso.items():
            if value == "0":
                qso[key] = ''

        # Time on and off: consideration of time between 0000 to 1000
        qso['TIME_ON'] = qso['TIME_ON'].zfill(4)
        qso['TIME_OFF'] = qso['TIME_OFF'].zfill(4)

        # Old European locator system: converted to Maidenhead locator system
        if len(qso['GRIDSQUARE']) == 5:
            latitude, longitude = locator_to_coordinates(qso['GRIDSQUARE'])
            qso['GRIDSQUARE'] = mh.to_maiden(latitude, longitude, 3)

        #
        # Write the data to the output file
        # See the ADIF spec on adif.org web site ...
        # Target : cqrlog software - ADIF import
        #
        WriteToAdifFile(qso, adiffile)
        #
    print("Write done!")
    adiffile.close()
    #
