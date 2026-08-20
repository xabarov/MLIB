import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { pascalTriangleMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  buildPascalTable,
  diagnosePascal,
  fillCell,
  initialFilled,
  isReady,
  pascalLevels,
  pascalLevelSuccess,
  readyCells,
  type PascalLevelId,
} from './pascalTriangleModel'

const levelIdMap: Record<string, PascalLevelId> = {
  'triangle-5': 'triangle-5',
  'triangle-6': 'triangle-6',
  'triangle-7': 'triangle-7',
}

export function PascalTriangleMission() {
  const definition = pascalTriangleMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <PascalTriangleLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function PascalTriangleLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = pascalTriangleMission
  const levelId = levelIdMap[activeLevel.id]
  const config = pascalLevels[levelId]
  const rows = config.rows
  const table = useMemo(() => buildPascalTable(rows), [rows])

  const [filled, setFilled] = useState<boolean[][]>(() => initialFilled(rows))
  const [lastNotReady, setLastNotReady] = useState(false)
  const [touched, setTouched] = useState(false)

  const diagnosis = diagnosePascal({ filled, touched, lastNotReady })
  const levelSuccess = pascalLevelSuccess(filled)
  const ready = readyCells(filled)
  const remaining = filled.reduce(
    (sum, row, i) =>
      sum + row.reduce((rowSum, cell, j) => rowSum + (j > 0 && j < i && !cell ? 1 : 0), 0),
    0,
  )

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker = touched && !levelSuccess && diagnosis.kind === 'not-ready'

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: ready.length > 0 && touched && !levelSuccess,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я слежу за порядком. Считай клетку, когда обе соседки сверху готовы.',
    idle: 'Заполняй внутренние клетки: каждая равна сумме двух клеток над ней.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'remaining',
      label: 'осталось',
      value: remaining,
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'ready',
      label: 'готово',
      value: ready.length,
      tone: ready.length > 0 ? 'target' : 'neutral',
    },
  ]

  const clickCell = (i: number, j: number) => {
    if (j <= 0 || j >= i || filled[i][j]) return
    setTouched(true)
    if (isReady(filled, i, j)) {
      setLastNotReady(false)
      setFilled((current) => fillCell(current, i, j))
      return
    }
    setLastNotReady(true)
  }

  const resetLevel = () => {
    setFilled(initialFilled(rows))
    setLastNotReady(false)
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
      sceneViewportClassName="h-[460px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_24%_18%,rgba(120,140,93,0.16),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess && touched} label="треугольник собран" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label="рано считать" xPercent={50} yPercent={3} />
          )}
          <div
            className="flex flex-col items-center gap-1.5 rounded-lg border border-ink/15 bg-paper p-4 shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="pascal-triangle-grid"
          >
            {table.map((row, i) => (
              <div key={`row-${i}`} className="flex gap-1.5">
                {row.map((value, j) => {
                  const isEdge = j === 0 || j === i
                  if (isEdge) {
                    return (
                      <span
                        key={`cell-${i}-${j}`}
                        className="flex size-9 items-center justify-center rounded bg-bg/60 text-sm font-semibold tabular-nums text-ink/55"
                      >
                        {value}
                      </span>
                    )
                  }
                  if (filled[i][j]) {
                    return (
                      <span
                        key={`cell-${i}-${j}`}
                        className="flex size-9 items-center justify-center rounded bg-success/15 text-sm font-bold tabular-nums text-ink"
                      >
                        {value}
                      </span>
                    )
                  }
                  const cellReady = isReady(filled, i, j)
                  return (
                    <button
                      key={`cell-${i}-${j}`}
                      type="button"
                      onClick={() => clickCell(i, j)}
                      className={`flex size-9 items-center justify-center rounded border text-sm font-bold transition ${
                        cellReady
                          ? 'border-orange/50 bg-orange/15 text-orange hover:bg-orange/25'
                          : 'border-ink/10 bg-paper/50 text-ink/30 hover:border-ink/20'
                      }`}
                      data-testid={`pascal-cell-${i}-${j}`}
                    >
                      {cellReady ? '?' : ''}
                    </button>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="pascal-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Клетка C(n, k) равна сумме двух соседок строкой выше: C(n−1, k−1) +
            C(n−1, k). Рёбра треугольника — единицы, а сумма строки n равна 2ⁿ.
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="pascal-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Осталось клеток: <span className="font-semibold">{remaining}</span>, готовых:{' '}
          <span className="font-semibold">{ready.length}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
