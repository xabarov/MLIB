import { CheckCircle2, XCircle } from 'lucide-react'

type InvariantCheckProps = {
  ok: boolean
  label: string
}

export function InvariantCheck({ ok, label }: InvariantCheckProps) {
  const Icon = ok ? CheckCircle2 : XCircle
  return (
    <div
      className={`flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-semibold ${
        ok
          ? 'border-success/30 bg-success/12 text-success'
          : 'border-danger/30 bg-danger/12 text-danger'
      }`}
    >
      <Icon className="size-4" />
      {label}
    </div>
  )
}
