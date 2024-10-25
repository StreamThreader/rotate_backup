#!/usr/local/bin/python3.11

import glob
import os
import shutil
from datetime import datetime

# VERSION v2.04

KEEP_DAYS = 31
KEEP_WEEKS = 4
KEEP_MONTHS = 0
rotate_dir = "/home/sthreader/dev/rotate_backup/test_dir/"
log_file = rotate_dir+"logfile.log"
name_pattern = "????-??-??-v8.3-TW-ERP--??-??-"
daily_suffix = "d.dt"
weekly_suffix = "w.dt"
montly_suffix = "m.dt"
all_daily_files = []
daily_array = {}
weekly_array = {}
weekly_files = []
montly_files = []
montly_array = {}
first_year = 0
last_year = 0
dir_size = 0
dir_free = 0

if not os.path.exists(rotate_dir):
    print("directory not exist: "+rotate_dir)
    exit(1)

# function for writing log file
def logwriter(message_text):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H:%M:%S")
    with open(log_file, "a") as logfile:
        logfile.write(dt_string+" "+message_text+"\n")

# function for creating link to file
def make_link(src_file, dst_file):
    if src_file == "empty":
        return 0

    if dst_file == "empty":
        return 0

    if not os.path.exists(src_file):
        logwriter("file not exist: "+src_file)
        return 0

    if os.path.exists(dst_file):
        return 1
    else:
        # create hardlink
        os.link(src_file, dst_file)
        logwriter("create file: "+dst_file)
        return 1

# function for deleting file
def remove_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        logwriter("delete file: "+file_name)
    else:
        logwriter("file not exist, exit: "+file_name)
        exit(1)

# function for extending year range
def extend_year_range(from_year, to_year):
    global first_year
    global last_year
    global year_range

    if from_year < first_year:
        first_year = from_year
    elif from_year > 0:
        first_year = from_year

    if to_year > last_year:
        last_year = to_year

    # generate at least one year (not empty)
    year_range = list(range(first_year, last_year+1))


logwriter("######################### [new rotate] ############################")

logwriter("rotate dir.: "+rotate_dir)

# calculate dir size
for path, dirs, files in os.walk(rotate_dir):
    for f in files:
        fp = os.path.join(path, f)
        dir_size += os.path.getsize(fp)

logwriter("used by dir: "+str(dir_size)+" bytes")

# calculate free space
statvfs = os.statvfs(rotate_dir)
dir_free = statvfs.f_frsize * statvfs.f_blocks

logwriter("disk free..: "+str(dir_free)+" bytes")

#################### get list #################################################

# list daily
for dt_file in glob.glob(rotate_dir+name_pattern+daily_suffix):
    all_daily_files.append(dt_file)
all_daily_files.sort()
all_daily_countmax=len(all_daily_files)

logwriter("daily backup files.: "+str(all_daily_countmax))

# list weekly
for dt_file in glob.glob(rotate_dir+name_pattern+weekly_suffix):
    weekly_files.append(dt_file)
weekly_files.sort()
weekly_countmax=len(weekly_files)

logwriter("weekly backup files: "+str(weekly_countmax))

# list montly
for dt_file in glob.glob(rotate_dir+name_pattern+montly_suffix):
    montly_files.append(dt_file)
montly_files.sort()
montly_countmax=len(montly_files)

logwriter("montly backup files: "+str(montly_countmax))

# get years range
if all_daily_countmax:
    # parse first-last years from days files
    first_day_file = all_daily_files[0].split("/")[-1].split("-")
    last_day_file = all_daily_files[-1].split("/")[-1].split("-")

    first_day_file = int(first_day_file[0])
    last_day_file = int(last_day_file[0])

    extend_year_range(first_day_file, last_day_file)


#################### create weeks #############################################

# skip if daily files 0
if all_daily_countmax:
    # generate empty daily list
    for gen_year in year_range:
        gen_year = str(gen_year)
        # init new year
        daily_array.update({gen_year: []})
        for _ in range(0,12):
            # init new month
            daily_array[gen_year].append([])
            for gen_day in range(1,32):
                # init list of files by day
                daily_array[gen_year][-1].append([])
                # init empty day first file path
                daily_array[gen_year][-1][-1].append("empty")

    # fill daily list by files
    for dt_file in all_daily_files:
        dt_dateday = dt_file.split("/")[-1]
        dt_dateday = dt_dateday.split("-")

        dt_year = int(dt_dateday[0])
        dt_month = int(dt_dateday[1])
        dt_day = int(dt_dateday[2])

        # remove empty value for this day
        if daily_array[str(dt_year)][dt_month-1][dt_day-1][0] == "empty":
            daily_array[str(dt_year)][dt_month-1][dt_day-1].remove("empty")

        # append daily file path to list
        daily_array[str(dt_year)][dt_month-1][dt_day-1].append(dt_file)

    for week_year in daily_array:
        for week_month in range(0,12):
            for week_day in 1, 8, 15, 22, 29:
                # get only first file from day
                daily_file = daily_array[week_year][week_month][week_day-1][0]
                # convert dailly file name to weekly
                week_new_file = daily_file.replace(daily_suffix, weekly_suffix)

                # try create new weekly file
                if make_link(daily_file, week_new_file):
                    # add to week list
                    if not week_new_file in weekly_files:
                        weekly_files.append(week_new_file)
                        weekly_files.sort()
                        weekly_countmax=len(weekly_files)
                    continue
                else:
                    # try to search alternative daily files
                    if week_day == 1:
                        alt_week_day = 2
                    else:
                        alt_week_day = week_day-6

                    # rewind backward, and try find file
                    for alt_day in range(alt_week_day, (alt_week_day+6)):
                        daily_file = daily_array[week_year][week_month]\
                            [alt_day-1][0]
                        week_new_file = daily_file.replace(daily_suffix, 
                            weekly_suffix)

                        if daily_file == "empty":
                            continue

                        # if alternative file created, break
                        if make_link(daily_file, week_new_file):
                            # add to week list
                            if not week_new_file in weekly_files:
                                weekly_files.append(week_new_file)
                                weekly_files.sort()
                                weekly_countmax=len(weekly_files)
                            break


#################### create monts #############################################

# skip if weekly files 0
# try to extend years range
if weekly_countmax:
    # parse first-last years from weekly files
    first_weekly_file = weekly_files[0].split("/")[-1].split("-")
    last_weekly_file = weekly_files[-1].split("/")[-1].split("-")

    first_weekly_file = int(first_weekly_file[0])
    last_weekly_file = int(last_weekly_file[0])

    extend_year_range(first_weekly_file, last_weekly_file)

    # generate empty weekly list
    for gen_year in year_range:
        gen_year = str(gen_year)
        # init new year
        weekly_array.update({gen_year: []})
        for _ in range(0,12):
            # init list of files by weeks
            weekly_array[gen_year].append([])

    # fill weekly list by files
    for dt_file in weekly_files:
        dt_dateday = dt_file.split("/")[-1]
        dt_dateday = dt_dateday.split("-")

        dt_year = int(dt_dateday[0])
        dt_month = int(dt_dateday[1])
        dt_day = int(dt_dateday[2])

        # append weekly file path to list
        weekly_array[str(dt_year)][dt_month-1].append(dt_file)

    # create month file
    for month_year in weekly_array:
        for month_month in range(0,12):
            for weekly_file in weekly_array[month_year][month_month]:
                if weekly_file == "":
                    continue

                # convert weekly file name to montly
                month_new_file = weekly_file.replace(weekly_suffix, \
                    montly_suffix)

                if make_link(weekly_file, month_new_file):
                    # add to month list
                    if not month_new_file in montly_files:
                        montly_files.append(month_new_file)
                        montly_files.sort()
                        montly_countmax=len(montly_files)
                    break

# skip if montly files 0
# extend years range from montly files
if montly_countmax:
    # parse first-last years from montly files
    first_montly_file = montly_files[0].split("/")[-1].split("-")
    last_montly_file = montly_files[-1].split("/")[-1].split("-")

    first_montly_file = int(first_montly_file[0])
    last_montly_file = int(last_montly_file[0])

    extend_year_range(first_montly_file, last_montly_file)

    # generate empty montly list
    for gen_year in year_range:
        gen_year = str(gen_year)
        # init new year
        montly_array.update({gen_year: []})
        for _ in range(0,12):
            # init list of files by weeks
            montly_array[gen_year].append([])

    # fill montly list by files
    for dt_file in montly_files:
        dt_dateday = dt_file.split("/")[-1]
        dt_dateday = dt_dateday.split("-")

        dt_year = dt_dateday[0]
        dt_month = int(dt_dateday[1])
        dt_day = int(dt_dateday[2])

        # append montly file path to list
        montly_array[dt_year][dt_month-1].append(dt_file)

#################### rotate days ##############################################

# if KEEP_DAYS set to 0, skip deletion
# skip if daily files 0
if KEEP_DAYS and all_daily_countmax:
    keep_cntr = KEEP_DAYS

    # exclude from list preserved days
    for rev_year in reversed(daily_array):
        for rev_month in reversed(range(0, 12)):
            for rev_day in reversed(range(0, 31)):
                # stop loop if reach KEEP_DAYS end
                if not keep_cntr:
                    break

                ret_val = 0
                # loop through each file for day
                day_file_pointer = 0
                for day_file in daily_array[rev_year][rev_month][rev_day]:
                    if not day_file == "empty":
                        # exclude from array (prevent deleting)
                        daily_array[str(rev_year)][rev_month][rev_day]\
                            [day_file_pointer] = "empty"
                        ret_val = 1
                    day_file_pointer += 1

                # if current day have at least one file
                if ret_val:
                    keep_cntr -= 1

    # delete files from resulted list
    for day_year in daily_array:
        for day_month in range(0, 12):
            for day_day in range(0, 31):
                for day_file in daily_array[day_year][day_month][day_day]:
                    if not day_file == "empty":
                        remove_file(day_file)


#################### rotate weeks #############################################

# if KEEP_WEEKS set to 0, skip deletion
# skip if weekly files 0
if KEEP_WEEKS and weekly_countmax:
    keep_cntr = KEEP_WEEKS

    # exclude from list preserved weeks
    for rev_year in reversed(weekly_array):
        for rev_month in reversed(range(0, 12)):
            # loop through each weekly file
            for week_file in reversed(weekly_array[rev_year][rev_month]):
                # stop loop if reach KEEP_WEEKS end
                if not keep_cntr:
                    break

                # exclude from array (prevent deleting)
                weekly_array[rev_year][rev_month].remove(week_file)
                keep_cntr -= 1

    # delete files from resulted list
    for week_year in weekly_array:
        for week_month in range(0, 12):
            for week_file in weekly_array[week_year][week_month]:
                remove_file(week_file)


#################### rotate months ############################################

# if KEEP_MONTHS set to 0, skip deletion
# skip if montly files 0
if KEEP_MONTHS and montly_countmax:
    keep_cntr = KEEP_MONTHS

    # exclude from list preserved months
    for rev_year in reversed(montly_array):
        for rev_month in reversed(range(0, 12)):
            # stop excluding month if reach KEEP_MONTHS
            if not keep_cntr:
                break

            ret_val = 0
            # if month contain at least one file, exclude this month
            for _ in montly_array[rev_year][rev_month]:
                # exclude from array (prevent deleting)
                montly_array[rev_year][rev_month] = ""
                ret_val = 1
                break

            # if current month have at least one file
            if ret_val:
                keep_cntr -= 1

    # delete files from resulted list
    for montly_year in montly_array:
        for month_month in range(0, 12):
            for month_file in montly_array[montly_year][month_month]:
                remove_file(month_file)
