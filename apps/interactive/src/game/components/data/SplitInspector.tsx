import type { SplitQuality } from '../../dataTypes'

type SplitInspectorProps = {
  quality: SplitQuality
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`
}

export function SplitInspector({ quality }: SplitInspectorProps) {
  return (
    <div
      className={`rounded-md border p-3 ${
        quality.ok ? 'border-target/25 bg-target/10' : 'border-orange/30 bg-orange/10'
      }`}
      data-testid="split-inspector"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
            split inspector
          </p>
          <p className="mt-1 text-sm font-semibold text-ink">
            {quality.ok ? 'Train/test похожи' : 'Train/test спорят'}
          </p>
        </div>
        <span className="rounded border border-ink/10 bg-paper/70 px-2 py-1 text-xs font-semibold text-ink/60">
          {quality.ok ? 'ok' : 'check'}
        </span>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div className="rounded border border-ink/10 bg-paper/70 p-2">
          <p className="text-ink/45">label gap</p>
          <p className="mt-1 font-semibold tabular-nums text-ink">{percent(quality.labelGap)}</p>
        </div>
        <div className="rounded border border-ink/10 bg-paper/70 p-2">
          <p className="text-ink/45">range gap</p>
          <p className="mt-1 font-semibold tabular-nums text-ink">{percent(quality.rangeGap)}</p>
        </div>
      </div>
    </div>
  )
}
