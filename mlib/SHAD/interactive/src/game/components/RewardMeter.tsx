import { KeyRound } from 'lucide-react'

type RewardMeterProps = {
  keys: number
  completed: number
  total: number
  success?: boolean
}

export function RewardMeter({ keys, completed, total, success = false }: RewardMeterProps) {
  return (
    <div
      className={`flex items-center gap-3 rounded-md border px-3 py-2 text-sm text-ink transition ${
        success
          ? 'border-success/35 bg-success/12 shadow-[0_8px_24px_rgba(95,141,101,0.16)]'
          : 'border-ink/10 bg-paper'
      }`}
      data-testid="reward-meter"
    >
      <span
        className={`inline-flex size-8 items-center justify-center rounded-full ${
          success ? 'bg-success/20 text-success' : 'bg-orange/15 text-orange'
        }`}
      >
        <KeyRound className="size-4" />
      </span>
      <div className="min-w-0">
        <p className="font-semibold tabular-nums">{keys} инвариант-ключей</p>
        <p className="text-xs text-ink/60">
          {success ? 'Ключ получен. Открывай следующий шаг.' : `Уровни: ${completed}/${total}`}
        </p>
      </div>
    </div>
  )
}
