# Calibration Test Cases and Expected Results

These are external validation procedures. The app does not expose calibration controls or create a calibration mass. Record actual measurements during verification; the expected values and tolerances below are the acceptance criteria.

## Free-Fall Calibration

Release a test mass from rest 10 ft above the ground plane. Record the elapsed time at ground contact. Expected time is calculated from `t = sqrt(2h/g)`, with `h = 10 ft`. Pass when the measured time is within ±1% of the expected value.

| Case | Gravity mode | Acceleration (ft/s²) | Expected time (s) | Acceptable range (s) | Actual time (s) | Result |
| --- | --- | ---: | ---: | ---: | --- | --- |
| FF-01 | Earth | 32.2 | 0.78811 | 0.78023–0.79599 | Record during verification | Pending |
| FF-02 | Mars | 12.21 | 1.2798 | 1.26700–1.29260 | Record during verification | Pending |
| FF-03 | Moon | 5.33 | 1.9371 | 1.91773–1.95647 | Record during verification | Pending |

## Shake-Table Calibration

Measure 10 complete cycles. Compare measured cycle duration and extreme displacement with the configured frequency and amplitude. Pass each measurement when it is within ±1% of its expected value.

| Case | Amplitude (in) | Frequency (Hz) | Expected period (s) | Expected duration, 10 cycles (s) | Expected extreme displacement (in) | Actual measurements | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| ST-01 (default) | 4 | 3 | 0.3333 | 3.3333 | 4 | Record during verification | Pending |
| ST-02 (minimum frequency) | 6 | 0.1 | 10 | 100 | 6 | Record during verification | Pending |
| ST-03 (maximum frequency) | 6 | 10 | 0.1 | 1 | 6 | Record during verification | Pending |
| ST-04 (zero amplitude) | 0 | 5 | 0.2 | 2 | 0 | Record during verification | Pending |
| ST-05 (maximum amplitude) | 12 | 5 | 0.2 | 2 | 12 | Record during verification | Pending |

The default case's expected peak horizontal acceleration is `Aω² = (4/12) ft × (2π × 3 Hz)² = 118.44 ft/s²`, or approximately 3.68 standard g using `1 g = 32.2 ft/s²`. Peak shaking acceleration in standard g is the same in Earth, Mars, and Moon modes; the selected gravity mode changes only vertical gravitational acceleration and weight. Cycle period and displacement do not change with gravity mode.

## Result Record

For each run, record the case ID, configured inputs, expected result, actual measurement, percentage error, tolerance, gravity mode where applicable, and pass/fail result. Percentage error is `abs(actual - expected) / expected × 100%`. A result passes at 1.00% error or less.
