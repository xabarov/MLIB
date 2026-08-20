# Coverage Analysis: Chapter 7. ML Workflows

Source: https://huyenchip.com/ml-interviews-book/contents/chapter-7.-machine-learning-workflows.html

---

## 7.1 Basics

| Book question | File | Status |
|---|---|---|
| Empirical risk minimization (what is risk, why empirical, how to minimize) | `basics/Empirical Risk Minimization.md` | ✅ |
| Hyperparameters: explain tuning algorithm | `basics/Алгоритм оптимизации гиперпараметров.md` | ✅ |
| Hyperparameters: why important, parameters vs hyperparameters | `basics/Parameters vs Hyperparameters.md` | ✅ |
| Classification vs regression | `basics/classification-vs-regression/lesson.md` 📖 | ✅ |
| Parametric vs non-parametric methods | `basics/Parametric vs Non-parametric Methods.md` | ✅ |
| Model performs well on test but poorly in production (hypotheses, validation, fix) | `basics/Your model performs really well on the test set but poorly in production.md` | ✅ |
| Occam's Razor in ML | `basics/Occam's Razor in ML.md` | ✅ |
| L1 regularization — sparsity | `basics/L1 Regularization.md` | ✅ |
| L2 regularization — weights near zero | `basics/L2 Regularization.md` | ✅ |
| Universal Approximation Theorem — why can't it reach arbitrary small error | `basics/Universal Approximation Theorem Limitations.md` | ✅ |
| Saddle points vs local minima — which cause more problems | `basics/Saddle Points and Local Minima.md` | ✅ |
| Wide vs deep NN (same params) — which is more expressive | `basics/Wide vs Deep Neural Network.md` | ✅ |
| Ensembling — why it improves performance | `basics/Ensembling.md` | ✅ |
| Supervised / unsupervised / semi-supervised / active learning | `basics/Supervised Unsupervised Semi-supervised Active Learning.md` | ✅ |
| Conditions that allowed deep learning popularity | `basics/Conditions for Deep Learning Popularity.md` | ✅ |
| Why ML model performance degrades in production | `basics/ML Model Performance Degradation in Production.md` | ✅ |
| Problems when deploying large ML models | `basics/Deploying Large ML Models.md` | ✅ |

### Extra notes (not directly from book question list)
*(none)*

---

## 7.2 Sampling and Creating Training Data

| Book question | File | Status |
|---|---|---|
| Candidate sampling algorithms (softmax over many classes) | `sampling-training-data/Candidate Sampling.md` | ✅ |
| Reddit 10M comments: how to sample 100K to label + quality check | `sampling-training-data/Reddit Comment Sampling.md` | ✅ |
| Selection bias: news translation example | `sampling-training-data/Selection Bias.md` | ✅ |
| Train/test from same distribution — how to determine | `sampling-training-data/Train Test Distribution.md` | ✅ |
| Sample duplication (train set or test set) | `sampling-training-data/Outliers and Duplicates.md` | ✅ |
| Missing data — selection bias, 30% missing variables | `sampling-training-data/Missing Data.md` | ✅ |
| Class imbalance — effect, why hard, techniques | `sampling-training-data/Class Imbalance.md` | ✅ |
| Training data leakage (random time-based split, oversampling before split) | `sampling-training-data/Data Leakage.md` | ✅ |
| Data sparsity — effect on models | `sampling-training-data/Data Sparsity.md` | ✅ |
| Feature leakage — detection, normalization, causes | `sampling-training-data/Feature Leakage.md` | ✅ |
| Curse of dimensionality (more features effect) | `sampling-training-data/Curse of Dimensionality.md` | ✅ |

### Extra notes (beyond book question list)
| File | Topic |
|---|---|
| `sampling-training-data/Combinatorics Basics.md` | Combinatorics review |
| `sampling-training-data/Enough Samples for ML.md` | Sample size estimation |
| `sampling-training-data/Experimental Design Randomization.md` | A/B test design |
| `sampling-training-data/High-dimensional Sampling.md` | Sampling in high dimensions |
| `sampling-training-data/Markov Chain Monte Carlo.md` | MCMC methods |
| `sampling-training-data/Numerical and Textual Features.md` | Feature engineering |
| `sampling-training-data/Sampling With and Without Replacement.md` | Sampling methods |
| `sampling-training-data/Tweet Misinformation Partitioning.md` | Applied partitioning problem |
| `sampling-training-data/Understanding Sampling With and Without Replacement (Python).md` | Code walkthrough |

---

## 7.3 Objective Functions, Metrics, and Evaluation

| Book question | File | Status |
|---|---|---|
| Convergence — what it means, how to detect | `objectives-metrics-evaluation/Convergence.md` | ✅ |
| Bias-variance trade-off + relation to over/underfitting | `objectives-metrics-evaluation/Bias-Variance Tradeoff.md` | ✅ |
| Cross-validation methods; why less used in DL | `objectives-metrics-evaluation/Cross-Validation.md` | ✅ |
| Train/valid/test splits — why val needed, why train≠test | `objectives-metrics-evaluation/Train Valid Test Splits.md` | ✅ |
| Loss curves (train/val/test) — causes and fixes | `objectives-metrics-evaluation/Train Valid Test Loss Curves Interpretation.md` | ✅ |
| Cancer prediction 99.99% accuracy — how to respond | `objectives-metrics-evaluation/Cancer Prediction 99.99 Accuracy.md` | ✅ |
| F1 score — benefit over accuracy, multiclass | `objectives-metrics-evaluation/F1 Score.md` | ✅ |
| Confusion matrix (TP=30, FN=20, FP=5, TN=40) — precision/recall/F1 | `objectives-metrics-evaluation/Confusion Matrix Precision Recall.md` | ✅ |
| F1 with 99%/1% imbalance — all-A model; random model | `objectives-metrics-evaluation/F1 Imbalance Edge Cases.md` | ✅ |
| MPE vs MAP — difference + example of divergence | `objectives-metrics-evaluation/MPE vs MAP.md` | ✅ |
| MAPE — stock price prediction metric | `objectives-metrics-evaluation/MAPE.md` | ✅ |
| Entropy and KL Divergence | `objectives-metrics-evaluation/Entropy and KL Divergence.md` | ✅ |

### Extra notes (beyond book question list)
| File | Topic |
|---|---|
| `objectives-metrics-evaluation/Cross-Entropy and NLL.md` | NLL = cross-entropy proof + why CE > MSE for classification |
| `objectives-metrics-evaluation/Log Loss vs MSE.md` | Comparison for classification tasks |
| `objectives-metrics-evaluation/RMSE vs MAE.md` | Regression metric comparison |
| `objectives-metrics-evaluation/Overfitting Underfitting Loss Curves.md` | ASCII diagrams of overfitting/underfitting curves |

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
