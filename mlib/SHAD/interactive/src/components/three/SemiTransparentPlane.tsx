import { useMemo } from 'react'
import * as THREE from 'three'

type SemiTransparentPlaneProps = {
  /** z = fn(x, y) */
  fn: (x: number, y: number) => number
  extent: number
  steps: number
  color: string
  opacity: number
}

export function SemiTransparentPlane({
  fn,
  extent,
  steps,
  color,
  opacity,
}: SemiTransparentPlaneProps) {
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    const verts: number[] = []
    const indices: number[] = []

    const xs = Array.from({ length: steps }, (_, i) => -extent + (2 * extent * i) / (steps - 1))
    const ys = Array.from({ length: steps }, (_, i) => -extent + (2 * extent * i) / (steps - 1))

    for (let j = 0; j < steps; j++) {
      for (let i = 0; i < steps; i++) {
        const x = xs[i]
        const y = ys[j]
        const z = fn(x, y)
        verts.push(x, y, z)
      }
    }

    for (let j = 0; j < steps - 1; j++) {
      for (let i = 0; i < steps - 1; i++) {
        const a = j * steps + i
        const b = a + 1
        const c = a + steps
        const d = c + 1
        indices.push(a, c, b, b, c, d)
      }
    }

    geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3))
    geo.setIndex(indices)
    geo.computeVertexNormals()
    return geo
  }, [fn, extent, steps])

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color={color}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
        depthWrite={false}
      />
    </mesh>
  )
}
