# Project: SCE Cleaner
#
# Goal: Input SCE CSV output, Output cleaned up CSV that's eaiser to analyze
#
##################################################
#
# REQUIREMENTS
#
# [x] Import CSV
# [-] Retreive Metadata
# [x] Find all data rows, parse their time stamps
# [x] Assign a rate to each row
# [x] Export CSV with all meta data in each row
#
##################################################
#
#  Export
#
# | Date | Start Time | End Time | kWh | Running kWh | Rate (Peak) | Rate (Tiered)
#
##################################################
#
# TODO
#
# [ ] Support any year (currently supports 2020 and 2021
# [ ] Convert to dataframe
# [ ] Run basic viz
# [ ] Configurable Rates/Plans
# [ ] Add simple rate and tiered cost (kWh * rate)
# [x] Figure out how to build in tiered pricing
# [ ] Host on website with Django or something
# [ ] Design FE plan input, basic viz output, and cleaned up CSV output
# [ ] Publish!
#
##################################################


import csv
from datetime import time


# Create Clean List

clean = [["Date", "Start Time", "End Time", "kWh", "Rate (Peak)", "Running kWh", "Rate (Tiered)"]]


# Found this online to get a CSV in here.


## Start Time	End Time	Rate
## 12:00 AM	8:00 AM         $0.27
## 8:00 AM	4:00 PM         $0.25
## 4:00 PM	9:00 PM         $0.36
## 9:00 PM	12:00 AM	$0.27

def get_peak_rate(ti):
    t = time.fromisoformat(ti)
    if t.hour >= 0 and t.hour < 8:
        return 0.27
    elif t.hour >= 8 and t.hour < 16:
        return 0.25
    elif t.hour >= 16 and t.hour < 21:
        return 0.36
    else:
        return 0.27

def get_tiered_rate(kwh, runningKwh):
    ## this can probably be handled better. Could even be adapted to work with n tiers.
    tier1Allocation = 14.4
    tier1Dollars    = 0.22
    tier2Allocation = tier1Allocation * 4
    tier2Dollars    = 0.28
    tier3Dollars    = 0.35

    yesterdayKwh = runningKwh - kwh # this produces yesterday's running total

    if runningKwh <= tier1Allocation:
        return tier1Dollars
    elif runningKwh > tier1Allocation and runningKwh <= tier2Allocation:
        # We can runningKwh - kwh to find the previous total. If prevTotal > 14.4, then we can safely charge at pure 0.28.
        if yesterdayKwh > tier1Allocation:
            return tier2Dollars
        # If it's part Tier 1/2.
        else:
            t1kwh = tier1Allocation - yesterdayKwh
            t2kwh = kwh - t1kwh
            return ((t1kwh / kwh) * tier1Dollars) + ((t2kwh / kwh) * tier2Dollars)

    else:
        # It's all Tier 3
        if yesterdayKwh > tier2Allocation:
            return tier3Dollars
        # It's Part Tier 2/Tier 3
        elif yesterdayKwh < tier2Allocation and yesterdayKwh > tier1Allocation:
            t2kwh = tier2Allocation - yesterdayKwh
            t3kwh = kwh - t2kwh
            return ((t2kwh / kwh) * tier2Dollars) + ((t3kwh / kwh) * tier3Dollars)
        # It's Part Tier 1/Tier2/Tier 3
        else:
            t1kwh = tier1Allocation - yesterdayKwh
            t2kwh = tier2Allocation - tier1Allocation
            t3kwh = kwh - tier2Allocation
            return ((t1kwh / kwh) * tier1Dollars) + ((t2kwh / kwh) * tier2Dollars) + ((t3kwh / kwh) * tier3Dollars)



f = open('data.csv')
csv_f = csv.reader(f)

thisDate = ""
dailyRunningKwh = 0.00

for row in csv_f:

    if not row:
        continue
    else:              
        if(row[0].startswith("2020") or row[0].startswith("2021")):
            # Does not handle other years

            temp = (row[0].split())    # Separate out the date/time and puts it in Temp
            del temp[2:4]              # Deletes what we don't need
            temp.append(row[1])        # Appends the kWh to Temp
            temp.append(get_peak_rate(temp[1])) # Sends time to the Peak function and gets a rate

            # Calculate the daily running total based on the date (temp[0])
            if thisDate == "":
                thisDate = temp[0]
                dailyRunningKwh = float(temp[3])
            elif thisDate == temp[0]:
                dailyRunningKwh += float(temp[3])
            else:
                dailyRunningKwh = float(temp[3])
                thisDate = temp[0]

            temp.append(round(dailyRunningKwh, 3))
            temp.append(round(get_tiered_rate(float(temp[3]),temp[5]),3))           
            clean.append(temp)
            
def csv_printer(li):
    for row in li:
         print(row)


# csv_printer(clean)

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(clean)

