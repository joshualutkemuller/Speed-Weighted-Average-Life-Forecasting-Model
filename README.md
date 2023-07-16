# Speed-Weighted-Average-Life-Forecasting-Model

This model focuses on building out different weighted average life scenarios based on term, rate, and monthly speed assumptions.

The convention is using a straight-line SMM value with an adjustment for seasonality if needed.

The inputs in the model can be adjusted through the 'dataset_generator' module and opening that source code and tweaking the security, yield, speed, and term list.

SMM = Unscheduled Principal / (Start of Month Balance - Scheduled Principal)
