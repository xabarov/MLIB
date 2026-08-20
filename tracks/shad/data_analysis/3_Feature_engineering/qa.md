# Задачи: Feature Engineering и категориальные признаки

## Задача 1 (Лёгкая). Log-трансформация

**Условие.** Признак `income` имеет следующие значения: 30 000, 45 000, 120 000, 850 000, 2 000 000. Примените трансформацию `log1p` и вычислите получившиеся значения (с точностью до 2 знаков). Почему эта трансформация полезна?

### Решение

```python
import numpy as np

income = [30_000, 45_000, 120_000, 850_000, 2_000_000]
log_income = [round(np.log1p(x), 2) for x in income]
print(log_income)
```

Шаги:
- `log1p(30000)   = ln(30001)   ≈ 10.31`
- `log1p(45000)   = ln(45001)   ≈ 10.71`
- `log1p(120000)  = ln(120001)  ≈ 11.70`
- `log1p(850000)  = ln(850001)  ≈ 13.65`
- `log1p(2000000) = ln(2000001) ≈ 14.51`

Исходный диапазон: 30 000 → 2 000 000 (множитель 67x). После `log1p`: 10.31 → 14.51 (множитель 1.4x). Распределение становится более симметричным, что помогает линейным моделям и улучшает числовую устойчивость.

### Ответ

`[10.31, 10.71, 11.70, 13.65, 14.51]`. Трансформация сжимает хвост распределения, убирает правостороннюю асимметрию и делает связь с целевой переменной более линейной.

---

## Задача 2 (Лёгкая). One-Hot Encoding вручную

**Условие.** Дана переменная `color`: `['red', 'blue', 'green', 'red', 'blue']`. Постройте OHE-матрицу вручную (с `drop='first'`) и напишите код sklearn, который делает то же самое.

### Решение

Уникальные категории в алфавитном порядке: `blue`, `green`, `red`. `drop='first'` убирает `blue`.

Итоговые столбцы: `color_green`, `color_red`.

| Исходный | color_green | color_red |
|----------|-------------|-----------|
| red      | 0           | 1         |
| blue     | 0           | 0         |
| green    | 1           | 0         |
| red      | 0           | 1         |
| blue     | 0           | 0         |

```python
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

df = pd.DataFrame({'color': ['red', 'blue', 'green', 'red', 'blue']})
enc = OneHotEncoder(drop='first', sparse_output=False)
X_ohe = enc.fit_transform(df[['color']])
cols = enc.get_feature_names_out(['color'])
result = pd.DataFrame(X_ohe, columns=cols, dtype=int)
print(result)
```

### Ответ

Матрица 5×2 (столбцы `color_green`, `color_red`) с бинарными значениями, показанными в таблице выше.

---

## Задача 3 (Лёгкая). Ordinal vs OHE: выбор метода

**Условие.** У вас есть три признака: `(A) shirt_size ∈ {S, M, L, XL}`, `(B) city ∈ {Moscow, SPb, Kazan, Novosibirsk}`, `(C) education ∈ {school, bachelor, master, phd}`. Для каждого укажите подходящий метод кодирования и объясните почему.

### Решение

Ключевой вопрос: есть ли естественный порядок между категориями?

- **(A) shirt_size**: порядок S < M < L < XL чётко определён — применяем `OrdinalEncoder(categories=[['S','M','L','XL']])`. Числовые коды 0–3 корректно отражают размер.

- **(B) city**: порядка нет, города равноправны — применяем `OneHotEncoder`. Ordinal-кодирование сообщило бы модели ложную информацию вида «Kazan(0) < Moscow(1) < Novosibirsk(2) < SPb(3)».

- **(C) education**: порядок school < bachelor < master < phd существует — применяем `OrdinalEncoder(categories=[['school','bachelor','master','phd']])`.

```python
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder

enc_a = OrdinalEncoder(categories=[['S', 'M', 'L', 'XL']])
enc_b = OneHotEncoder(handle_unknown='ignore')
enc_c = OrdinalEncoder(categories=[['school', 'bachelor', 'master', 'phd']])
```

### Ответ

A → OrdinalEncoder (упорядоченный), B → OneHotEncoder (номинальный), C → OrdinalEncoder (упорядоченный).

---

## Задача 4 (Средняя). Вычисление Target Encoding со сглаживанием

**Условие.** Датасет (train):

| city     | target |
|----------|--------|
| Moscow   | 5      |
| Moscow   | 7      |
| Moscow   | 6      |
| SPb      | 3      |
| SPb      | 4      |
| Kazan    | 2      |

Глобальное среднее $\bar{y} = 4.5$, параметр сглаживания $\lambda = 2$.
Вычислите сглаженный Target Encoding для каждого города.

### Решение

Формула: $\hat{\mu}_c^{(\lambda)} = \dfrac{n_c \cdot \bar{y}_c + \lambda \cdot \bar{y}_{\text{global}}}{n_c + \lambda}$

**Moscow** ($n_c = 3$, $\bar{y}_c = (5+7+6)/3 = 6.0$):
$$\hat{\mu}_{\text{Moscow}} = \frac{3 \cdot 6.0 + 2 \cdot 4.5}{3 + 2} = \frac{18 + 9}{5} = \frac{27}{5} = 5.4$$

**SPb** ($n_c = 2$, $\bar{y}_c = (3+4)/2 = 3.5$):
$$\hat{\mu}_{\text{SPb}} = \frac{2 \cdot 3.5 + 2 \cdot 4.5}{2 + 2} = \frac{7 + 9}{4} = 4.0$$

**Kazan** ($n_c = 1$, $\bar{y}_c = 2.0$):
$$\hat{\mu}_{\text{Kazan}} = \frac{1 \cdot 2.0 + 2 \cdot 4.5}{1 + 2} = \frac{2 + 9}{3} = \frac{11}{3} \approx 3.67$$

Kazan сильнее всего притягивается к глобальному среднему — она редкая (1 наблюдение), поэтому оценка ненадёжна.

```python
import pandas as pd

df = pd.DataFrame({
    'city': ['Moscow','Moscow','Moscow','SPb','SPb','Kazan'],
    'target': [5, 7, 6, 3, 4, 2]
})
lam = 2
global_mean = df['target'].mean()   # 4.5
stats = df.groupby('city')['target'].agg(['mean', 'count'])
stats['enc'] = (stats['count'] * stats['mean'] + lam * global_mean) / (stats['count'] + lam)
print(stats['enc'])
```

### Ответ

Moscow → 5.40, SPb → 4.00, Kazan → 3.67.

---

## Задача 5 (Средняя). Взрыв размерности при OHE

**Условие.** В датасете 200 000 строк и 1 категориальный признак с 5 000 уникальными значениями. Вы применяете One-Hot Encoding (dense float64). Сколько памяти потребуется для этой матрицы? Сколько потребует sparse-представление (uint8, одна единица на строку)? Предложите альтернативный подход к кодированию.

### Решение

**Dense float64:**
$$\text{MB} = \frac{200\,000 \times 5\,000 \times 8\text{ байт}}{1024^2} = \frac{8\,000\,000\,000}{1\,048\,576} \approx 7\,629 \text{ MB} \approx 7.4 \text{ GB}$$

**Sparse uint8 (хранит только ненулевые элементы, 200 000 единиц):**
$$\text{MB} = \frac{200\,000 \times 1\text{ байт}}{1024^2} \approx 0.19 \text{ MB}$$

Выигрыш в памяти: ~40 000x.

```python
from sklearn.preprocessing import OneHotEncoder
import numpy as np

enc_sparse = OneHotEncoder(sparse_output=True, dtype=np.uint8)
# X_sparse займёт ~0.2 MB вместо 7.4 GB
```

**Альтернативы для 5000 категорий:**
1. **Target Encoding** — 1 столбец, хорошо работает с деревьями
2. **Binary Encoding** — $\lceil\log_2 5000\rceil = 13$ столбцов
3. **Frequency Encoding** — 1 столбец (доля в train)
4. **Hashing Trick** с `n_features=128` — фиксированный размер без словаря

### Ответ

Dense: ~7.4 GB. Sparse uint8: ~0.19 MB. Рекомендация: Target Encoding или Binary Encoding для 5 000 категорий.

---

## Задача 6 (Средняя). Циклические признаки времени

**Условие.** Вы предсказываете потребление электроэнергии по часу суток. Наивный подход: записать час как целое число 0–23. Почему это плохо? Как правильно закодировать час?

### Решение

**Проблема наивного подхода:** модель видит, что час 23 и час 0 разделяет расстояние 23 — огромное. Но фактически полночь — один момент времени, и суточный паттерн потребления непрерывен. Линейные модели не смогут это выучить; деревья потребуют дополнительных разбивок.

**Решение: sin/cos кодирование:**
$$h_{\sin} = \sin\!\left(\frac{2\pi \cdot \text{hour}}{24}\right), \quad h_{\cos} = \cos\!\left(\frac{2\pi \cdot \text{hour}}{24}\right)$$

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({'hour': list(range(24))})
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# Проверка: часы 0 и 23 близки?
h0  = np.array([df.loc[0,  'hour_sin'], df.loc[0,  'hour_cos']])
h23 = np.array([df.loc[23, 'hour_sin'], df.loc[23, 'hour_cos']])
dist = np.linalg.norm(h0 - h23)
print(f'Расстояние 0–23: {dist:.4f}')   # ~0.261 — близко!
print(f'Расстояние 0–12: {np.linalg.norm(h0 - np.array([df.loc[12,"hour_sin"], df.loc[12,"hour_cos"]])):.4f}')  # 2.0 — максимальное
```

Пара (sin, cos) однозначно задаёт позицию на окружности: часы 23 и 0 оказываются рядом.

### Ответ

Наивное кодирование разрывает циклическую структуру. Правильный подход: два столбца `hour_sin = sin(2π·h/24)` и `hour_cos = cos(2π·h/24)`, расстояние между 23 и 0 в этом пространстве минимально.

---

## Задача 7 (Средняя). Mutual Information vs Корреляция

**Условие.** Признак $X$ равномерно распределён на $[-1, 1]$, целевая переменная $Y = X^2 + \varepsilon$, где $\varepsilon \sim \mathcal{N}(0, 0.01)$. Оцените корреляцию Пирсона $r(X, Y)$ и объясните, почему MI обнаружит связь, а корреляция — нет. Подтвердите численно.

### Решение

Корреляция Пирсона измеряет **линейную** связь. Если $X \sim U(-1, 1)$, то $E[X] = 0$ и $E[X \cdot X^2] = E[X^3] = 0$ (нечётный момент симметричного распределения). Следовательно, $r(X, X^2) = 0$ несмотря на сильную функциональную зависимость.

$$r(X, Y) \approx 0, \quad I(X; Y) \gg 0$$

```python
import numpy as np
from sklearn.feature_selection import mutual_info_regression

rng = np.random.default_rng(42)
X = rng.uniform(-1, 1, size=(5000, 1))
y = X.ravel() ** 2 + rng.normal(0, 0.1, size=5000)

pearson_r = np.corrcoef(X.ravel(), y)[0, 1]
mi = mutual_info_regression(X, y, random_state=42)[0]

print(f'Pearson r: {pearson_r:.4f}')  # ~0.0 (близко к нулю)
print(f'Mutual Information: {mi:.4f}')  # >0 (обнаруживает зависимость)
```

MI основана на совместном распределении $p(x, y)$ и выявляет **любую** статистическую зависимость, не только линейную.

### Ответ

$r(X, Y) \approx 0$ из-за симметрии $Y = X^2$ — квадратичная связь не улавливается. MI > 0, поскольку MI измеряет общую (нелинейную) зависимость через KL-дивергенцию между совместным и произведением маргинальных распределений.

---

## Задача 8 (Сложная). Лейбл-лик при Target Encoding: диагностика и исправление

**Условие.** Исследователь закодировал категориальный признак `region` с помощью Target Encoding на всём датасете, затем обучил градиентный бустинг и получил ROC-AUC = 0.94 на кросс-валидации. При деплое модель показала 0.71. Объясните причину. Напишите правильный код.

### Решение

**Причина оптимистичного bias:** при вычислении `E[y | region=c]` на **всех** данных (включая объект $i$) значение `y_i` участвует в формировании признака для того же объекта $i$. Это прямая утечка целевой переменной в признак. Модель «подглядывает» в ответы, поэтому CV-метрика завышена. На продакшн данных такой информации нет → просадка.

```python
# НЕПРАВИЛЬНО (data leakage):
df['region_enc'] = df.groupby('region')['target'].transform('mean')
```

**Правильное решение №1 — CV-based encoding:**

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

def target_encode_oof(df, col, target, n_splits=5, smoothing=20):
    global_mean = df[target].mean()
    encoded = pd.Series(index=df.index, dtype=float)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    for tr_idx, val_idx in kf.split(df):
        tr_df = df.iloc[tr_idx]
        stats = tr_df.groupby(col)[target].agg(['sum', 'count'])
        stats['enc'] = (stats['sum'] + smoothing * global_mean) / (stats['count'] + smoothing)
        encoded.iloc[val_idx] = df.iloc[val_idx][col].map(stats['enc']).fillna(global_mean)
    return encoded

# На train: OOF encoding
X_train['region_enc'] = target_encode_oof(X_train.assign(target=y_train), 'region', 'target')

# На test: энкодер обученный на всём train
global_mean = y_train.mean()
stats = X_train.assign(target=y_train).groupby('region')['target'].agg(['sum','count'])
stats['enc'] = (stats['sum'] + 20 * global_mean) / (stats['count'] + 20)
X_test['region_enc'] = X_test['region'].map(stats['enc']).fillna(global_mean)
```

**Правильное решение №2 — category_encoders с Pipeline:**

```python
from category_encoders import TargetEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

pipe = Pipeline([
    ('enc',   TargetEncoder(cols=['region'], smoothing=20)),
    ('model', GradientBoostingClassifier(random_state=42)),
])
# Pipeline гарантирует, что enc.fit() вызывается только на tr-фолде:
scores = cross_val_score(pipe, X, y, cv=5, scoring='roc_auc')
```

### Ответ

Лейбл-лик возник из-за вычисления средней метки с использованием самого объекта. Решение: OOF (out-of-fold) encoding на тренировочных данных или Pipeline с category_encoders, где `fit` вызывается только на train-фолде.

---

## Задача 9 (Сложная). Полный Pipeline с ColumnTransformer

**Условие.** Датасет содержит:
- Числовые: `age`, `income`, `distance` (правостороннее распределение)
- Категориальные номинальные: `city` (50 уник.), `product_type` (10 уник.)
- Категориальные порядковые: `education` (4 уровня)
- Дата: `signup_date`

Постройте полный sklearn Pipeline с правильными трансформациями для каждого типа признаков.

### Решение

```python
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    FunctionTransformer, StandardScaler, OneHotEncoder, OrdinalEncoder
)
from sklearn.ensemble import RandomForestClassifier

# --- Функции для дат ---
def extract_date_features(X):
    X = pd.DataFrame(X, columns=['signup_date'])
    X['signup_date'] = pd.to_datetime(X['signup_date'])
    result = pd.DataFrame()
    result['dayofweek']   = X['signup_date'].dt.dayofweek
    result['month_sin']   = np.sin(2 * np.pi * X['signup_date'].dt.month / 12)
    result['month_cos']   = np.cos(2 * np.pi * X['signup_date'].dt.month / 12)
    result['is_weekend']  = (X['signup_date'].dt.dayofweek >= 5).astype(int)
    return result.values

# --- Sub-pipelines ---
numeric_pipe = Pipeline([
    ('log',    FunctionTransformer(np.log1p)),
    ('scaler', StandardScaler()),
])

cat_nominal_pipe = Pipeline([
    ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
])

cat_ordinal_pipe = Pipeline([
    ('ord', OrdinalEncoder(
        categories=[['school', 'bachelor', 'master', 'phd']],
        handle_unknown='use_encoded_value',
        unknown_value=-1,
    )),
])

date_pipe = Pipeline([
    ('date_feats', FunctionTransformer(extract_date_features)),
])

# --- ColumnTransformer ---
preprocessor = ColumnTransformer([
    ('num',     numeric_pipe,     ['age', 'income', 'distance']),
    ('cat_nom', cat_nominal_pipe, ['city', 'product_type']),
    ('cat_ord', cat_ordinal_pipe, ['education']),
    ('date',    date_pipe,        ['signup_date']),
], remainder='drop')

# --- Full Pipeline ---
full_pipe = Pipeline([
    ('preproc', preprocessor),
    ('model',   RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
])

# full_pipe.fit(X_train, y_train)
# full_pipe.predict_proba(X_test)
```

Все трансформации выполняются автоматически: `fit` только на train-данных, `transform` на test.

### Ответ

ColumnTransformer объединяет четыре sub-pipeline: log+scaler для числовых, OHE для номинальных, OrdinalEncoder для порядковых, ручное извлечение признаков для дат. Всё упаковано в один Pipeline для корректной кросс-валидации.

---

## Задача 10 (Синтез). Проектирование стратегии Feature Engineering

**Условие.** Вы участвуете в соревновании: предсказать вероятность дефолта по кредиту. Признаки: `age`, `salary`, `loan_amount`, `loan_term_months`, `city` (500 уникальных), `employment_type` (5 категорий), `issue_date`. Целевая переменная: `default` (0/1), дисбаланс 1:15. Опишите полную стратегию Feature Engineering: какие трансформации, какие новые признаки, какой метод кодирования city и почему. Какие признаки вы добавите первыми?

### Решение

**Шаг 1. Анализ и трансформации базовых признаков:**

```python
import pandas as pd
import numpy as np

# Монотонные трансформации для числовых (правостороннее распределение):
df['log_salary']      = np.log1p(df['salary'])
df['log_loan_amount'] = np.log1p(df['loan_amount'])

# Взаимодействия — финансово осмысленные:
df['dti_ratio']       = df['loan_amount'] / (df['salary'] * df['loan_term_months'] / 12 + 1)
df['monthly_payment'] = df['loan_amount'] / df['loan_term_months']
df['payment_to_income'] = df['monthly_payment'] / (df['salary'] / 12 + 1)
df['loan_per_year']   = df['loan_amount'] / (df['age'] - 18 + 1)  # кредит на год жизни
```

**Шаг 2. Кодирование `city` (500 уникальных):**

OHE → 500 столбцов — слишком много для 1:15 дисбаланса (мало примеров класса 1 на регион).

Выбор: **Target Encoding со сглаживанием** (OOF-стратегия):

```python
# Target = default rate по городу; редкие города притягиваются к глобальному дефолт-рейту
# smoothing=50 — агрессивное сглаживание из-за дисбаланса
```

**Шаг 3. `employment_type` (5 категорий):**

OHE (5 → 4 столбца с `drop='first'`) — безопасно при таком числе категорий.

**Шаг 4. Дата:**

```python
df['issue_date'] = pd.to_datetime(df['issue_date'])
df['issue_month_sin'] = np.sin(2 * np.pi * df['issue_date'].dt.month / 12)
df['issue_month_cos'] = np.cos(2 * np.pi * df['issue_date'].dt.month / 12)
df['issue_quarter']   = df['issue_date'].dt.quarter
df['loan_age_days']   = (pd.Timestamp.now() - df['issue_date']).dt.days  # просрочка
```

**Шаг 5. Отбор признаков:**

```python
from sklearn.feature_selection import mutual_info_classif

mi = mutual_info_classif(X_train, y_train, random_state=42)
top_features = pd.Series(mi, index=X_train.columns).nlargest(30).index.tolist()
```

**Приоритет признаков по финансовой логике:**
1. `payment_to_income` — главный предиктор дефолта
2. `dti_ratio` — Debt-to-Income ratio
3. `city_target_enc` — региональный риск
4. `log_salary` — платёжеспособность
5. `loan_term_months` — срок риска

### Ответ

Стратегия: (1) log-трансформации для перекошенных числовых; (2) осмысленные финансовые взаимодействия (DTI, payment-to-income); (3) Target Encoding с OOF и сглаживанием для `city` — OHE создаст 500 разреженных столбцов при критически малом числе дефолтов; (4) OHE для `employment_type`; (5) циклические признаки из даты; (6) отбор через MI. Первыми добавляем `dti_ratio` и `payment_to_income` — они несут максимальную предметную информацию.

---

<details>
<summary>Что тренируют эти задачи</summary>

| Задача | Навык |
|--------|-------|
| 1. Log-трансформация | Понимание монотонных преобразований и их эффекта на распределение |
| 2. OHE вручную + sklearn | Механика One-Hot Encoding, параметр `drop='first'` |
| 3. Ordinal vs OHE | Выбор метода кодирования исходя из природы признака |
| 4. Сглаженный Target Encoding | Вычисление по формуле, понимание сглаживания для редких категорий |
| 5. Взрыв размерности | Расчёт памяти, понимание sparse vs dense, выбор альтернатив |
| 6. Циклические признаки | Sin/Cos кодирование для временных и угловых данных |
| 7. MI vs корреляция Пирсона | Нелинейные зависимости, понимание ограничений корреляции |
| 8. Лейбл-лик | Диагностика data leakage, OOF-стратегия, Pipeline |
| 9. ColumnTransformer | Построение полного ML-пайплайна с разными типами признаков |
| 10. Синтез стратегии | Комплексное проектирование Feature Engineering под реальную задачу |

</details>
