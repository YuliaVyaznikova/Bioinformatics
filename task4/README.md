# Клиническая аннотация генетических вариантов

Вариант `student_34.vcf`

## 1. Исходные данные

- Файл [`student_34.vcf`](student_34.vcf)
- 50 однонуклеотидных вариантов (SNV) человека на хромосомах 21 и 22
- Сборка генома: GRCh38
- Происхождение: подвыборка из тестового файла Ensembl VEP (`Ensembl_VEP_example_homo_sapiens_GRCh38.vcf`, release 116), это указано в заголовке VCF

---

## 2. Структура VCF и статистика

| Поле | Значение | В файле `student_34.vcf` |
|---|---|---|
| CHROM | хромосома | `21` или `22` |
| POS | позиция на хромосоме (с 1, GRCh38) | например `17188416` |
| ID | идентификатор варианта | rsID из dbSNP у всех 50 записей |
| REF | референсный аллель | один нуклеотид |
| ALT | альтернативный аллель | один нуклеотид, мультиаллельных записей нет |
| QUAL | качество вызова варианта (phred) | `.` у всех записей |
| FILTER | результат фильтрации вызова | `.` у всех записей |
| INFO | дополнительные аннотации | `.` у всех записей |

Колонки FORMAT и колонок с образцами в файле нет, поэтому генотип и зиготность неизвестны.

Скрипт [`vcf_stats.py`](vcf_stats.py)

```bash
python3 vcf_stats.py student_34.vcf > vcf_stats.txt
```

Результат в [`vcf_stats.txt`](vcf_stats.txt)

| Показатель | Значение |
|---|---|
| Число записей | 50 (все SNV) |
| Хромосома 21 | 9 |
| Хромосома 22 | 41 |
| Транзиции (A<->G, C<->T) | 38 |
| Трансверсии | 12 |
| Ts/Tv | 3.17 |

Ts/Tv = 3.17 близко к значению для кодирующих областей (около 3). Для полногеномных данных оно обычно около 2.0-2.1. Это согласуется с тем, что все 50 вариантов лежат в экзонах белок-кодирующих генов (см. раздел 4).

---

## 3. Аннотация

Аннотация выполнена скриптами, настройки каждого источника сохранены в файлах рядом с результатами.

```bash
python3 vep_annotate.py student_34.vcf
python3 clinvar_annotate.py student_34.vcf
python3 gnomad_annotate.py student_34.vcf
python3 build_table.py vep/vep_output.json clinvar/clinvar_results.tsv gnomad/gnomad_results.tsv annotated_variants.tsv
```

Нужен только Python 3 (стандартная библиотека) и доступ в интернет.

### 3.1. Ensembl VEP

Скрипт [`vep_annotate.py`](vep_annotate.py)

Аннотирует варианты в Ensembl VEP по всем транскриптам.

Настройки ([`vep/vep_settings.txt`](vep/vep_settings.txt)):
- Ensembl release 116, сборка GRCh38.p14
- набор транскриптов Ensembl/GENCODE, все транскрипты без фильтрации (`--pick` не используется), чтобы видеть разные последствия в разных транскриптах
- MANE Select, Ensembl canonical, APPRIS, TSL, CCDS, UniProt
- HGVS (c. и p.), номера экзонов и интронов
- известные варианты в той же позиции (dbSNP 156, ClinVar 09/2025, COSMIC 102) и частоты gnomAD из кэша VEP
- предсказатели: SIFT, PolyPhen-2, AlphaMissense, REVEL, CADD, SpliceAI

#### Результаты:

| Файл | Содержимое |
|---|---|
| [`vep/vep_output.json`](vep/vep_output.json) | полный ответ VEP |
| [`vep/vep_output.tsv`](vep/vep_output.tsv) | табличный экспорт VEP: одна строка на пару вариант + транскрипт (1383 строки) |

### 3.2. ClinVar

Скрипт [`clinvar_annotate.py`](clinvar_annotate.py)

Ищет записи для каждого варианта в ClinVar (https://www.ncbi.nlm.nih.gov/clinvar/).

Настройки ([`clinvar/clinvar_settings.txt`](clinvar/clinvar_settings.txt)):
- версия ClinVar на момент запроса: обновление от 2026/10/25
- поиск записей по позиции: `esearch db=clinvar term="<chrom>[CHR] AND <pos>[CPOS]"`, затем `esummary` по найденным ID
- запись засчитывается варианту, только если её canonical SPDI совпадает с позицией, REF и ALT из VCF
- остальные записи в той же позиции (другие аллели, инделы, инверсии) сохраняются в колонке `other_records_at_position` и к варианту не относятся
- используется агрегированная germline-классификация уровня VCV и её review status

#### Зачем сверять аллель
VEP показывает клиническую значимость для rsID целиком. Например, для rs2231495 VEP даёт `benign, uncertain_significance`. Статус uncertain significance относится к другому аллелю той же позиции (p.His335Pro), а у нашего аллеля p.His335Arg в ClinVar статус Benign/Likely benign.

#### Результаты:

| Файл | Содержимое |
|---|---|
| [`clinvar/clinvar_results.tsv`](clinvar/clinvar_results.tsv) | таблица по 50 вариантам: найдена ли запись, VCV, классификация, review status, заболевания, другие записи в позиции |
| [`clinvar/clinvar_output.json`](clinvar/clinvar_output.json) | исходные ответы esummary по каждому варианту |

### 3.3. gnomAD

Скрипт [`gnomad_annotate.py`](gnomad_annotate.py)

Получает частоты вариантов из gnomAD (https://gnomad.broadinstitute.org).

Настройки ([`gnomad/gnomad_settings.txt`](gnomad/gnomad_settings.txt)):
- датасет `gnomad_r4` (gnomAD v4, GRCh38), экзомы и геномы
- вариант ищется по ID вида `22-17188416-T-C`
- AF = AC / AN отдельно для экзомов, геномов и объединённых данных (joint), в итоговую таблицу идёт joint AF
- grpmax: наибольшая AF среди групп afr, amr, eas, nfe, sas
- фильтры gnomAD: PASS или причина (например, `discrepant_frequencies`)

#### Результаты:

| Файл | Содержимое |
|---|---|
| [`gnomad/gnomad_results.tsv`](gnomad/gnomad_results.tsv) | AC, AN, AF, число гомозигот и фильтры для экзомов, геномов и joint, grpmax |
| [`gnomad/gnomad_output.json`](gnomad/gnomad_output.json) | полный ответ gnomAD по каждому варианту |

---

## 4. Сводная таблица

Скрипт [`build_table.py`](build_table.py)

Файл [`annotated_variants.tsv`](annotated_variants.tsv), 50 строк, по одной на каждый вариант из VCF.

### Правило выбора транскрипта

1. MANE Select транскрипт. Если вариант попадает в несколько генов, берётся MANE Select с самым тяжёлым последствием.
2. Если MANE Select нет, Ensembl canonical белок-кодирующий транскрипт.
3. Если нет и его, транскрипт с самым тяжёлым последствием.

Для всех 50 вариантов нашёлся MANE Select. Последствия ранжируются по шкале тяжести Ensembl (stop_gained > missense_variant > splice_region_variant > synonymous_variant > ...). Если в каком-то другом транскрипте последствие тяжелее, чем в MANE Select, оно записано в колонки `vep_most_severe_any` и `most_severe_transcripts`.

### Колонки

| Колонка | Описание |
|---|---|
| `input_id` | исходный идентификатор из VCF |
| `location`, `ref_alt` | координата GRCh38 и замена REF>ALT |
| `gene` | ген выбранного транскрипта |
| `vep_consequence`, `impact` | последствие по VEP в выбранном транскрипте и его impact |
| `transcript`, `refseq_mane`, `transcript_rule` | выбранный транскрипт Ensembl, соответствующий ему RefSeq и правило выбора |
| `hgvsc`, `hgvsp` | HGVS-нотация в выбранном транскрипте |
| `vep_most_severe_any`, `most_severe_transcripts` | самое тяжёлое последствие по всем транскриптам и в каких транскриптах оно встречается |
| `sift`, `polyphen`, `alphamissense`, `cadd_phred` | предсказания патогенности |
| `rsid` | rsID известного варианта в этой позиции по данным VEP |
| `gnomad_af`, `gnomad_grpmax_af`, `gnomad_filters` | joint AF gnomAD v4, максимальная AF по группам, фильтры |
| `clinvar` | есть ли запись ClinVar для этого аллеля (yes/no) |
| `clinvar_classification`, `clinvar_review_status`, `clinvar_accession` | классификация, статус рецензирования и номер VCV |
| `clinvar_other_records` | число других записей ClinVar в той же позиции, которые к варианту не относятся |
| `vep_clin_sig` | значимость этого аллеля по ClinVar из кэша VEP (09/2025), для сравнения |

### Сводка

| Показатель | Значение |
|---|---|
| Последствие в MANE Select | 28 синонимичных, 22 миссенс (в каждой группе у одного варианта ещё и `splice_region_variant`) |
| Самое тяжёлое последствие по всем транскриптам | 25 missense, 23 synonymous, 1 stop_gained, 1 splice_polypyrimidine_tract |
| В другом транскрипте последствие тяжелее, чем в MANE Select | 5 вариантов |
| Найдены в gnomAD | 50 из 50 |
| gnomAD AF < 0.1% | 24 |
| 0.1% <= AF < 1% | 14 |
| 1% <= AF < 5% | 2 |
| AF >= 5% | 10 |
| Фильтр gnomAD не PASS | 14 (`discrepant_frequencies`) |
| Есть запись ClinVar для аллеля | 18 из 50 |
| ClinVar: Benign / Benign/Likely benign / Likely benign | 7 / 7 / 2 |
| ClinVar: Uncertain significance | 2 (rs115157927 в HIRA, rs114565111 в GAL3ST1) |
| ClinVar: Pathogenic, Likely pathogenic, Conflicting | 0 |

### Таблица

Сокращённый вид `annotated_variants.tsv`. В скобках указано, в скольких транскриптах гена встречается более тяжёлое последствие, чем в MANE Select.

| № | rsID | Позиция | REF>ALT | Ген | Последствие (MANE Select) | HGVSp | gnomAD AF | ClinVar |
|---|---|---|---|---|---|---|---|---|
| 1 | rs7278168 | 21:25603910 | C>T | MRPL39 | synonymous_variant | p.Lys102= | 0.0231 | нет записи |
| 2 | rs75377686 | 21:25606478 | T>C | MRPL39 | missense_variant | p.Asn84Ser | 0.00153 | нет записи |
| 3 | rs9808753 | 21:33415005 | A>G | IFNGR2 | missense_variant | p.Gln64Arg | 0.164 | Benign/Likely benign |
| 4 | rs17878711 | 21:33427015 | A>G | IFNGR2 | missense_variant | p.Lys182Glu | 0.00187 | Benign/Likely benign |
| 5 | rs73901831 | 21:37065660 | T>G | PIGP | synonymous_variant (в 1/55 тр.: missense_variant) | p.Pro109= | 0.00125 | Benign |
| 6 | rs457705 | 21:38819507 | T>G | ETS2 | synonymous_variant | p.Thr272= | 0.797 | нет записи |
| 7 | rs61737061 | 21:43094699 | G>A | U2AF1 | synonymous_variant | p.Pro146= | 0.00214 | нет записи |
| 8 | rs115397760 | 21:43968034 | C>T | AGPAT3 | synonymous_variant | p.His89= | 4.78e-04 | нет записи |
| 9 | rs115875072 | 21:43969246 | G>A | AGPAT3 | synonymous_variant | p.Leu159= | 1.24e-04 | нет записи |
| 10 | rs7289170 | 22:17181903 | A>G | ADA2 | synonymous_variant | p.Tyr453= | 0.307 | Benign/Likely benign |
| 11 | rs2231495 | 22:17188416 | T>C | ADA2 | missense_variant | p.His335Arg | 0.336 | Benign/Likely benign |
| 12 | rs115877869 | 22:19378003 | G>C | HIRA | synonymous_variant (в 1/40 тр.: splice_polypyrimidine_tract_variant) | p.Leu493= | 1.43e-05 | нет записи |
| 13 | rs115157927 | 22:19385577 | A>T | HIRA | missense_variant | p.Ser425Thr | 6.32e-05 | Uncertain significance |
| 14 | rs9618556 | 22:19396832 | C>T | HIRA | synonymous_variant | p.Thr203= | 0.0014 | Benign/Likely benign |
| 15 | rs116458396 | 22:19396916 | G>A | HIRA | synonymous_variant | p.Gly175= | 2.54e-05 | нет записи |
| 16 | rs115736959 | 22:19973143 | G>A | ARVCF | missense_variant | p.Ala805Val | 0.00242 | Benign |
| 17 | rs76496156 | 22:19979039 | C>T | ARVCF | missense_variant | p.Val480Ile | 0.00112 | Benign |
| 18 | rs1058399 | 22:19980020 | G>A | ARVCF | synonymous_variant | p.Pro373= | 0.0115 | Benign |
| 19 | rs116398106 | 22:19981410 | G>A | ARVCF | missense_variant | p.Arg233Trp | 2.66e-04 | нет записи |
| 20 | rs2073747 | 22:19981552 | A>G | ARVCF | synonymous_variant | p.Ser185= | 0.764 | нет записи |
| 21 | rs33992092 | 22:19981972 | G>T | ARVCF | synonymous_variant | p.Val110= | 0.00641 | Benign |
| 22 | rs115706909 | 22:21643926 | C>T | SDF2L1 | synonymous_variant (в 1/6 тр.: stop_gained) | p.Gly139= | 1.51e-04 | нет записи |
| 23 | rs116048331 | 22:21970233 | C>T | TOP3B | synonymous_variant | p.Leu186= | 4.65e-05 | Likely benign |
| 24 | rs61747143 | 22:23146672 | C>T | RAB36 | missense_variant | p.Ala19Val | 4.75e-04 | нет записи |
| 25 | rs114023206 | 22:23152491 | C>T | RAB36 | synonymous_variant | p.Gly64= | 8.49e-05 | нет записи |
| 26 | rs5759612 | 22:23160983 | A>G | RAB36 | missense_variant | p.Asn242Asp | 0.503 | нет записи |
| 27 | rs115180746 | 22:24184189 | C>G | SUSD2 | missense_variant | p.Arg165Gly | 0.00125 | нет записи |
| 28 | rs8141797 | 22:24186073 | A>G | SUSD2 | missense_variant | p.Asn466Ser | 0.0702 | Benign |
| 29 | rs114572804 | 22:24187599 | C>T | SUSD2 | synonymous_variant | p.Leu640= | 1.24e-06 | нет записи |
| 30 | rs116796967 | 22:30263994 | C>T | OSM | synonymous_variant | p.Pro216= | 8.45e-04 | нет записи |
| 31 | rs2240345 | 22:30461386 | A>C | SEC14L3 | missense_variant | p.Asp335Glu | 0.641 | нет записи |
| 32 | rs4820853 | 22:30468623 | A>G | SEC14L3 | missense_variant | p.Ile103Thr | 0.355 | нет записи |
| 33 | rs115083767 | 22:30470253 | G>A | SEC14L3 | missense_variant, splice_region_variant | p.Arg45Trp | 1.00e-04 | нет записи |
| 34 | rs115862749 | 22:30555417 | G>A | GAL3ST1 | synonymous_variant | p.Leu270= | 0.00116 | нет записи |
| 35 | rs114565111 | 22:30555495 | G>C | GAL3ST1 | missense_variant | p.Arg244Gly | 2.71e-04 | Uncertain significance |
| 36 | rs11913728 | 22:31091696 | C>T | SMTN | missense_variant | p.Ala494Val | 0.0018 | нет записи |
| 37 | rs116593437 | 22:31091747 | G>A | SMTN | missense_variant | p.Arg511His | 5.88e-04 | Benign |
| 38 | rs5997927 | 22:31262170 | C>T | LIMK2 | synonymous_variant (в 2/36 тр.: missense_variant) | p.Asn196= | 4.96e-05 | нет записи |
| 39 | rs114246562 | 22:33274442 | G>A | LARGE1 | synonymous_variant | p.Ala752= | 6.38e-05 | Likely benign |
| 40 | rs63446460 | 22:33650610 | C>G | LARGE1 | synonymous_variant | p.Thr55= | 0.00261 | Benign/Likely benign |
| 41 | rs6001200 | 22:38699844 | G>C | JOSD1 | missense_variant | p.Ser48Arg | 0.00484 | нет записи |
| 42 | rs114180421 | 22:38699942 | A>G | JOSD1 | synonymous_variant | p.Leu16= | 3.03e-04 | нет записи |
| 43 | rs17565 | 22:39231816 | T>C | PDGFB | missense_variant | p.Ile88Val | 3.84e-04 | Benign/Likely benign |
| 44 | rs112945971 | 22:39744158 | G>A | ENTHD1 | synonymous_variant | p.Leu449= | 9.97e-05 | нет записи |
| 45 | rs114100360 | 22:39835936 | C>A | ENTHD1 | missense_variant | p.Leu205Phe | 6.22e-07 | нет записи |
| 46 | rs8139570 | 22:39887557 | A>G | ENTHD1 | synonymous_variant | p.His64= | 0.00189 | нет записи |
| 47 | rs115837035 | 22:40021368 | G>A | FAM83F | synonymous_variant | p.Thr286= | 1.33e-04 | нет записи |
| 48 | rs5995794 | 22:40021816 | A>G | FAM83F | missense_variant | p.Arg436Gly | 0.278 | нет записи |
| 49 | rs114043304 | 22:44920488 | A>G | PHF21B | splice_region_variant, synonymous_variant (в 1/11 тр.: missense_variant) | p.Ala41= | 1.80e-05 | нет записи |
| 50 | rs35195493 | 22:50177576 | C>G | PANX2 | synonymous_variant | p.Arg288= | 7.86e-04 | нет записи |

---

## 5. Отчёт

Краткий отчёт с разбором трёх вариантов и заключением в [`report.md`](report.md)

Разобранные варианты:
- rs115706909 (SDF2L1): stop_gained только в одном второстепенном транскрипте, в MANE Select синонимичная замена, записи в ClinVar нет
- rs2231495 (ADA2, p.His335Arg): в кэше VEP выглядит как конфликт интерпретаций, в ClinVar для этого аллеля Benign/Likely benign
- rs115157927 (HIRA, p.Ser425Thr): вариант неопределённой значимости (VUS)