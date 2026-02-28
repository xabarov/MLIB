# Coverage Analysis: Chapter 7. ML Workflows

Source: https://huyenchip.com/ml-interviews-book/contents/chapter-7.-machine-learning-workflows.html

---

## 7.1 Basics

| Book question | File | Status |
|---|---|---|
| Empirical risk minimization (what is risk, why empirical, how to minimize) | `Basics/Empirical Risk Minimization.md` | ✅ |
| Hyperparameters: explain tuning algorithm | `Basics/Алгоритм оптимизации гиперпараметров.md` | ✅ |
| Hyperparameters: why important, parameters vs hyperparameters | `Basics/Parameters vs Hyperparameters.md` | ✅ |
| Classification vs regression | `Basics/Classification vs Regression.md` | ✅ |
| Parametric vs non-parametric methods | `Basics/Parametric vs Non-parametric Methods.md` | ✅ |
| Model performs well on test but poorly in production (hypotheses, validation, fix) | `Basics/Your model performs really well on the test set but poorly in production.md` | ✅ |
| Occam's Razor in ML | `Basics/Occam's Razor in ML.md` | ✅ |
| L1 regularization — sparsity | `Basics/L1 Regularization.md` | ✅ |
| L2 regularization — weights near zero | `Basics/L2 Regularization.md` | ✅ |
| Universal Approximation Theorem — why can't it reach arbitrary small error | `Basics/Universal Approximation Theorem Limitations.md` | ✅ |
| Saddle points vs local minima — which cause more problems | `Basics/Saddle Points and Local Minima.md` | ✅ |
| Wide vs deep NN (same params) — which is more expressive | `Basics/Wide vs Deep Neural Network.md` | ✅ |
| Ensembling — why it improves performance | `Basics/Ensembling.md` | ✅ |
| Supervised / unsupervised / semi-supervised / active learning | `Basics/Supervised Unsupervised Semi-supervised Active Learning.md` | ✅ |
| Conditions that allowed deep learning popularity | `Basics/Conditions for Deep Learning Popularity.md` | ✅ |
| Why ML model performance degrades in production | `Basics/ML Model Performance Degradation in Production.md` | ✅ |
| Problems when deploying large ML models | `Basics/Deploying Large ML Models.md` | ✅ |

### Extra notes (not directly from book question list)
*(none)*

---

## 7.2 Sampling and Creating Training Data

| Book question | File | Status |
|---|---|---|
| Candidate sampling algorithms (softmax over many classes) | `Sampling.../Candidate Sampling.md` | ✅ |
| Reddit 10M comments: how to sample 100K to label + quality check | `Sampling.../Reddit Comment Sampling.md` | ✅ |
| Selection bias: news translation example | `Sampling.../Selection Bias.md` | ✅ |
| Train/test from same distribution — how to determine | `Sampling.../Train Test Distribution.md` | ✅ |
| Sample duplication (train set or test set) | `Sampling.../Outliers and Duplicates.md` | ✅ |
| Missing data — selection bias, 30% missing variables | `Sampling.../Missing Data.md` | ✅ |
| Class imbalance — effect, why hard, techniques | `Sampling.../Class Imbalance.md` | ✅ |
| Training data leakage (random time-based split, oversampling before split) | `Sampling.../Data Leakage.md` | ✅ |
| Data sparsity — effect on models | `Sampling.../Data Sparsity.md` | ✅ |
| Feature leakage — detection, normalization, causes | `Sampling.../Feature Leakage.md` | ✅ |
| Curse of dimensionality (more features effect) | `Sampling.../Curse of Dimensionality.md` | ✅ |

### Extra notes (beyond book question list)
| File | Topic |
|---|---|
| `Combinatorics Basics.md` | Combinatorics review |
| `Enough Samples for ML.md` | Sample size estimation |
| `Experimental Design Randomization.md` | A/B test design |
| `High-dimensional Sampling.md` | Sampling in high dimensions |
| `Markov Chain Monte Carlo.md` | MCMC methods |
| `Numerical and Textual Features.md` | Feature engineering |
| `Sampling With and Without Replacement.md` | Sampling methods |
| `Tweet Misinformation Partitioning.md` | Applied partitioning problem |
| `Understanding Sampling With and Without Replacement (Python).md` | Code walkthrough |

---

## 7.3 Objective Functions, Metrics, and Evaluation

| Book question | File | Status |
|---|---|---|
| Convergence — what it means, how to detect | `Metrics.../Convergence.md` | ✅ |
| Bias-variance trade-off + relation to over/underfitting | `Metrics.../Bias-Variance Tradeoff.md` | ✅ |
| Cross-validation methods; why less used in DL | `Metrics.../Cross-Validation.md` | ✅ |
| Train/valid/test splits — why val needed, why train≠test | `Metrics.../Train Valid Test Splits.md` | ✅ |
| Loss curves (train/val/test) — causes and fixes | `Metrics.../Train Valid Test Loss Curves Interpretation.md` | ✅ |
| Cancer prediction 99.99% accuracy — how to respond | `Metrics.../Cancer Prediction 99.99 Accuracy.md` | ✅ |
| F1 score — benefit over accuracy, multiclass | `Metrics.../F1 Score.md` | ✅ |
| Confusion matrix (TP=30, FN=20, FP=5, TN=40) — precision/recall/F1 | `Metrics.../Confusion Matrix Precision Recall.md` | ✅ |
| F1 with 99%/1% imbalance — all-A model; random model | `Metrics.../F1 Imbalance Edge Cases.md` | ✅ |
| MPE vs MAP — difference + example of divergence | `Metrics.../MPE vs MAP.md` | ✅ |
| MAPE — stock price prediction metric | `Metrics.../MAPE.md` | ✅ |
| Entropy and KL Divergence | `Metrics.../Entropy and KL Divergence.md` | ✅ |

### Extra notes (beyond book question list)
| File | Topic |
|---|---|
| `Cross-Entropy and NLL.md` | NLL = cross-entropy proof + why CE > MSE for classification |
| `Log Loss vs MSE.md` | Comparison for classification tasks |
| `RMSE vs MAE.md` | Regression metric comparison |
| `Overfitting Underfitting Loss Curves.md` | ASCII diagrams of overfitting/underfitting curves |

---

## Summary

| Section | Book questions | Covered | Missing |
|---|---|---|---|
| 7.1 Basics | ~17 | 17 | 0 |
| 7.2 Sampling | ~11 | 11 | 0 |
| 7.3 Metrics | ~12 | 12 | 0 |
| **Total** | **~40** | **40** | **0** |

**Coverage: 100% of identified book questions.**  
Extra notes: 13 additional files beyond the book question list.
