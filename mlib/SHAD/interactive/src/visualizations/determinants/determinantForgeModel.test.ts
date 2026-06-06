import { describe, expect, it } from 'vitest'
import {
  determinant,
  determinantArea,
  determinantLevelSuccess,
  isDegenerate,
  snapCoord,
  svgPointToCoord,
} from './determinantForgeModel'

describe('determinantForgeModel', () => {
  it('computes determinant, area and degeneracy', () => {
    expect(determinant([1, 0], [0, 2])).toBe(2)
    expect(determinantArea([1, 0], [0, 2])).toBe(2)
    expect(isDegenerate([1, 1], [2, 2])).toBe(true)
  })

  it('snaps and clamps coordinates', () => {
    expect(snapCoord(1.12)).toBe(1)
    expect(snapCoord(1.13)).toBe(1.25)
    expect(snapCoord(9)).toBe(3)
    expect(snapCoord(-9)).toBe(-3)
  })

  it('checks level-specific success predicates', () => {
    expect(
      determinantLevelSuccess({
        levelId: 'area-two',
        u: [1, 0],
        v: [0, 2],
        completedLevelIds: [],
      }),
    ).toBe(true)
    expect(
      determinantLevelSuccess({
        levelId: 'flip-orientation',
        u: [1, 0],
        v: [0, -2],
        completedLevelIds: ['area-two'],
      }),
    ).toBe(true)
    expect(
      determinantLevelSuccess({
        levelId: 'repair-matrix',
        u: [1, 0],
        v: [0, 1],
        completedLevelIds: ['break-invertibility'],
      }),
    ).toBe(true)
  })

  it('maps SVG pointer positions to snapped math coordinates', () => {
    expect(
      svgPointToCoord({
        clientX: 100,
        clientY: 100,
        rect: { left: 0, top: 0, width: 200, height: 200 },
      }),
    ).toEqual([0, 0])
  })
})
