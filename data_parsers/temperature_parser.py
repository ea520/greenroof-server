import parse
import glob
import pickle
import linecache
import math
from SQL_app.models import Temperature
import re
import datetime

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
parsed_temps_file = os.path.join(dir_path, "parsed_temps.pickle")

@parse.with_pattern(r"\s*[0-9a-f]{2}-[0-9a-f]{12}\s*")  # hh-hhhhhhhhhh where h is a character 0-f whitespace allowed either side
# @parse.with_pattern(r"[^,]*")  # hh-hhhhhhhhhh where h is a character 0-f whitespace allowed either side
def parse_identifier(str):
    assert re.match("^\s*[0-9a-f]{2}-[0-9a-f]{12}\s*$", str) is not None
    return

@parse.with_pattern(r"[^,]*")   # 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan

temperature_format = "{timestamp:ti}," + ",".join(f"{{:identifier}},{{temperature_{i:02}:float}}" for i in range(1,18+1))
compiled_format = parse.compile(temperature_format, extra_types={"identifier": parse_identifier, "float": parse_float})

def get_temperatures(start_date: datetime.datetime):
    while True:
        parsed_filenames = set()
        try:
            with open(parsed_temps_file, "rb") as f:
                parsed_filenames = pickle.load(f)
        except (EOFError, FileNotFoundError) as e:
            print(e)
        unparsed_files = set(glob.glob("/home/nrfis/Documents/blue_roof/temp/data/tempdata_*.csv")) - parsed_filenames
        current_file = min(unparsed_files) # earliest file that hasn't been parsed
        linenum = 2 # line 1 is for the headers
        line_count = sum(1 for line in open(current_file))
        while True:
            line_count = sum(1 for line in open(current_file))
            linecache.checkcache()
            unparsed_files = set(glob.glob("/home/nrfis/Documents/blue_roof/temp/data/tempdata_*.csv")) - parsed_filenames
            if(linenum <= line_count):
                line = linecache.getline(current_file, linenum).replace("\n", "")
                result = compiled_format.parse(line)
                if result is None:
                    line_count = sum(1 for line in open(current_file))
                    if(linenum < line_count):
                        print(current_file, linenum)
                    yield None
                    linenum = min(linenum, line_count)
                else:
                    yield Temperature(**result.named)
                linenum+=1
            elif (len(unparsed_files) > 1):
                parsed_filenames.add(current_file)
                with open(parsed_temps_file, "wb") as f: pickle.dump(parsed_filenames, f)
                print("new_file")
                break
            else:
                yield None

if __name__ == "__main__":
    for temp in get_temperatures():
        if temp is not None:
            print(temp.timestamp)