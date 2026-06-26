import { useEffect, useMemo, useState } from 'react'
import { Dices, RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { monteCarloMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseMonteCarlo,
  estimateValue,
  formatEstimate,
  monteCarloLevels,
  monteCarloLevelSuccess,
  runMonteCarlo,
  sampleSizeStops,
  type MonteCarloLevelId,
} from './monteCarloModel'

const levelIdMap: Record<string, MonteCarloLevelId> = {
  'circle-pi': 'circle-pi',
  triangle: 'triangle',
  parabola: 'parabola',
}

const SIZE = 100

function toScreen(x: number, y: number): [number, number] {
  return [x * SIZE, (1 - y) * SIZE]
}

function regionPolygon(levelId: MonteCarloLevelId): string {
  const points: Array<[number, number]> = []
  if (levelId === 'circle-pi') {
    points.push([0, 0], [1, 0])
    for (let i = 0; i <= 24; i += 1) {
      const t = (i / 24) * (Math.PI / 2)
      points.push([Math.cos(t), Math.sin(t)])
    }
  } else if (levelId === 'triangle') {
    points.push([0, 0], [1, 0], [1, 1])
  } else {
    points.push([0, 0], [1, 0])
    for (let i = 24; i >= 0; i -= 1) {
      const x = i / 24
      points.push([x, x * x])
    }
  }
  return points.map(([x, y]) => toScreen(x, y).join(',')).join(' ')
}

export function MonteCarloMission() {
  const definition = monteCarloMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <MonteCarloLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function MonteCarloLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = monteCarloMission
  const levelId = levelIdMap[activeLevel.id]
  const config = monteCarloLevels[levelId]
  const [sampleSize, setSampleSize] = useState<number>(sampleSizeStops[0])
  const [touched, setTouched] = useState(false)

  const run = useMemo(() => runMonteCarlo(levelId, sampleSize), [levelId, sampleSize])
  const estimate = estimateValue(levelId, run)
  const diagnosis = diagnoseMonteCarlo({ levelId, sampleSize, touched })
  const levelSuccess = monteCarloLevelSuccess({ levelId, sampleSize })

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel = diagnosis.kind === 'too-few-samples' ? 'мало точек' : 'оценка шумит'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && sampleSize >= config.minSamples,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я считаю долю точек в области. Брось больше — оценка площади устаканится.',
    idle: 'Брось точки в квадрат. Доля внутри области оценивает её площадь.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'estimate',
      label: config.estimator === 'pi' ? 'pi≈' : 'area≈',
      value: formatEstimate(estimate),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'target',
      label: 'target',
      value: formatEstimate(config.target),
      tone: 'target',
    },
    {
      id: 'samples',
      label: 'n',
      value: sampleSize,
      tone: sampleSize >= config.minSamples ? 'success' : 'neutral',
    },
  ]

  const polygon = useMemo(() => regionPolygon(levelId), [levelId])

  const resetLevel = () => {
    setSampleSize(sampleSizeStops[0])
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
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(124,108,207,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="площадь поймана" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox={`-4 -4 ${SIZE + 8} ${SIZE + 8}`}
            className="aspect-square max-h-full w-full max-w-[520px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="monte-carlo-canvas"
            aria-label="Метод Монте-Карло на единичном квадрате"
          >
            <rect x={0} y={0} width={SIZE} height={SIZE} className="fill-none stroke-ink/30" strokeWidth="0.4" />
            <polygon points={polygon} className="fill-target/14 stroke-target/60" strokeWidth="0.5" data-testid="monte-carlo-region" />
            {run.points.map((point, index) => {
              const [sx, sy] = toScreen(point.x, point.y)
              return (
                <circle
                  key={index}
                  cx={sx}
                  cy={sy}
                  r={0.8}
                  className={point.inside ? 'fill-success' : 'fill-ink/25'}
                />
              )
            })}
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">точек</p>
            <div className="flex flex-wrap gap-2" data-testid="monte-carlo-sample-controls">
              {sampleSizeStops.map((stop) => (
                <button
                  key={stop}
                  type="button"
                  onClick={() => {
                    setTouched(true)
                    setSampleSize(stop)
                  }}
                  className={`inline-flex items-center gap-1 rounded border px-2.5 py-1.5 text-xs font-semibold transition ${
                    sampleSize === stop
                      ? 'border-target bg-target text-bg'
                      : 'border-ink/10 bg-paper text-ink hover:border-target/50'
                  }`}
                  data-testid={`mc-sample-${stop}`}
                >
                  <Dices size={13} /> {stop}
                </button>
              ))}
            </div>
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="mc-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            <p className="mt-1 text-ink/55">
              внутри {run.hits} из {sampleSize} ({config.estimator === 'pi' ? 'pi≈' : 'площадь≈'}{' '}
              {formatEstimate(estimate)}, цель {formatEstimate(config.target)})
            </p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="mc-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          seed = <span className="font-semibold">{config.seed}</span>, оценка ={' '}
          <span className="font-semibold">{formatEstimate(estimate)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
