from image_output import HilbertCurve, SweepingBlocks, Sweeping
from text_output import CSVOutput, SampleOutput

output_methods: dict = {
    'sample-output': SampleOutput,
    'csv': CSVOutput,
    'sweeping': Sweeping,
    'sweeping-blocks': SweepingBlocks,
    'hilbert-curve': HilbertCurve
}
