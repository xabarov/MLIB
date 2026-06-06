import type { ReactNode } from 'react'

type StateTokenProps = {
  children: ReactNode
  tone?: 'neutral' | 'current' | 'visited' | 'frontier' | 'danger'
}

const toneClass: Record<NonNullable<StateTokenProps['tone']>, string> = {
  neutral: 'border-ink/10 bg-bg text-ink/70',
  current: 'border-orange/35 bg-orange/15 text-orange',
  visited: 'border-success/35 bg-success/15 text-success',
  frontier: 'border-target/35 bg-target/12 text-target',
  danger: 'border-danger/35 bg-danger/12 text-danger',
}

export function StateToken({ children, tone = 'neutral' }: StateTokenProps) {
  return (
    <span
      className={`inline-flex min-h-7 items-center rounded border px-2 py-1 text-xs font-semibold tabular-nums ${toneClass[tone]}`}
    >
      {children}
    </span>
  )
}
