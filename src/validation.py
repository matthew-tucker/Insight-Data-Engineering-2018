# coding: utf-8

## TODO: Unicode input?
## TODO: Graceful handling of read_table errors
## TODO: README
## TODO: Code headers
## TODO: Unit Tests
## TODO: Python style
## TODO: Bad datatypes in input
## TODO: handle file i/o errors
## TODO: run.sh
## TODO: Comment code
## TODO: window.txt doesn't contain an integer

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
        return "%.2f" % err_mean # two significant digits


## utility function for formatting output with pipe delimiters
## INPUT: a window tuple win and an error value error
## RETURNS: A string of format "window_start|window_end|error"
def format_result(win, error):
    tmp = [str(win[0]), str(win[len(win)-1]), error]
    return '|'.join(tmp)
#### FUNCTION DEFINITIONS END ####

#### COMMAND-LINE ARGUMENTS ####
argparser = argparse.ArgumentParser(description='Validate predictions of a stock model.')
argparser.add_argument('actuals_file', help='The actual values file.')
argparser.add_argument('predicts_file', help='The predicted values file.')
argparser.add_argument('window_file', help='The window size file.')
argparser.add_argument('output_file', help='The name of the output file.')
argparser.add_argument('--verbose', dest='verbose', action='store_const', const=True, default=False,
                        help='Print verbose command line output (default: off).')

args=argparser.parse_args()
#### COMMAND-LINE ARGUMENTS END ####

#### DIRECTORY SETUP & I/O ####

# set up the directory structure
root_dir = os.getcwd()

# get file locations and load
f_actual = os.path.join(root_dir, args.actuals_file)
f_predicted = os.path.join(root_dir, args.predicts_file)
f_window = os.path.join(root_dir, args.window_file)
f_out = os.path.join(root_dir, args.output_file)

actual = pd.read_table(f_actual, sep='|', header=None)
predicted = pd.read_table(f_predicted, sep='|', header=None)
window = int(open(f_window).readline())
#### DIRECTORY SETUP & I/O END ####

#### DATA CLEANING & VALIDATION ####
# drop rows with null values
actual = actual.dropna()
predicted = predicted.dropna()



# relabel column headers for convenience
actual.columns = ['Time', 'Stock', 'Value']
predicted.columns = ['Time', 'Stock', 'Value']

# we assume stock ids are case-insensitive
actual['Stock'] = map(lambda x: x.upper(), actual['Stock'])
predicted['Stock'] = map(lambda x: x.upper(), predicted['Stock'])
#### DATA CLEANING & VALIDATION END ####

#### TIME WINDOW SETUP ####
# calculate the times intervals needed to roll averages
# TODO: What if the time intervals aren't the same in both files?
t_min, t_max = int(actual['Time'].min()), int(actual['Time'].max())
t_wins = nwise(range(t_min, t_max+1), n=window)

if args.verbose:
    print "Starting to compute %s window averages from time %s to time %s." % (len(t_wins), t_min, t_max)
#### TIME WINDOW SETUP END ####

#### MAIN LOOP ####
# calculate a grand average error for all windows and write to file
with open(f_out, 'w') as out_f:
    for t_win in t_wins:
        if args.verbose:
            print "Averaging window %s..." % str(t_win)
    
        avg_err = avg_window(actual, predicted, t_win)
        err_formatted = format_result(t_win, avg_err)
        out_f.write(err_formatted + '\n')
        
#### MAIN LOOP END ####

#### PRINT RESULTS ####
if args.verbose:
    print "Finished computing %s window averages from time %s to time %s." % (len(t_wins), t_min, t_max)
    print "Total time elapsed: %s seconds." % (time.time() - start_time)
#### PRINT RESULTS END ####