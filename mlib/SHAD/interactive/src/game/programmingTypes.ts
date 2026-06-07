import type { MissionBadge } from './missionTypes'

export type CostMetric = {
  id: string
  label: string
  value: number | string
  tone?: MissionBadge['tone']
}

export type CodeTraceLine = {
  id: string
  text: string
  active?: boolean
  executed?: boolean
  invariantOk?: boolean
}

export type StrategyOption = {
  id: string
  label: string
  complexity: string
  setupCost?: string
  memoryCost?: string
  bestFor: string
}

export type GrowthPoint = {
  n: number
  cost: number
}
