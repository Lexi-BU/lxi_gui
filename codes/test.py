import pandas as pd
import numpy as np
start_time = "2025-03-04 15:50:00"
# Convert to datetime with utc timezone
start_time = pd.to_datetime(start_time)
start_time = start_time.tz_localize('UTC')


# Select only thos evalues in the dataframe that are after the start time
df_hki = df_hki[df_hki['timestamp'] > start_time]