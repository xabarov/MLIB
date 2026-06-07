import { useEffect, useMemo, useState } from 'react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { substitutionWorkshopMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  cycleNotation,
  diagnoseSubstitutionState,
  parity,
  substitutionLevelSuccess,
  substitutionLevels,
  swapImages,
  type Permutation,
} from './substitutionWorkshopModel'

function permutationLabel(permutation: Permutation): string {
  return permutation.map((value, index) => `${index + 1}→${value}`).join(', ')
}

export function SubstitutionWorkshopMission() {
  const definition = substitutionWorkshopMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <SubstitutionWorkshopLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function SubstitutionWorkshopLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = substitutionWorkshopMission
  const levelSpec = substitutionLevels[activeLevel.id]
  const [permutation, setPermutation] = useState<Permutation>(levelSpec.start)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [swapCount, setSwapCount] = useState(0)

  const currentParity = parity(permutation)
  const currentCycles = cycleNotation(permutation)
  const overBudget = levelSpec.maxSwaps !== undefined && swapCount > levelSpec.maxSwaps
  const diagnosis = diagnoseSubstitutionState({
    levelId: activeLevel.id,
    permutation,
    swapCount,
  })
  const levelSuccess = useMemo(
    () =>
      substitutionLevelSuccess({
        levelId: activeLevel.id,
        permutation,
        swapCount,
      }),
    [activeLevel.id, permutation, swapCount],
  )

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning:
      overBudget ||
      (swapCount > 0 && ['wrong-parity', 'target-mismatch'].includes(diagnosis.kind)),
    hint:
      diagnosis.kind === 'near-target' ||
      (levelSpec.requiredParity !== undefined && currentParity === levelSpec.requiredParity),
    thinking: selectedIndex !== null,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking:
      selectedIndex === null
        ? 'Выбери позицию для транспозиции.'
        : `Меби держит позицию ${selectedIndex + 1}. Выбери вторую, чтобы сделать транспозицию.`,
    idle: 'Кликни две позиции, чтобы сделать транспозицию образов.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'cycles',
      label: 'cycles',
      value: currentCycles,
      tone: levelSuccess ? 'success' : 'target',
    },
    {
      id: 'parity',
      label: 'sign',
      value: currentParity === 'even' ? 'even' : 'odd',
      tone: currentParity === 'even' ? 'energy' : 'target',
    },
    {
      id: 'swaps',
      label: 'swaps',
      value:
        levelSpec.maxSwaps === undefined ? String(swapCount) : `${swapCount}/${levelSpec.maxSwaps}`,
      tone: overBudget ? 'danger' : levelSuccess ? 'success' : 'neutral',
    },
  ]

  const selectPosition = (index: number) => {
    if (levelSuccess) return
    if (selectedIndex === null) {
      setSelectedIndex(index)
      return
    }
    if (selectedIndex === index) {
      setSelectedIndex(null)
      return
    }
    setPermutation((current) => swapImages(current, selectedIndex, index))
    setSwapCount((current) => current + 1)
    setSelectedIndex(null)
  }

  const resetLevel = () => {
    setPermutation(levelSpec.start)
    setSelectedIndex(null)
    setSwapCount(0)
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      scene={
        <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_28%_18%,rgba(124,108,207,0.12),transparent_28%),linear-gradient(180deg,#fffdf7,#faf9f5)] p-4">
          <div className="w-full max-w-4xl">
            <div className="mb-5 grid grid-cols-[repeat(auto-fit,minmax(72px,1fr))] gap-3">
              {permutation.map((value, index) => {
                const selected = selectedIndex === index
                const targetValue = levelSpec.target?.[index]
                const correct = targetValue === undefined || targetValue === value
                const mismatch = diagnosis.mismatchPositions.includes(index + 1)
                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => selectPosition(index)}
                    className={`min-h-24 rounded-md border p-3 text-left shadow-[0_10px_28px_rgba(20,20,19,0.08)] transition ${
                      selected
                        ? 'border-purple bg-purple/12'
                        : mismatch
                          ? 'border-danger/35 bg-danger/8'
                        : correct
                          ? 'border-success/25 bg-paper'
                          : 'border-orange/30 bg-highlight'
                    }`}
                    data-testid={`substitution-tile-${index + 1}`}
                  >
                    <span className="block text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                      позиция {index + 1}
                    </span>
                    <span className="mt-1 block text-2xl font-semibold tabular-nums text-ink">
                      {index + 1} → {value}
                    </span>
                    {targetValue !== undefined && (
                      <span className="mt-1 block text-xs text-ink/55">цель → {targetValue}</span>
                    )}
                  </button>
                )
              })}
            </div>

            <div className="rounded-md border border-ink/10 bg-paper/85 p-4 text-sm text-ink shadow-[0_16px_36px_rgba(20,20,19,0.08)]">
              <div className="grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                    текущая запись
                  </p>
                  <p className="mt-1 font-semibold">{permutationLabel(permutation)}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                    циклы
                  </p>
                  <p className="mt-1 font-semibold">{currentCycles}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                    цель
                  </p>
                  <p className="mt-1 font-semibold">
                    {levelSpec.target ? cycleNotation(levelSpec.target) : `sign ${levelSpec.requiredParity}`}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      }
      controls={
        <div className="space-y-2">
          <p className="text-xs leading-relaxed text-ink/65">
            Выбери две плитки: их образы поменяются местами. Это одна
            транспозиция.
          </p>
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="substitution-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            {selectedIndex !== null && (
              <p className="mt-1 text-target">
                Меби держит позицию {selectedIndex + 1}; следующий клик сделает транспозицию.
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={resetLevel}
            className="rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="substitution-reset"
          >
            Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Сейчас: {permutationLabel(permutation)}. Циклическая запись:{' '}
          <span className="font-semibold">{currentCycles}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
