import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { heapForgeMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseHeap,
  formatHeapValue,
  heapLevels,
  heapLevelSuccess,
  heapViolations,
  parentIndex,
  swapNodes,
  type Heap,
  type HeapLevelId,
} from './heapForgeModel'

const levelIdMap: Record<string, HeapLevelId> = {
  'fix-one-break': 'fix-one-break',
  'bubble-up': 'bubble-up',
  'sift-down': 'sift-down',
}

function nodePosition(index: number): { x: number; y: number } {
  const depth = Math.floor(Math.log2(index + 1))
  const countInLevel = 2 ** depth
  const positionInLevel = index - (countInLevel - 1)
  return {
    x: ((positionInLevel + 0.5) / countInLevel) * 100,
    y: 10 + depth * 17,
  }
}

export function HeapForgeMission() {
  const definition = heapForgeMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <HeapForgeLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function HeapForgeLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = heapForgeMission
  const levelId = levelIdMap[activeLevel.id]
  const config = heapLevels[levelId]
  const [heap, setHeap] = useState<Heap>(config.start)
  const [selected, setSelected] = useState<number | null>(null)
  const [touched, setTouched] = useState(false)

  const violations = useMemo(() => heapViolations(heap), [heap])
  const violationChildSet = useMemo(
    () => new Set(violations.map((violation) => violation.child)),
    [violations],
  )
  const diagnosis = diagnoseHeap({ heap, touched })
  const levelSuccess = heapLevelSuccess(heap)

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker = touched && !levelSuccess

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: selected !== null,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Красное ребро — там родитель больше ребёнка. Меняй их местами.',
    idle: 'Кликни два узла, чтобы поменять их местами.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'violations',
      label: 'breaks',
      value: violations.length,
      tone: levelSuccess ? 'success' : 'danger',
    },
    {
      id: 'size',
      label: 'size',
      value: heap.length,
      tone: 'neutral',
    },
    {
      id: 'root',
      label: 'min',
      value: formatHeapValue(heap[0]),
      tone: levelSuccess ? 'success' : 'target',
    },
  ]

  const selectNode = (index: number) => {
    if (selected === null) {
      setSelected(index)
      return
    }
    if (selected === index) {
      setSelected(null)
      return
    }
    setHeap((current) => swapNodes(current, selected, index))
    setTouched(true)
    setSelected(null)
  }

  const resetLevel = () => {
    setHeap(config.start)
    setSelected(null)
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
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_26%_16%,rgba(77,134,168,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess && touched} label="куча корректна" />
          {showRepairMarker && (
            <RepairMarker tone="danger" label={`${violations.length} breaks`} xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox="0 0 100 64"
            className="w-full max-w-[680px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="heap-forge-canvas"
            aria-label="Двоичная куча как дерево"
          >
            {heap.map((_, index) => {
              if (index === 0) return null
              const parent = parentIndex(index)
              const a = nodePosition(parent)
              const b = nodePosition(index)
              const broken = violationChildSet.has(index)
              return (
                <line
                  key={`edge-${index}`}
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  className={broken ? 'stroke-danger' : 'stroke-ink/25'}
                  strokeWidth={broken ? 0.8 : 0.4}
                  data-testid={broken ? `heap-edge-broken-${index}` : undefined}
                />
              )
            })}
            {heap.map((value, index) => {
              const pos = nodePosition(index)
              const isSelected = selected === index
              const isFocus = config.focusIndex === index
              const inViolation = violationChildSet.has(index) || violations.some((v) => v.parent === index)
              return (
                <g
                  key={`node-${index}`}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  className="cursor-pointer"
                  onClick={() => selectNode(index)}
                  data-testid={`heap-node-${index}`}
                >
                  <circle
                    r={4.4}
                    className={
                      isSelected
                        ? 'fill-orange stroke-ink'
                        : inViolation
                          ? 'fill-danger/15 stroke-danger'
                          : isFocus
                            ? 'fill-target/15 stroke-target'
                            : 'fill-paper stroke-ink/40'
                    }
                    strokeWidth={0.4}
                  />
                  <text
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize="3.4"
                    className={isSelected ? 'fill-bg font-semibold' : 'fill-ink font-semibold'}
                  >
                    {formatHeapValue(value)}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="heap-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            {selected !== null && (
              <p className="mt-1 text-target">Выбран узел {formatHeapValue(heap[selected])}; кликни второй для обмена.</p>
            )}
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Инвариант min-heap: каждый родитель не больше своих детей. Красное ребро
            показывает, где он нарушен.
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="heap-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Массив: [{heap.map((value) => formatHeapValue(value)).join(', ')}]. Нарушений:{' '}
          <span className="font-semibold">{violations.length}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
