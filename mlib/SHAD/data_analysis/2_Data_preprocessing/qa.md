# Задачи к лекции 2. Предобработка и очистка данных

---

## Задача 1. IQR и обнаружение выбросов (лёгкая)

**Условие.** Дан ряд значений температур (°C):

```
14, 16, 15, 18, 17, 16, 14, 15, 13, 82, 16, 17
```

Вычислите межквартильный размах (IQR) и определите, какие значения являются выбросами по правилу 1.5·IQR.

### Решение

Шаг 1. Отсортируем: 13, 14, 14, 15, 15, 16, 16, 16, 17, 17, 18, 82.

Шаг 2. n = 12. Q1 = медиана нижней половины (6 элементов: 13,14,14,15,15,16):
$$Q_1 = (14 + 15)/2 = 14.5$$

Шаг 3. Q3 = медиана верхней половины (16,16,17,17,18,82):
$$Q_3 = (17 + 17)/2 = 17.0$$

Шаг 4. IQR = Q3 - Q1 = 17.0 - 14.5 = **2.5**

Шаг 5. Границы:
- нижняя: $14.5 - 1.5 \times 2.5 = 14.5 - 3.75 = 10.75$
- верхняя: $17.0 + 1.5 \times 2.5 = 17.0 + 3.75 = 20.75$

Шаг 6. Значения вне [10.75, 20.75]: **82** — выброс.

```python
import pandas as pd

s = pd.Series([14, 16, 15, 18, 17, 16, 14, 15, 13, 82, 16, 17])
q1, q3 = s.quantile(0.25), s.quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print(s[(s < lower) | (s > upper)])  # 9    82
```

### Ответ

IQR = 2.5. Граница выброса: (10.75, 20.75). Выброс: **82**.

---

## Задача 2. Определение механизма пропуска (лёгкая)

**Условие.** Для каждого из сценариев определите тип пропуска (MCAR / MAR / MNAR):

1. В датасете медицинских обследований у пациентов с тяжёлой формой заболевания не заполнен результат теста (они не явились на осмотр из-за плохого самочувствия).
2. В опросе уровня зарплаты 20% анкет случайно повреждены при сканировании.
3. В датасете HR-опроса мужчины значимо реже сообщают об эмоциональном выгорании, чем женщины (пол зафиксирован у всех).

### Решение

Сценарий 1: Пропуск в результате теста зависит от тяжести заболевания, а тяжесть — это и есть то самое значение, которое отсутствует. Чем хуже пациент себя чувствует (истинно высокое значение тяжести), тем больше вероятность пропуска. Пропуск зависит от *себя* — **MNAR**.

Сценарий 2: Повреждение при сканировании — внешнее случайное событие, не связанное ни с уровнем зарплаты, ни с другими переменными. — **MCAR**.

Сценарий 3: Пропуск в «эмоциональном выгорании» зависит от *пола* — переменной, которая полностью наблюдается. Если мы знаем пол, можем оценить вероятность пропуска. Это и есть MAR: пропуск зависит от наблюдаемой переменной, но не от самого значения выгорания — **MAR**.

### Ответ

1. **MNAR** — пропуск зависит от значения пропущенной переменной.  
2. **MCAR** — пропуск не зависит ни от чего.  
3. **MAR** — пропуск зависит от наблюдаемого признака (пол).

---

## Задача 3. Выбор стратегии импутации (лёгкая–средняя)

**Условие.** Датасет содержит признаки: `salary` (числовой, правосторонняя асимметрия, есть выбросы), `department` (категориальный, 10 уникальных), `years_exp` (числовой, близкий к нормальному), `has_degree` (бинарный, 0/1). В каждом признаке ~15% пропусков, анализ показал MAR. Предложите стратегию импутации для каждого признака и запишите код с `sklearn`.

### Решение

**`salary`** — числовой, скошенный с выбросами: среднее сильно сдвинуто выбросами, лучше использовать **медиану**. При MAR оба дают несмещённые оценки среднего при нормальном распределении, но медиана устойчива.

**`department`** — категориальный: `most_frequent` или специальная категория `'Unknown'`.

**`years_exp`** — близкий к нормальному: **среднее** или **KNN** (KNN учтёт корреляцию с `department`).

**`has_degree`** — бинарный: `most_frequent` (0 или 1).

```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

num_median = ['salary']
num_knn    = ['years_exp']
cat_cols   = ['department', 'has_degree']

# Для KNN нужны числовые признаки — сначала кодируем категориальные
enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

preprocessor = ColumnTransformer([
    ('sal',  SimpleImputer(strategy='median'), num_median),
    ('exp',  KNNImputer(n_neighbors=7),        num_knn),
    ('cat',  SimpleImputer(strategy='most_frequent'), cat_cols),
], remainder='passthrough')
```

При MAR предпочтительнее KNNImputer или IterativeImputer, так как они учитывают зависимость между признаками.

### Ответ

| Признак | Стратегия | Обоснование |
|---------|-----------|-------------|
| `salary` | `median` | Устойчивость к выбросам |
| `department` | `most_frequent` | Категориальный |
| `years_exp` | `KNN` | MAR, корреляция с другими признаками |
| `has_degree` | `most_frequent` | Бинарный |

---

## Задача 4. Исправление data leakage (средняя)

**Условие.** Аналитик написал следующий код. Найдите ошибку и исправьте её.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

X = np.random.randn(1000, 10)
y = (X[:, 0] + X[:, 1] > 0).astype(int)

# Масштабирование всего датасета
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=0
)

model = LogisticRegression()
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

### Решение

**Ошибка:** `scaler.fit_transform(X)` вызывается до разбивки на train/test. Это значит, что при вычислении среднего и стандартного отклонения используется информация из тестовой выборки. Модель косвенно «видит» test-данные через параметры скейлера — **data leakage**.

В реальной задаче мы не знаем тестовых данных в момент обучения. Любая статистика (mean, std, медиана, квантили) должна вычисляться только по обучающей части.

**Исправленный код:**

```python
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import numpy as np

X = np.random.randn(1000, 10)
y = (X[:, 0] + X[:, 1] > 0).astype(int)

# ПРАВИЛЬНО: сначала split, потом fit скейлера только на train
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0
)

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model',  LogisticRegression()),
])
pipe.fit(X_train, y_train)
print(pipe.score(X_test, y_test))
```

Pipeline гарантирует правильный порядок при кросс-валидации.

### Ответ

Ошибка: масштабирование производится до train/test split. Исправление: разбить данные сначала, затем `fit_transform` — только на `X_train`, `transform` — на `X_test`. Лучшее решение — обернуть в `Pipeline`.

---

## Задача 5. Z-score и сравнение с IQR (средняя)

**Условие.** Набор данных: `[2, 3, 4, 3, 3, 100, 4, 3, 2, 4]`.

a) Найдите z-score каждого элемента. Какой элемент является выбросом при пороге |z| > 2?

b) Найдите IQR-границы. Одинаковы ли результаты двух методов?

c) Объясните, почему z-score может «не заметить» выброс в малой выборке.

### Решение

**a) Z-score:**

```python
import numpy as np
from scipy import stats

data = np.array([2, 3, 4, 3, 3, 100, 4, 3, 2, 4])
z = stats.zscore(data)
print(z.round(2))
# mean ≈ 12.8, std ≈ 29.6
# z[5] ≈ (100 - 12.8) / 29.6 ≈ 2.95 > 2 → выброс
```

Среднее: $(2+3+4+3+3+100+4+3+2+4)/10 = 128/10 = 12.8$

Std: $\sigma = \sqrt{\frac{\sum (x_i - 12.8)^2}{10}} \approx 29.56$

z(100) = $(100 - 12.8) / 29.56 \approx 2.95$ — выброс при |z| > 2.

**b) IQR:**

Отсортированные: 2, 2, 3, 3, 3, 3, 4, 4, 4, 100.
Q1 = 3.0, Q3 = 4.0, IQR = 1.0.
Нижняя граница: 3.0 − 1.5 = 1.5; верхняя: 4.0 + 1.5 = 5.5.
100 > 5.5 — выброс. Результаты совпадают.

**c) Эффект маскировки:**

При малой выборке один большой выброс сдвигает среднее и сильно увеличивает стандартное отклонение. Из-за этого z-score остальных «нормальных» значений оказывается очень маленьким, а z-score самого выброса может не превышать порог 3, особенно если выброс один и выборка мала. IQR лишён этого дефекта: квантили не чувствительны к отдельным экстремальным значениям.

### Ответ

a) z(100) ≈ 2.95 > 2 — выброс. Остальные значения: |z| < 0.4.  
b) Граница IQR: [1.5, 5.5]. 100 — выброс. Методы согласуются.  
c) Выброс увеличивает std, сжимая z-score к нулю для остальных и занижая z для себя — эффект маскировки.

---

## Задача 6. Формула Рубина (средняя–сложная)

**Условие.** Проведено $m = 3$ варианта множественной импутации. Получены оценки среднего и их дисперсии:

| Импутация | $\hat{\mu}_i$ | $W_i$ |
|-----------|--------------|-------|
| 1 | 5.2 | 0.10 |
| 2 | 5.8 | 0.12 |
| 3 | 5.5 | 0.11 |

a) Вычислите $\bar{\theta}$, $\bar{W}$, $B$ и полную дисперсию $T$ по формуле Рубина.

b) Чему равен 95%-й доверительный интервал для $\mu$?

### Решение

**a) Вычисление компонент:**

$$\bar{\theta} = \frac{5.2 + 5.8 + 5.5}{3} = \frac{16.5}{3} = 5.5$$

$$\bar{W} = \frac{0.10 + 0.12 + 0.11}{3} = \frac{0.33}{3} = 0.11$$

$$B = \frac{1}{m-1} \sum_{i=1}^{3} (\hat{\mu}_i - \bar{\theta})^2$$

$(5.2 - 5.5)^2 = 0.09$, $(5.8 - 5.5)^2 = 0.09$, $(5.5 - 5.5)^2 = 0.00$

$$B = \frac{0.09 + 0.09 + 0.00}{2} = \frac{0.18}{2} = 0.09$$

Полная дисперсия:

$$T = \bar{W} + \left(1 + \frac{1}{m}\right) B = 0.11 + \left(1 + \frac{1}{3}\right) \times 0.09 = 0.11 + \frac{4}{3} \times 0.09$$

$$T = 0.11 + 0.12 = 0.23$$

**b) Доверительный интервал (приближённо нормальный):**

$$\hat{\mu} \pm 1.96 \sqrt{T} = 5.5 \pm 1.96 \times \sqrt{0.23} = 5.5 \pm 1.96 \times 0.480 = 5.5 \pm 0.94$$

$$\text{ДИ} \approx [4.56,\ 6.44]$$

### Ответ

$\bar{\theta} = 5.5$, $\bar{W} = 0.11$, $B = 0.09$, $T = 0.23$.  
95%-й ДИ: $[4.56,\ 6.44]$.

---

## Задача 7. Выбор скейлера по задаче (сложная)

**Условие.** Датасет содержит признаки `bmi` (ИМТ, близко к нормальному) и `hospital_cost` (расходы, сильная правосторонняя асимметрия, 5% выбросов — реальные дорогостоящие случаи). Целевой алгоритм — **Ridge-регрессия**. Обоснуйте выбор скейлера для каждого признака и покажите, как применить два разных скейлера.

### Решение

**`bmi`:** Распределение близко к нормальному, выбросов мало — подходит **StandardScaler** (z-нормализация). Ridge-регрессия предполагает, что признаки имеют нулевое среднее и единичную дисперсию; StandardScaler удовлетворяет этому.

**`hospital_cost`:** Сильная асимметрия + 5% реальных выбросов. MinMaxScaler разрушится одним крупным значением. StandardScaler будет смещён из-за выбросов. Лучший выбор — **RobustScaler**: использует медиану и IQR, нечувствителен к хвостам.

Альтернативно: логарифмировать `hospital_cost` (`np.log1p`), что приведёт к нормальному распределению, а потом применить StandardScaler.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

X = pd.DataFrame({
    'bmi':           np.random.randn(500) * 3 + 25,
    'hospital_cost': np.abs(np.random.exponential(5000, 500)),
})
y = X['bmi'] * 10 + X['hospital_cost'] * 0.001 + np.random.randn(500)

preprocessor = ColumnTransformer([
    ('std', StandardScaler(), ['bmi']),
    ('rob', RobustScaler(),   ['hospital_cost']),
])

pipe = Pipeline([
    ('prep',  preprocessor),
    ('model', Ridge(alpha=1.0)),
])
pipe.fit(X, y)
print(pipe.score(X, y))
```

### Ответ

`bmi` → StandardScaler (нормальное, нет выбросов).  
`hospital_cost` → RobustScaler (асимметрия + реальные выбросы не должны исказить масштаб).  
ColumnTransformer позволяет применить разные трансформации к разным признакам внутри одного Pipeline.

---

## Задача 8. Bias при complete-case analysis (сложная)

**Условие.** Переменная $Y$ — уровень стресса (0–10). У людей с высоким стрессом ($Y > 7$) вероятность ответить на вопрос снижается вдвое (механизм MNAR). Истинное $E[Y] = 5$.

a) Выразите $E[Y_{\text{obs}}]$ через $E[Y | Y \leq 7]$ и $P(Y \leq 7)$.

b) Покажите, что полный случай даёт смещённую оценку и направление смещения.

### Решение

**a)** Пусть $R$ — индикатор наблюдения (1 = значение наблюдается). При MNAR:

$$P(R=1 \mid Y \leq 7) = p, \quad P(R=1 \mid Y > 7) = p/2$$

По формуле полного ожидания:

$$E[Y \mid R=1] = \frac{E[Y \cdot P(R=1 \mid Y)]}{P(R=1)}$$

$$= \frac{E[Y \cdot p \cdot \mathbf{1}_{Y \leq 7}] + E[Y \cdot (p/2) \cdot \mathbf{1}_{Y > 7}]}{p \cdot P(Y \leq 7) + (p/2) \cdot P(Y > 7)}$$

Числитель: $p \cdot E[Y \mathbf{1}_{Y \leq 7}] + (p/2) \cdot E[Y \mathbf{1}_{Y > 7}]$.

Значения с $Y > 7$ недопредставлены (вес $p/2$ вместо $p$), поэтому их вклад в среднее уменьшен. Следовательно $E[Y_{\text{obs}}] < E[Y] = 5$.

**b)** Направление смещения: вниз (underestimation). Люди с высоким стрессом редко отвечают — выборочное среднее будет ниже истинного.

Численный пример на Python:

```python
import numpy as np

rng = np.random.default_rng(42)
Y = rng.uniform(0, 10, 10000)
p = 0.8
prob_respond = np.where(Y > 7, p / 2, p)
respond = rng.random(10000) < prob_respond

print('Истинное E[Y]:     ', round(Y.mean(), 3))          # ≈ 5.0
print('E[Y | наблюдаемые]:', round(Y[respond].mean(), 3)) # < 5.0
```

### Ответ

$E[Y_{\text{obs}}] < E[Y]$. Смещение отрицательное: наблюдаемые данные систематически занижают уровень стресса, потому что высокострессовые люди реже отвечают. Complete-case analysis даёт смещённую оценку при MNAR; направление смещения определяется тем, «куда» ведёт зависимость пропуска от значения.

---

## Задача 9. Pipeline для смешанного датасета (сложная)

**Условие.** Датасет клиентов банка:
- `age` — числовой, 8% пропусков, нормальное распределение
- `credit_score` — числовой, 20% пропусков, MAR (зависит от `age`), есть выбросы
- `region` — категориальный, 5% пропусков, 50 уникальных значений
- `is_active` — бинарный, 0% пропусков

Целевая модель — случайный лес. Требование: никаких утечек при CV. Напишите полный Pipeline.

### Решение

Особенности задачи:
- `credit_score`: MAR + выбросы → KNNImputer (использует `age`) + RobustScaler.
- `age`: SimpleImputer(mean), потом StandardScaler — нормальное распределение.
- `region`: 50 уникальных → лучше TargetEncoder или OrdinalEncoder, дефолтная заглушка для редких.
- `is_active`: без пропусков, бинарный — без обработки.
- Скейлер для случайного леса не нужен, но оставим для унификации.

```python
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import RobustScaler, OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# Синтетический датасет
rng = np.random.default_rng(0)
n = 2000
df = pd.DataFrame({
    'age':          rng.normal(40, 12, n),
    'credit_score': rng.normal(650, 80, n),
    'region':       rng.choice(['North', 'South', 'East', 'West'], n),
    'is_active':    rng.integers(0, 2, n),
})
# Вводим пропуски
df.loc[rng.choice(n, 160, replace=False), 'age'] = np.nan
df.loc[rng.choice(n, 400, replace=False), 'credit_score'] = np.nan
df.loc[rng.choice(n, 100, replace=False), 'region'] = np.nan

y = (df['credit_score'].fillna(650) > 650).astype(int).values

num_normal = ['age']
num_outlier = ['credit_score']
cat_cols = ['region']
passthrough = ['is_active']

preprocessor = ColumnTransformer([
    ('age_pipe', Pipeline([
        ('imp',   SimpleImputer(strategy='mean')),
        ('scale', RobustScaler()),
    ]), num_normal),
    ('credit_pipe', Pipeline([
        ('imp',   KNNImputer(n_neighbors=10)),
        ('scale', RobustScaler()),
    ]), num_outlier),
    ('cat_pipe', Pipeline([
        ('imp', SimpleImputer(strategy='most_frequent')),
        ('enc', OrdinalEncoder(handle_unknown='use_encoded_value',
                               unknown_value=-1)),
    ]), cat_cols),
], remainder='passthrough')

full_pipe = Pipeline([
    ('prep',  preprocessor),
    ('model', RandomForestClassifier(n_estimators=100, random_state=0)),
])

scores = cross_val_score(full_pipe, df, y, cv=5, scoring='roc_auc')
print('ROC-AUC:', scores.round(3), 'mean:', round(scores.mean(), 3))
```

### Ответ

Весь пайплайн обёрнут в `Pipeline`, поэтому при `cross_val_score` каждый фолд обучает imputer и scaler только на train-части. KNNImputer для `credit_score` использует `age` для поиска соседей, что корректно при MAR. OrdinalEncoder с `handle_unknown` обрабатывает категории, которые могут появиться в test.

---

## Задача 10. Синтез: проектирование предобработки для реального кейса

**Условие.** Вам дан датасет медицинских записей (5 000 пациентов, 30 признаков). Первичный анализ показал:

1. 6 столбцов с пропусками >70% — предположительно, эти данные просто не собирались в ранних записях (временной паттерн).
2. `blood_pressure` — 25% пропусков, корреляция маски пропуска с `age` = 0.41 (MAR).
3. `bmi` — 12% пропусков, нет корреляции с наблюдаемыми (MCAR).
4. `diagnosis_severity` (таргет) — нет пропусков.
5. `patient_id`, `date_of_birth` — идентификаторы.
6. `lab_result_rare` — числовой, 3% значений > 10σ (реальные редкие патологии).

Опишите и реализуйте полный preprocessing workflow: что удалить, что импутировать, как обработать выбросы, как собрать Pipeline без утечек.

### Решение

**Шаг 1. Удаление столбцов с >70% пропусков.**

6 столбцов несут мало информации и сложны для импутации. Удаляем.

**Шаг 2. Удаление идентификаторов.**

`patient_id`, `date_of_birth` — не признаки модели. Из `date_of_birth` можно извлечь `age`.

**Шаг 3. Обработка выбросов в `lab_result_rare`.**

3% — реальные патологии, не ошибки ввода. Не удалять, но логарифмировать, чтобы уменьшить влияние на линейные алгоритмы, или использовать Isolation Forest для флага.

**Шаг 4. Импутация `blood_pressure` (MAR) и `bmi` (MCAR).**

- `bmi` (MCAR): SimpleImputer(mean) даёт несмещённую оценку.
- `blood_pressure` (MAR): IterativeImputer — учитывает `age` и другие признаки.

**Шаг 5. Индикатор пропуска для `blood_pressure`.**

MAR не гарантирует — добавим индикатор для надёжности.

**Шаг 6. Масштабирование и Pipeline.**

```python
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, MissingIndicator
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

# --- Загрузка и первичная очистка (до Pipeline) ---
# df = pd.read_csv('medical_data.csv')

# Удаляем столбцы с >70% пропусков (вне Pipeline — это EDA-решение)
# high_miss_cols = df.columns[df.isnull().mean() > 0.70].tolist()
# df = df.drop(columns=high_miss_cols + ['patient_id'])

# Возраст из даты рождения
# df['age'] = (pd.Timestamp.today() - df['date_of_birth']).dt.days // 365
# df = df.drop(columns=['date_of_birth'])

# --- Pipeline ---
log1p_transform = FunctionTransformer(np.log1p)

blood_pressure_pipe = Pipeline([
    ('indicator', MissingIndicator()),   # флаг пропуска
    # MissingIndicator — только маска; будем добавлять отдельно через CT
])

# Более аккуратная схема: добавить индикатор через ColumnTransformer
blood_pipe = Pipeline([
    ('iter_imp', IterativeImputer(max_iter=10, random_state=0)),
    ('scale',    StandardScaler()),
])
bmi_pipe = Pipeline([
    ('mean_imp', SimpleImputer(strategy='mean')),
    ('scale',    StandardScaler()),
])
lab_pipe = Pipeline([
    ('log',   log1p_transform),
    ('scale', StandardScaler()),
])

# Для демонстрации — синтетические данные
rng = np.random.default_rng(42)
n = 500
X_demo = pd.DataFrame({
    'blood_pressure': np.where(
        rng.random(n) < 0.25, np.nan, rng.normal(120, 15, n)),
    'bmi': np.where(
        rng.random(n) < 0.12, np.nan, rng.normal(26, 4, n)),
    'lab_result_rare': np.abs(rng.exponential(1, n)),
    'age': rng.normal(50, 15, n),
})
y_demo = (X_demo['blood_pressure'].fillna(120) > 130).astype(int).values

preprocessor = ColumnTransformer([
    ('bp',  blood_pipe, ['blood_pressure', 'age']),
    ('bmi', bmi_pipe,   ['bmi']),
    ('lab', lab_pipe,   ['lab_result_rare']),
], remainder='passthrough')

full_pipe = Pipeline([
    ('prep',  preprocessor),
    ('model', GradientBoostingClassifier(n_estimators=100, random_state=0)),
])

scores = cross_val_score(full_pipe, X_demo, y_demo, cv=5, scoring='roc_auc')
print('ROC-AUC:', scores.round(3), '| mean:', round(scores.mean(), 3))
```

**Итог решения по шагам:**

| Шаг | Действие | Инструмент |
|-----|----------|-----------|
| Удаление колонок | >70% пропусков, идентификаторы | `df.drop` (до Pipeline) |
| Выбросы `lab_result_rare` | Логарифмирование | `FunctionTransformer(np.log1p)` |
| `bmi` (MCAR) | Среднее | `SimpleImputer(strategy='mean')` |
| `blood_pressure` (MAR) | Итеративная импутация | `IterativeImputer` |
| Масштабирование | Все числовые | `StandardScaler` |
| Сборка | Предотвращение утечек | `Pipeline` + `cross_val_score` |

### Ответ

Правильный preprocessing workflow: (1) удалить неинформативные столбцы вне Pipeline, (2) обработать выбросы через логарифм (не удалять реальные патологии), (3) выбрать стратегию импутации по механизму пропуска, (4) добавить индикатор пропуска для MAR-признаков, (5) всё обернуть в Pipeline для гарантии отсутствия data leakage при CV.

---

<details>
<summary>Что тренируют эти задачи</summary>

| Задача | Навык |
|--------|-------|
| 1. IQR выбросы | Ручное вычисление квантилей и границ |
| 2. Механизм пропуска | Диагностика MCAR/MAR/MNAR по описанию |
| 3. Выбор стратегии | Сопоставление типа данных с методом импутации |
| 4. Data leakage | Обнаружение и исправление утечки данных |
| 5. Z-score vs IQR | Сравнение методов, эффект маскировки |
| 6. Формула Рубина | Вычисление T, понимание между- и внутри-импутационных компонент |
| 7. Выбор скейлера | Обоснование по распределению и наличию выбросов |
| 8. MNAR bias | Аналитическое доказательство смещения complete-case |
| 9. Pipeline для смешанного | Проектирование сложного ColumnTransformer |
| 10. Полный workflow | Синтез всех навыков в реалистичном сценарии |

</details>
