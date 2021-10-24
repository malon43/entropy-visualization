# Disk sector entropy visualization utility
## Descriptive Description
## Usage
    python script.py [-h] [-s SIZE] [-m OUTPUT_METHOD]  [output method arguments] file
### Set sector size to 4KiB
    ./script.py --size 4096 disk.img
### Change output method to CSV
    ./script.py --method csv disk.img
### Output method arguments
#### sample-output
`--entropy-threshold 0.9`
omits every sector the entropy of which is higher or equal to 0.9
#### csv
`--entropy-threshold 0.9`
omits every sector the entropy of which is higher or equal to 0.9

`--no-header` the resulting csv file will not contain a header

`--separator '|'` will set | as a seperator of the csv file
## TODO
- Description
- Usage
- Better Project Structure
