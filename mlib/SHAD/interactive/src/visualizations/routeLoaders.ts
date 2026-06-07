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

export const QuadraticLensMission = lazy(() =>
  import('./quadratic-lens/QuadraticLensMission').then((module) => ({
    default: module.QuadraticLensMission,
  })),
)

export const OrthogonalWorkshopMission = lazy(() =>
  import('./orthogonal-workshop/OrthogonalWorkshopMission').then((module) => ({
    default: module.OrthogonalWorkshopMission,
  })),
)

export const UnitaryCompassMission = lazy(() =>
  import('./unitary-compass/UnitaryCompassMission').then((module) => ({
    default: module.UnitaryCompassMission,
  })),
)

export const SvdLensMission = lazy(() =>
  import('./svd-lens/SvdLensMission').then((module) => ({
    default: module.SvdLensMission,
  })),
)

export const SubstitutionWorkshopMission = lazy(() =>
  import('./substitutions/SubstitutionWorkshopMission').then((module) => ({
    default: module.SubstitutionWorkshopMission,
  })),
)

export const AsymptoticArenaMission = lazy(() =>
  import('./asymptotics/AsymptoticArenaMission').then((module) => ({
    default: module.AsymptoticArenaMission,
  })),
)

export const MlPlaygroundMission = lazy(() =>
  import('./ml-playground/MlPlaygroundMission').then((module) => ({
    default: module.MlPlaygroundMission,
  })),
)

export const FeatureFactoryMission = lazy(() =>
  import('./feature-factory/FeatureFactoryMission').then((module) => ({
    default: module.FeatureFactoryMission,
  })),
)
