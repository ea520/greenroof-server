# take the file that contains all of the data and split it into smaller daily data files
update_daily_text_files(){
    input_filename=$1
    output_folder=$2
    data_start="3" # line number where the data starts (after headers)
    date_length="10" # the number of characters in dd/mm/yyyy
    # make a list of the dates 
    # 1) get the lines after the header
    # 2) make a list of the lines for which the first 10 characters are unique (remove other lines with the same date)
    # 3) for each of the filtered lines, cut them so they're 10 characters long
    dates=$( tail -n +$data_start "$input_filename" | uniq -w$date_length | cut -c-$date_length )
    last_date=$(echo $dates | tail -c 11)
    table_header="$( head -1 $input_filename )"
    for date in $dates
    do
        day=${date:0:2} # get the day, month and year using substrings
        month=${date:3:2}
        year=${date:6:4}
        dashed_date="$year-$month-$day" # write it as yyyy-mm-dd
        output_file="$output_folder/$dashed_date.csv" # make a filename out of the date
        if [ ! -f "$output_file" ] || [ "$date" = "$last_date" ]; then
                # make a temporary to put the data for that date in
                temp_file=/tmp/daily-data-$dashed_date
                # make the table header replacing tabs with commas
                echo "timestamp$table_header" | tr '\t' ',' > $temp_file
                # put all the lines with the corresponding date this file
                grep $date $input_filename | tr '\t' ',' >> $temp_file
                # put the data into the correct file name
                mv -f $temp_file $output_file
                # if there's a new file yet to be made, this file is
                # complete (should be 24 hours of recorded data) 
                # make the file read only then
                if [ "$date" != "$last_date" ]; then
                    chmod 0444 $output_file
                fi
        fi
    done
}
update_daily_text_files "/home/nrfis/Documents/blue_roof/weather/weather.csv" '/home/nrfis/Documents/blue_roof/weather/daily'
update_daily_text_files "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_1.csv" '/home/nrfis/Documents/blue_roof/soil_moisture/daily1'
update_daily_text_files "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_2.csv" '/home/nrfis/Documents/blue_roof/soil_moisture/daily2'