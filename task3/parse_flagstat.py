#!/usr/bin/env python3
import sys
import re


def parse_flagstat(filepath):
    stats = {}
    with open(filepath, 'r') as f:
        content = f.read()
    total_match = re.search(r'(\d+) \+ \d+ in total', content)
    if total_match:
        stats['total_reads'] = int(total_match.group(1))
    mapped_match = re.search(r'(\d+) \+ \d+ mapped \((\d+\.\d+)%', content)
    if mapped_match:
        stats['mapped_reads'] = int(mapped_match.group(1))
        stats['mapped_percent'] = float(mapped_match.group(2))
    secondary_match = re.search(r'(\d+) \+ \d+ secondary', content)
    if secondary_match:
        stats['secondary'] = int(secondary_match.group(1))
    supp_match = re.search(r'(\d+) \+ \d+ supplementary', content)
    if supp_match:
        stats['supplementary'] = int(supp_match.group(1))
    dup_match = re.search(r'(\d+) \+ \d+ duplicates', content)
    if dup_match:
        stats['duplicates'] = int(dup_match.group(1))
    return stats


def main():
    if len(sys.argv) < 2:
        print("usage: python parse_flagstat.py <path_to_stats.txt>")
        sys.exit(1)
    filepath = sys.argv[1]
    try:
        stats = parse_flagstat(filepath)
    except FileNotFoundError:
        print(f"file not found: {filepath}")
        sys.exit(1)
    if not stats:
        print("could not parse flagstat output")
        sys.exit(1)
    print("=== mapping quality ===")
    print(f"  total reads:    {stats.get('total_reads', 'N/A')}")
    print(f"  mapped:         {stats.get('mapped_reads', 'N/A')}")
    print(f"  mapped percent: {stats.get('mapped_percent', 'N/A')}%")
    print(f"  secondary:      {stats.get('secondary', 'N/A')}")
    print(f"  supplementary:  {stats.get('supplementary', 'N/A')}")
    print(f"  duplicates:     {stats.get('duplicates', 'N/A')}")
    mapped_percent = stats.get('mapped_percent')
    print()
    if mapped_percent is not None:
        if mapped_percent >= 90.0:
            print(f"  status: OK ({mapped_percent}% >= 90%)")
            return 0
        else:
            print(f"  status: NOT OK ({mapped_percent}% < 90%)")
            return 1
    else:
        print("  status: ERROR (could not parse mapped percent)")
        return 1


if __name__ == '__main__':
    sys.exit(main())