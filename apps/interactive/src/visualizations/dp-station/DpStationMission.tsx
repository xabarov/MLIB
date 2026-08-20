import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { dpStationMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseDp,
  dpLevels,
  dpLevelSuccess,
  editTable,
  fillCell,
  initialFilled,
  isReady,
  readyCells,
  type DpLevelId,
} from './dpStationModel'

const levelIdMap: Record<string, DpLevelId> = {
  'cot-cat': 'cot-cat',
  'cat-cart': 'cat-cart',
  'food-gold': 'food-gold',
}

export function DpStationMission() {
  const definition = dpStationMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <DpStationLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function DpStationLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = dpStationMission
  const levelId = levelIdMap[activeLevel.id]
  const config = dpLevels[levelId]
  const m = config.rowWord.length
  const n = config.colWord.length
  const table = useMemo(() => editTable(config.rowWord, config.colWord), [config])

  const [filled, setFilled] = useState<boolean[][]>(() => initialFilled(m, n))
  const [lastNotReady, setLastNotReady] = useState(false)
  const [touched, setTouched] = useState(false)

  const diagnosis = diagnoseDp({ filled, touched, lastNotReady })
  const levelSuccess = dpLevelSuccess(filled)
  const ready = readyCells(filled)
  const remaining = filled.reduce(
    (sum, row, i) =>
      sum + row.reduce((rowSum, cell, j) => rowSum + (i > 0 && j > 0 && !cell ? 1 : 0), 0),
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
    thinking: 'Я слежу за порядком. Считай только те клетки, у которых готовы все три соседки.',
    idle: 'Заполняй таблицу по порядку: каждая клетка зависит от left, top и diagonal.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'remaining',
      label: 'left',
      value: remaining,
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'ready',
      label: 'ready',
      value: ready.length,
      tone: ready.length > 0 ? 'target' : 'neutral',
    },
  ]

  const clickCell = (i: number, j: number) => {
    if (i === 0 || j === 0 || filled[i][j]) return
    setTouched(true)
    if (isReady(filled, i, j)) {
      setLastNotReady(false)
      setFilled((current) => fillCell(current, i, j))
      return
    }
    setLastNotReady(true)
  }

  const resetLevel = () => {
    setFilled(initialFilled(m, n))
    setLastNotReady(false)
    setTouched(false)
  }

  const columns = n + 2 // row-letter + (n+1) cells
  const answer = table[m][n]

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
        <div className="relative flex h-full flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_24%_18%,rgba(124,108,207,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess && touched} label={`расстояние = ${answer}`} />
          {showRepairMarker && (
            <RepairMarker tone="warning" label="рано считать" xPercent={50} yPercent={3} />
          )}
          <div
            className="rounded-lg border border-ink/15 bg-paper p-3 shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="dp-station-grid"
          >
            <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${columns}, 2.3rem)` }}>
              <span />
              <span className="flex h-9 items-center justify-center text-xs font-bold text-ink/40">∅</span>
              {config.colWord.split('').map((ch, index) => (
                <span key={`col-${index}`} className="flex h-9 items-center justify-center text-sm font-black text-target">
                  {ch}
                </span>
              ))}

              {Array.from({ length: m + 1 }, (_, i) => (
                <RowFragment
                  key={`row-${i}`}
                  i={i}
                  n={n}
                  rowLabel={i === 0 ? '∅' : config.rowWord[i - 1]}
                  table={table}
                  filled={filled}
                  onCell={clickCell}
                />
              ))}
            </div>
          </div>

          {levelSuccess && (
            <div
              className="rounded-md border border-success/30 bg-success/10 px-3 py-2 text-sm font-semibold text-ink"
              data-testid="dp-answer"
            >
              Редакционное расстояние {config.rowWord} → {config.colWord} = {answer}
            </div>
          )}
        </div>
      }
      controls={
        <div className="space-y-3">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="dp-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Если буквы совпали, берём диагональ; иначе 1 + минимум из left, top и
            diagonal. Клетку можно считать только когда готовы все три соседки.
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="dp-reset"
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

function RowFragment({
  i,
  n,
  rowLabel,
  table,
  filled,
  onCell,
}: {
  i: number
  n: number
  rowLabel: string
  table: number[][]
  filled: boolean[][]
  onCell: (i: number, j: number) => void
}) {
  return (
    <>
      <span className="flex h-9 items-center justify-center text-sm font-black text-orange">{rowLabel}</span>
      {Array.from({ length: n + 1 }, (_, j) => {
        const isBase = i === 0 || j === 0
        const isFilled = filled[i][j]
        if (isBase) {
          return (
            <span
              key={`cell-${i}-${j}`}
              className="flex h-9 items-center justify-center rounded bg-bg/60 text-sm font-semibold tabular-nums text-ink/55"
            >
              {table[i][j]}
            </span>
          )
        }
        if (isFilled) {
          return (
            <span
              key={`cell-${i}-${j}`}
              className="flex h-9 items-center justify-center rounded bg-success/12 text-sm font-bold tabular-nums text-ink"
            >
              {table[i][j]}
            </span>
          )
        }
        const ready = isReady(filled, i, j)
        return (
          <button
            key={`cell-${i}-${j}`}
            type="button"
            onClick={() => onCell(i, j)}
            className={`flex h-9 items-center justify-center rounded border text-sm font-bold transition ${
              ready
                ? 'border-orange/50 bg-orange/15 text-orange hover:bg-orange/25'
                : 'border-ink/10 bg-paper/50 text-ink/30 hover:border-ink/20'
            }`}
            data-testid={`dp-cell-${i}-${j}`}
          >
            {ready ? '?' : ''}
          </button>
        )
      })}
    </>
  )
}
