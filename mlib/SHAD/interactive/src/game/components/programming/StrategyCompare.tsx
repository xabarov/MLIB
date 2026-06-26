import type { GrowthPoint, StrategyOption } from '../../programmingTypes'

type StrategyCompareProps = {
  strategies: StrategyOption[]
  selectedStrategyId: string
  onSelect: (strategyId: string) => void
  growthPointsByStrategy: Record<string, GrowthPoint[]>
  recommendedStrategyId?: string
  diagnosis: string
}

function formatCost(value: number): string {
  if (value >= 1_000_000) return `${Math.round(value / 1_000_000)}M`
  if (value >= 1_000) return `${Math.round(value / 1_000)}k`
  return String(Math.round(value))
}

export function StrategyCompare({
  strategies,
  selectedStrategyId,
  onSelect,
  growthPointsByStrategy,
  recommendedStrategyId,
  diagnosis,
}: StrategyCompareProps) {
  const allCosts = Object.values(growthPointsByStrategy).flatMap((points) =>
    points.map((point) => point.cost),
  )
  const maxCost = Math.max(...allCosts, 1)
  const selectedGrowth = growthPointsByStrategy[selectedStrategyId] ?? []

  return (
    <div className="space-y-3" data-testid="strategy-compare">
      <div className="grid gap-2 sm:grid-cols-2">
        {strategies.map((strategy) => {
          const selected = strategy.id === selectedStrategyId
          const recommended = strategy.id === recommendedStrategyId
          return (
            <button
              key={strategy.id}
              type="button"
              onClick={() => onSelect(strategy.id)}
              className={`min-h-24 rounded-md border p-3 text-left transition ${
                selected
                  ? 'border-orange/55 bg-orange/12 text-ink shadow-sm'
                  : recommended
                    ? 'border-success/35 bg-success/10 text-ink/80'
                    : 'border-ink/10 bg-bg/78 text-ink/72 hover:border-orange/35'
              }`}
              data-testid={`strategy-${strategy.id}`}
            >
              <span className="block text-sm font-semibold text-ink">{strategy.label}</span>
              <span className="mt-1 block break-words font-mono text-[11px] leading-snug text-target">
                {strategy.complexity}
              </span>
              <span className="mt-2 block text-xs leading-snug text-ink/58">
                {strategy.bestFor}
              </span>
              {(strategy.setupCost || strategy.memoryCost) && (
                <span className="mt-2 block text-[10px] uppercase tracking-wide text-ink/42">
                  {strategy.setupCost && `setup ${strategy.setupCost}`}
                  {strategy.setupCost && strategy.memoryCost ? ' · ' : ''}
                  {strategy.memoryCost && `memory ${strategy.memoryCost}`}
                </span>
              )}
            </button>
          )
        })}
      </div>

      <div className="rounded-md border border-ink/10 bg-bg/78 p-3">
        <div className="mb-2 flex items-center justify-between gap-2">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
            growth
          </p>
          <span className="text-xs font-semibold text-ink/58">{diagnosis}</span>
        </div>
        <div className="space-y-2">
          {selectedGrowth.map((point) => (
            <div key={point.n} className="grid grid-cols-[52px_1fr_54px] items-center gap-2">
              <span className="text-xs font-semibold tabular-nums text-ink/60">n={point.n}</span>
              <div className="h-2 overflow-hidden rounded-full bg-panel">
                <div
                  className="h-full rounded-full bg-orange"
                  style={{ width: `${Math.max(4, (point.cost / maxCost) * 100)}%` }}
                />
              </div>
              <span className="text-right text-xs font-semibold tabular-nums text-ink">
                {formatCost(point.cost)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
