# coding: utf-8

""" validation.py: Validate stock prediction models with rolling windows.
Author: Matthew A. Tucker <matucker@gmail.com>

This script validates stock prices from a model with actual observed
stock prices via rolling window averages. It is a solution to the 2018
Insight Data Engineering Fellowshio Coding Challenge.

Usage: validation.py [-h] [--verbose]
                     actuals_file predicts_file window_file output_file

        Validate predictions of a stock model.

        positional arguments:
         actuals_file   The actual values file.
         predicts_file  The predicted values file.
         window_file    The window size file.
         output_file    The name of the output file.

        optional arguments:
         -h, --help     show this help message and exit
         --verbose      Print verbose command line output (default: off).

--verobse is intended for debugging purposes only.
"""

import time
import os
import sys
import argparse
from itertools import tee, islice, izip
import numpy as np
import pandas as pd

start_time = time.time()

#### FUNCTION DEFINITIONS ####
def nwise(iterable, N=2):
    """Get a list of all time windows in a sliding window.

    Arguments:
    iterable -- the element to form tuples over; must be iterable
    N -- size of the rolling window (default 2)

    Returns:
    A list of tuples containing each time window to be analyzed.
    """
    acc = []
    iters = tee(iterable, N)
    for i, it in enumerate(iters):
        next(islice(it, i, i), None)
    for tup in izip(*iters):
        acc.append(tup)
    return acc


def avg_window(df_actual, df_predict, win):
    """Get the average stock error for a given window.

    Arguments:
    df_actual -- the actual stock values (DataFrame)
    df_predicted -- the predicted stock values (DataFrame)
    win -- the time window (tuple of included times)

    Returns:
    A string containing the average_error or 'NA' if no matching
    time/stock pairs are found for the entire window.
    """
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
    return '%.2f' % err_mean # two significant digits


## utility function for formatting output with pipe delimiters
## INPUT: a window tuple win and an error value error
## RETURNS: A string of format 'window_start|window_end|error'
def format_result(win, error):
    """Format output using pipe delimiters.

    Arguments:
    win -- the time window (tuple of included values)
    error -- string representing average_error

    Returns:
    A string formatted start|end|avg_error.
    """
    tmp = [str(win[0]), str(win[len(win)-1]), error]
    return '|'.join(tmp)


#### FUNCTION DEFINITIONS END ####

#### COMMAND-LINE ARGUMENTS ####
parser = argparse.ArgumentParser(description='Validate predictions of\
                                 a stock model.')
parser.add_argument('actuals_file', help='The actual values file.')
parser.add_argument('predicts_file', help='The predicted values file.')
parser.add_argument('window_file', help='The window size file.')
parser.add_argument('output_file', help='The name of the output file.')
parser.add_argument('--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='Print verbose command line output (default: off).')

args=parser.parse_args()
#### COMMAND-LINE ARGUMENTS END ####

#### DIRECTORY SETUP & I/O ####
# set up the directory structure
root_dir = os.getcwd()
f_actual = os.path.join(root_dir, args.actuals_file)
f_predicted = os.path.join(root_dir, args.predicts_file)
f_window = os.path.join(root_dir, args.window_file)
f_out = os.path.join(root_dir, args.output_file)

# actually conduct the i/o
try:
    actual = pd.read_table(f_actual, sep='|', header=None,
                           skipinitialspace=True, error_bad_lines=False)
except IOError as e:
    print 'Could not read file %s.\n\
        Please ensure it exists and can be read.' % f_actual
    sys.exit(1)
except pd.errors.EmptyDataError as e:
    print 'Could not parse data from file %s.\n\
        Please ensure it follows the specification in the README.' % f_actual
    sys.exit(1)

try:
    predicted = pd.read_table(f_predicted, sep='|', header=None,
                              skipinitialspace=True, error_bad_lines=False)
except IOError as e:
    print 'Could not read file %s.\n\
        Please ensure it exists and can be read.' % f_predicted
    sys.exit(1)
except pd.errors.EmptyDataError as e:
    print 'Could not parse data from file %s.\n\
        Please ensure it follows the specification in README.md.' % f_predicted
    sys.exit(1)

try:
    window = open(f_window).readline()
    window = int(window)
except IOError as e:
    print 'Could not read file %s.\n\
        Please ensure it exists and can be read.' % f_window
    sys.exit(1)
except ValueError as e:
    print 'Window.txt must contain a single integer on line one.\n\
        Cannot parse value %s.' % window
    sys.exit(1)
#### DIRECTORY SETUP & I/O END ####

#### DATA CLEANING & VALIDATION ####
# if there are non-numeric entries in columns 1,3
# we force them to NaN to be dropped later
actual[0] = pd.to_numeric(actual[0], errors='coerce')
predicted[0] = pd.to_numeric(predicted[0], errors='coerce')
actual[2] = pd.to_numeric(actual[2], errors='coerce')
predicted[2] = pd.to_numeric(predicted[2], errors='coerce')

# we don't want leading/trailing whitespace in stock ids
actual[1] = actual[1].str.strip()
predicted[1] = predicted[1].str.strip()

# if the first line has >2 delimiters, we drop all extra columns
actual = actual[[0, 1, 2]]
predicted = predicted[[0,1,2]]

# drop rows with null values
actual = actual.dropna()
predicted = predicted.dropna()

# relabel column headers for convenience
actual.columns = ['Time', 'Stock', 'Value']
predicted.columns = ['Time', 'Stock', 'Value']

# because numpy/pandas are bad with null integers, cast back
actual['Time'] = actual['Time'].astype(np.dtype('int32'))
predicted['Time'] = predicted['Time'].astype(np.dtype('int32'))

# we assume stock ids are case-insensitive
actual['Stock'] = map(lambda x: x.upper(), actual['Stock'])
predicted['Stock'] = map(lambda x: x.upper(), predicted['Stock'])

# at this point we can drop duplicate rows
actual = actual.drop_duplicates(subset=['Time', 'Stock'])
predicted = predicted.drop_duplicates(subset=['Time', 'Stock'])
#### DATA CLEANING & VALIDATION END ####

#### TIME WINDOW SETUP ####
# calculate the times intervals needed to roll averages
t_min, t_max = actual['Time'].min(), actual['Time'].max()
t_range = range(t_min, t_max+1)

# it's not sensible to have a window larger than our entire
# observation period. In this case, we just average
# the whole data set but warn the user.
if window > len(t_range):
    print 'WARNING: Window size is bigger than observation period. \
Using window size of %s instead.' % len(t_range)
    window = len(t_range)

t_wins = nwise(t_range, N=window)

if args.verbose:
    print 'Starting to compute %s window averages from time %s to time %s.'\
        % (len(t_wins), t_min, t_max)
#### TIME WINDOW SETUP END ####

#### MAIN LOOP ####
# calculate a grand average error for all windows and write to file
try:
    with open(f_out, 'w') as out_f:
        for t_win in t_wins:
            if args.verbose:
                print 'Averaging window %s...' % str(t_win)

            avg_err = avg_window(actual, predicted, t_win)
            err_formatted = format_result(t_win, avg_err)
            out_f.write(err_formatted + '\n')
except IOError as e:
    print 'Could not write results to file %s.\n\
        Please make sure this diectory exists and can be written to.' % f_out
    sys.exit(1)
#### MAIN LOOP END ####

#### PRINT RESULTS ####
if args.verbose:
    print 'Finished computing %s window averages from time %s to time %s.'\
        % (len(t_wins), t_min, t_max)
    print 'Total time elapsed: %s seconds.' % (time.time() - start_time)
#### PRINT RESULTS END ####
