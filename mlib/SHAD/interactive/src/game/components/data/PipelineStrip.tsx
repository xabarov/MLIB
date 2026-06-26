import type { DataPipelineStep } from '../../dataTypes'

type PipelineStripProps = {
  steps: DataPipelineStep[]
}

export function PipelineStrip({ steps }: PipelineStripProps) {
  return (
    <div className="space-y-2" data-testid="pipeline-strip">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          pipeline
        </p>
        <span className="text-xs font-semibold tabular-nums text-ink/50">
          {steps.length} steps
        </span>
      </div>

      <div className="flex min-h-10 flex-wrap gap-1.5 rounded-md border border-ink/10 bg-paper/70 p-2">
        {steps.length === 0 ? (
          <span className="text-xs text-ink/45">Pipeline пуст: выбери действие над данными.</span>
        ) : (
          steps.map((step, index) => (
            <span
              key={step.id}
              className={`rounded border px-2 py-1 text-[10px] font-semibold ${
                step.valid
                  ? 'border-target/30 bg-target/10 text-target'
                  : 'border-danger/30 bg-danger/10 text-danger'
              }`}
              data-testid={`pipeline-step-${step.kind}-${step.targetId}`}
            >
              {index + 1}. {step.label}
            </span>
          ))
        )}
      </div>
    </div>
  )
}
