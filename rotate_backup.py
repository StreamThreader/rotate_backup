#!/usr/local/bin/python3.11

import glob
import os
import shutil
from datetime import datetime

# VERSION v2.00

# keep minimum days = 7
# keep minimum weeks = 4

KEEP_DAYS = 31
KEEP_WEEKS = 4
rotate_dir = "/home/sthreader/dev/rotate_backup/test_dir/"
log_file = rotate_dir+"logfile.log"
name_pattern = "????-??-??-v8.3-TW-ERP--??-??-"
daily_suffix = "d.dt"
weekly_suffix = "w.dt"
montly_suffix = "m.dt"
all_daily_files = []
only_daily_files = []
weekly_files = []
montly_files = []
keep_date_days = {}
how_many_weeks = 0
how_many_monts = 0
latest_week = []
start_from_scratch = 0

if not os.path.exists(rotate_dir):
    exit(1)

def logwriter(message_text):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H:%M:%S")
    with open(log_file, "a") as logfile:
        logfile.write(dt_string+" "+message_text+"\n")


logwriter("######################### [new rotate] ############################")

#################### get list #################################################

# list daily
for dt_file in glob.glob(rotate_dir+name_pattern+daily_suffix):
    all_daily_files.append(dt_file)
all_daily_files.sort(reverse=True)
all_daily_countmax=len(all_daily_files)

logwriter("daily backup files: "+str(all_daily_countmax))

# list weekly
for dt_file in glob.glob(rotate_dir+name_pattern+weekly_suffix):
    weekly_files.append(dt_file)
weekly_files.sort(reverse=True)
weekly_countmax=len(weekly_files)

logwriter("weekly backup files: "+str(weekly_countmax))

# list montly
for dt_file in glob.glob(rotate_dir+name_pattern+montly_suffix):
    montly_files.append(dt_file)
montly_files.sort(reverse=True)
montly_countmax=len(montly_files)

logwriter("montly backup files: "+str(montly_countmax))

# create list only for daily files
# exclude multiple backup per day
date_position = 0
tmp_var = [0,0,0]
for dt_file in all_daily_files:
    tmp_dateday = dt_file.split("/")[-1]
    tmp_dateday = tmp_dateday.split("-")

    # year comparsion
    if tmp_var[0] == tmp_dateday[0]:
        # month comparsion
        if tmp_var[1] == tmp_dateday[1]:
            # day comparsion
            if tmp_var[2] == tmp_dateday[2]:
                continue

    # if not duplicate, write to array
    only_daily_files.append(dt_file)

    # remember previous date
    tmp_var[0] = tmp_dateday[0]
    tmp_var[1] = tmp_dateday[1]
    tmp_var[2] = tmp_dateday[2]

    keep_date_days[date_position] = {}
    keep_date_days[date_position]["year"] = tmp_var[0]
    keep_date_days[date_position]["mont"] = tmp_var[1]
    keep_date_days[date_position]["day"] = tmp_var[2]
    date_position +=1

only_daily_countmax=len(only_daily_files)
logwriter("daily backup dates: "+str(all_daily_countmax))

#################### create weeks #############################################

if weekly_countmax:
    # search daily file from latest weekly file
    search_daily_file = weekly_files[0].replace(weekly_suffix, daily_suffix)
    tmp_index = 0
    start_from_scratch = 0

    logwriter("latest week file: "+weekly_files[0])
    logwriter("searching day file: "+search_daily_file)

    while tmp_index < only_daily_countmax:
        # if we found daily file from week
        if only_daily_files[tmp_index] == search_daily_file:
            logwriter("founded daily file: "+only_daily_files[tmp_index])
            if tmp_index > 6:
                logwriter("days count: "+str(tmp_index))
                how_many_weeks = tmp_index // 7
                logwriter("how many weeks can be created from daily files: "+\
                    str(how_many_weeks))
                # copy every 7 daily file as weeks
                # starting from latest week
                tmp_counter = tmp_index - 7
                while how_many_weeks:
                    tmp_week_dtfile = only_daily_files[tmp_counter]
                    tmp_week_cp_dtfile = tmp_week_dtfile.replace(daily_suffix,\
                        weekly_suffix)
                    os.link(tmp_week_dtfile, tmp_week_cp_dtfile)

                    # add new week to list
                    weekly_files.insert(0, tmp_week_cp_dtfile)
                    weekly_countmax=len(weekly_files)

                    logwriter("normal create weekly file: "+tmp_week_cp_dtfile)

                    if tmp_counter > 7:
                        tmp_counter -= 7
                    how_many_weeks -= 1

            # if we found, break
            break

        # otherwise continue searching
        tmp_index += 1

        # we reach end of list, and not found daily file
        # init recreate weekly file
        if tmp_index == only_daily_countmax:
            start_from_scratch = 1
            logwriter("not found daily file for latest week")

# if we not found any weekly file
# or we can not find daily file for latest week
if start_from_scratch == 1 or weekly_countmax == 0:
    if only_daily_countmax > 6:
        if start_from_scratch == 0:
            # how many weeks from daily list we can get
            how_many_weeks = only_daily_countmax // 7
            logwriter("how many weeks can be created from daily files: "+\
                str(how_many_weeks))
        else:
            # get only 1 week from latest day
            how_many_weeks = 1
            logwriter("we start from scratch, and create only 1 weekly file")

        # copy every 7 daily file as weeks
        # starting from latest daily file
        tmp_counter = 6
        while how_many_weeks:
            tmp_week_dtfile = only_daily_files[tmp_counter]
            tmp_week_cp_dtfile = tmp_week_dtfile.replace(daily_suffix,\
                weekly_suffix)
            os.link(tmp_week_dtfile, tmp_week_cp_dtfile)

            logwriter("create weekly file from last daily file: "\
                +tmp_week_cp_dtfile)

            # add new week to list
            weekly_files.append(tmp_week_cp_dtfile)
            weekly_countmax=len(weekly_files)

            tmp_counter += 7
            how_many_weeks -= 1

#################### create monts #############################################

# create monts files (from latest weeks or exist monts)
if montly_countmax:
    # if monts file exist
    # get latest month date

    # search weekly file from what created latest monts file
    search_weekly_file = montly_files[0].replace(montly_suffix, weekly_suffix)
    tmp_index = 0
    start_from_scratch = 0

    while tmp_index < weekly_countmax:
        # if we found weekly file from montly
        if weekly_files[tmp_index] == search_weekly_file:
            if tmp_index > 3:
                how_many_monts = tmp_index // 4

                # copy every 4 weekly file as monts
                # starting from latest monts
                tmp_counter = tmp_index - 4
                while how_many_monts:
                    tmp_montly_dtfile = weekly_files[tmp_counter]
                    tmp_montly_cp_dtfile = \
                        tmp_montly_dtfile.replace(weekly_suffix, \
                            montly_suffix)
                    os.link(tmp_montly_dtfile, \
                        tmp_montly_cp_dtfile)

                    logwriter("create montly file: "+tmp_montly_cp_dtfile)

                    # add new mont to list
                    montly_files.insert(0, tmp_montly_cp_dtfile)

                    if tmp_counter > 4:
                        tmp_counter -= 4
                    how_many_monts -= 1

            # if we found, break
            break

        # otherwise continue searching
        tmp_index += 1

        # we reach end of list, and not found weekly file
        # init recreate montly file
        if tmp_index == weekly_countmax:
            start_from_scratch = 1

# if we not found any monts file
# or we can not find weekly file for latest monts
if start_from_scratch == 1 or montly_countmax == 0:
    if weekly_countmax > 3:
        if start_from_scratch == 0:
            # how many monts from weekly list we can get
            how_many_monts = weekly_countmax // 4
        else:
            # get only 1 monts from latest week
            how_many_monts = 1

        # copy every 4 weekly file as monts
        # limited by how_many_monts variable
        tmp_counter = 3
        while how_many_monts:
            tmp_montly_dtfile = weekly_files[tmp_counter]
            tmp_montly_cp_dtfile = \
                tmp_montly_dtfile.replace(weekly_suffix, montly_suffix)

            os.link(tmp_montly_dtfile, tmp_montly_cp_dtfile)

            logwriter("create montly file from latest: "+tmp_montly_cp_dtfile)

            # add new mont to list
            montly_files.insert(0, tmp_montly_cp_dtfile)

            tmp_counter += 4
            how_many_monts -= 1




#################### rotate days ##############################################

# if daily files more than limit
if KEEP_DAYS < only_daily_countmax:
    limit_counter = 0

    # for each date in list, before limit
    for date_compare in range(0, len(keep_date_days)):

        # loop run not endless
        # run by count files
        for _ in all_daily_files:
            # for each daily file
            for dt_file in all_daily_files:
                # get date from daily file
                tmp_dateday = dt_file.split("/")[-1]
                tmp_dateday = tmp_dateday.split("-")

                # compare date with each date in filename
                if keep_date_days[date_compare]["year"] == tmp_dateday[0]:
                    if keep_date_days[date_compare]["mont"] == tmp_dateday[1]:
                        if keep_date_days[date_compare]["day"] == tmp_dateday[2]:
                            # if we found date for exlude
                            # remove it from array
                            all_daily_files.remove(dt_file)
                            logwriter("keep daily file: "+dt_file)

                            # break because we shift list
                            # for restart loop
                            break

        limit_counter += 1
        # if we reach limit, break from date list
        if KEEP_DAYS == limit_counter:
            break

    # loop trought remain list after exclude
    for dt_file in all_daily_files:
        os.remove(dt_file)
        logwriter("remove daily file: "+dt_file)


#################### rotate weeks #############################################

# if weekly files more than limit
if KEEP_WEEKS < weekly_countmax:
    logwriter("start delete weeks")

    tmp_counter = 0
    # exclude keep weeks
    while KEEP_WEEKS > tmp_counter:
        logwriter("keep weekly file: "+weekly_files[0])
        del weekly_files[0]
        tmp_counter += 1

    # delete over limit weeks
    for dt_file in weekly_files:
        os.remove(dt_file)
        logwriter("remove weekly file: "+dt_file)
