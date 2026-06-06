import type { TraceStep } from '../../missionTypes'
import { InvariantCheck } from './InvariantCheck'
import { QueueStackView } from './QueueStackView'
import { StateToken } from './StateToken'
import { TraceStepList } from './TraceStepList'

type TracePanelProps = {
  mode: 'queue' | 'stack'
  frontier: string[]
  visited: string[]
  current?: string
  cost: number
  invariantOk: boolean
  invariantLabel: string
  steps: TraceStep[]
}

export function TracePanel({
  mode,
  frontier,
  visited,
  current,
  cost,
  invariantOk,
  invariantLabel,
  steps,
}: TracePanelProps) {
  return (
    <div className="space-y-3" data-testid="trace-panel">
      <QueueStackView label={mode === 'queue' ? 'очередь' : 'стек'} items={frontier} mode={mode} />
      <div className="rounded-md border border-ink/10 bg-bg/78 p-3">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          посещены
        </p>
        <div className="flex min-h-8 flex-wrap gap-1.5">
          {visited.length > 0 ? (
            visited.map((item) => (
              <StateToken key={item} tone={item === current ? 'current' : 'visited'}>
                {item}
              </StateToken>
            ))
          ) : (
            <span className="text-xs text-ink/45">пока нет</span>
          )}
        </div>
      </div>
      <div className="grid grid-cols-[1fr_auto] gap-2">
        <InvariantCheck ok={invariantOk} label={invariantLabel} />
        <StateToken tone="neutral">cost {cost}</StateToken>
      </div>
      <TraceStepList steps={steps} />
    </div>
  )
}
