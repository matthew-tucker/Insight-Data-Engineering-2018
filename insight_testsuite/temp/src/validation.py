
# coding: utf-8

## TODO: Unicode input?
## TODO: Graceful handling of read_table errors
## TODO: Case-insensitive support?
## TODO: Command line options
## TODO: README
## TODO: Check File Structure
## TODO: Code headers
## TODO: Unit Tests
## TODO: Python style
## TODO: Better directory handling
## TODO: run.sh
## TODO: make sure times are ordered in the output file? (they may be already)
## TODO: Comment code
## TODO: window.txt doesn't contain an integer
## TODO: timing/general output -- take it out?

import time
start_time = time.time()

import numpy as np
import pandas as pd
import os
import argparse
from itertools import tee, islice, izip

#### FUNCTION DEFINITIONS ####

## get a list of all time windows in a sliding window of size n
## INPUT: a range of integers and a window size, n
## RETURNS: a list of tuples of size n formed by rolling a window of size n over iterable
def nwise(iterable, n=2):
    acc = []
    iters = tee(iterable, n)                                                     
    for i, it in enumerate(iters):                                               
        next(islice(it, i, i), None)
    for tup in izip(*iters):
        acc.append(tup)
    return acc


## get the average stock error for a given window
## INPUT: a dataframe of actual & predicted values as well as a time window tuple
## RETURNS: an average of the error for all stocks in that window, rounded to 2 digits
def avg_window(df_actual, df_predict, win):
    # subset the data by time window
    actuals_in_win = df_actual.loc[df_actual['Time'].isin(win)]
    predicts_in_win = df_predict.loc[df_predict['Time'].isin(win)]
    
    # a full outer join gets us NaN for missing values on either side
    joined_wins = actuals_in_win.merge(right=predicts_in_win, 
                                   how='outer', on=['Time', 'Stock'])
                                   
    # compute the average error and return
    joined_wins['Error'] = abs(joined_wins['Value_x'] - joined_wins['Value_y'])
    err_mean = round(joined_wins['Error'].mean(), 2)
    
    # if there are no matching stocks in a window, return NA
    if np.isnan(err_mean):
        return 'NA'
    else:
        return "%.2f" % err_mean


## utility function for formatting output with pipe delimiters
## INPUT: a window tuple win and an error value error
## RETURNS: A string of format "window_start|window_end|error"
def format_result(win, error):
    tmp = [str(win[0]), str(win[len(win)-1]), error]
    return '|'.join(tmp)


#### FUNCTION DEFINITIONS END ####

#### DIRECTORY SETUP & I/O ####

# set up the directory structure
root_dir = os.getcwd()
data_dir = os.path.join(root_dir, 'input')
out_dir = os.path.join(root_dir, 'output')

# get file locations and load
f_actual = os.path.join(data_dir, 'actual.txt')
f_predicted = os.path.join(data_dir, 'predicted.txt')
f_window = os.path.join(data_dir, 'window.txt')
f_out = os.path.join(out_dir, 'comparison.txt')

actual = pd.read_table(f_actual, sep='|', header=None)
predicted = pd.read_table(f_predicted, sep='|', header=None)
window = int(open(f_window).readline())
#### DIRECTORY SETUP & I/O END ####

#### TIME WINDOW SETUP ####
# relabel column headers for convenience
actual.columns = ['Time', 'Stock', 'Value']
predicted.columns = ['Time', 'Stock', 'Value']

# calculate the times intervals needed to roll averages
# TODO: What if the time intervals aren't the same in both files?
t_min, t_max = actual['Time'].min(), actual['Time'].max()
t_wins = nwise(range(t_min, t_max+1), n=window)

#### TIME WINDOW SETUP END ####

#### MAIN LOOP ####
# calculate a grand average error for all windows and write to file
with open(f_out, 'w') as out_f:
    for t_win in t_wins:
        print "Computing frame %s..." % str(t_win)
        avg_err = avg_window(actual, predicted, t_win)
        err_formatted = format_result(t_win, avg_err)
        out_f.write(err_formatted + '\n')
        
#### MAIN LOOP END ####

#### PRINT RESULTS ####
print "Finished computing %s window averages from time %s to time %s." % (len(t_wins), t_min, t_max)
print "Total time elapsed: %s seconds." % (time.time() - start_time)
#### PRINT RESULTS END ####