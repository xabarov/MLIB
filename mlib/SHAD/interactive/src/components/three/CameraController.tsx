import { OrbitControls } from '@react-three/drei'
import { useThree } from '@react-three/fiber'
import { useCallback, useEffect, useRef, type ComponentRef } from 'react'
import * as THREE from 'three'
import { useSceneStore } from '../../store/sceneStore'

type CameraControllerProps = {
  distance: number
  elevDeg: number
  azimDeg: number
}

function sphericalPosition(distance: number, elevDeg: number, azimDeg: number): THREE.Vector3 {
  const elev = THREE.MathUtils.degToRad(elevDeg)
  const azim = THREE.MathUtils.degToRad(azimDeg)
  const r = distance
  const x = r * Math.cos(elev) * Math.sin(azim)
  const y = r * Math.cos(elev) * Math.cos(azim)
  const z = r * Math.sin(elev)
  return new THREE.Vector3(x, y, z)
}

export function CameraController({ distance, elevDeg, azimDeg }: CameraControllerProps) {
  const controlsRef = useRef<ComponentRef<typeof OrbitControls>>(null)
  const { camera } = useThree()
  const cameraReset = useSceneStore((s) => s.cameraReset)

  const applyView = useCallback(() => {
    const pos = sphericalPosition(distance, elevDeg, azimDeg)
    camera.position.copy(pos)
    camera.lookAt(0, 0, 0)
    camera.updateProjectionMatrix()
    controlsRef.current?.target.set(0, 0, 0)
    controlsRef.current?.update()
  }, [azimDeg, camera, distance, elevDeg])

  useEffect(() => {
    applyView()
  }, [applyView, cameraReset])

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      enableDamping
      dampingFactor={0.08}
      minDistance={4}
      maxDistance={18}
    />
  )
}
