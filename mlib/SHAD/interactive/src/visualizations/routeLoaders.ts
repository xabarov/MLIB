import { lazy } from 'react'

export const DeterminantForgeMission = lazy(() =>
  import('./determinants/DeterminantForgeMission').then((module) => ({
    default: module.DeterminantForgeMission,
  })),
)

export const KernelHuntMission = lazy(() =>
  import('./linear-maps/KernelHuntMission').then((module) => ({
    default: module.KernelHuntMission,
  })),
)

export const GraphDispatcherMission = lazy(() =>
  import('./graphs/GraphDispatcherMission').then((module) => ({
    default: module.GraphDispatcherMission,
  })),
)

export const MatrixMachineMission = lazy(() =>
  import('./matrices/MatrixMachineMission').then((module) => ({
    default: module.MatrixMachineMission,
  })),
)

export const SubstitutionWorkshopMission = lazy(() =>
  import('./substitutions/SubstitutionWorkshopMission').then((module) => ({
    default: module.SubstitutionWorkshopMission,
  })),
)
