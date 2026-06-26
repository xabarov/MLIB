# 10 задач в стиле вступительного экзамена ШАД  
по теме: неравенства, виды сходимости, законы больших чисел

---

## Задача 1. Неравенство Маркова

Время выполнения задачи — неотрицательная с.в. $T$ с $\mathbb{E}[T] = 5$ секунд.  
Оценить сверху $\mathbb{P}(T \ge 20)$.

### Решение

По неравенству Маркова ($T \ge 0$):

$$
\mathbb{P}(T \ge 20) \le \frac{\mathbb{E}[T]}{20} = \frac{5}{20} = \frac{1}{4}.
$$

### Ответ

$\mathbb{P}(T \ge 20) \le 1/4$.

---

## Задача 2. Неравенство Чебышёва

С.в. $X$ имеет $\mathbb{E}[X] = 10$, $\mathrm{Var}(X) = 4$.  
(а) Оценить $\mathbb{P}(|X - 10| \ge 6)$.  
(б) Оценить $\mathbb{P}(X \ge 14)$.

### Решение

**(а)** Прямо по Чебышёву:

$$
\mathbb{P}(|X-10| \ge 6) \le \frac{\mathrm{Var}(X)}{6^2} = \frac{4}{36} = \frac{1}{9}.
$$

**(б)** $\{X \ge 14\} = \{X - 10 \ge 4\} \subseteq \{|X-10| \ge 4\}$, поэтому:

$$
\mathbb{P}(X \ge 14) \le \mathbb{P}(|X-10| \ge 4) \le \frac{4}{16} = \frac{1}{4}.
$$

### Ответ

(а) $\le 1/9$; (б) $\le 1/4$.

---

## Задача 3. Неравенство Йенсена

Пусть $X$ — с.в. с $\mathbb{E}[X] = 2$.  
(а) Оценить снизу $\mathbb{E}[e^X]$.  
(б) Является ли $\mathbb{E}[\sqrt{X}]$ (при $X \ge 0$) не меньше $\sqrt{\mathbb{E}[X]}$?

### Решение

**(а)** $\varphi(x) = e^x$ выпукла ($\varphi''(x) = e^x > 0$). По Йенсену:

$$
\mathbb{E}[e^X] \ge e^{\mathbb{E}[X]} = e^2.
$$

**(б)** $\varphi(x) = \sqrt{x}$ — вогнутая ($\varphi''(x) = -\frac{1}{4}x^{-3/2} < 0$). По Йенсену для вогнутой:

$$
\mathbb{E}[\sqrt{X}] \le \sqrt{\mathbb{E}[X]}.
$$

Значит $\mathbb{E}[\sqrt{X}] \le \sqrt{2}$, то есть неравенство обратное — $\mathbb{E}[\sqrt{X}]$ не больше $\sqrt{\mathbb{E}[X]}$.

### Ответ

(а) $\mathbb{E}[e^X] \ge e^2$; (б) нет, $\mathbb{E}[\sqrt{X}] \le \sqrt{\mathbb{E}[X]} = \sqrt{2}$.

---

## Задача 4. Лемма Бореля–Кантелли

$X_1, X_2, \ldots$ — независимые, $\mathbb{P}(|X_n| > n) = 1/n^2$.  
Доказать, что п.н. выполнено лишь конечное число неравенств $|X_n| > n$.

### Решение

Обозначим $A_n = \{|X_n| > n\}$. Тогда:

$$
\sum_{n=1}^\infty \mathbb{P}(A_n) = \sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6} < \infty.
$$

По прямой лемме Бореля–Кантелли:

$$
\mathbb{P}(A_n \text{ б.ч.}) = 0,
$$

то есть п.н. лишь конечное число $A_n$ произойдут. $\square$

### Ответ

Ряд $\sum \mathbb{P}(A_n)$ сходится $\Rightarrow$ по лемме Б.-К. п.н. наступит конечное число событий $A_n$.

---

## Задача 5. Сходимость по вероятности

$X_1, X_2, \ldots$ — независимые, $X_n \sim \mathrm{Uniform}(0, 1/n)$.  
Доказать, что $X_n \xrightarrow{P} 0$.

### Решение

Для любого $\varepsilon > 0$ при $n > 1/\varepsilon$ все значения $X_n$ лежат в $[0, 1/n] \subseteq [0, \varepsilon)$:

$$
\mathbb{P}(|X_n - 0| \ge \varepsilon) = \mathbb{P}(X_n \ge \varepsilon) = \begin{cases} 1 - n\varepsilon, & n\varepsilon \le 1 \\ 0, & n\varepsilon > 1. \end{cases}
$$

При $n > 1/\varepsilon$ имеем $\mathbb{P}(X_n \ge \varepsilon) = 0 \to 0$. Значит $X_n \xrightarrow{P} 0$.

### Ответ

$X_n \xrightarrow{P} 0$.

---

## Задача 6. Сходимость в $L^2$

Пусть $X_n = Z/n$, где $Z$ — фиксированная с.в. с $\mathbb{E}[Z^2] < \infty$.  
Показать, что $X_n \xrightarrow{L^2} 0$.

### Решение

$$
\mathbb{E}[|X_n - 0|^2] = \mathbb{E}\!\left[\frac{Z^2}{n^2}\right] = \frac{\mathbb{E}[Z^2]}{n^2} \xrightarrow{n\to\infty} 0.
$$

Значит $X_n \xrightarrow{L^2} 0$.

**Бонус:** из $\xrightarrow{L^2}$ следует $\xrightarrow{P}$ (по неравенству Маркова), а из $\xrightarrow{P}$ — $\xrightarrow{d}$.

### Ответ

$\mathbb{E}[X_n^2] = \mathbb{E}[Z^2]/n^2 \to 0$, поэтому $X_n \xrightarrow{L^2} 0$.

---

## Задача 7. Контрпример: $\xrightarrow{P}$ не влечёт $\xrightarrow{\text{п.н.}}$

На $(\Omega, \mathcal{F}, \mathbb{P}) = ([0,1], \mathcal{B}([0,1]), \lambda)$ определим:

$$
X_1 = \mathbf{1}_{[0,1]},\quad X_2 = \mathbf{1}_{[0,1/2]},\quad X_3 = \mathbf{1}_{[1/2,1]},\quad X_4 = \mathbf{1}_{[0,1/3]},\quad \ldots
$$

(Группируем: $n$-й элемент — индикатор $k$-го из $m$ равных частей, $m$ растёт.)

Показать: $X_n \xrightarrow{P} 0$, но $X_n \not\xrightarrow{\text{п.н.}} 0$.

### Решение

**Сходимость по вероятности.** Длина носителя $n$-й функции стремится к 0:

$$
\mathbb{P}(X_n \ne 0) = \mathbb{P}(X_n = 1) = \text{длина отрезка} \to 0.
$$

Поэтому $\mathbb{P}(|X_n| > \varepsilon) \to 0$ для любого $\varepsilon \in (0,1)$ ✓.

**Отсутствие п.н.** Для любого $\omega \in [0,1]$ каждый отрезок $[0, 1/m]$ содержит $\omega$ при $\omega < 1/m$, а значит $X_n(\omega) = 1$ бесконечно часто. Таким образом $X_n(\omega) \not\to 0$ для всех $\omega$.

### Ответ

$X_n \xrightarrow{P} 0$, но $X_n(\omega)$ не сходится ни при каком $\omega \in [0,1]$.

---

## Задача 8. Применение слабого ЗБЧ

Монету бросают независимо. $X_i = 1$ (орёл) или $0$ (решка), $p = 0.6$.  
Используя неравенство Чебышёва, найти минимальное $n$ такое, что:

$$
\mathbb{P}\!\left(\left|\frac{X_1+\cdots+X_n}{n} - 0.6\right| \ge 0.05\right) \le 0.01.
$$

### Решение

$\mathrm{Var}(X_i) = p(1-p) = 0.6 \cdot 0.4 = 0.24$. По Чебышёву:

$$
\mathbb{P}(|\bar{X}_n - 0.6| \ge 0.05) \le \frac{0.24}{n \cdot (0.05)^2} = \frac{0.24}{0.0025\, n} = \frac{96}{n}.
$$

Требуем $96/n \le 0.01$, значит $n \ge 9600$.

### Ответ

$n \ge 9600$.

---

## Задача 9. Теорема Слуцкого

Пусть $Z_n \xrightarrow{d} \mathcal{N}(0,1)$ и $\hat{\sigma}_n \xrightarrow{P} \sigma > 0$.  
Найти предельное распределение $Y_n = \sigma Z_n / \hat{\sigma}_n$.

### Решение

Запишем $Y_n = Z_n \cdot (\sigma / \hat{\sigma}_n)$.

Так как $\hat{\sigma}_n \xrightarrow{P} \sigma$, то $\sigma / \hat{\sigma}_n \xrightarrow{P} \sigma / \sigma = 1$ (непрерывное отображение).

По теореме Слуцкого ($Z_n \xrightarrow{d} Z$, $\sigma/\hat{\sigma}_n \xrightarrow{P} 1$):

$$
Y_n = Z_n \cdot \frac{\sigma}{\hat{\sigma}_n} \xrightarrow{d} Z \cdot 1 = \mathcal{N}(0,1).
$$

### Ответ

$Y_n \xrightarrow{d} \mathcal{N}(0,1)$.

---

## Задача 10. Синтез: УЗБЧ + Йенсен + оценка хвоста

$X_1, X_2, \ldots$ — н.о.р., $X_i \ge 0$, $\mathbb{E}[X_i] = 2$, $\mathbb{E}[X_i^2] = 8$.

(а) Что утверждает УЗБЧ о $\bar{X}_n$?  
(б) Оценить $\mathbb{P}(\bar{X}_n \ge 3)$ с помощью неравенства Маркова.  
(в) Оценить $\mathbb{E}[1/\bar{X}_n]$ снизу для фиксированного $n$, используя Йенсена.

### Решение

**(а)** По УЗБЧ: $\bar{X}_n \xrightarrow{\text{п.н.}} \mathbb{E}[X_1] = 2$.

**(б)** $\bar{X}_n \ge 0$, $\mathbb{E}[\bar{X}_n] = 2$. По Маркову:

$$
\mathbb{P}(\bar{X}_n \ge 3) \le \frac{\mathbb{E}[\bar{X}_n]}{3} = \frac{2}{3}.
$$

Более точно — через Чебышёва: $\mathrm{Var}(\bar{X}_n) = \mathrm{Var}(X_1)/n = (8-4)/n = 4/n$:

$$
\mathbb{P}(\bar{X}_n \ge 3) \le \mathbb{P}(|\bar{X}_n - 2| \ge 1) \le \frac{4/n}{1^2} = \frac{4}{n}.
$$

**(в)** $\varphi(x) = 1/x$ — выпукла при $x > 0$. По Йенсену:

$$
\mathbb{E}\!\left[\frac{1}{\bar{X}_n}\right] \ge \frac{1}{\mathbb{E}[\bar{X}_n]} = \frac{1}{2}.
$$

### Ответ

(а) $\bar{X}_n \xrightarrow{\text{п.н.}} 2$; (б) $\mathbb{P}(\bar{X}_n \ge 3) \le 4/n$; (в) $\mathbb{E}[1/\bar{X}_n] \ge 1/2$.

---

<details>
<summary>Что тренируют эти задачи</summary>

1. Неравенство Маркова: прямое применение для хвоста $\mathbb{P}(T \ge a)$.
2. Неравенство Чебышёва: двустороннее и одностороннее (включение событий).
3. Неравенство Йенсена: определение выпуклости/вогнутости через $\varphi''$, направление неравенства.
4. Прямая лемма Бореля–Кантелли: проверка сходимости ряда вероятностей.
5. Сходимость по вероятности: вычисление $\mathbb{P}(|X_n - 0| \ge \varepsilon)$ явно.
6. Сходимость в $L^2$: вычисление $\mathbb{E}[X_n^2]$ и предельный переход.
7. Контрпример «убегающий горб»: $\xrightarrow{P}$ без $\xrightarrow{\text{п.н.}}$.
8. Слабый ЗБЧ: нахождение $n$ из условия на точность через Чебышёва.
9. Теорема Слуцкого: произведение $\xrightarrow{d}$ и $\xrightarrow{P}$.
10. Синтез: УЗБЧ, Марков, Йенсен — три инструмента в одной задаче.

</details>
