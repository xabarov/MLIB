import type { FeatureState } from '../../dataTypes'

type FeatureTogglePanelProps = {
  features: FeatureState[]
  onToggle: (featureId: string) => void
  onEncode?: (featureId: string) => void
}

function featureTone(feature: FeatureState) {
  if (feature.flaggedAsLeakage && feature.enabled) return 'border-danger/35 bg-danger/10 text-danger'
  if (!feature.enabled) return 'border-ink/10 bg-bg/65 text-ink/42'
  if (feature.encoded) return 'border-target/30 bg-target/10 text-target'
  return 'border-ink/10 bg-paper/80 text-ink'
}

export function FeatureTogglePanel({ features, onToggle, onEncode }: FeatureTogglePanelProps) {
  return (
    <div className="space-y-2" data-testid="feature-toggle-panel">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
          features
        </p>
        <span className="text-xs font-semibold tabular-nums text-ink/50">
          {features.filter((feature) => feature.enabled).length}/{features.length} on
        </span>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {features.map((feature) => (
          <div
            key={feature.id}
            className={`rounded-md border p-2 transition ${featureTone(feature)}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold">{feature.label}</p>
                <p className="mt-0.5 text-[10px] text-ink/48">
                  {feature.flaggedAsLeakage
                    ? 'leakage risk'
                    : feature.kind === 'category'
                      ? feature.encoded
                        ? 'encoded category'
                        : 'raw category'
                      : feature.kind ?? 'number'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => onToggle(feature.id)}
                className={`shrink-0 rounded border px-2 py-1 text-[10px] font-semibold transition ${
                  feature.enabled
                    ? 'border-ink/15 bg-bg/80 text-ink/70 hover:border-orange/35'
                    : 'border-target/30 bg-target/10 text-target'
                }`}
                data-testid={`feature-toggle-${feature.id}`}
              >
                {feature.enabled ? 'off' : 'on'}
              </button>
            </div>
            {feature.kind === 'category' && (
              <button
                type="button"
                onClick={() => onEncode?.(feature.id)}
                disabled={!feature.enabled || feature.encoded}
                className="mt-2 w-full rounded border border-ink/10 bg-bg/75 px-2 py-1 text-[10px] font-semibold text-ink/62 transition enabled:hover:border-orange/30 disabled:opacity-45"
                data-testid={`feature-encode-${feature.id}`}
              >
                {feature.encoded ? 'encoded' : 'encode'}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
