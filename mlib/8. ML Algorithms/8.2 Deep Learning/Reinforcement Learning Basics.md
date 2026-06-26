# Reinforcement Learning — основы

**Вопросы (EN)**: Explore vs exploit? Finite vs infinite horizon? Why discount term? On-policy vs off-policy? Model-based vs model-free?

## Ответ

### Explore vs Exploit

- **Exploit** — выбор действия с максимальной ожидаемой наградой по текущим оценкам.
- **Explore** — пробовать другие действия для улучшения оценок.
- Trade-off: ε-greedy, UCB, Thompson sampling, softmax.

### Finite vs Infinite Horizon

- **Finite** — T шагов; оптимизация суммарной награды за T шагов.
- **Infinite** — бесконечное время; нужен discount γ < 1, иначе сумма может расходиться.

### Discount (γ)

- Учитывает предпочтение ближайших наград.
- γ < 1 гарантирует сходимость при бесконечном горизонте.
- Отражает «терпение» агента.

### On-policy vs Off-policy

- **On-policy** — данные собираются той же политикой, которая обновляется (SARSA, A2C).
- **Off-policy** — используются данные от другой политики (Q-learning, DQN). Эффективнее по данным, но сложнее и менее стабильно.

### Model-based vs Model-free

- **Model-based** — модель переходов/наград; планирование; обычно более data-efficient.
- **Model-free** — без явной модели; прямое обучение value function или policy. Часто проще, но может требовать больше данных.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
