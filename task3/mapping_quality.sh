#!/bin/bash
REFERENCE="NC_000913.3.fasta"
READS="ecoli_ont.fastq"
SAM_FILE="alignments.sam"
BAM_FILE="aln.bam"
SORTED_BAM="alns.bam"
VCF_FILE="variants.vcf"
STATS_FILE="stats.txt"
QC_REPORT_DIR="qc_report"

echo "1. FastQC"
mkdir -p "$QC_REPORT_DIR"
fastqc "$READS" --extract --nogroup -o "$QC_REPORT_DIR" 2>/dev/null || echo "fastqc warning (non-critical for ONT long reads)"

echo ""
echo "2. minimap2 indexing"
minimap2 -d "${REFERENCE}.mmi" "$REFERENCE"

echo ""
echo "3. minimap2 mapping (ONT)"
minimap2 -ax map-ont "${REFERENCE}.mmi" "$READS" > "$SAM_FILE"

echo ""
echo "4. samtools view (sam to bam)"
samtools view -bo "$BAM_FILE" "$SAM_FILE"

echo ""
echo "5. samtools flagstat"
samtools flagstat "$BAM_FILE" > "$STATS_FILE"
cat "$STATS_FILE"

echo ""
echo "6. parsing mapped percent"
MAPPED_LINE=$(grep -E 'mapped \(' "$STATS_FILE" | head -n 1)
MAPPED_PERCENT=$(echo "$MAPPED_LINE" | grep -oP '\(\K[0-9]+\.[0-9]+(?=%)')
echo "mapped: ${MAPPED_PERCENT}%"

echo ""
echo "7. checking mapping quality"
if (( $(echo "$MAPPED_PERCENT >= 90.0" | bc -l) )); then
    echo "OK" >> "$STATS_FILE"
    echo "mapping ok: ${MAPPED_PERCENT}% >= 90%"

    echo ""
    echo "8. samtools sort"
    samtools sort "$BAM_FILE" -o "$SORTED_BAM"

    echo ""
    echo "9. freebayes"
    freebayes -f "$REFERENCE" "$SORTED_BAM" > "$VCF_FILE"

    echo ""
    echo "10. finished"
    echo "Finished!" >> "$STATS_FILE"
else
    echo "NOT OK" >> "$STATS_FILE"
    echo "mapping low: ${MAPPED_PERCENT}% < 90%"
fi

echo ""
echo "== result =="
tail -n 2 "$STATS_FILE"