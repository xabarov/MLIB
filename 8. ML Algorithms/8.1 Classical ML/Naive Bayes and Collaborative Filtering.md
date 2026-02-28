# Naive Bayes и Collaborative Filtering

**Вопросы (EN)**: Why is Naive Bayes naive? User-item vs item-item matrix? New user with no purchases? Feature scaling for kernel methods?

## Ответ

### Naive Bayes

«Наивное» предположение: признаки условно независимы при данном классе. \(P(X|Y) = \prod P(x_i|Y)\). На практике признаки часто коррелированы, но модель остаётся полезной и быстрой.

### User-item vs item-item

- **User-item:** для пользователя ищем похожих пользователей; рекомендации по их поведению. Много пользователей → большая матрица; cold start для новых пользователей.
- **Item-item:** для товара ищем похожие товары. Стабильнее при изменении пользователей; cold start для новых товаров.

### Новый пользователь без покупок

- Контентные признаки (демография, on-boarding).
- Popular items, random/exploration.
- Гибридные системы: content-based + collaborative.

### Feature scaling для kernel methods

Важно. SVM с RBF чувствителен к масштабу: \(|x - x'|^2\) в экспоненте. Признаки в разных масштабах искажают расстояния. Рекомендуется стандартизация.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
