from spacepy.pycdf import CDF as cdf
from pathlib import Path
import pandas as pd
import datetime
from pathlib import Path

# fn = "/home/cephadrius/Desktop/git/Lexi-BU/lexi/lexi/.lexi_data/lexi_payload_1716565227_3332_1716586535_4809_sci_output.cdf"
fn = "/home/cephadrius/Desktop/git/Lexi-BU/lexi/lexi/.lexi_data/PIT_shifted_jul08.cdf"

file_name = Path(fn).name

dat = cdf(fn)

print(dat)

# Convert the dat to a pandas dataframe
df = pd.DataFrame(index=dat["Epoch"][:])

# Add the data to the dataframe
for key in dat.keys():
    if key != "Epoch":
        df[key] = dat[key][:]
"""
# Find the time difference between the first index and the datetime 2025-03-02 08:00:00
time_diff = df.index[0] - datetime.datetime(2025, 3, 2, 8, 0, 0)

# Shift the time by the time difference
df.index = df.index - time_diff

# Set the timezones to UTC
df.index = df.index.tz_localize('UTC')

print(df.head())

# Save the dataframe to a CDF file
cdf_file = fn.replace(".cdf", "_shifted.cdf")

cdf_data = cdf.CDF(cdf_file, "")
cdf_data.attrs["title"] = file_name
cdf_data.attrs["created"] = str(pd.Timestamp.now())
cdf_data.attrs["TimeZone"] = "UTC"
cdf_data.attrs["creator"] = "Ramiz A. Qudsi"
cdf_data.attrs["source"] = fn
cdf_data.attrs["source_type"] = "csv"
cdf_data.attrs["source_format"] = "lxi"
cdf_data.attrs["source_version"] = "0.1.0"
cdf_data.attrs["source_description"] = "LXI data from the LXI data logger"
cdf_data.attrs["source_description_url"] = "something"
cdf_data.attrs["source_description_email"] = "qudsira@bu.edu"
cdf_data.attrs["source_description_institution"] = "BU"

cdf_data["Epoch"] = df.index
"""
