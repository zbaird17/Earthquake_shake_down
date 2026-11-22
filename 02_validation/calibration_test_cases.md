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
| ST-01 (default) | 6 | 5 | 0.2 | 2 | 6 | Record during verification | Pending |
| ST-02 (minimum frequency) | 6 | 0.1 | 10 | 100 | 6 | Record during verification | Pending |
| ST-03 (maximum frequency) | 6 | 10 | 0.1 | 1 | 6 | Record during verification | Pending |
| ST-04 (zero amplitude) | 0 | 5 | 0.2 | 2 | 0 | Record during verification | Pending |
| ST-05 (maximum amplitude) | 12 | 5 | 0.2 | 2 | 12 | Record during verification | Pending |

The default case's expected peak horizontal acceleration is `Aω² = 0.5 ft × (2π × 5 Hz)² = 493.48 ft/s²`. That is approximately 15.33 g under Earth gravity. The peak acceleration value changes with the selected gravity mode; cycle period and displacement do not.

## Result Record

For each run, record the case ID, configured inputs, expected result, actual measurement, percentage error, tolerance, gravity mode where applicable, and pass/fail result. Percentage error is `abs(actual - expected) / expected × 100%`. A result passes at 1.00% error or less.
