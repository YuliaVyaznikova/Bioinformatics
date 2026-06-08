# Оценка качества картирования ONT-прочтений E. coli

Вариант: Oxford Nanopore (ONT) + minimap2 + ClearML Pipelines
Организм: *Escherichia coli* K-12 MG1655

## 1. Данные из NCBI SRA

ONT-прочтения **Escherichia coli**:

- SRA-идентификатор: [SRR38324904](https://www.ncbi.nlm.nih.gov/sra/?term=SRR38324904)
- Формат: FASTQ (single-end, Oxford Nanopore long reads)
- Объем: 174 MB (SRA), 452 MB (FASTQ)
- Количество чтений: 27,768
- Run: Oxford Nanopore Technologies
- Архив fastq/sam/bam: [Google Drive](https://drive.google.com/drive/folders/12oKdipaKr7Gs0oKhT9CO-wueR9HQw0ey?usp=sharing)

### Референсный геном

- Сборка: GCF_000005845.2 (NC_000913.3)
- Файл: [`NC_000913.3.fasta`](NC_000913.3.fasta)
- Источник: [NCBI Assembly](https://www.ncbi.nlm.nih.gov/assembly/GCF000005845.2/)

---

## 2. Bash-скрипт

Файл: [`mapping_quality.sh`](mapping_quality.sh)

Шаги:
1. FastQC (c флагом `--nogroup` для длинных ONT-чтений)
2. minimap2 indexing (`minimap2 -d`)
3. minimap2 mapping (`-ax map-ont`)
4. SAM to BAM via `samtools view -b`
5. `samtools flagstat`
6. парсинг процента картированных чтений (`grep 'mapped ('`)
7. ветвление: >= 90% => OK => sort => freebayes; < 90% => NOT OK

---

## 3. Результаты samtools flagstat

Файл: [`stats.txt`](stats.txt) (получен после запуска `mapping_quality.sh`)

```
35878 + 0 in total (QC-passed reads + QC-failed reads)
27768 + 0 primary
3495 + 0 secondary
4615 + 0 supplementary
0 + 0 duplicates
31131 + 0 mapped (86.77% : N/A)
23021 + 0 primary mapped (82.90% : N/A)
0 + 0 paired in sequencing
```

**Результат: 86.77% картированных чтений (< 90%) => статус NOT OK**

variant calling (freebayes) не выполнялся, так как порог 90% не достигнут.

---

## 4. Скрипт парсинга flagstat

Файл: [`parse_flagstat.py`](parse_flagstat.py)

Парсит вывод `samtools flagstat`, извлекает процент картированных чтений, выводит OK/NOT OK.

```bash
python3 parse_flagstat.py stats.txt
```

Вывод:

```
=== mapping quality ===
  total reads:    35878
  mapped:         31131
  mapped percent: 86.77%
  secondary:      3495
  supplementary:  4615
  duplicates:     0

  status: NOT OK (86.77% < 90%)
```

---

## 5. ClearML Pipelines

### 5.1. Инструкция по установке

Файл: [`INSTALL_CLEARML.md`](INSTALL_CLEARML.md)

Шаги: установка pip, `pip install clearml`, `clearml-init`, настройка credentials.

### 5.2. Hello World

Файл: [`hello_pipeline.py`](hello_pipeline.py)

Тестовый пайплайн с двумя компонентами: `check_python_version` и `hello_world_component`. Запуск:

```bash
python3 hello_pipeline.py
```

### 5.3. Пайплайн оценки качества (clearml)

Файл: [`clearml_pipeline.py`](clearml_pipeline.py)

Компоненты:
- `check_dependencies` - проверка наличия samtools, minimap2, fastqc, freebayes
- `fastqc_check` - FastQC с извлечением
- `index_reference` - minimap2 -d
- `alignment` - minimap2 -ax map-ont
- `sam_to_bam` - samtools view -b
- `flagstat` - samtools flagstat + парсинг процента
- `sort_and_variant_calling` - sort + freebayes

Условная ветка: если `mapped_percent >= 90.0` => sort_and_variant_calling, иначе NOT OK.

### 5.4. standalone пайплайн (без clearml)

Файл: [`standalone_pipeline.py`](standalone_pipeline.py)

Запускает те же компоненты (check_dependencies, fastqc_check, index_reference, alignment, sam_to_bam, flagstat, decision) без clearml pipeline decorator. Логика та же, можно использовать когда сервер clearml недоступен:

```bash
python3 standalone_pipeline.py
```

---

## 6. визуализация

- Способ: graphviz (автоматическая генерация)
- Скрипт генерации: [`viz/generate_viz.py`](viz/generate_viz.py)
- Изображения:
  - [`viz/pipeline_dag.png`](viz/pipeline_dag.png) - dag онт пайплайна
  - [`viz/hello_pipeline_dag.png`](viz/hello_pipeline_dag.png) - dag hello world
  - [`viz/algorithm_block_diagram.png`](viz/algorithm_block_diagram.png) - блок-схема алгоритма

---

## Файлы

| Файл | Описание |
|---|---|
| `mapping_quality.sh` | bash-ск��ипт оценки качества картирования |
| `parse_flagstat.py` | парсинг samtools flagstat |
| `hello_pipeline.py` | тестовый clearml пайплайн |
| `clearml_pipeline.py` | основной clearml пайплайн |
| `INSTALL_CLEARML.md` | инструкция по установке ClearML |
| `clearml.conf` | конфигурация ClearML |
| `README.md` | данный файл |
| `NC_000913.3.fasta` | референсный геном E. coli K-12 MG1655 |
| `stats.txt` | flagstat + результат оценки (mapping_quality.sh) |
| `mapping_stats.txt` | flagstat + результат оценки (standalone_pipeline.py) |
| `viz/generate_viz.py` | генерация dag и блок-схем через graphviz |
| `viz/pipeline_dag.png` | dag пайплайна clearml |
| `viz/hello_pipeline_dag.png` | dag hello world |
| `viz/algorithm_block_diagram.png` | блок-схема алгоритма |
| `standalone_pipeline.py` | пайплайн без clearml для локального запуска |

Большие файлы (`ecoli_ont.fastq`, `alignment.sam`, `alignment.bam`, `NC_000913.3.fasta.mmi`, `task3_data.tar.gz`) не отслеживаются в git. Архив доступен на [Google Drive](https://drive.google.com/drive/folders/12oKdipaKr7Gs0oKhT9CO-wueR9HQw0ey?usp=sharing).