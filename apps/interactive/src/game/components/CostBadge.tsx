import { InvariantBadge } from './InvariantBadge'

type CostBadgeProps = {
  label: string
  value: string | number
}

export function CostBadge({ label, value }: CostBadgeProps) {
  return <InvariantBadge label={label} value={value} tone="energy" />
}
