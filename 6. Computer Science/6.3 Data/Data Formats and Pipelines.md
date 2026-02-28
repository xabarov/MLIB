# Форматы данных и пайплайны

**Контекст (EN)**: Data pipeline, formats, tools for ML.

## Ответ

### Row-based vs Column-based

| | Row-based | Column-based |
|---|-----------|--------------|
| Примеры | CSV, JSON, Avro | Parquet, ORC |
| Запись | Эффективна | Медленнее (много колонок) |
| Чтение | Целые строки | Выборочные колонки |
| Когда использовать | Write-heavy, доступ по строке | Read-heavy, аналитика, feature extraction |

**Row-based** — данные хранятся построчно; удобно для transactional workload.  
**Column-based** — данные хранятся по колонкам; эффективно при выборке нескольких признаков по всем объектам (ML: извлечение одной фичи).

### Parquet, ORC

- **Сжатие** по колонкам (тип одинаковый в колонке → лучше сжатие).
- **Predicate pushdown** — фильтрация на уровне хранилища до чтения.
- **Партиционирование** по полям (дата, категория).

### pandas, dask

- **pandas** — один датасет в памяти; до ~ГБ.
- **dask** — отложенные вычисления, разбиение на чанки; масштабируется на кластер; API похож на pandas.

### SQL для ML-пайплайнов

- Агрегации, джойны, фильтрация перед загрузкой в Python.
- Feature store, версионирование через SQL-схему.
- ETL: extract из БД → transform (SQL или Python) → load в хранилище для обучения.

### Spark, Hadoop

- **Spark** — in-memory, быстрее MapReduce; Spark SQL, MLlib для feature engineering и простых моделей.
- **Hadoop (HDFS, MapReduce)** — распределённое хранилище и batch-обработка; Hive для SQL поверх данных.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
