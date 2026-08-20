# Тригонометрические формулы

Краткий, но практичный справочник по тригонометрии для решения задач, особенно по пределам, производным, интегралам и преобразованию выражений.

Основной акцент здесь — на формулах, которые реально часто применяются в задачах уровня ШАД, в том числе в теме `mathematical_analysis/2_func_limits`.

---

## 0. Обозначения и замечания

- Используем радианную меру углов.
- Обозначения: $\tan x = \tg x$, $\cot x = \ctg x$.
- Все формулы предполагают, что выражения имеют смысл, то есть знаменатели не равны нулю.
- Для пределов особенно важны разделы 7, 9, 13, 14, 15 и 17.

---

## 1. Основное тригонометрическое тождество

$$
\sin^2 x + \cos^2 x = 1
$$

Следствия:

$$
\sin^2 x = 1 - \cos^2 x, \qquad \cos^2 x = 1 - \sin^2 x
$$

Связь с тангенсом и котангенсом (делим на $\cos^2 x$ и на $\sin^2 x$):

$$
1 + \tan^2 x = \frac{1}{\cos^2 x}, \qquad 1 + \cot^2 x = \frac{1}{\sin^2 x}
$$

---

## 2. Определения $\tan$ и $\cot$

$$
\tan x = \frac{\sin x}{\cos x}, \qquad \cot x = \frac{\cos x}{\sin x}
$$

$$
\tan x \cdot \cot x = 1, \qquad \cot x = \frac{1}{\tan x}
$$

---

## 3. Чётность и нечётность

$$
\cos(-x) = \cos x \quad \text{— чётная}
$$

$$
\sin(-x) = -\sin x \quad \text{— нечётная}
$$

$$
\tan(-x) = -\tan x, \qquad \cot(-x) = -\cot x
$$

---

## 4. Формулы приведения

Знак определяется четвертью, в которой находится угол.

Основные формулы:

$$
\sin\left(\frac{\pi}{2} - x\right) = \cos x, \qquad
\sin\left(\frac{\pi}{2} + x\right) = \cos x
$$

$$
\cos\left(\frac{\pi}{2} - x\right) = \sin x, \qquad
\cos\left(\frac{\pi}{2} + x\right) = -\sin x
$$

$$
\sin(\pi - x) = \sin x, \qquad \sin(\pi + x) = -\sin x
$$

$$
\cos(\pi - x) = -\cos x, \qquad \cos(\pi + x) = -\cos x
$$

$$
\sin(2\pi - x) = -\sin x, \qquad \sin(2\pi + x) = \sin x
$$

$$
\cos(2\pi - x) = \cos x, \qquad \cos(2\pi + x) = \cos x
$$

> **Правило:** если угол откладывается от вертикальной оси ($\pi/2$, $3\pi/2$), то функция меняется: $\sin \leftrightarrow \cos$. Если от горизонтальной оси ($0$, $\pi$, $2\pi$), то название функции сохраняется.

Для тангенса и котангенса:

$$
\tan(\pi \pm x) = \pm \tan x, \qquad \tan\left(\frac{\pi}{2} \pm x\right) = \mp \cot x
$$

$$
\cot(\pi \pm x) = \pm \cot x, \qquad \cot\left(\frac{\pi}{2} \pm x\right) = \mp \tan x
$$

---

## 5. Формулы сложения

$$
\sin(\alpha \pm \beta) = \sin \alpha \cos \beta \pm \cos \alpha \sin \beta
$$

$$
\cos(\alpha \pm \beta) = \cos \alpha \cos \beta \mp \sin \alpha \sin \beta
$$

> Обратите внимание: у косинуса знаки **обратные** по сравнению с аргументом.

$$
\tan(\alpha \pm \beta) = \frac{\tan \alpha \pm \tan \beta}{1 \mp \tan \alpha \tan \beta}
$$

---

## 6. Формулы двойного угла

$$
\sin 2x = 2 \sin x \cos x
$$

$$
\cos 2x = \cos^2 x - \sin^2 x = 2\cos^2 x - 1 = 1 - 2\sin^2 x
$$

$$
\tan 2x = \frac{2\tan x}{1 - \tan^2 x}
$$

---

## 7. Формулы двойного угла — **понижение степени**

> Особенно полезны для пределов и интегралов:

$$
\sin^2 x = \frac{1 - \cos 2x}{2}
$$

$$
\cos^2 x = \frac{1 + \cos 2x}{2}
$$

$$
\tan^2 x = \frac{1 - \cos 2x}{1 + \cos 2x}
$$

---

## 8. Формулы половинного угла

$$
\sin\frac{x}{2} = \pm \sqrt{\frac{1 - \cos x}{2}}
$$

$$
\cos\frac{x}{2} = \pm \sqrt{\frac{1 + \cos x}{2}}
$$

$$
\tan\frac{x}{2} = \frac{\sin x}{1 + \cos x} = \frac{1 - \cos x}{\sin x}
$$

---

## 9. Формулы суммы и разности, особенно полезные для пределов

### 9.1. Разность косинусов

$$
1 - \cos x = 2\sin^2\frac{x}{2}
$$

Эта формула **критически важна** для вычисления пределов типа:

$$
\lim_{x \to 0} \frac{1 - \cos x}{x^2} = \frac{1}{2}
$$

### 9.2. Разность синусов

$$
\sin \alpha - \sin \beta = 2\cos\frac{\alpha+\beta}{2} \sin\frac{\alpha-\beta}{2}
$$

### 9.3. Разность косинусов (общий случай)

$$
\cos \alpha - \cos \beta = -2\sin\frac{\alpha+\beta}{2} \sin\frac{\alpha-\beta}{2}
$$

### 9.4. Сумма синусов

$$
\sin \alpha + \sin \beta = 2\sin\frac{\alpha+\beta}{2} \cos\frac{\alpha-\beta}{2}
$$

### 9.5. Сумма косинусов

$$
\cos \alpha + \cos \beta = 2\cos\frac{\alpha+\beta}{2} \cos\frac{\alpha-\beta}{2}
$$

---

## 10. Формулы произведение ↔ сумма

$$
\sin \alpha \sin \beta = \frac{1}{2}\bigl[\cos(\alpha-\beta) - \cos(\alpha+\beta)\bigr]
$$

$$
\cos \alpha \cos \beta = \frac{1}{2}\bigl[\cos(\alpha-\beta) + \cos(\alpha+\beta)\bigr]
$$

$$
\sin \alpha \cos \beta = \frac{1}{2}\bigl[\sin(\alpha+\beta) + \sin(\alpha-\beta)\bigr]
$$

$$
\cos \alpha \sin \beta = \frac{1}{2}\bigl[\sin(\alpha+\beta) - \sin(\alpha-\beta)\bigr]
$$

---

## 11. Выражение через тангенс половинного угла

Универсальная тригонометрическая подстановка:

$$
\sin x = \frac{2\tan(x/2)}{1 + \tan^2(x/2)}, \qquad \cos x = \frac{1 - \tan^2(x/2)}{1 + \tan^2(x/2)}
$$

$$
\tan x = \frac{2\tan(x/2)}{1 - \tan^2(x/2)}
$$

---

## 12. Формулы тройного угла

$$
\sin 3x = 3\sin x - 4\sin^3 x
$$

$$
\cos 3x = 4\cos^3 x - 3\cos x
$$

$$
\tan 3x = \frac{3\tan x - \tan^3 x}{1 - 3\tan^2 x}
$$

---

## 13. Замечательные пределы с тригонометрией

### Первый замечательный предел

$$
\lim_{x \to 0} \frac{\sin x}{x} = 1
$$

Это одна из главных формул во всей теме пределов. Очень часто задачу нужно просто привести именно к этому виду.

Следствия:


$$
\lim_{x \to 0} \frac{\sin \alpha x}{\alpha x} = 1
$$

$$
\lim_{x \to 0} \frac{\tan x}{x} = 1
$$

$$
\lim_{x \to 0} \frac{\arcsin x}{x} = 1
$$

$$
\lim_{x \to 0} \frac{\arctan x}{x} = 1
$$

$$
\lim_{x \to 0} \frac{1 - \cos x}{x} = 0
$$

$$
\lim_{x \to 0} \frac{1 - \cos x}{x^2} = \frac{1}{2}
$$

$$
\lim_{x \to 0} \frac{\sin kx}{\sin mx} = \frac{k}{m}
$$

$$
\lim_{x \to 0} \frac{1 - \cos kx}{x^2} = \frac{k^2}{2}
$$

$$
\lim_{x \to 0} \frac{\sin ax}{\sin bx} = \frac{a}{b}
$$

$$
\lim_{x \to 0} \frac{\tan ax}{\tan bx} = \frac{a}{b}
$$

### Второй замечательный предел

$$
\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e
$$

$$
\lim_{x \to 0} (1 + x)^{1/x} = e
$$

Следствия:

$$
\lim_{x \to 0} \frac{\ln(1+x)}{x} = 1
$$

$$
\lim_{x \to 0} \frac{e^x - 1}{x} = 1
$$

$$
\lim_{x \to 0} \frac{a^x - 1}{x} = \ln a
$$

---

## 14. Эквивалентные бесконечно малые при $x \to 0$

| Бесконечно малая | Эквивалент |
|---|---|
| $\sin x$ | $x$ |
| $\tan x$ | $x$ |
| $\arcsin x$ | $x$ |
| $\arctan x$ | $x$ |
| $1 - \cos x$ | $\dfrac{x^2}{2}$ |
| $\ln(1+x)$ | $x$ |
| $e^x - 1$ | $x$ |
| $a^x - 1$ | $x \ln a$ |
| $(1+x)^\alpha - 1$ | $\alpha x$ |
| $\sin x - x$ | $-\dfrac{x^3}{6}$ |
| $1 - \cos x - \dfrac{x^2}{2}$ | $-\dfrac{x^4}{24}$ |
| $\cos x - 1 + \dfrac{x^2}{2}$ | $\dfrac{x^4}{24}$ |

> Важно: в произведениях и отношениях эквивалентные бесконечно малые обычно можно заменять друг на друга, а вот в суммах и разностях — вообще говоря, нельзя без дополнительного обоснования.

---

## 15. Разложение в ряд Тейлора (часто нужно для пределов)

$$
\sin x = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \frac{x^7}{7!} + \cdots
$$

$$
\cos x = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \frac{x^6}{6!} + \cdots
$$

$$
e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots
$$

$$
\ln(1+x) = x - \frac{x^2}{2} + \frac{x^3}{3} - \frac{x^4}{4} + \cdots
$$

$$
(1+x)^\alpha = 1 + \alpha x + \frac{\alpha(\alpha-1)}{2}x^2 + \cdots
$$

---

## 16. Пример применения для пределов

### Задача: найти

$$
\lim_{x \to 0} \frac{1 - \cos x}{x^2}
$$

**Решение** через формулу $1 - \cos x = 2\sin^2(x/2)$:

$$
\frac{1 - \cos x}{x^2} = \frac{2\sin^2(x/2)}{x^2} = \frac{1}{2}\left(\frac{\sin(x/2)}{x/2}\right)^2 \to \frac{1}{2}.
$$

### Задача: найти

$$
\lim_{x \to 0} \frac{\sin 3x}{\sin 5x}
$$

**Решение** через эквивалентные:

$$
\frac{\sin 3x}{\sin 5x} \sim \frac{3x}{5x} = \frac{3}{5}.
$$

### Задача: найти

$$
\lim_{x \to 0} \frac{\tan x - \sin x}{x^3}
$$

**Решение**:

$$
\tan x - \sin x = \sin x\left(\frac{1}{\cos x} - 1\right) = \sin x \cdot \frac{1 - \cos x}{\cos x}
$$

$$
= \sin x \cdot \frac{2\sin^2(x/2)}{\cos x}.
$$

Тогда

$$
\frac{\tan x - \sin x}{x^3} = \frac{\sin x}{x} \cdot \frac{1}{\cos x} \cdot \frac{2\sin^2(x/2)}{x^2} \sim 1 \cdot 1 \cdot \frac{2 \cdot (x/2)^2}{x^2} = \frac{1}{2}.
$$

### Задача: найти

$$
\lim_{x \to 0} \frac{\cos x - \cos 3x}{x^2}
$$

**Решение** через формулу разности косинусов:

$$
\cos x - \cos 3x = -2\sin\frac{x+3x}{2} \sin\frac{x-3x}{2} = -2\sin(2x) \sin(-x) = 2\sin(2x)\sin x.
$$

Тогда

$$
\frac{\cos x - \cos 3x}{x^2} = 2 \cdot \frac{\sin(2x)}{x} \cdot \frac{\sin x}{x} \to 2 \cdot 2 \cdot 1 = 4.
$$

---

## 17. Что чаще всего применять в задачах на пределы

### Если видишь синус

- Увидел $\dfrac{\sin \Box}{\Box}$ при $\Box \to 0$ — это стремится к $1$.
- Увидел $\dfrac{\sin ax}{\sin bx}$ при $x \to 0$ — ответ обычно $\dfrac{a}{b}$.
- Увидел разность синусов — попробуй формулу
  $$
  \sin \alpha - \sin \beta = 2\cos\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}.
  $$

### Если видишь косинус

- Увидел $1 - \cos \Box$ — заменяй на $2\sin^2(\Box/2)$.
- Для малых $x$ полезно помнить:
  $$
  1 - \cos x \sim \frac{x^2}{2}.
  $$
- Разность косинусов часто удобно раскрывать так:
  $$
  \cos \alpha - \cos \beta = -2\sin\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}.
  $$

### Если видишь тангенс

- Увидел $\dfrac{\tan x}{x}$ при $x \to 0$ — это $1$.
- Увидел $\dfrac{\tan ax}{\tan bx}$ при $x \to 0$ — это $\dfrac{a}{b}$.
- Иногда полезно писать
  $$
  \tan x = \frac{\sin x}{\cos x}.
  $$

### Если видишь степень вида $1^\infty$

- Используй второй замечательный предел.
- Часто нужно взять логарифм или привести выражение к виду
  $$
  \left(1 + u(x)\right)^{v(x)}.
  $$

### Если стандартные формулы не срабатывают

- Используй эквивалентные бесконечно малые.
- Используй разложения Тейлора до нужного порядка.
- Пробуй зажать выражение.

---

## 18. Мини-набор формул, которые стоит помнить наизусть

$$
\sin^2 x + \cos^2 x = 1
$$

$$
\tan x = \frac{\sin x}{\cos x}
$$

$$
\sin(\alpha \pm \beta) = \sin \alpha \cos \beta \pm \cos \alpha \sin \beta
$$

$$
\cos(\alpha \pm \beta) = \cos \alpha \cos \beta \mp \sin \alpha \sin \beta
$$

$$
\sin 2x = 2\sin x\cos x
$$

$$
\cos 2x = 1 - 2\sin^2 x = 2\cos^2 x - 1
$$

$$
1 - \cos x = 2\sin^2 \frac{x}{2}
$$

$$
\sin \alpha - \sin \beta = 2\cos\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}
$$

$$
\cos \alpha - \cos \beta = -2\sin\frac{\alpha+\beta}{2}\sin\frac{\alpha-\beta}{2}
$$

$$
\lim_{x \to 0} \frac{\sin x}{x} = 1
$$

$$
1 - \cos x \sim \frac{x^2}{2}
$$

$$
\tan x \sim x \quad (x \to 0)
$$
