# Program Description

This program compares stock values predicted by a provided model to actual stock values observed over the same time frame and calcuates the average error over a specified sliding time window. The error for a given stock's prediction is defined as: `error = | actual_value - predicted_value|` and the program finds the mean of the error for a given time window.

Given an input file with stock values for a time interval `(1, ..., n)` and a window size `x`, this program finds the average error for all the windows formed by sliding a window of size `x` from `1` to `n-x`, with all intervals inclusive (thus, `(1, 2, 3, 4)` with a window size of four includes both `1` and `4`.)

# Usage

For directory structures that match the Insight challenge prompt requirements, the program can be run by executing `run.sh` in the root directory. For non-trivial directory setups, `src/validation.py` can be called directly:

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

where `verbose` prints several landmark messages as well as the total running time of the script.

## Input

The input should contain three files, all stored in `input/`:

* `actual.txt`: the actual observed stock values
* `predicted.txt`: the model-predicted stock values
* `window.txt`: the size of the sliding window

`actual.txt` and `predicted.txt` are, as per the instructions, assumed to be pipe-delimited text files where each line contains one stock value in the format:

```
time|stock_name|stock_value
```

`window.txt` is assumed to be a single integer on the first line of the file.

**Note:** The program assumes that stock ids are case-insensitive and it will therefore treat ids such as `AAPL` and `aapl` as identical.

## Output

The output is a file, `output/comparison.txt` which contains one line for each sliding time window, all of the form:

```
start_time|end_time|average_error
```

If there are no matching stocks for an entire time window, `average_error` is reported as `NA`.

# Dependencies

This analysis tool has a handful of dependencies, all of which are standard packages for Python scientific computing. In each case, the version of the package present on the test system is noted in parentheses. This tool was developed in Python 2.7 in a vanilla Anaconda installation.

* **NumPy** (`1.15.0`)
* **Pandas** (`0.23.4`)

# Unit Tests

This repository also includes all the unit tests used to prepare this submission. These tests are all contained in the `insight_testsuite/tests/` directory. This section describes each test's purpose as well as any commentary on the script's performance on the test.

* `test_0`: A test consisting of the example data from the Insight-provided README.
* `test_1`: Insight's included test of a larger sample size.
    * The system used to test this code produced the rounding discrepencies addressed by email. `comparison.txt` was edited in this test to reflect the rounding values obtained on that system.
* `test_2`: A test of proper handling of windows with no matching stock (output should be `NA`).
* `test_3`: A test of missing values in `actual.txt`
    * It's not clear what the use-case is here, but it's a possible corner case so I cover it.
* `test_4`: A test of a window size of `1`
* `test_5`: A test of a window size which covers the entire interval in actual.txt.
* `test_6`: A test of stock ids that do not match in case.


# Miscellaneous Notes