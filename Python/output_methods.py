from image_output import HilbertCurve, ScanBlocks, Scanning
from text_output import CSVOutput, SampleOutput

output_methods: dict = {
    'sample-output': SampleOutput,
    'csv': CSVOutput,
    'scanning': Scanning,
    'scan-blocks': ScanBlocks,
    'hilbert-curve': HilbertCurve
}
