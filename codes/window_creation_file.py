import os
import datetime
import pywintypes
import win32file

def get_file_creation_time(file_path):
    file_handle = win32file.CreateFile(
        file_path,
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_ATTRIBUTE_NORMAL,
        None,
    )
    creation_time = win32file.GetFileTime(file_handle)[0]
    win32file.CloseHandle(file_handle)
    return pywintypes.Time(creation_time).AsDateTime()

input_file_name = "path_to_your_file"

creation_date_utc = get_file_creation_time(input_file_name)

print(creation_date_utc)
