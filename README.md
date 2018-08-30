# Program Description

This repository contains a solution to the [Fall 2018 Insight Data Engineering Coding Challenge](https://github.com/InsightDataScience/prediction-validation) written in python 2.7. The program compares stock values predicted by a provided model to actual stock values observed over the same time frame and calcuates the average error over a specified sliding time window. The error for a given stock's prediction is defined as: `error = | actual_value - predicted_value |` and the program finds the mean of the error for a given time window.

Given an input file with stock values for a time interval `(1, ..., t)` and a window size `x`, this program finds the average error for all the windows formed by sliding a window of size `x` starting from `1` to `t-x`, with all intervals inclusive (thus, `(1, 2, 3, 4)` with a window size of four includes both `1` and `4`.)

The program does this, essentially, by constructing `DataFrame` objects from the [pandas](https://pandas.pydata.org/) package for both the actual and predicted value input files. These two frames are then subject a full outer join/merge to pair predicted (time, stock) pairs with actual (time, stock) pairs. The individual colums are then subtracted an an average taken. The program only assesses predictions for times at which there are actual values recorded; it does not validate predictions for times at which there are no actual recorded values to validate against.

# Usage

For directory structures that match the Insight challenge prompt requirements, the program can be run by executing `run.sh` in the root directory. For non-trivial directory setups, `src/validation.py` can be called directly with the following usage:

```
usage: validation.py [-h] [--verbose]
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
```

where `verbose` prints several landmark messages as well as the total running time of the script. `run.sh` does not ever set `--verbose`, as this flag is intended for debugging purposes only.

## Input

The input must contain contain three files, all stored in `input/`. The program will exit with status 1 if none of the following files exist:

* `actual.txt`: the actual observed stock values
* `predicted.txt`: the model-predicted stock values
* `window.txt`: the size of the sliding window

### `actual.txt` & `predicted.txt`

`actual.txt` and `predicted.txt` are, as per the instructions, assumed to be pipe-delimited text files where each line contains one stock value in the format:

```
time|stock_name|stock_value
```

Where `time` is assumed to be an integer greater than 0. Per the directions, the script assumes these files are sorted by `time`, though nothing in the running of the script should require this to be the case. Missing values for the `time`, `stock_name` or `stock_value` in either `actual.txt` or `predicted.txt` will result that observation being discarded prior to averaging. Entries for the `time` and `stock_value` fields are treated as missing and discarded if they are not integers or floats, respectively. Numeric values are explictly cast. Whitespace on either side of a `stock_name` is discarded; whitespace internal to a `stock_id` will be treated as distinctive, and so `AAPL` and `AA PL` are distinct values for `stock_id`, but `AAPL` and ` AAPL ` are not.

Additionally, a remark about the time domain of analysis is in order: The time window over which the rolling average is constructed is defined by the range of times seen in `actual.txt`, *not* `predicted.txt`. Since this is a model validation tool, we do not consider cases where predictions have been made for times at which we do not have actual data to validate against. Thus, times at the edges of time ranges in `predicted.txt` will not appear in the result file if they are not in the range constructed using `actual.txt`.

### `window.txt`

`window.txt` is assumed to be a single integer greater than 0 on the first line of the file. The program only looks at the first line of `window.txt`, so all subsequent lines are ignored and the window size on the first line is used. The program exits with status 1 if the first line of `window.txt` does not contain something which can be parsed as an integer. If the window size is larger than the entire observation period, a single average error is computed for the entire observation period.

## Output

The output is a file, `output/comparison.txt` which contains one line for each sliding time window, all of the form:

```
start_time|end_time|average_error
```


Where `start_time` is the minimum value and `end_time` the maximum value for the times contained in the window. `average_error` is computed by column after dropping missing values. If there are no matching stocks for an entire time window, `average_error` is reported as `NA`. If this file cannot be written to, the program will exit with status 1.

# Dependencies

This analysis tool has two dependencies, both of which are standard packages for Python scientific computing. In each case, the version of the package present on the test system is noted in parentheses. This tool was developed in Python 2.7 in a vanilla Anaconda installation.

* [NumPy](http://www.numpy.org/) (`1.15.0`)
* [Pandas](https://pandas.pydata.org/) (`0.23.4`)

# Unit Tests

This repository also includes all the unit tests used to prepare this submission. These tests are all contained in the `insight_testsuite/tests/` directory. This section describes each test's purpose as well as any commentary on the script's performance on the test.

* `test_0`: A test consisting of the example data from the Insight-provided README.
* `test_1`: Insight's included test of a larger sample size.
    * The system used to test this code produced the rounding discrepencies addressed by email. `comparison.txt` was edited in this test to reflect the rounding values obtained on that system.
* `test_2`: A test of proper handling of windows with no matching stock (output should be `NA`).
* `test_3`: A test of missing values in `actual.txt`
* `test_4`: A test of a window size of `1`
* `test_5`: A test of a window size which covers the entire interval in actual.txt.
* `test_6`: A test of stock ids that do not match in case.
* `test_7`: A test of null/missing values in the input files.
* `test_8`: A test where `actual.txt` has fewer times than `predicted.txt`.
* `test_9`: A test where `predicted.txt` has fewer times than `actual.txt`. 
* `test_10`: A test of stock names with unicode characters.
* `test_11`: A test of non-numeric stock values and times.
* `test_12`: A test of window sizes larger than the observation period.
* `test_13`: A test of whitespace in the input files.
* `test_14`: A test where input files are sorted by stock_id (but still in chronological order).
* `test_15`: A test where the input contains lines with only whitespace.
