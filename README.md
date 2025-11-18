#
#######################
##### csv2adif.py #####
#######################
Input csv file from libreoffice Calc (or other spreadsheet software)

QSO data order: Date Time_on Time_off Call Mode Frequency RST_Sent RST_Rcvd Name QTH QSL_Sent QSL_Rcvd Gridsquare QSL_Via Comment

Date format: YYYYMMDD

Time format: HHMM

Frequency: in kHz

Name and QTH: only one word (no blank)

QSL_Sent QSL_Rcvd: "Y" if QSL Sent / Received - "N" if not

Comment: words separated by blank

Enter "0" if no data in a field.

ADIF output file to be used by cqrlog software
#
This script uses maidenhead python package. Install it in an activated virtual environment with: pip install maidenhead.
#
F6HSV - November 2025
###############################################################################################################################################
