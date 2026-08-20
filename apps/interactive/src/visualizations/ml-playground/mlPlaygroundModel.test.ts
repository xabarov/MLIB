import { describe, expect, it } from 'vitest'
import {
  accuracy,
  applyModel,
  confusionCounts,
  diagnoseModel,
  mlBaseRows,
  precisionRecallF1,
  rowsForLevel,
  trainTestMetrics,
} from './mlPlaygroundModel'

describe('mlPlaygroundModel', () => {
  it('predicts threshold labels and confusion counts', () => {
    const rows = applyModel(mlBaseRows, { featureId: 'signal', threshold: 58, direction: 'gte' })
    expect(confusionCounts(rows.filter((row) => row.split === 'test'))).toEqual({
      tp: 3,
      fp: 0,
      tn: 3,
      fn: 0,
    })
    expect(accuracy(rows.filter((row) => row.split === 'test'))).toBe(1)
  })

  it('computes precision recall and f1 with zero-division safety', () => {
    const rows = applyModel(rowsForLevel('f1-threshold'), {
      featureId: 'signal',
      threshold: 100,
      direction: 'gte',
    })
    const metrics = precisionRecallF1(rows)
    expect(metrics.precision).toBe(0)
    expect(metrics.recall).toBe(0)
    expect(metrics.f1).toBe(0)
  })

  it('diagnoses train/test gap before accepting a high train metric', () => {
    const rows = rowsForLevel('test-control')
    expect(
      diagnoseModel('test-control', rows, { featureId: 'signal', threshold: 45, direction: 'gte' })
        .kind,
    ).toBe('train-test-gap')
    expect(
      diagnoseModel('test-control', rows, { featureId: 'signal', threshold: 58, direction: 'gte' })
        .kind,
    ).toBe('good-fit')
  })

  it('diagnoses accuracy trap on imbalanced data', () => {
    const rows = rowsForLevel('f1-threshold')
    expect(
      diagnoseModel('f1-threshold', rows, {
        featureId: 'signal',
        threshold: 75,
        direction: 'gte',
      }).kind,
    ).toBe('accuracy-trap')
    expect(
      diagnoseModel('f1-threshold', rows, {
        featureId: 'signal',
        threshold: 59,
        direction: 'gte',
      }).kind,
    ).toBe('good-fit')
  })

  it('rejects leakage even when raw metrics look good', () => {
    const rows = rowsForLevel('leakage-trap')
    const predicted = applyModel(rows, {
      featureId: 'leakage_score',
      threshold: 0.5,
      direction: 'gte',
    })
    const metrics = trainTestMetrics(predicted)
    expect(metrics.find((metric) => metric.id === 'accuracy')?.train).toBe(1)
    expect(diagnoseModel('leakage-trap', rows, mlLevel('leakage_score', 0.5)).kind).toBe(
      'leakage-used',
    )
    expect(diagnoseModel('leakage-trap', rows, mlLevel('signal', 58)).kind).toBe('good-fit')
  })
})

function mlLevel(featureId: string, threshold: number) {
  return { featureId, threshold, direction: 'gte' as const }
}
