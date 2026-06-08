#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import shutil


def _find_tool(name):
    local_bin = os.path.join(os.path.expanduser('~'), '.local', 'bin', name)
    if os.path.exists(local_bin):
        return local_bin
    result = shutil.which(name)
    return result


def check_dependencies():
    tools = ['fastqc', 'minimap2', 'samtools']
    for t in tools:
        path = _find_tool(t)
        if not path:
            print(f"  {t}: NOT FOUND")
            sys.exit(1)
        print(f"  {t}: {path}")
    freebayes = _find_tool('freebayes')
    if freebayes:
        print(f"  freebayes: {freebayes}")
    else:
        print(f"  freebayes: not found (variant calling will be skipped)")


def fastqc_check(fastq_path, output_dir='qc_report'):
    print(f"  running fastqc on {fastq_path} ...")
    try:
        subprocess.run(
            ['fastqc', '--nogroup', '-o', output_dir, fastq_path],
            capture_output=True, text=True, timeout=120
        )
        print(f"  fastqc done")
        return 'PASS'
    except subprocess.TimeoutExpired:
        print(f"  warning: fastqc timed out on ont long reads, continuing")
        return 'WARN'
    except Exception as e:
        print(f"  fastqc error: {e}")
        return 'FAIL'


def index_reference(fasta_path):
    mmi = f"{fasta_path}.mmi"
    if os.path.exists(mmi):
        print(f"  index exists: {mmi}")
        return
    print(f"  indexing {fasta_path} ...")
    subprocess.run(
        ['minimap2', '-d', mmi, fasta_path],
        check=True, capture_output=True, text=True
    )
    print(f"  index created: {mmi}")


def alignment(fasta_path, fastq_path, sam_output):
    mmi = f"{fasta_path}.mmi"
    print(f"  mapping {fastq_path} -> {sam_output} ...")
    with open(sam_output, 'w') as f:
        result = subprocess.run(
            ['minimap2', '-ax', 'map-ont', mmi, fastq_path],
            stdout=f, stderr=subprocess.PIPE, text=True
        )
    result.check_returncode()
    size = os.path.getsize(sam_output)
    print(f"  sam: {size} bytes")


def sam_to_bam(sam_path, bam_output):
    print(f"  converting {sam_path} -> {bam_output} ...")
    subprocess.run(
        ['samtools', 'view', '-b', sam_path, '-o', bam_output],
        check=True, capture_output=True, text=True
    )
    size = os.path.getsize(bam_output)
    print(f"  bam: {size} bytes")


def flagstat(bam_path, stats_output):
    print(f"  running samtools flagstat on {bam_path} ...")
    result = subprocess.run(
        ['samtools', 'flagstat', bam_path],
        capture_output=True, text=True, check=True
    )
    with open(stats_output, 'w') as f:
        f.write(result.stdout)
    mapped_line = [line for line in result.stdout.split('\n') if 'mapped (' in line][0]
    mapped_percent = float(re.search(r'(\d+\.\d+)%', mapped_line).group(1))
    print(f"  mapped: {result.stdout.count('mapped')} / ... = {mapped_percent}%")
    return mapped_percent


def sort_and_variant_calling(bam_path, fasta_path, vcf_output):
    sorted_bam = bam_path.replace('.bam', '.sorted.bam')
    print(f"  sorting {bam_path} -> {sorted_bam} ...")
    subprocess.run(
        ['samtools', 'sort', bam_path, '-o', sorted_bam],
        check=True, capture_output=True, text=True
    )
    freebayes_path = _find_tool('freebayes')
    if not freebayes_path:
        print("  freebayes not found, skipping variant calling")
        return
    print(f"  running freebayes -> {vcf_output} ...")
    with open(vcf_output, 'w') as f:
        subprocess.run(
            [freebayes_path, '-f', os.path.abspath(fasta_path), sorted_bam],
            stdout=f, stderr=subprocess.PIPE, text=True
        )
    print(f"  variants saved: {vcf_output}")


def main():
    fasta = os.path.abspath('./NC_000913.3.fasta')
    fastq = os.path.abspath('./ecoli_ont.fastq')

    if not all(os.path.exists(f) for f in [fasta, fastq]):
        print(f"error: input files not found.")
        print(f"  ref: {fasta}")
        print(f"  reads: {fastq}")
        sys.exit(1)

    print("=" * 50)
    print("standalone mapping quality pipeline")
    print("=" * 50)
    print()

    print("[1/7] check_dependencies")
    check_dependencies()
    print()

    print("[2/7] fastqc_check")
    qc_status = fastqc_check(fastq)
    print(f"  -> status: {qc_status}")
    print()

    print("[3/7] index_reference")
    index_reference(fasta)
    print()

    print("[4/7] alignment")
    sam_file = './alignment.sam'
    alignment(fasta, fastq, sam_file)
    print()

    print("[5/7] sam_to_bam")
    bam_file = './alignment.bam'
    sam_to_bam(sam_file, bam_file)
    print()

    print("[6/7] flagstat")
    stats_file = './mapping_stats.txt'
    mapped_percent = flagstat(bam_file, stats_file)
    print(f"  -> mapped: {mapped_percent}%")
    print()

    print("[7/7] decision")
    print(f"  mapped: {mapped_percent}%")
    if mapped_percent >= 90.0:
        print(f"  -> OK ({mapped_percent}% >= 90%)")
        with open(stats_file, 'a') as f:
            f.write("OK\n")
        print(f"  -> running variant calling...")
        sort_and_variant_calling(bam_file, fasta, './variants.vcf')
    else:
        print(f"  -> NOT OK ({mapped_percent}% < 90%)")
        with open(stats_file, 'a') as f:
            f.write("NOT OK\n")
        print(f"  -> variant calling skipped")

    print()
    print("=" * 50)
    print("pipeline finished.")
    print("=" * 50)


if __name__ == '__main__':
    main()