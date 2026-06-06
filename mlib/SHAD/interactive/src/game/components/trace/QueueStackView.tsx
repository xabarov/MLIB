import { StateToken } from './StateToken'

type QueueStackViewProps = {
  label: string
  items: string[]
  mode: 'queue' | 'stack'
}

export function QueueStackView({ label, items, mode }: QueueStackViewProps) {
  return (
    <div className="rounded-md border border-ink/10 bg-bg/78 p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">{label}</p>
        <span className="text-[10px] font-semibold uppercase tracking-wide text-target">
          {mode === 'queue' ? 'FIFO' : 'LIFO'}
        </span>
      </div>
      <div className="flex min-h-8 flex-wrap gap-1.5">
        {items.length > 0 ? (
          items.map((item, index) => (
            <StateToken key={`${item}-${index}`} tone={index === 0 ? 'current' : 'frontier'}>
              {item}
            </StateToken>
          ))
        ) : (
          <span className="text-xs text-ink/45">пусто</span>
        )}
      </div>
    </div>
  )
}
