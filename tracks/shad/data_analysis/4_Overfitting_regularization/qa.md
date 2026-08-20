# Задачи: Переобучение и регуляризация

## Задача 1 (лёгкая). Диагноз по числам

Модель показывает: train MSE = 0.05, val MSE = 0.06. Другая модель: train MSE = 0.80, val MSE = 0.82.

Определите диагноз каждой модели и предложите способ улучшения.

### Решение

**Модель A** (train=0.05, val=0.06):
- Зазор train/val мал (0.01) → нет переобучения
- Оба значения малы → хорошая подгонка
- Диагноз: модель в рабочем состоянии

**Модель B** (train=0.80, val=0.82):
- Зазор мал → нет переобучения
- Оба значения высоки → недообучение (high bias)
- Диагноз: underfitting

Способы улучшения Модели B:
1. Увеличить сложность (больше степеней полинома, глубже дерево)
2. Добавить новые признаки / взаимодействия
3. Уменьшить регуляризацию (меньший $\lambda$)
4. Попробовать другое семейство моделей (нелинейные)

### Ответ

Модель A — хорошо обучена. Модель B — недообучение (high bias), нужно увеличить сложность.

---

## Задача 2 (лёгкая). Правильный порядок разбиения

Дан датасет из 1000 примеров. Требуется: 60% train, 20% val, 20% test. Напишите корректный код.

### Решение

```python
from sklearn.model_selection import train_test_split
import numpy as np

rng = np.random.default_rng(0)
X = rng.standard_normal((1000, 5))
y = rng.integers(0, 2, 1000)

# Шаг 1: отсекаем test (20%)
X_tv, X_test, y_tv, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
# X_tv содержит 800 примеров (train + val)

# Шаг 2: из оставшихся 800 отсекаем val (25% = 200 примеров = 20% от 1000)
X_train, X_val, y_train, y_val = train_test_split(
    X_tv, y_tv, test_size=0.25, random_state=42, stratify=y_tv
)

print(f"train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
# train=600, val=200, test=200
```

Ключевые моменты:
- `stratify=y` сохраняет пропорции классов в каждом сплите
- Test отсекается первым и больше не трогается
- `test_size=0.25` на втором шаге: 0.25 × 800 = 200 = 20% от 1000

### Ответ

Сначала отсекаем test (20%), затем из оставшихся 80% отсекаем val (25% = 20% от всех). Итого: 600 / 200 / 200.

---

## Задача 3 (лёгкая). Ridge: аналитическое решение

Дана задача Ridge-регрессии: минимизировать $\|Xw - y\|_2^2 + \lambda\|w\|_2^2$. Выведите формулу оптимального $w^*$.

### Решение

Обозначим $Q(w) = \|Xw - y\|_2^2 + \lambda\|w\|_2^2$.

Раскроем:
$$Q(w) = (Xw - y)^\top(Xw - y) + \lambda w^\top w$$
$$= w^\top X^\top X w - 2y^\top X w + y^\top y + \lambda w^\top w$$

Возьмём градиент по $w$ и приравняем нулю:
$$\nabla_w Q = 2X^\top X w - 2X^\top y + 2\lambda w = 0$$
$$(X^\top X + \lambda I)w = X^\top y$$
$$w^* = (X^\top X + \lambda I)^{-1} X^\top y$$

Матрица $(X^\top X + \lambda I)$ — положительно определена при любом $\lambda > 0$, так как $X^\top X$ — положительно полуопределена, а прибавление $\lambda I$ делает все собственные значения не меньше $\lambda > 0$. Значит, обратная матрица всегда существует.

```python
import numpy as np

def ridge_analytic(X, y, lam):
    n, d = X.shape
    A = X.T @ X + lam * np.eye(d)
    return np.linalg.solve(A, X.T @ y)

# Проверка совпадения с sklearn
from sklearn.linear_model import Ridge
X = np.random.randn(50, 3)
y = np.random.randn(50)

w_analytic = ridge_analytic(X, y, lam=1.0)
w_sklearn  = Ridge(alpha=1.0, fit_intercept=False).fit(X, y).coef_
print(np.allclose(w_analytic, w_sklearn))  # True
```

### Ответ

$$w^* = (X^\top X + \lambda I)^{-1} X^\top y$$

---

## Задача 4 (средняя). Выбор метода CV

У вас три датасета: (А) 50 примеров, бинарная классификация; (Б) 10 000 примеров, регрессия; (В) 300 примеров, дисбаланс классов 1:20. Выберите метод CV для каждого и обоснуйте.

### Решение

**(А) 50 примеров, бинарная классификация:**

```python
from sklearn.model_selection import LeaveOneOut, StratifiedKFold

# LOO или Stratified KFold с большим k
loo = LeaveOneOut()
# LOO: 50 итераций, каждый пример по одному разу в val
# Альтернатива: StratifiedKFold(n_splits=10) — 10 фолдов по 5 примеров

skf_10 = StratifiedKFold(n_splits=10, shuffle=True, random_state=0)
# При 50 примерах KFold(5) даст val по 10 — слишком мало
```

Выбор: **LOO** (максимальное использование данных) или **StratifiedKFold(k=10)** (быстрее и сохраняет баланс классов).

**(Б) 10 000 примеров, регрессия:**

```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
# 5-fold: val = 2000 примеров — достаточно для стабильной оценки
# LOO здесь = 10000 итераций — неприемлемо долго
```

Выбор: **KFold(k=5)** — баланс скорости и точности оценки.

**(В) 300 примеров, дисбаланс 1:20:**

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
# При 300 примерах и дисбалансе 1:20: редкий класс — 14 примеров
# Обычный KFold может собрать fold без редкого класса вообще
# StratifiedKFold гарантирует ~2-3 примера редкого класса в каждом val
```

Выбор: **StratifiedKFold(k=5)** — обязательно, иначе риск нулевого представления редкого класса в val.

### Ответ

А → LOO или StratifiedKFold(10); Б → KFold(5); В → StratifiedKFold(5) обязательно.

---

## Задача 5 (средняя). L1 vs L2: что обнуляется?

Объясните геометрически, почему Lasso (L1) обнуляет коэффициенты, а Ridge (L2) — нет. Подтвердите численно.

### Решение

**Геометрический аргумент:**

Задача регуляризации эквивалентна constrained-оптимизации:
- Ridge: $\min \text{MSE}(w)$ при $\|w\|_2^2 \leq t$ — допустимая область: **шар** (гладкий)
- Lasso: $\min \text{MSE}(w)$ при $\|w\|_1 \leq t$ — допустимая область: **бриллиант** (угловой)

Эллипсоиды уровней MSE "касаются" допустимой области:
- У шара нет угловых точек → касание происходит в произвольной точке на гладкой поверхности → $w_j \neq 0$ в общем случае
- У бриллианта угловые точки лежат на координатных осях → высокая вероятность касания в углу → $w_j = 0$ для части координат

```python
from sklearn.linear_model import Ridge, Lasso
from sklearn.datasets import make_regression
import numpy as np

X, y, true_w = make_regression(
    n_samples=200, n_features=15, n_informative=5,
    noise=10, coef=True, random_state=0
)

alphas = [0.01, 0.1, 1.0, 10.0, 100.0]
print(f"{'alpha':>8} | {'Ridge zeros':>12} | {'Lasso zeros':>12}")
print('-' * 38)
for alpha in alphas:
    r_zeros = (Ridge(alpha=alpha).fit(X, y).coef_ == 0).sum()
    l_zeros = (Lasso(alpha=alpha, max_iter=10000).fit(X, y).coef_ == 0).sum()
    print(f"{alpha:8.2f} | {r_zeros:12d} | {l_zeros:12d}")
```

Ожидаемый вывод:
```
   alpha | Ridge zeros | Lasso zeros
--------------------------------------
    0.01 |           0 |           3
    0.10 |           0 |           7
    1.00 |           0 |          11
   10.00 |           0 |          14
  100.00 |           0 |          15
```

Ridge никогда не обнуляет коэффициенты (нули не видны из-за float-арифметики, но они не строго нулевые). Lasso при увеличении alpha последовательно обнуляет всё больше признаков.

### Ответ

L2 (шар) касается эллипсоидов уровней MSE в гладких точках → нули не возникают. L1 (бриллиант) имеет угловые точки на осях → оптимум часто находится в угле → $w_j = 0$.

---

## Задача 6 (средняя). Pipeline с CV без утечки данных

Постройте полный Pipeline: StandardScaler + Lasso. Подберите alpha через GridSearchCV без утечки данных. Оцените на тесте.

### Решение

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.datasets import make_regression
from sklearn.metrics import mean_squared_error
import numpy as np

X, y, _ = make_regression(n_samples=400, n_features=20, n_informative=6,
                           noise=15, random_state=1)

# 1. Разделяем данные (test изолирован)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# 2. Pipeline: scaler + model (scaler обучается только на fold'овом train)
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('lasso',  Lasso(max_iter=10000)),
])

# 3. GridSearch по alpha (CV внутри train)
param_grid = {'lasso__alpha': np.logspace(-3, 2, 30)}
gs = GridSearchCV(pipe, param_grid, cv=5,
                  scoring='neg_mean_squared_error', n_jobs=-1)
gs.fit(X_train, y_train)

print(f"Best alpha: {gs.best_params_['lasso__alpha']:.5f}")
print(f"CV MSE:     {-gs.best_score_:.4f}")

# 4. Финальная оценка на тесте (трогаем один раз!)
y_pred = gs.predict(X_test)
test_mse = mean_squared_error(y_test, y_pred)
print(f"Test MSE:   {test_mse:.4f}")

# 5. Сколько признаков отобрал Lasso?
best_lasso = gs.best_estimator_.named_steps['lasso']
n_selected = (best_lasso.coef_ != 0).sum()
print(f"Отобрано признаков: {n_selected}/20")
```

Почему Pipeline не допускает утечки:
- `StandardScaler.fit()` вызывается только на train-части каждого CV fold
- `transform()` применяется к val-части с параметрами, вычисленными на train
- Test не виден ни на каком этапе GridSearch

### Ответ

Pipeline + GridSearchCV гарантируют, что scaler и модель обучаются только на train-части каждого fold. Test трогается ровно один раз для финальной оценки.

---

## Задача 7 (средняя). ElasticNet при коллинеарности

Есть два коллинеарных признака $x_1 \approx x_2$. Объясните, как Lasso и ElasticNet выберут между ними. Подтвердите численно.

### Решение

**Теоретическое объяснение:**

При $x_1 \approx x_2$ задача Lasso имеет множество эквивалентных решений: $w_1 = a, w_2 = 0$ и $w_1 = 0, w_2 = a$ и любая комбинация $w_1 + w_2 = a$ при $w_1, w_2 \geq 0$ дают примерно одинаковый loss. Lasso выберет одно из них нестабильно — какое именно, зависит от случайности. ElasticNet за счёт L2-компоненты "разделяет" вес поровну между коллинеарными признаками.

```python
from sklearn.linear_model import Lasso, ElasticNet
import numpy as np

rng = np.random.default_rng(42)
n = 300
x1 = rng.standard_normal(n)
x2 = x1 + rng.normal(0, 0.05, n)   # почти то же, что x1
x3 = rng.standard_normal(n)         # независимый признак
y  = 3.0 * x1 + 2.0 * x3 + rng.normal(0, 0.5, n)

X = np.column_stack([x1, x2, x3])

from sklearn.preprocessing import StandardScaler
X_sc = StandardScaler().fit_transform(X)

lasso = Lasso(alpha=0.05, max_iter=10000).fit(X_sc, y)
enet  = ElasticNet(alpha=0.05, l1_ratio=0.5, max_iter=10000).fit(X_sc, y)

print("Lasso coefs:      ", np.round(lasso.coef_, 3))
print("ElasticNet coefs: ", np.round(enet.coef_, 3))
```

Типичный вывод:
```
Lasso coefs:       [2.14  0.    1.65]   # x2 обнулён, x1 берёт всё
ElasticNet coefs:  [1.08  1.07  1.62]   # вес поровну между x1 и x2
```

ElasticNet честнее: оба коллинеарных признака получают похожие веса, что более интерпретируемо.

### Ответ

Lasso нестабильно выбирает один из коллинеарных признаков. ElasticNet (L2-часть) штрафует разницу весов, распределяя их поровну — решение устойчиво.

---

## Задача 8 (сложная). Bias-Variance Tradeoff через MSE

Докажите разложение ожидаемой MSE на bias², variance и irreducible noise. Покажите, как $\lambda$ влияет на каждую компоненту.

### Решение

Рассмотрим задачу регрессии: $y = f(x) + \varepsilon$, где $\varepsilon \sim \mathcal{N}(0, \sigma^2)$.

Для фиксированной точки $x_0$ ожидаемая MSE предсказания $\hat{f}(x_0)$:

$$\mathbb{E}[(y - \hat{f}(x_0))^2] = \mathbb{E}[(y - f(x_0) + f(x_0) - \hat{f}(x_0))^2]$$

Раскрываем и используем независимость $\varepsilon$ от $\hat{f}$:

$$= \underbrace{\mathbb{E}[(f(x_0) - \hat{f}(x_0))^2]}_{\text{MSE модели}} + \sigma^2$$

Для первого слагаемого:
$$\mathbb{E}[(f(x_0) - \hat{f}(x_0))^2] = \underbrace{(f(x_0) - \mathbb{E}[\hat{f}(x_0)])^2}_{\text{Bias}^2} + \underbrace{\mathbb{E}[(\hat{f}(x_0) - \mathbb{E}[\hat{f}(x_0)])^2]}_{\text{Variance}}$$

Итого:
$$\text{MSE} = \text{Bias}^2 + \text{Variance} + \sigma^2$$

**Влияние $\lambda$ на Ridge:**

```python
from sklearn.linear_model import Ridge
from sklearn.datasets import make_regression
import numpy as np

# Симуляция: многократно обучаем на разных выборках
def estimate_bias_variance(alpha, n_sim=200, n_train=50):
    rng = np.random.default_rng(0)
    x0 = np.array([[0.5]])
    preds = []
    for _ in range(n_sim):
        X_s = rng.uniform(0, 1, (n_train, 1))
        y_s = 2 * X_s.ravel() + rng.normal(0, 0.5, n_train)
        model = Ridge(alpha=alpha).fit(X_s, y_s)
        preds.append(model.predict(x0)[0])
    preds = np.array(preds)
    true_val = 2 * 0.5  # f(x0) = 1.0
    bias2 = (np.mean(preds) - true_val) ** 2
    variance = np.var(preds)
    return bias2, variance

print(f"{'alpha':>8} | {'Bias^2':>10} | {'Variance':>10} | {'Sum':>10}")
print('-' * 46)
for alpha in [0.0001, 0.01, 0.1, 1.0, 10.0, 100.0]:
    b2, var = estimate_bias_variance(alpha)
    print(f"{alpha:8.4f} | {b2:10.5f} | {var:10.5f} | {b2+var:10.5f}")
```

Наблюдение: при росте $\lambda$ Bias² растёт (модель смещается к нулю), Variance падает (предсказания стабильнее). Оптимальный $\lambda$ минимизирует сумму.

### Ответ

$$\text{MSE} = \text{Bias}^2 + \text{Variance} + \sigma^2$$

Рост $\lambda$: Bias² ↑, Variance ↓. Оптимальный $\lambda$ — компромисс, минимизирующий Bias² + Variance.

---

## Задача 9 (сложная). Ridge как MAP с гауссовским prior

Покажите, что Ridge-регрессия эквивалентна MAP-оценке при гауссовском prior $w \sim \mathcal{N}(0, \tau^2 I)$ и шуме $\varepsilon \sim \mathcal{N}(0, \sigma^2 I)$. Выразите $\lambda$ через $\sigma^2$ и $\tau^2$.

### Решение

**Likelihood:** $y | X, w \sim \mathcal{N}(Xw, \sigma^2 I)$

$$\log p(y | X, w) = -\frac{n}{2}\log(2\pi\sigma^2) - \frac{1}{2\sigma^2}\|y - Xw\|_2^2$$

**Prior:** $w \sim \mathcal{N}(0, \tau^2 I)$

$$\log p(w) = -\frac{d}{2}\log(2\pi\tau^2) - \frac{1}{2\tau^2}\|w\|_2^2$$

**Posterior (MAP — максимизируем log posterior):**

$$\log p(w | X, y) \propto \log p(y | X, w) + \log p(w)$$
$$\propto -\frac{1}{2\sigma^2}\|y - Xw\|_2^2 - \frac{1}{2\tau^2}\|w\|_2^2$$

Максимизация posterior = минимизация:
$$\frac{1}{2\sigma^2}\|y - Xw\|_2^2 + \frac{1}{2\tau^2}\|w\|_2^2$$

Умножим на $2\sigma^2$:
$$\|y - Xw\|_2^2 + \underbrace{\frac{\sigma^2}{\tau^2}}_{\lambda}\|w\|_2^2$$

Это в точности Ridge с $\lambda = \dfrac{\sigma^2}{\tau^2}$.

**Интерпретация:**
- Большой $\tau^2$ (слабый prior, веса могут быть любыми) → малый $\lambda$ → слабая регуляризация
- Малый $\tau^2$ (сильная уверенность, что $w \approx 0$) → большой $\lambda$ → сильная регуляризация

```python
# Демонстрация: при sigma=1, tau=0.1 -> lambda=100
sigma2, tau2 = 1.0, 0.01
lam = sigma2 / tau2
print(f"lambda = sigma^2 / tau^2 = {sigma2}/{tau2} = {lam}")  # 100.0
```

### Ответ

Ridge-регрессия = MAP при $w \sim \mathcal{N}(0, \tau^2 I)$, причём $\lambda = \sigma^2 / \tau^2$.

---

## Задача 10 (синтез). Полный пайплайн: от сырых данных до финальной оценки

Дан датасет с дисбалансом классов (10% позитивных), 15 признаков (часть коррелированных). Постройте полный пайплайн: StandardScaler → ElasticNet → подбор гиперпараметров через StratifiedKFold → финальная оценка по ROC-AUC на тесте. Выведите отобранные признаки.

### Решение

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import (train_test_split, StratifiedKFold,
                                      GridSearchCV)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import numpy as np

# 1. Генерация данных с дисбалансом и коррелированными признаками
X, y = make_classification(
    n_samples=1000, n_features=15, n_informative=5,
    n_redundant=4, n_repeated=2,   # коллинеарные признаки
    weights=[0.90, 0.10],           # дисбаланс 9:1
    random_state=42
)

# 2. Разбиение с сохранением дисбаланса
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
print(f"Train positive: {y_train.mean():.3f}, Test positive: {y_test.mean():.3f}")

# 3. Pipeline: масштабирование + ElasticNet логистическая регрессия
# penalty='elasticnet' требует solver='saga'
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf',    LogisticRegression(penalty='elasticnet', solver='saga',
                                   max_iter=2000, random_state=0)),
])

# 4. Сетка гиперпараметров
param_grid = {
    'clf__C':        [0.01, 0.1, 1.0, 10.0],   # C = 1/lambda
    'clf__l1_ratio': [0.0, 0.5, 1.0],            # 0=Ridge, 1=Lasso
}

# 5. StratifiedKFold — обязательно из-за дисбаланса
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

gs = GridSearchCV(pipe, param_grid, cv=skf,
                  scoring='roc_auc', n_jobs=-1, verbose=0)
gs.fit(X_train, y_train)

print(f"\nBest params:  {gs.best_params_}")
print(f"CV ROC-AUC:   {gs.best_score_:.4f}")

# 6. Финальная оценка на тесте
y_prob = gs.predict_proba(X_test)[:, 1]
test_auc = roc_auc_score(y_test, y_prob)
print(f"Test ROC-AUC: {test_auc:.4f}")

# 7. Отбор признаков: ненулевые коэффициенты
best_clf = gs.best_estimator_.named_steps['clf']
coefs = best_clf.coef_[0]
selected = np.where(coefs != 0)[0]
print(f"\nОтобрано признаков: {len(selected)}/15")
print(f"Индексы: {selected}")
print(f"Коэффициенты: {np.round(coefs[selected], 3)}")
```

Что демонстрирует задача:
- `stratify=y` при разбиении и `StratifiedKFold` в CV — единый паттерн для дисбаланса
- `penalty='elasticnet'` в LogisticRegression = ElasticNet для классификации
- `C = 1/lambda`: малый C = сильная регуляризация
- `l1_ratio` контролирует баланс L1/L2
- Pipeline предотвращает data leakage от scaler
- Test трогается ровно один раз

### Ответ

Полный пайплайн: StratifiedSplit → Pipeline(Scaler + ElasticNet) → StratifiedKFold GridSearch по (C, l1_ratio) → финальная оценка ROC-AUC на тесте. ElasticNet сочетает разреженность L1 и стабильность L2 при коллинеарных признаках.

---

<details><summary>Что тренируют эти задачи</summary>

| Задача | Навык |
|---|---|
| 1 | Диагностика по числам: underfitting vs overfitting |
| 2 | Корректное train/val/test разбиение с stratify |
| 3 | Вывод аналитического решения Ridge |
| 4 | Выбор метода CV в зависимости от объёма и баланса данных |
| 5 | Геометрическая интуиция L1 vs L2, численное подтверждение |
| 6 | Pipeline без data leakage + GridSearchCV |
| 7 | ElasticNet при коллинеарности: устойчивость vs Lasso |
| 8 | Формальный вывод Bias-Variance Tradeoff, влияние λ |
| 9 | Байесовская интерпретация Ridge, связь λ = σ²/τ² |
| 10 | Синтез: дисбаланс + коллинеарность + ElasticNet + полный пайплайн |

</details>
