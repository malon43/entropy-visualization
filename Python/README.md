# Disk sector entropy visualization utility
## Descriptive Description
## Usage
    python script.py [-h] [-s SIZE] [-m OUTPUT_METHOD]  [output method arguments] file
### Set sector size to 4KiB
    ./script.py --size 4096 disk.img
### Change output method to CSV
    ./script.py --method csv disk.img
### Output method arguments
#### scanning
Visualizes image as a png image.
Each sector as a pixel order from left to right.

`--output-file out.png`
will set the output file out out.png

`--width 2048`
will set the resulting image width to 2048 pixels

#### scan-blocks
Same as **scanning**, but the sectors are grouped in blocks of defined size.

`--output-file out.png`
will set the output file out out.png

`--scan-block-size 64`
will set the size of the side of the blocks to 64 pixels

`--width 2048`
will set the resulting image width to 2048 pixels, needs to be divisible by scan-block-size

#### hilbert-curve
Same as **scanning**, but the order of sectors follows the [Hilbert Curve](https://en.wikipedia.org/wiki/Hilbert_curve)

`--output-file out.png`
will set the output file out out.png


#### sample-output
`--output-file out.txt`
will set the output file to out.txt

`--err-file err.txt`
will set the error output file to err.txt (idk why you would use it, but you can)

`--entropy-limit 0.9`
omits every sector the entropy of which is higher than 0.9
#### csv
`--output-file out.txt`
will set the output file to out.txt

`--err-file err.txt`
will set the error output file to err.txt 

`--entropy-limit 0.9`
omits every sector the entropy of which is higher than 0.9

`--no-header` the resulting csv file will not contain a header

`--separator '|'` will set | as a separator of the csv file
## TODO
- More descriptive description
- Usage
- Better project structure
- Color pallete choice
- speed up entropy calculation