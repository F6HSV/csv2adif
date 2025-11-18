#!/usr/bin/python
import maidenhead as mh
#
#######################
##### csv2adif.py #####
#######################
# Input csv file from libreoffice Calc (or other spreadsheet software)
# QSO data order: Date Time_on Time_off Call Mode Frequency RST_Sent RST_Rcvd Name QTH QSL_Sent QSL_Rcvd Gridsquare QSL_Via Comment
# Date format: YYYYMMDD
# Time format: HHMM
# Frequency: in kHz
# Name and QTH: only one word (no blank)
# QSL_Sent QSL_Rcvd: "Y" if QSL Sent / Received - "N" if not
# Comment: words separated by blank
# Enter "0" if no data in a field.
# ADIF output file to be used by cqrlog software
#
# This script uses maidenhead python package. Install it in an activated virtual environment with: pip install maidenhead.
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

################
##### MAIN #####
################

# Input / output files
fileName = input("Enter the csv input file name, without extension: ")
inputFileName = fileName + '.csv'
print("csv file name: ", inputFileName)
infile = open(inputFileName, mode = "r")

outputFileName = fileName + '.adi'
print("adi file name: ", outputFileName)
outfile = open(outputFileName, mode = 'w')

# Read the csv file line by line up to the end
csvline = infile.readline()
while csvline:
  # Testing the first line of the cvs file to remove the title (if exists)
  firstline_firstdata = csvline.split()[0][0:8]
  if firstline_firstdata == 'QSO_DATE':
    csvline = infile.readline()

  # Splitting each line into data
  dataline = csvline.split()

  # Some adjustments before writing data in output file...
  # Case of blank field: Data "0" replaced by nothing
  i = 0
  while i < 15:
      if dataline[i] == '0':
          dataline[i] = ''
      i = i+1

  # Comment: concatenation of datas and deleting of few characters (, [ ] ' ")
  comment = str(dataline[14:]) # concatenation
  comment = comment.replace(',' , '')
  comment = comment.replace('[' , '')
  comment = comment.replace(']' , '')
  comment = comment.replace('\'' , '')
  comment = comment.replace('"' , '')

  # Time on and off: consideration of time between 0000 to 1000
  if str(len(dataline[1])) == '1':
    time_on = '000' + dataline[1]
  elif str(len(dataline[1])) == '2':
    time_on = '00' + dataline[1]
  elif str(len(dataline[1])) == '3':
    time_on = '0' + dataline[1]
  else :
    time_on = dataline[1]

  if str(len(dataline[2])) == '1':
    time_off = '000' + dataline[2]
  elif str(len(dataline[2])) == '2':
    time_off = '00' + dataline[2]
  elif str(len(dataline[2])) == '3':
    time_off = '0' + dataline[2]
  else :
    time_off = dataline[2]

  # Old European locator system: converted to Maidenhead locator system
  if str(len(dataline[12])) == '5':
      latitude, longitude = locator_to_coordinates(dataline[12])
      locator = mh.to_maiden(latitude, longitude, 3)
  else :
      locator = dataline[12]

  #
  # Write the data to the output file
  # See the ADIF spec on adif.org web site ...
  # Target : cqrlog software - ADIF import
  #
  outfile.write('<QSO_DATE:'    + str(len(dataline[0]))                  + '>' + dataline[0]                  + ' ' +
                '<TIME_ON:'     + str(len(time_on))                      + '>' + time_on                      + ' ' +
                '<TIME_OFF:'    + str(len(time_off))                     + '>' + time_off                     + ' ' +
                '<CALL:'        + str(len(dataline[3]))                  + '>' + dataline[3].upper()          + ' ' +
                '<MODE:'        + str(len(dataline[4]))                  + '>' + dataline[4].upper()          + ' ' +
                '<FREQ:'        + str(len(str(float(dataline[5])/1000))) + '>' + str(float(dataline[5])/1000) + ' ' +
                '<RST_SENT:'    + str(len(dataline[6]))                  + '>' + dataline[6]                  + ' ' +
                '<RST_RCVD:'    + str(len(dataline[7]))                  + '>' + dataline[7]                  + ' ' +
                '<NAME_INTL:'   + str(len(dataline[8]))                  + '>' + dataline[8]                  + ' ' +
                '<QTH_INTL:'    + str(len(dataline[9]))                  + '>' + dataline[9]                  + ' ' +
                '<QSL_SENT:'    + str(len(dataline[10]))                 + '>' + dataline[10].upper()         + ' ' +
                '<QSL_RCVD:'    + str(len(dataline[11]))                 + '>' + dataline[11].upper()         + ' ' +
                '<GRIDSQUARE:'  + str(len(locator))                      + '>' + locator.upper()              + ' ' +
                '<QSL_VIA:'     + str(len(dataline[13]))                 + '>' + dataline[13].upper()         + ' ' +
                '<COMMENT:'     + str(len(comment))                      + '>' + comment                      + ' ' +
                '<EOR>'+"\n")
  csvline = infile.readline()
#
print("write done!")
infile.close()
outfile.close()
#
