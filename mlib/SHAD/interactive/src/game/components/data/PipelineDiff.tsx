type PipelineDiffProps = {
  rowsDelta: number
  missingDelta: number
  leakageEnabled: boolean
  testStabilityDelta: number
  badSteps: number
}

function signed(value: number) {
  if (value === 0) return '0'
  return value > 0 ? `+${value}` : String(value)
}

function signedPercent(value: number) {
  const percent = Math.round(value * 100)
  if (percent === 0) return '0%'
  return percent > 0 ? `+${percent}%` : `${percent}%`
}

function tone(ok: boolean) {
  return ok ? 'border-target/25 bg-target/10 text-target' : 'border-danger/30 bg-danger/10 text-danger'
}

export function PipelineDiff({
  rowsDelta,
  missingDelta,
  leakageEnabled,
  testStabilityDelta,
  badSteps,
}: PipelineDiffProps) {
  return (
    <div className="space-y-2" data-testid="pipeline-diff">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          before / after
        </p>
        <span className={`rounded border px-2 py-1 text-xs font-semibold ${tone(badSteps === 0)}`}>
          {badSteps} risky
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className={`rounded border p-2 ${tone(rowsDelta >= -2)}`}>
          <p className="text-ink/45">rows</p>
          <p className="mt-1 font-semibold tabular-nums">{signed(rowsDelta)}</p>
        </div>
        <div className={`rounded border p-2 ${tone(missingDelta < 0)}`}>
          <p className="text-ink/45">missing</p>
          <p className="mt-1 font-semibold tabular-nums">{signed(missingDelta)}</p>
        </div>
        <div className={`rounded border p-2 ${tone(!leakageEnabled)}`}>
          <p className="text-ink/45">leakage</p>
          <p className="mt-1 font-semibold">{leakageEnabled ? 'on' : 'off'}</p>
        </div>
        <div className={`rounded border p-2 ${tone(testStabilityDelta >= 0)}`}>
          <p className="text-ink/45">test</p>
          <p className="mt-1 font-semibold tabular-nums">{signedPercent(testStabilityDelta)}</p>
        </div>
      </div>
    </div>
  )
}
