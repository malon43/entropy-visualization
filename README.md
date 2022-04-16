# Disk sector entropy visualization utility
## Descriptive Description
## Usage
    python script.py [-h] [-s SIZE] [-m OUTPUT_METHOD] [-a ANALYSIS_METHOD] [-l SIG_LEVEL | [--rand-lim RAND_LIM --sus-rand-lim SUS_RAND_LIM]] [output method arguments] disk_image
### Set sector size to 4KiB
    ./script.py --size 4096 disk.img
### Change output method to CSV
    ./script.py --method csv disk.img
### Change analysis method to chi2-8
    ./script.py --analysis chi2-8 disk.img
### analysis methods
Available methods are `chi2-8`, `chi2-4`, `chi2-3`, `chi2-1`, `shannon`

- `chi2-n` are chi squared tests, which decide the randomness of sectors based on the distribution of groups of n consecutive bits (with no overlap).
If the expected count of each group ($\frac{\lfloor\frac{\text{sector size * 8}}{n}\rfloor}{2^n}$) is below 5, for the given sector size might be imprecise. (e.g. `chi2-8` for the sector size of 512)
- `shannon` calculates the [normalized entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)#Efficiency_(normalized_entropy)) of the distribution of byte values in the sector.

### Output method arguments
#### sweeping
Visualizes image as a png image.
Each sector as a pixel order from left to right.
- `--output-file out.png`
will set the output file out out.png
- `--width 2048`
will set the resulting image width to 2048 pixels
- `--palette asalor` will match the color palette of the result to the palette used [here](https://asalor.blogspot.com/2011/08/trim-dm-crypt-problems.html)

#### sweeping-blocks
Same as **sweeping**, but the sectors are grouped in blocks of defined size.
- `--output-file out.png`
will set the output file out out.png
- `--sweeping-block-size 64`
will set the size of the side of the blocks to 64 pixels
- `--width 2048`
will set the resulting image width to 2048 pixels, needs to be divisible by sweeping-block-size
- `--palette asalor` will match the color palette of the result to the palette used [here](https://asalor.blogspot.com/2011/08/trim-dm-crypt-problems.html)

#### hilbert-curve
Same as **sweeping**, but the order of sectors follows the [Hilbert Curve](https://en.wikipedia.org/wiki/Hilbert_curve)

- `--output-file out.png`
will set the output file out out.png
- `--palette asalor` will match the color palette of the result to the palette used [here](https://asalor.blogspot.com/2011/08/trim-dm-crypt-problems.html)

#### sample-output
One line per sector in the format

sector number (sector offset in hexadecimal) - randomness, result flag (pattern: repeated byte value of pattern)
- `--output-file out.txt`
will set the output file to out.txt

- `--err-file err.txt`
will set the error output file to err.txt (idk why you would use it, but you can)

<!--- - `--entropy-limit 0.9`
omits every sector the entropy of which is higher than 0.9 
--->
#### csv
Creates csv file, which can be used by `from_csv.py` to produce the other methods later, without the need to run the analysing again.
- `--output-file out.txt`
will set the output file to out.txt

- `--err-file err.txt`
will set the error output file to err.txt 

<!--- `--entropy-limit 0.9`
omits every sector the entropy of which is higher than 0.9
---> 
- `--no-header` the resulting csv file will not contain a header

- `--separator '|'` will set | as a separator of the csv file

## Generating from csv files
It is possible to produce output using one of the output methods from generated csv file using `from_csv.py`.
### Usage
    from_csv.py [-h] [-d DELIMITER] method file [output method arguments]
available methods are `sample-output`, `csv`, `sweeping`, `sweeping-blocks`, `hilbert-curve`
#### Set delimiter to '|'
    from_csv.py -d '|' hilbert-curve disk.csv
#### set width of resulting image to 2048 pixels
    from_csv.py sweeping disk.csv --width 2048

## TODO
- More descriptive description
- Usage
- Better project structure
- speed up entropy calculation