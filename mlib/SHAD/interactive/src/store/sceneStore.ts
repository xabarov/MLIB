import { create } from 'zustand'

type SceneState = {
  showAuxiliaryPlane: boolean
  cameraReset: number
  togglePlane: () => void
  resetCamera: () => void
}

export const useSceneStore = create<SceneState>((set) => ({
  showAuxiliaryPlane: true,
  cameraReset: 0,
  togglePlane: () => set((s) => ({ showAuxiliaryPlane: !s.showAuxiliaryPlane })),
  resetCamera: () => set((s) => ({ cameraReset: s.cameraReset + 1 })),
}))
