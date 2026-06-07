import { AlertTriangle, CheckCircle2, Crosshair } from 'lucide-react'

type RepairMarkerTone = 'warning' | 'danger' | 'target' | 'success'

type RepairMarkerProps = {
  tone: RepairMarkerTone
  label: string
  xPercent?: number
  yPercent?: number
}

const toneClass: Record<RepairMarkerTone, string> = {
  warning: 'border-orange/40 bg-orange/15 text-orange',
  danger: 'border-danger/40 bg-danger/12 text-danger',
  target: 'border-target/40 bg-target/12 text-target',
  success: 'border-success/45 bg-success/14 text-success',
}

const iconByTone = {
  warning: AlertTriangle,
  danger: AlertTriangle,
  target: Crosshair,
  success: CheckCircle2,
}

export function RepairMarker({ tone, label, xPercent, yPercent }: RepairMarkerProps) {
  const Icon = iconByTone[tone]
  const positioned = typeof xPercent === 'number' && typeof yPercent === 'number'
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[10px] font-black uppercase tracking-wide shadow-sm ${toneClass[tone]} ${
        positioned ? 'absolute z-30 -translate-x-1/2 -translate-y-1/2' : ''
      }`}
      style={positioned ? { left: `${xPercent}%`, top: `${yPercent}%` } : undefined}
      data-testid="repair-marker"
    >
      <Icon className="size-3" />
      {label}
    </span>
  )
}
