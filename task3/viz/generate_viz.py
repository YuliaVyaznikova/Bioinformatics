from graphviz import Digraph
import os


def generate_pipeline_dag():
    dot = Digraph(
        name='ONT_Mapping_Quality_Pipeline',
        comment='DAG of ONT Mapping Quality Assessment Pipeline',
        format='png',
        node_attr={'shape': 'box', 'style': 'filled', 'fontname': 'Arial'},
        edge_attr={'fontname': 'Arial'}
    )
    dot.attr(rankdir='TD', label='ont mapping quality assessment pipeline', labelloc='t', fontsize='16')

    dot.node('start', 'start: fasta, fastq', shape='ellipse', fillcolor='#lightblue')
    dot.node('check_dep', 'check_dependencies', fillcolor='#E8E8E8')
    dot.node('fastqc', 'fastqc_check (--nogroup)', fillcolor='#FFF2CC')
    dot.node('index_ref', 'index_reference (minimap2 -d)', fillcolor='#D5E8D4')
    dot.node('align', 'alignment (minimap2 -ax map-ont)', fillcolor='#D5E8D4')
    dot.node('sam2bam', 'sam_to_bam (samtools view)', fillcolor='#D5E8D4')
    dot.node('flagstat', 'flagstat (samtools flagstat)', fillcolor='#DAE8FC')

    dot.node('decision', 'mapped >= 90%?', shape='diamond', fillcolor='#FFE6CC')
    dot.node('ok', 'OK: sort + freebayes', fillcolor='#D5E8D4')
    dot.node('not_ok', 'NOT OK: quality too low', fillcolor='#F8CECC')
    dot.node('end', 'end', shape='ellipse', fillcolor='#E8E8E8')

    dot.edge('start', 'check_dep')
    dot.edge('check_dep', 'fastqc')
    dot.edge('start', 'index_ref')
    dot.edge('index_ref', 'align')
    dot.edge('fastqc', 'align')
    dot.edge('align', 'sam2bam')
    dot.edge('sam2bam', 'flagstat')
    dot.edge('flagstat', 'decision')
    dot.edge('decision', 'ok', label='>= 90%')
    dot.edge('decision', 'not_ok', label='< 90%')
    dot.edge('ok', 'end')
    dot.edge('not_ok', 'end')

    output_path = os.path.join(os.path.dirname(__file__), 'pipeline_dag')
    dot.render(output_path, cleanup=True)
    print(f'pipeline DAG saved: {output_path}.png')


def generate_hello_pipeline_graph():
    dot = Digraph(
        name='Hello_World_Pipeline',
        comment='Hello World ClearML Pipeline',
        format='png',
        node_attr={'shape': 'box', 'style': 'filled', 'fontname': 'Arial'},
        edge_attr={'fontname': 'Arial'}
    )
    dot.attr(rankdir='TD', label='hello world pipeline', labelloc='t', fontsize='16')

    dot.node('start', 'start', shape='ellipse', fillcolor='#lightblue')
    dot.node('check_py', 'check_python_version', fillcolor='#DAE8FC')
    dot.node('hello', 'hello_world_component', fillcolor='#D5E8D4')
    dot.node('end', 'end', shape='ellipse', fillcolor='#E8E8E8')

    dot.edge('start', 'check_py')
    dot.edge('check_py', 'hello')
    dot.edge('hello', 'end')

    output_path = os.path.join(os.path.dirname(__file__), 'hello_pipeline_dag')
    dot.render(output_path, cleanup=True)
    print(f'hello pipeline DAG saved: {output_path}.png')


def generate_algorithm_block_diagram():
    dot = Digraph(
        name='Algorithm_Block_Diagram',
        comment='Block diagram of the mapping quality algorithm',
        format='png',
        node_attr={'shape': 'box', 'style': 'filled', 'fontname': 'Arial'},
        edge_attr={'fontname': 'Arial'}
    )
    dot.attr(rankdir='TB', label='algorithm block diagram (bash)', labelloc='t', fontsize='16')

    dot.node('sra', 'download SRA / FASTQ', fillcolor='#E8E8E8')
    dot.node('ref', 'reference genome (FASTA)', fillcolor='#E8E8E8')
    dot.node('fastqc', 'fastqc qc check', fillcolor='#FFF2CC')
    dot.node('index', 'minimap2 indexing', fillcolor='#D5E8D4')
    dot.node('align', 'minimap2 alignment (map-ont)', fillcolor='#D5E8D4')
    dot.node('sam2bam', 'samtools view SAM->BAM', fillcolor='#D5E8D4')
    dot.node('flagstat', 'samtools flagstat', fillcolor='#DAE8FC')
    dot.node('parse', 'parse_flagstat.py: extract %', fillcolor='#DAE8FC')

    dot.node('decision', '% >= 90?', shape='diamond', fillcolor='#FFE6CC')

    dot.node('sort', 'samtools sort BAM', fillcolor='#D5E8D4')
    dot.node('freebayes', 'freebayes variant calling', fillcolor='#D5E8D4')
    dot.node('vcf', 'variants.vcf', fillcolor='#E8E8E8')

    dot.node('reject', 'not ok - low quality', fillcolor='#F8CECC')

    dot.edge('sra', 'fastqc')
    dot.edge('ref', 'index')
    dot.edge('index', 'align')
    dot.edge('align', 'sam2bam')
    dot.edge('sam2bam', 'flagstat')
    dot.edge('flagstat', 'parse')
    dot.edge('parse', 'decision')
    dot.edge('decision', 'sort', label='yes (>= 90%)', fontsize='10')
    dot.edge('sort', 'freebayes')
    dot.edge('freebayes', 'vcf')
    dot.edge('decision', 'reject', label='no (< 90%)', fontsize='10')

    output_path = os.path.join(os.path.dirname(__file__), 'algorithm_block_diagram')
    dot.render(output_path, cleanup=True)
    print(f'algorithm block diagram saved: {output_path}.png')


if __name__ == '__main__':
    generate_pipeline_dag()
    generate_hello_pipeline_graph()
    generate_algorithm_block_diagram()