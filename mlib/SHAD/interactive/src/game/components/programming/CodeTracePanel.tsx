import type { CodeTraceLine, CostMetric } from '../../programmingTypes'
import { InvariantCheck } from '../trace/InvariantCheck'
import { StateToken } from '../trace/StateToken'

type CodeTracePanelProps = {
  lines: CodeTraceLine[]
  variables: Record<string, string | number>
  metrics: CostMetric[]
  invariantOk: boolean
  invariantLabel: string
}

const metricToneClass: Record<NonNullable<CostMetric['tone']>, string> = {
  neutral: 'border-ink/10 bg-bg text-ink/70',
  success: 'border-success/35 bg-success/12 text-success',
  warning: 'border-orange/30 bg-orange/12 text-orange',
  danger: 'border-danger/35 bg-danger/12 text-danger',
  energy: 'border-energy/30 bg-energy/12 text-energy',
  target: 'border-target/35 bg-target/12 text-target',
}

export function CodeTracePanel({
  lines,
  variables,
  metrics,
  invariantOk,
  invariantLabel,
}: CodeTracePanelProps) {
  return (
    <div className="space-y-3" data-testid="code-trace-panel">
      <div className="rounded-md border border-ink/10 bg-ink/[0.035] p-3">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          pseudocode
        </p>
        <ol className="space-y-1 font-mono text-xs leading-relaxed text-ink/72">
          {lines.map((line, index) => (
            <li
              key={line.id}
              className={`grid grid-cols-[2ch_1fr] gap-2 rounded px-2 py-1 ${
                line.active
                  ? 'border border-orange/30 bg-orange/12 text-ink'
                  : line.invariantOk === false
                    ? 'border border-danger/25 bg-danger/10 text-danger'
                    : line.executed
                      ? 'bg-success/8 text-ink/78'
                      : ''
              }`}
            >
              <span className="select-none text-ink/38">{index + 1}</span>
              <span>{line.text}</span>
            </li>
          ))}
        </ol>
      </div>

      <div className="rounded-md border border-ink/10 bg-bg/78 p-3">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          variables
        </p>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(variables).map(([key, value]) => (
            <StateToken key={key} tone="neutral">
              {key}={value}
            </StateToken>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-[1fr_auto] gap-2">
        <InvariantCheck ok={invariantOk} label={invariantLabel} />
        <div className="flex flex-wrap justify-end gap-1.5">
          {metrics.map((metric) => (
            <span
              key={metric.id}
              className={`inline-flex min-h-8 items-center rounded border px-2 py-1 text-xs font-semibold tabular-nums ${
                metricToneClass[metric.tone ?? 'neutral']
              }`}
            >
              {metric.label} {metric.value}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
