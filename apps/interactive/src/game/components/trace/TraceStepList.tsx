import type { TraceStep } from '../../missionTypes'
import { StateToken } from './StateToken'

type TraceStepListProps = {
  steps: TraceStep[]
}

export function TraceStepList({ steps }: TraceStepListProps) {
  return (
    <div className="rounded-md border border-ink/10 bg-bg/78 p-3">
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-ink/45">
        trace
      </p>
      <ol className="space-y-1.5">
        {steps.length > 0 ? (
          steps.slice(-5).map((step) => (
            <li key={step.id} className="flex items-center justify-between gap-2 text-xs">
              <span className="min-w-0 truncate text-ink/72">{step.label}</span>
              <div className="flex shrink-0 items-center gap-1">
                {step.cost !== undefined && <StateToken>{step.cost}</StateToken>}
                <StateToken tone={step.invariantOk === false ? 'danger' : 'visited'}>
                  {step.invariantOk === false ? 'ошибка' : 'ok'}
                </StateToken>
              </div>
            </li>
          ))
        ) : (
          <li className="text-xs text-ink/45">сделай первый шаг</li>
        )}
      </ol>
    </div>
  )
}
