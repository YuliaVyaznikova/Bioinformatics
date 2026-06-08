#!/usr/bin/env python3
from clearml import PipelineDecorator


@PipelineDecorator.component()
def hello_world_component():
    print("Hello, ClearML! Bioinformatics pipeline framework is ready.")


@PipelineDecorator.component()
def check_python_version():
    import sys
    print(f"Python version: {sys.version}")
    print("ClearML Pipeline is operational.")


@PipelineDecorator.pipeline(
    name='hello_world_pipeline',
    project='Bioinformatics Task 3',
    version='0.1'
)
def pipeline_definition():
    check_python_version()
    hello_world_component()


if __name__ == '__main__':
    PipelineDecorator.run_locally()
    pipeline_definition()