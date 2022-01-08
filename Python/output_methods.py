from image_output import ScanBlocks, Scanning
from text_output import CSVOutput, SampleOutput

output_methods: dict = {
    'sample-output': SampleOutput,
    'csv': CSVOutput,
    'scanning': Scanning,
    'scan-blocks': ScanBlocks
}
