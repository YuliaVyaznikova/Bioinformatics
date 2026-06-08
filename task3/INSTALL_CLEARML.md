# Инструкция по установке ClearML

ClearML - платформа для управления пайплайнами, подходит для биоинформатики.

## 1. Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install clearml clearml-agent
```

## 2. Настройка

```bash
clearml-init
```

Потребуются данные из аккаунта на https://app.clear.ml:

| Параметр | Где взять |
|---|---|
| API Server URL | Settings > Workspace |
| Web Application URL | https://app.clear.ml |
| Files Server URL | https://files.clear.ml |
| Access Key | Settings > Workspace Credentials |
| Secret Key | Settings > Workspace Credentials |

## 3. Проверка

```bash
python -c "import clearml; print(clearml.__version__)"
clearml-config
```

## 4. Биоинформатические инструменты

```bash
conda create -n bioinf3 -c bioconda fastqc minimap2 samtools freebayes -y
conda activate bioinf3
```

## 5. Запуск пайплайнов

```bash
conda activate bioinf3
python hello_pipeline.py
python clearml_pipeline.py
```

## Ссылки

- https://clear.ml
- https://clear.ml/docs/latest/docs/guides/pipeline/
- https://github.com/allegroai/clearml
- https://app.clear.ml