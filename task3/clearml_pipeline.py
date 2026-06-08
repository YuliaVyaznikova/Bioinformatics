#!/usr/bin/env python3
from clearml import PipelineDecorator, Logger, Task
import subprocess
import os
import re
import logging


def _find_tool(name):
    local_bin = os.path.join(os.path.expanduser('~'), '.local', 'bin', name)
    if os.path.exists(local_bin):
        return local_bin
    result = subprocess.run(['which', name], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def check_dependencies():
    required_tools = ['samtools', 'minimap2', 'fastqc', 'freebayes']
    missing = []
    for tool in required_tools:
        if _find_tool(tool) is None:
            missing.append(tool)
    if missing:
        raise EnvironmentError(
            f"missing tools: {', '.join(missing)}. "
            f"install: conda install -c bioconda {' '.join(missing)}"
        )
    Logger.current_logger().report_text("all dependencies found.")


@PipelineDecorator.component(return_values=['qc_status'], cache=True)
def fastqc_check(fastq_path, output_dir):
    try:
        fastq_path = os.path.abspath(fastq_path)
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        Logger.current_logger().report_text(f"running fastqc for {fastq_path}")
        result = subprocess.run(
            ['fastqc', fastq_path, '--nogroup', '--extract', '-o', output_dir],
            capture_output=True, text=True, timeout=120
        )
        result.check_returncode()
        fastq_basename = os.path.splitext(os.path.basename(fastq_path))[0]
        if fastq_basename.endswith('.fastq'):
            fastq_basename = os.path.splitext(fastq_basename)[0]
        html_report = os.path.join(output_dir, f"{fastq_basename}_fastqc.html")
        if os.path.exists(html_report):
            Logger.current_logger().report_text(f"fastqc report: {html_report}")
            return "PASS"
        else:
            Logger.current_logger().report_text("fastqc report not found")
            return "FAIL"
    except subprocess.TimeoutExpired:
        Logger.current_logger().report_text(
            "fastqc timed out on ont long reads (known issue), continuing pipeline",
            level=logging.WARNING
        )
        return "WARN"
    except Exception as e:
        Logger.current_logger().report_text(f"fastqc error: {str(e)}", level=logging.ERROR)
        return "FAIL"


@PipelineDecorator.component(cache=True)
def index_reference(fasta_path):
    try:
        fasta_path = os.path.abspath(fasta_path)
        mmi_path = f"{fasta_path}.mmi"
        Logger.current_logger().report_text(f"indexing reference: {fasta_path}")
        result = subprocess.run(
            ['minimap2', '-d', mmi_path, fasta_path],
            capture_output=True, text=True
        )
        result.check_returncode()
        if os.path.exists(mmi_path):
            Logger.current_logger().report_text(
                f"index created: {mmi_path} ({os.path.getsize(mmi_path)} bytes)"
            )
        else:
            raise FileNotFoundError(f"index not created: {mmi_path}")
    except Exception as e:
        err_msg = f"indexing failed: {str(e)}"
        if result.stderr:
            err_msg += f"\nstderr: {result.stderr}"
        Logger.current_logger().report_text(err_msg, level=logging.ERROR)
        raise


@PipelineDecorator.component(cache=True)
def alignment(fasta_path, fastq_path, sam_output):
    try:
        fasta_path = os.path.abspath(fasta_path)
        fastq_path = os.path.abspath(fastq_path)
        sam_output = os.path.abspath(sam_output)
        mmi_path = f"{fasta_path}.mmi"
        Logger.current_logger().report_text(
            f"mapping with minimap2 (ONT): {fastq_path} -> {sam_output}"
        )
        result = subprocess.run(
            ['minimap2', '-ax', 'map-ont', mmi_path, fastq_path],
            stdout=open(sam_output, 'w'), stderr=subprocess.PIPE, text=True
        )
        result.check_returncode()
        if os.path.getsize(sam_output) == 0:
            raise ValueError("empty sam file")
        Logger.current_logger().report_text(
            f"mapping done, sam: {os.path.getsize(sam_output)} bytes"
        )
    except Exception as e:
        err_msg = f"alignment failed: {str(e)}"
        if result.stderr:
            err_msg += f"\nstderr: {result.stderr}"
        Logger.current_logger().report_text(err_msg, level=logging.ERROR)
        raise


@PipelineDecorator.component(cache=True)
def sam_to_bam(sam_path, bam_output):
    try:
        sam_path = os.path.abspath(sam_path)
        bam_output = os.path.abspath(bam_output)
        Logger.current_logger().report_text(f"sam to bam: {sam_path}")
        result = subprocess.run(
            ['samtools', 'view', '-b', sam_path, '-o', bam_output],
            capture_output=True, text=True
        )
        result.check_returncode()
        if os.path.getsize(bam_output) == 0:
            raise ValueError("empty bam file")
        Logger.current_logger().report_text(
            f"bam created: {bam_output} ({os.path.getsize(bam_output)} bytes)"
        )
    except Exception as e:
        err_msg = f"sam to bam failed: {str(e)}"
        if result.stderr:
            err_msg += f"\nstderr: {result.stderr}"
        Logger.current_logger().report_text(err_msg, level=logging.ERROR)
        raise


@PipelineDecorator.component(return_values=['mapped_percent'], cache=True)
def flagstat(bam_path, stats_output):
    try:
        bam_path = os.path.abspath(bam_path)
        stats_output = os.path.abspath(stats_output)
        if not os.path.exists(bam_path):
            raise FileNotFoundError(f"bam not found: {bam_path}")
        if os.path.getsize(bam_path) == 0:
            raise ValueError("empty bam file")
        Logger.current_logger().report_text("running samtools flagstat")
        result = subprocess.run(
            ['samtools', 'flagstat', bam_path],
            capture_output=True, text=True, check=True
        )
        with open(stats_output, 'w') as f:
            f.write(result.stdout)
        mapped_line = [line for line in result.stdout.split('\n') if 'mapped (' in line][0]
        mapped_percent = float(re.search(r'(\d+\.\d+)%', mapped_line).group(1))
        Logger.current_logger().report_text(f"mapped percent: {mapped_percent}%")
        Logger.current_logger().report_scalar(
            title="Alignment Quality",
            series="Mapped Reads (%)",
            value=mapped_percent,
            iteration=0
        )
        return mapped_percent
    except Exception as e:
        Logger.current_logger().report_text(f"flagstat error: {str(e)}", level=logging.ERROR)
        raise


@PipelineDecorator.component(cache=True)
def sort_and_variant_calling(bam_path, fasta_path, vcf_output):
    try:
        sorted_bam = bam_path.replace('.bam', '.sorted.bam')
        Logger.current_logger().report_text("sorting bam")
        result_sort = subprocess.run(
            ['samtools', 'sort', bam_path, '-o', sorted_bam],
            capture_output=True, text=True
        )
        result_sort.check_returncode()
        if os.path.getsize(sorted_bam) == 0:
            raise ValueError("empty sorted bam")
        Logger.current_logger().report_text("running freebayes")
        vcf_path = os.path.abspath(vcf_output)
        freebayes_path = _find_tool('freebayes')
        if freebayes_path is None:
            raise FileNotFoundError("freebayes not found in PATH or ~/.local/bin")
        with open(vcf_path, 'w') as f:
            result_fb = subprocess.run(
                [freebayes_path, '-f', os.path.abspath(fasta_path), sorted_bam],
                stdout=f, stderr=subprocess.PIPE, text=True
            )
            result_fb.check_returncode()
        Logger.current_logger().report_text(f"variants written: {vcf_path}")
    except Exception as e:
        Logger.current_logger().report_text(f"variant calling error: {str(e)}", level=logging.ERROR)
        raise


@PipelineDecorator.pipeline(
    name='ont mapping quality assessment pipeline',
    project='Bioinformatics Task 3',
    version='1.0'
)
def genome_pipeline(fasta_path, fastq_path):
    check_dependencies()
    qc_status = fastqc_check(fastq_path, 'qc_report')
    Logger.current_logger().report_text(f"fastqc status: {qc_status}")
    index_reference(fasta_path)
    sam_file = 'alignment.sam'
    alignment(fasta_path, fastq_path, sam_file)
    bam_file = 'alignment.bam'
    sam_to_bam(sam_file, bam_file)
    stats_file = 'mapping_stats.txt'
    mapped_percent = flagstat(bam_file, stats_file)

    mapped_percent = float(mapped_percent)

    if mapped_percent >= 90.0:
        Logger.current_logger().report_text(
            f"mapping ok: {mapped_percent}% >= 90% -> OK"
        )
        with open(stats_file, 'a') as f:
            f.write("OK\n")
        sort_and_variant_calling(bam_file, fasta_path, 'variants.vcf')
    else:
        Logger.current_logger().report_text(
            f"mapping low: {mapped_percent}% < 90% -> NOT OK",
            level=logging.ERROR
        )
        with open(stats_file, 'a') as f:
            f.write("NOT OK\n")

    Logger.current_logger().report_text("pipeline finished.")


if __name__ == '__main__':
    try:
        local_bin = os.path.expanduser('~/.local/bin')
        if local_bin not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{local_bin}:{os.environ.get('PATH', '')}"
        task = Task.init(
            project_name='Bioinformatics Task 3',
            task_name='ont mapping quality assessment pipeline'
        )
        PipelineDecorator.run_locally()
        fasta = os.path.abspath('./NC_000913.3.fasta')
        fastq = os.path.abspath('./ecoli_ont.fastq')
        if not all(os.path.exists(f) for f in [fasta, fastq]):
            raise FileNotFoundError(
                f"input files not found.\n"
                f"  ref: {fasta}\n"
                f"  reads: {fastq}\n"
                f"make sure files are in current directory."
            )
        if os.path.getsize(fasta) == 0 or os.path.getsize(fastq) == 0:
            raise ValueError("empty input files")
        genome_pipeline(fasta, fastq)
    except Exception as e:
        if Logger.current_logger():
            Logger.current_logger().report_text(
                f"pipeline error: {str(e)}", level=logging.ERROR
            )
        else:
            print(f"critical error: {str(e)}")
        raise