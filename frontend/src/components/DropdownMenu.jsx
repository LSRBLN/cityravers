import React, { useState, useRef, useEffect } from 'react'
import { useDevice } from '../hooks/useDevice'
import './DropdownMenu.css'

export default function DropdownMenu({ activeTab, setActiveTab, isAdmin }) {
  const { isMobile } = useDevice()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  const menuItems = [
    { id: 'accounts', label: 'Accounts', icon: '👤' },
    { id: 'groups', label: 'Gruppen', icon: '👥' },
    { id: 'messages', label: 'Geplante Nachrichten', icon: '📅' },
    { id: 'scraper', label: 'User-Scraping', icon: '👥' },
    { id: 'forwarder', label: 'Weiterleiten', icon: '📤' },
    { id: 'warmer', label: 'Account-Warmer', icon: '🔥' },
    { id: 'templates', label: 'Vorlagen', icon: '📝' },
    { id: 'proxies', label: 'Proxies', icon: '🔒' },
    { id: 'account-to-groups', label: 'Account zu Gruppen', icon: '👤→👥' },
    { id: 'subscriptions', label: 'Pakete', icon: '📦' },
    { id: 'handbook', label: '📖 Handbuch & Anleitungen', icon: '📖', highlight: true },
  ]

  if (isAdmin) {
    menuItems.push({ 
      id: 'admin', 
      label: '🔐 Admin Console', 
      icon: '🔐',
      highlight: true 
    })
  }

  const activeItem = menuItems.find(item => item.id === activeTab)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      document.addEventListener('touchstart', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('touchstart', handleClickOutside)
    }
  }, [isOpen])

  const handleSelect = (itemId) => {
    setActiveTab(itemId)
    setIsOpen(false)
  }

  return (
    <>
      {isOpen && isMobile && (
        <div 
          className="dropdown-menu-overlay"
          onClick={() => setIsOpen(false)}
        />
      )}
      <div className="dropdown-menu-container" ref={dropdownRef}>
        <button
          className="dropdown-menu-trigger"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Menu öffnen"
          aria-expanded={isOpen}
        >
          <span className="dropdown-menu-icon">☰</span>
          <span className="dropdown-menu-label">
            {activeItem ? `${activeItem.icon} ${activeItem.label}` : '☰ Menü'}
          </span>
          <span className={`dropdown-menu-arrow ${isOpen ? 'open' : ''}`}>▼</span>
        </button>

        {isOpen && (
          <div className={`dropdown-menu ${isMobile ? 'mobile' : ''}`}>
            {menuItems.map((item) => (
              <button
                key={item.id}
                className={`dropdown-menu-item ${activeTab === item.id ? 'active' : ''} ${item.highlight ? 'highlight' : ''}`}
                onClick={() => handleSelect(item.id)}
                aria-label={item.label}
              >
                <span className="dropdown-menu-item-icon">{item.icon}</span>
                <span className="dropdown-menu-item-label">{item.label}</span>
                {activeTab === item.id && (
                  <span className="dropdown-menu-item-check">✓</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

