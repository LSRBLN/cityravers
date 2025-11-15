import React from 'react'
import { useDevice } from '../hooks/useDevice'
import './Navigation.css'

export default function Navigation({ activeTab, setActiveTab, isAdmin }) {
  const { isMobile } = useDevice()

  // Quick-Access Buttons (2 Reihen)
  const quickAccessItems = [
    [
      { id: 'accounts', label: 'Accounts', icon: '👤', color: 'blue' },
      { id: 'groups', label: 'Gruppen', icon: '👥', color: 'purple' },
      { id: 'messages', label: 'Geplante Nachrichten', icon: '📅', color: 'blue' },
      { id: 'forwarder', label: 'Weiterleiten', icon: '📤', color: 'green' }
    ],
    [
      { id: 'scraper', label: 'User-Scraping', icon: '👥', color: 'purple' },
      { id: 'warmer', label: 'Account-Warmer', icon: '🔥', color: 'orange' },
      { id: 'templates', label: 'Vorlagen', icon: '📝', color: 'blue' },
      { id: 'proxies', label: 'Proxies', icon: '🔒', color: 'purple' }
    ]
  ]

  // Navigationsleiste Items
  const navItems = [
    { id: 'accounts', label: 'Accounts', icon: '👤' },
    { id: 'groups', label: 'Gruppen', icon: '👥' },
    { id: 'messages', label: 'Nachrichten', icon: '📅' },
    { id: 'scraper', label: 'Scraping', icon: '👥' },
    { id: 'forwarder', label: 'Weiterleiten', icon: '📤' },
    { id: 'warmer', label: 'Warmer', icon: '🔥' },
    { id: 'templates', label: 'Vorlagen', icon: '📝' },
    { id: 'proxies', label: 'Proxies', icon: '🔒' },
    { id: 'account-to-groups', label: 'Account→Gruppen', icon: '👤→👥' },
    { id: 'subscriptions', label: 'Pakete', icon: '📦' },
    { id: 'handbook', label: 'Handbuch', icon: '📖' }
  ]

  if (isAdmin) {
    navItems.push({ id: 'admin', label: 'Admin', icon: '🔐' })
  }

  const handleSelect = (itemId) => {
    setActiveTab(itemId)
  }

  return (
    <div className="navigation-container">
      {/* Quick-Access Dashboard (2 Reihen) */}
      <div className="quick-access-dashboard">
        {quickAccessItems.map((row, rowIndex) => (
          <div key={rowIndex} className="quick-access-row">
            {row.map((item) => (
              <button
                key={item.id}
                className={`quick-access-button ${activeTab === item.id ? 'active' : ''} ${item.color}`}
                onClick={() => handleSelect(item.id)}
                title={item.label}
              >
                <div className="quick-access-icon">{item.icon}</div>
                <div className="quick-access-label">{item.label}</div>
                {activeTab === item.id && (
                  <div className="quick-access-indicator"></div>
                )}
              </button>
            ))}
          </div>
        ))}
      </div>

      {/* Navigationsleiste */}
      <div className="navigation-bar">
        <div className="navigation-scroll">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => handleSelect(item.id)}
              title={item.label}
            >
              <span className="nav-item-icon">{item.icon}</span>
              <span className="nav-item-label">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

