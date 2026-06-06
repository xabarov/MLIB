import { AxesGrid } from '../../components/three/AxesGrid'
import { CameraController } from '../../components/three/CameraController'
import { LabeledLine } from '../../components/three/LabeledLine'
import { OriginMarker } from '../../components/three/OriginMarker'
import { SceneCanvas } from '../../components/three/SceneCanvas'
import { SemiTransparentPlane } from '../../components/three/SemiTransparentPlane'
import { useSceneStore } from '../../store/sceneStore'
import { kernelLineConfig } from './kernelLineConfig'

export function KernelLineViz() {
  const showPlane = useSceneStore((s) => s.showAuxiliaryPlane)
  const cfg = kernelLineConfig

  return (
    <SceneCanvas>
      <CameraController
        distance={cfg.camera.distance}
        elevDeg={cfg.camera.elevDeg}
        azimDeg={cfg.camera.azimDeg}
      />
      <AxesGrid limit={cfg.axisLimit} />
      <OriginMarker color={cfg.colors.origin} />
      <LabeledLine
        direction={cfg.direction}
        tMin={cfg.tMin}
        tMax={cfg.tMax}
        color={cfg.colors.line}
        lineWidth={3.4}
        label="ker φ"
        labelAt={cfg.labelPosition}
      />
      {showPlane && (
        <SemiTransparentPlane
          fn={cfg.planeFn}
          extent={cfg.planeExtent}
          steps={cfg.planeGridSteps}
          color={cfg.colors.plane}
          opacity={cfg.colors.planeOpacity}
        />
      )}
    </SceneCanvas>
  )
}
