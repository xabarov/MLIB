import { KeyRound } from 'lucide-react'

type RewardMeterProps = {
  keys: number
  completed: number
  total: number
}

export function RewardMeter({ keys, completed, total }: RewardMeterProps) {
  return (
    <div className="flex items-center gap-3 rounded-md border border-ink/10 bg-paper px-3 py-2 text-sm text-ink">
      <span className="inline-flex size-8 items-center justify-center rounded-full bg-orange/15 text-orange">
        <KeyRound className="size-4" />
      </span>
      <div className="min-w-0">
        <p className="font-semibold tabular-nums">{keys} инвариант-ключей</p>
        <p className="text-xs text-ink/60">
          Уровни: {completed}/{total}
        </p>
      </div>
    </div>
  )
}
