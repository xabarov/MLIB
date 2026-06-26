/**
 * Geometry synced with SHAD/algebra/8_Linear_maps/generate_visuals.py — draw_kernel_line()
 */
export const kernelLineConfig = {
  direction: [-1, 1, -1] as const,
  tMin: -2,
  tMax: 2,
  axisLimit: 2.2,
  planeGridSteps: 10,
  planeExtent: 2.2,
  /** z = -x - y  <=>  x + y + z = 0 */
  planeFn: (x: number, y: number) => -x - y,
  camera: {
    distance: 5.6,
    elevDeg: 24,
    azimDeg: 42,
  },
  colors: {
    line: '#d97757',
    origin: '#141413',
    plane: '#7c6ccf',
    planeOpacity: 0.1,
  },
  labelPosition: [-1.9, 1.8, -1.9] as const,
} as const
