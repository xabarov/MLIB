import { InvariantBadge } from './InvariantBadge'

type MetricBadgeProps = {
  label: string
  value: string | number
}

export function MetricBadge({ label, value }: MetricBadgeProps) {
  return <InvariantBadge label={label} value={value} tone="target" />
}
