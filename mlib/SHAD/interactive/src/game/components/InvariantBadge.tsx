import type { ReactNode } from 'react'

type BadgeTone = 'neutral' | 'success' | 'warning' | 'danger' | 'energy' | 'target'

type InvariantBadgeProps = {
  label: string
  value: ReactNode
  tone?: BadgeTone
}

const toneClass: Record<BadgeTone, string> = {
  neutral: 'border-ink/10 bg-bg/75 text-ink',
  success: 'border-success/30 bg-success/10 text-ink',
  warning: 'border-orange/35 bg-highlight text-ink',
  danger: 'border-danger/30 bg-danger/10 text-ink',
  energy: 'border-energy/30 bg-energy/10 text-ink',
  target: 'border-target/35 bg-target/10 text-ink',
}

export function InvariantBadge({ label, value, tone = 'neutral' }: InvariantBadgeProps) {
  return (
    <span
      className={`inline-flex min-h-10 min-w-0 flex-col justify-center rounded-md border px-3 py-1.5 shadow-[0_1px_0_rgba(20,20,19,0.05)] ${toneClass[tone]}`}
    >
      <span className="text-[10px] font-semibold uppercase tracking-wide text-ink/50">
        {label}
      </span>
      <span className="truncate text-sm font-semibold tabular-nums">{value}</span>
    </span>
  )
}
