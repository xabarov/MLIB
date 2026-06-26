import { create } from 'zustand'

type NavigationState = {
  sidebarCollapsed: boolean
  mobileNavOpen: boolean
  expandedSections: Record<string, boolean>
  expandedTopics: Record<string, boolean>
  toggleSidebar: () => void
  toggleMobileNav: () => void
  closeMobileNav: () => void
  toggleSection: (sectionId: string) => void
  toggleTopic: (topicId: string) => void
}

export const useNavigationStore = create<NavigationState>((set) => ({
  sidebarCollapsed: false,
  mobileNavOpen: false,
  expandedSections: { algebra: true },
  expandedTopics: { 'linear-maps': true },
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  toggleMobileNav: () => set((s) => ({ mobileNavOpen: !s.mobileNavOpen })),
  closeMobileNav: () => set({ mobileNavOpen: false }),
  toggleSection: (sectionId) =>
    set((s) => ({
      expandedSections: {
        ...s.expandedSections,
        [sectionId]: !s.expandedSections[sectionId],
      },
    })),
  toggleTopic: (topicId) =>
    set((s) => ({
      expandedTopics: {
        ...s.expandedTopics,
        [topicId]: !s.expandedTopics[topicId],
      },
    })),
}))
