# Предсказание и парное выравнивание третичной структуры белка

Используются ESMFold, RoseTTAFold2 и jFATCAT-flexible.

## 1. Исходные данные

Анализируемая последовательность содержит 100 аминокислот и находится в файле [`sequence.fasta`](sequence.fasta).

```
MENEDGYMTLSFKNRCKSKQKSKDFSLYPQYYCLLLIFGCIVILIFIMTGIDLKFWHKKMDFSQNVNVSSLSGHNYLCPNDWLLNEGKCYWFSTSFKTWK
```

## 2. Инструменты

| Этап | Инструмент |
|---|---|
| Первое предсказание структуры | ESMFold, Google Colab |
| Второе предсказание структуры | RoseTTAFold2, Google Colab |
| Парное структурное выравнивание | jFATCAT-flexible, [RCSB PDB Pairwise Structure Alignment Tool](https://www.rcsb.org/alignment) |
| Визуализация | Mol* (RCSB) и PyMOL |

## 3. Параметры вычислений

Предсказания выполняются в Google Colab с использованием GPU.

ESMFold использует модель `esmfold_v1` и 3 recycle. Веса модели загружаются непосредственно в вычислительной среде без обращения к ESMFold API. Для совместимости с текущим PyTorch используется сборка OpenFold с флагом C++20 без изоляции сборки. Ноутбук: [`esmfold.ipynb`](esmfold.ipynb).

RoseTTAFold2 использует параметры `RF2_apr23`, MSA через MMseqs2, 6 recycles, 1 модель и random seed 0. Отдельное окружение Python 3.10, PyTorch 2.2, CUDA 12.1 и DGL 2.0 создаётся через `micromamba`. Ноутбук: [`rosettafold2.ipynb`](rosettafold2.ipynb). Код вычислений: [`rosettafold2_driver.py`](rosettafold2_driver.py).

Фактический запуск ESMFold с сохранёнными выводами: [`esmfold_executed.ipynb`](esmfold_executed.ipynb).

Исходные ноутбуки ColabFold: [ESMFold](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/ESMFold.ipynb) и [RoseTTAFold2](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/RoseTTAFold2.ipynb).

## 4. Результат ESMFold

Результаты находятся в [`esmfold/`](esmfold/):

| Файл | Содержимое |
|---|---|
| `ptm0.262_r3_default.pdb` | Предсказанная структура, цепь A, 100 остатков |
| `ptm0.262_r3_default.pae.txt` | Матрица predicted aligned error, 100 × 100 |
| `ptm0.262_r3_default.png` | Графики pLDDT, PAE и контактов |

Проверка PDB подтверждает полное совпадение последовательности с исходной. Структура содержит 837 атомов. PTM = 0,262, средний pLDDT по Cα = 60,18.

## 5. Метод структурного выравнивания

Для сравнения предсказаний используется jFATCAT-flexible в RCSB с Assembly 1 и Chain A для обеих структур. Регистрируются координаты выровненных структур, последовательность выравнивания, матрицы трансформации и метрики сходства. Визуализация выполняется с различной окраской двух исходных структур.
