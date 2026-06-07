# SHAD Interactive: human mission review

Generated audit lives in `mission_quality_report.md` and is rewritten by
`make mission-audit`. This file is manual and should survive audit reruns.

## Review 2026-06-07

### Available Candidates Promoted

| Mission | Status | Evidence |
| --- | --- | --- |
| `Кузница определителя` | `available` | Pure model tests, happy/mistake smoke, determinant field pulse, orientation/collapse repair marker and result moment. |
| `Графовый диспетчер` | `available` | Queue/stack state is playable, mistake path now shows expected ghost vertex and repair marker, smoke covers marker. |
| `Фабрика признаков` | `available` | Data cleaning has alternative bad/good actions, pipeline diff, split check, dirty-column repair markers and smoke-covered repair. |

### Still Prototype

| Mission | Reason |
| --- | --- |
| `PCA-компрессор` | New mission; needs one extra pass on residual hotspot and component rail before promotion. |
| `Унитарный компас` | Dense complex geometry; needs mobile density and field-marker review. |
| `SVD-линза` | Strong geometry, but controls and PCA transfer should be reviewed after compression stage. |
| `Евклидова мастерская` | Good model coverage; needs a field-level failure marker pass. |
| `Матрица как машина` | Clear concept, but still has worksheet-like levels. |
| `Охота за ядром` | Strong visual scene, but residual failures need clearer 2D support. |

### One-Click Risks

- `Матрица как машина`: several levels can still be solved by setting one obvious column.
- `Охота за ядром`: coordinate entry can become direct answer entry without enough visible repair.
- `PCA-компрессор`: `fit budget` and `fix artifact` are useful smoke affordances, but final user flow should still expose metric tradeoff.

### Visible-Failure Gaps

- `Унитарный компас`: fake Hermitian and non-unitary states are diagnosed well, but the failed object could be marked more directly.
- `SVD-линза`: eigenvalue trap is clear in text; field could show wrong-space selection more explicitly.
- `Kernel Hunt`: failed row equation should be marked outside the 3D canvas.

### Screenshot Notes

- `PCA-компрессор`: mobile is readable; desktop component rail is acceptable after compact layout, but local residual hotspot marker remains P1.
- `Feature Factory`: intentionally dense/operational; markers should stay compact and not become decorative.
- `Graph Dispatcher`: graph field has enough room for repair marker without covering vertices.

### Next Polish Backlog

1. Add residual hotspot marker to `PCA-компрессор`.
2. Add row-equation residual board to `Охота за ядром`.
3. Add challenge variants to `Матрица как машина`.
4. Review mobile density for `Унитарный компас`, `SVD-линза` and
   `Евклидова мастерская`.
