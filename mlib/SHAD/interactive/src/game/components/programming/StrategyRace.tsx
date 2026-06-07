type StrategyRaceProps = {
  entries: Array<{
    strategyId: string
    label: string
    setup: number
    comparisons: number
    memory: number
    total: number
    rank: number
    winner: boolean
  }>
  selectedStrategyId: string
  recommendedStrategyId?: string
}

function formatCost(value: number): string {
  if (value >= 1_000_000) return `${Math.round(value / 1_000_000)}M`
  if (value >= 1_000) return `${Math.round(value / 1_000)}k`
  return String(Math.round(value))
}

export function StrategyRace({
  entries,
  selectedStrategyId,
  recommendedStrategyId,
}: StrategyRaceProps) {
  const slowest = Math.max(...entries.map((entry) => entry.total), 1)
  const winner = entries.find((entry) => entry.winner)

  return (
    <div className="space-y-3" data-testid="strategy-race">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          strategy race
        </p>
        <span
          className="rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-target"
          data-testid="race-result"
        >
          winner {winner?.label ?? '-'}
        </span>
      </div>

      <div className="space-y-2">
        {entries.map((entry) => {
          const selected = entry.strategyId === selectedStrategyId
          const recommended = entry.strategyId === recommendedStrategyId
          const progress = Math.max(8, (1 - entry.total / slowest) * 72 + 18)
          return (
            <div
              key={entry.strategyId}
              className={`rounded-md border p-2 ${
                selected
                  ? 'border-orange/45 bg-orange/12'
                  : recommended
                    ? 'border-target/25 bg-target/10'
                    : 'border-ink/10 bg-bg/72'
              }`}
              data-testid={`race-row-${entry.strategyId}`}
            >
              <div className="flex items-center justify-between gap-2 text-xs">
                <span className="font-semibold text-ink">
                  #{entry.rank} {entry.label}
                </span>
                <span className="font-semibold tabular-nums text-ink/62">
                  {formatCost(entry.total)}
                </span>
              </div>
              <div className="mt-2 grid grid-cols-[1fr_42px] items-center gap-2">
                <div className="h-3 overflow-hidden rounded-full bg-panel">
                  <div
                    className={`h-full rounded-full ${
                      entry.winner ? 'bg-target' : selected ? 'bg-orange' : 'bg-ink/24'
                    }`}
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <span className="text-right text-[10px] font-semibold text-ink/45">
                  {entry.winner ? 'fast' : 'slow'}
                </span>
              </div>
              <div className="mt-2 grid grid-cols-3 gap-1 text-[10px] text-ink/52">
                <span>setup {formatCost(entry.setup)}</span>
                <span>cmp {formatCost(entry.comparisons)}</span>
                <span>mem {formatCost(entry.memory)}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
