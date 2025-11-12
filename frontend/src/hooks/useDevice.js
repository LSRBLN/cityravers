import { useState, useEffect } from 'react'

/**
 * Hook zur Erkennung von Desktop/Mobile/Tablet
 * @returns {Object} { isMobile, isTablet, isDesktop, screenWidth }
 */
export function useDevice() {
  const [deviceInfo, setDeviceInfo] = useState({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    screenWidth: typeof window !== 'undefined' ? window.innerWidth : 1200
  })

  useEffect(() => {
    const updateDeviceInfo = () => {
      const width = window.innerWidth
      const isMobile = width < 768
      const isTablet = width >= 768 && width < 1024
      const isDesktop = width >= 1024

      setDeviceInfo({
        isMobile,
        isTablet,
        isDesktop,
        screenWidth: width
      })
    }

    // Initial check
    updateDeviceInfo()

    // Listen to resize events
    window.addEventListener('resize', updateDeviceInfo)

    return () => {
      window.removeEventListener('resize', updateDeviceInfo)
    }
  }, [])

  return deviceInfo
}

