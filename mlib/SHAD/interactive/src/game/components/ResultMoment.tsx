import { Sparkles } from 'lucide-react'

type ResultMomentProps = {
  show: boolean
  label: string
}

export function ResultMoment({ show, label }: ResultMomentProps) {
  if (!show) return null

  return (
    <div
      className="result-moment pointer-events-none absolute left-1/2 top-4 z-30 -translate-x-1/2 rounded-full border border-success/35 bg-bg/92 px-3 py-1.5 text-xs font-black uppercase tracking-wide text-success shadow-[0_12px_30px_rgba(95,141,101,0.22)]"
      data-testid="result-moment"
    >
      <span className="inline-flex items-center gap-1">
        <Sparkles className="size-3.5" />
        {label}
      </span>
    </div>
  )
}
