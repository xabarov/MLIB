import { describe, expect, it } from 'vitest'
import {
  chooseSplitSeed,
  diagnoseFactory,
  dropRow,
  dropMissingRows,
  encodeCategory,
  factoryBaseRows,
  fillZero,
  imputeMedian,
  initialFactoryState,
  pipelineDiff,
  medianOfColumn,
  splitQuality,
  toggleFeature,
} from './featureFactoryModel'

describe('featureFactoryModel', () => {
  it('fills missing numeric values with the column median', () => {
    const state = initialFactoryState('missing-values')
    const median = medianOfColumn(state.rows, 'temperature')
    const next = imputeMedian(state, 'temperature')

    expect(median).toBe(58)
    expect(next.rows.some((row) => row.values.temperature === null)).toBe(false)
    expect(next.rows.find((row) => row.id === 'ff-02')?.values.temperature).toBe(58)
    expect(diagnoseFactory('missing-values', next).invariantOk).toBe(true)
  })

  it('shows why zero-fill and dropping missing rows are risky alternatives', () => {
    const state = initialFactoryState('missing-values')
    const zeroFilled = fillZero(state, 'temperature')
    const dropped = dropMissingRows(state, 'temperature')

    expect(diagnoseFactory('missing-values', zeroFilled).kind).toBe('zero-filled')
    expect(diagnoseFactory('missing-values', dropped).kind).toBe('coverage-lost')
    expect(pipelineDiff(zeroFilled).badSteps).toBe(1)
    expect(pipelineDiff(dropped).rowsDelta).toBe(-2)
  })

  it('accepts dropping the flagged outlier and rejects over-cleaning', () => {
    const state = initialFactoryState('outlier-repair')
    const repaired = dropRow(state, 'ff-07')

    expect(repaired.rows).toHaveLength(factoryBaseRows.length - 1)
    expect(diagnoseFactory('outlier-repair', repaired).kind).toBe('ready')

    const overCleaned = dropRow(dropRow(dropRow(state, 'ff-07'), 'ff-06'), 'ff-05')
    expect(diagnoseFactory('outlier-repair', overCleaned).kind).toBe('over-cleaned')
  })

  it('detects leakage until the leakage feature is disabled', () => {
    const state = initialFactoryState('leakage-off')

    expect(diagnoseFactory('leakage-off', state).kind).toBe('leakage-enabled')
    expect(diagnoseFactory('leakage-off', toggleFeature(state, 'leakage_code')).kind).toBe(
      'ready',
    )
  })

  it('requires encoding the categorical segment feature', () => {
    const state = initialFactoryState('encode-category')

    expect(diagnoseFactory('encode-category', state).kind).toBe('category-raw')
    expect(diagnoseFactory('encode-category', encodeCategory(state, 'segment')).kind).toBe(
      'ready',
    )
  })

  it('rejects disabling useful non-leakage features', () => {
    const state = initialFactoryState('encode-category')
    const withoutSignal = toggleFeature(state, 'signal')

    expect(diagnoseFactory('encode-category', withoutSignal).kind).toBe(
      'useful-feature-disabled',
    )
  })

  it('reports split quality gaps after repairs', () => {
    const state = dropRow(initialFactoryState('outlier-repair'), 'ff-07')
    const quality = splitQuality(state.rows)

    expect(quality.labelGap).toBeLessThanOrEqual(0.2)
    expect(quality.ok).toBe(true)
  })

  it('turns split selection into a checked decision', () => {
    const state = initialFactoryState('split-check')
    const skewed = chooseSplitSeed(state, 'train-heavy')
    const balanced = chooseSplitSeed(state, 'balanced')

    expect(diagnoseFactory('split-check', skewed).kind).toBe('split-skewed')
    expect(diagnoseFactory('split-check', balanced).kind).toBe('ready')
    expect(splitQuality(balanced.rows).ok).toBe(true)
  })
})
