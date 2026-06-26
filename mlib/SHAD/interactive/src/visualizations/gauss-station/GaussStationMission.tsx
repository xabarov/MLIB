import { useEffect, useMemo, useState } from 'react'
import { ArrowDownUp, RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { gaussStationMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  backSubstitution,
  canEliminate,
  COLS,
  diagnoseGauss,
  eliminableCells,
  eliminate,
  formatGaussNumber,
  gaussLevels,
  gaussLevelSuccess,
  ROWS,
  swapRows,
  type GaussLevelId,
  type Matrix,
} from './gaussStationModel'

const levelIdMap: Record<string, GaussLevelId> = {
  forward: 'forward',
  'need-swap': 'need-swap',
  fractions: 'fractions',
}

const swapPairs: Array<[number, number]> = [
  [0, 1],
  [1, 2],
  [0, 2],
]

export function GaussStationMission() {
  const definition = gaussStationMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <GaussStationLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function GaussStationLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = gaussStationMission
  const levelId = levelIdMap[activeLevel.id]
  const config = gaussLevels[levelId]
  const [matrix, setMatrix] = useState<Matrix>(config.start)
  const [touched, setTouched] = useState(false)

  const cells = useMemo(() => eliminableCells(matrix), [matrix])
  const diagnosis = diagnoseGauss({ matrix, touched })
  const levelSuccess = gaussLevelSuccess(matrix)
  const solution = useMemo(() => (levelSuccess ? backSubstitution(matrix) : null), [levelSuccess, matrix])

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker = touched && !levelSuccess && diagnosis.kind === 'pivot-zero'

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: cells.length > 0 && touched,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я опорный элемент. Обнуляй то, что под диагональю, через опорные строки.',
    idle: 'Кликай подсвеченные элементы под диагональю, чтобы привести систему к ступенчатому виду.',
  })

  const belowDiagonalNonzero = (() => {
    let count = 0
    for (let i = 1; i < ROWS; i += 1) {
      for (let j = 0; j < i; j += 1) {
        if (Math.abs(matrix[i][j]) > 0.005) count += 1
      }
    }
    return count
  })()

  const badges: MissionBadge[] = [
    {
      id: 'below',
      label: 'below',
      value: belowDiagonalNonzero,
      tone: levelSuccess ? 'success' : 'danger',
    },
    {
      id: 'ready',
      label: 'moves',
      value: cells.length,
      tone: cells.length > 0 ? 'energy' : 'neutral',
    },
  ]

  const eliminateAt = (i: number, j: number) => {
    if (!canEliminate(matrix, i, j)) return
    setTouched(true)
    setMatrix((current) => eliminate(current, i, j))
  }

  const swap = (i: number, k: number) => {
    setTouched(true)
    setMatrix((current) => swapRows(current, i, k))
  }

  const resetLevel = () => {
    setMatrix(config.start)
    setTouched(false)
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[440px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_24%_18%,rgba(77,134,168,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess && touched} label="ступенчатый вид" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label="нужен обмен строк" xPercent={50} yPercent={3} />
          )}
          <div
            className="rounded-lg border border-ink/15 bg-paper p-3 shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="gauss-station-grid"
          >
            <div className="grid grid-cols-[repeat(3,3rem)_0.5rem_3rem] gap-1.5">
              {matrix.map((row, i) =>
                row.map((value, j) => {
                  if (j === COLS - 1) {
                    return [
                      <span key={`bar-${i}`} className="row-span-1 w-px justify-self-center bg-ink/25" />,
                      <span
                        key={`b-${i}`}
                        className="flex h-11 items-center justify-center rounded bg-bg/70 text-sm font-semibold tabular-nums text-ink"
                      >
                        {formatGaussNumber(value)}
                      </span>,
                    ]
                  }
                  const eliminable = canEliminate(matrix, i, j)
                  const belowDiagonal = i > j
                  if (eliminable) {
                    return (
                      <button
                        key={`c-${i}-${j}`}
                        type="button"
                        onClick={() => eliminateAt(i, j)}
                        className="flex h-11 items-center justify-center rounded border border-orange/50 bg-orange/15 text-sm font-bold tabular-nums text-orange transition hover:bg-orange/25"
                        data-testid={`gauss-cell-${i}-${j}`}
                      >
                        {formatGaussNumber(value)}
                      </button>
                    )
                  }
                  return (
                    <span
                      key={`c-${i}-${j}`}
                      className={`flex h-11 items-center justify-center rounded text-sm font-semibold tabular-nums ${
                        belowDiagonal && Math.abs(value) > 0.005
                          ? 'bg-danger/10 text-danger'
                          : i === j
                            ? 'bg-target/10 text-ink'
                            : 'bg-bg/60 text-ink/80'
                      }`}
                    >
                      {formatGaussNumber(value)}
                    </span>
                  )
                }),
              )}
            </div>
          </div>

          {solution && (
            <div
              className="rounded-md border border-success/30 bg-success/10 px-3 py-2 text-sm font-semibold text-ink"
              data-testid="gauss-solution"
            >
              Обратный ход: x = {formatGaussNumber(solution[0])}, y = {formatGaussNumber(solution[1])}, z ={' '}
              {formatGaussNumber(solution[2])}
            </div>
          )}
        </div>
      }
      controls={
        <div className="space-y-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">обмен строк</p>
            <div className="flex flex-wrap gap-2">
              {swapPairs.map(([i, k]) => (
                <button
                  key={`swap-${i}-${k}`}
                  type="button"
                  onClick={() => swap(i, k)}
                  className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2.5 py-1.5 text-xs font-semibold text-ink transition hover:border-target/50"
                  data-testid={`gauss-swap-${i}-${k}`}
                >
                  <ArrowDownUp size={13} /> R{i + 1} ↔ R{k + 1}
                </button>
              ))}
            </div>
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="gauss-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <p className="text-xs leading-relaxed text-ink/60">
            Прямой ход метода Гаусса: обнуляй элементы под диагональю опорными
            строками, пока система не станет ступенчатой.
          </p>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="gauss-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Под диагональю ненулевых: <span className="font-semibold">{belowDiagonalNonzero}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
