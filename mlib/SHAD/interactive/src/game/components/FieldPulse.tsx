import type { ReactNode } from 'react'

export type FieldPulseTone = 'success' | 'warning' | 'danger' | 'target'

type FieldPulseProps = {
  tone: FieldPulseTone
  active: boolean
  label: string
  children: ReactNode
  className?: string
}

const toneClass: Record<FieldPulseTone, string> = {
  success: 'field-pulse-success',
  warning: 'field-pulse-warning',
  danger: 'field-pulse-danger',
  target: 'field-pulse-target',
}

export function FieldPulse({ tone, active, label, children, className = '' }: FieldPulseProps) {
  return (
    <div
      className={`field-pulse ${active ? toneClass[tone] : ''} ${className}`}
      aria-label={label}
      data-testid={active ? `field-pulse-${tone}` : 'field-pulse-idle'}
    >
      {children}
    </div>
  )
}
