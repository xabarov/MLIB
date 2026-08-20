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

export const PcaCompressionMission = lazy(() =>
  import('./pca-compression/PcaCompressionMission').then((module) => ({
    default: module.PcaCompressionMission,
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

export const BernoulliLabMission = lazy(() =>
  import('./bernoulli-lab/BernoulliLabMission').then((module) => ({
    default: module.BernoulliLabMission,
  })),
)

export const GradientSlopeMission = lazy(() =>
  import('./gradient-slope/GradientSlopeMission').then((module) => ({
    default: module.GradientSlopeMission,
  })),
)

export const HeapForgeMission = lazy(() =>
  import('./heap-forge/HeapForgeMission').then((module) => ({
    default: module.HeapForgeMission,
  })),
)

export const RootsOrbitMission = lazy(() =>
  import('./roots-orbit/RootsOrbitMission').then((module) => ({
    default: module.RootsOrbitMission,
  })),
)

export const FourierSynthMission = lazy(() =>
  import('./fourier-synth/FourierSynthMission').then((module) => ({
    default: module.FourierSynthMission,
  })),
)

export const MonteCarloMission = lazy(() =>
  import('./monte-carlo/MonteCarloMission').then((module) => ({
    default: module.MonteCarloMission,
  })),
)

export const BayesForkMission = lazy(() =>
  import('./bayes-fork/BayesForkMission').then((module) => ({
    default: module.BayesForkMission,
  })),
)

export const ExpectationLabMission = lazy(() =>
  import('./expectation-lab/ExpectationLabMission').then((module) => ({
    default: module.ExpectationLabMission,
  })),
)

export const TaylorLabMission = lazy(() =>
  import('./taylor-lab/TaylorLabMission').then((module) => ({
    default: module.TaylorLabMission,
  })),
)

export const PascalTriangleMission = lazy(() =>
  import('./pascal-triangle/PascalTriangleMission').then((module) => ({
    default: module.PascalTriangleMission,
  })),
)

export const GaussStationMission = lazy(() =>
  import('./gauss-station/GaussStationMission').then((module) => ({
    default: module.GaussStationMission,
  })),
)

export const DsuForestMission = lazy(() =>
  import('./dsu-forest/DsuForestMission').then((module) => ({
    default: module.DsuForestMission,
  })),
)

export const DpStationMission = lazy(() =>
  import('./dp-station/DpStationMission').then((module) => ({
    default: module.DpStationMission,
  })),
)

export const EigenChaseMission = lazy(() =>
  import('./eigen-chase/EigenChaseMission').then((module) => ({
    default: module.EigenChaseMission,
  })),
)

export const EulerTrailMission = lazy(() =>
  import('./euler-trail/EulerTrailMission').then((module) => ({
    default: module.EulerTrailMission,
  })),
)

export const BstQuestMission = lazy(() =>
  import('./bst-quest/BstQuestMission').then((module) => ({
    default: module.BstQuestMission,
  })),
)
