import { Canvas } from '@react-three/fiber'
import type { ReactNode } from 'react'
import { tokens } from '../../theme/tokens'

type SceneCanvasProps = {
  children: ReactNode
  className?: string
}

export function SceneCanvas({ children, className = '' }: SceneCanvasProps) {
  return (
    <div className={`relative min-h-[320px] h-full w-full ${className}`}>
      <Canvas
        camera={{ fov: 45, near: 0.1, far: 100, position: [5, 5, 5] }}
        gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
        style={{ background: tokens.bg }}
      >
        <color attach="background" args={[tokens.bg]} />
        <ambientLight intensity={0.85} />
        <directionalLight position={[4, 6, 8]} intensity={0.55} />
        {children}
      </Canvas>
    </div>
  )
}
