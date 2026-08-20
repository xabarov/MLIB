import type { ConfusionCounts, ModelMetric } from '../../dataTypes'

type MetricBoardProps = {
  metrics: ModelMetric[]
  primaryMetricId: string
  diagnosis: string
  confusionTrain?: ConfusionCounts
  confusionTest?: ConfusionCounts
}

function formatMetric(metric: ModelMetric, value: number): string {
  if (metric.format === 'number') return value.toFixed(2)
  return `${Math.round(value * 100)}%`
}

function gapTone(metric: ModelMetric) {
  const gap = metric.train - metric.test
  if (gap > 0.2) return 'border-danger/35 bg-danger/10 text-danger'
  if (gap > 0.1) return 'border-orange/35 bg-orange/10 text-orange'
  return 'border-success/25 bg-success/8 text-success'
}

function ConfusionMini({ title, counts }: { title: string; counts?: ConfusionCounts }) {
  if (!counts) return null
  return (
    <div className="rounded-md border border-ink/10 bg-bg/78 p-2">
      <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-ink/45">{title}</p>
      <div className="grid grid-cols-2 gap-1 text-center text-[11px] font-semibold tabular-nums">
        <span className="rounded bg-success/10 px-1 py-0.5 text-success">TP {counts.tp}</span>
        <span className="rounded bg-danger/10 px-1 py-0.5 text-danger">FP {counts.fp}</span>
        <span className="rounded bg-success/10 px-1 py-0.5 text-success">TN {counts.tn}</span>
        <span className="rounded bg-danger/10 px-1 py-0.5 text-danger">FN {counts.fn}</span>
      </div>
    </div>
  )
}

export function MetricBoard({
  metrics,
  primaryMetricId,
  diagnosis,
  confusionTrain,
  confusionTest,
}: MetricBoardProps) {
  return (
    <div className="space-y-3" data-testid="metric-board">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          train / test
        </p>
        <span className="rounded border border-ink/10 bg-bg/78 px-2 py-1 text-xs font-semibold text-ink/58">
          {diagnosis}
        </span>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {metrics.map((metric) => {
          const primary = metric.id === primaryMetricId
          return (
            <div
              key={metric.id}
              className={`rounded-md border p-2 ${primary ? gapTone(metric) : 'border-ink/10 bg-bg/78 text-ink/72'}`}
              data-testid={`metric-${metric.id}`}
            >
              <p className="text-[10px] font-semibold uppercase tracking-wide opacity-70">
                {metric.label}
              </p>
              <div className="mt-1 grid grid-cols-2 gap-2 text-sm font-semibold tabular-nums">
                <span>
                  <span className="block text-[10px] uppercase tracking-wide opacity-55">train</span>
                  {formatMetric(metric, metric.train)}
                </span>
                <span>
                  <span className="block text-[10px] uppercase tracking-wide opacity-55">test</span>
                  {formatMetric(metric, metric.test)}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        <ConfusionMini title="train confusion" counts={confusionTrain} />
        <ConfusionMini title="test confusion" counts={confusionTest} />
      </div>
    </div>
  )
}
