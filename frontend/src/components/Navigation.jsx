import React from 'react'
import { useDevice } from '../hooks/useDevice'
import { useAuth } from '../contexts/AuthContext'
import './Navigation.css'

export default function Navigation({ activeTab, setActiveTab, isAdmin, user }) {
  const { isMobile } = useDevice()
  const { logout } = useAuth()

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

  // User-Statistiken für kompakte Anzeige
  const subscription = user?.subscription || {}
  const stats = user?.stats || {}

  return (
    <div className="navigation-container">
      {/* Kompakte User-Leiste */}
      {user && (
        <div className="user-info-bar">
          <div className="user-info-main">
            <div className="user-info-header">
              <span className="user-info-name">👤 {user.username}</span>
              <span className="user-info-email">{user.email}</span>
            </div>
            <div className="user-info-stats">
              <div className="user-stat-item">
                <span className="user-stat-value">{stats.account_count || 0}</span>
                <span className="user-stat-label">Accounts</span>
                <span className="user-stat-max">/ {subscription.max_accounts || 1}</span>
              </div>
              <div className="user-stat-item">
                <span className="user-stat-value">{stats.group_count || 0}</span>
                <span className="user-stat-label">Gruppen</span>
                <span className="user-stat-max">/ {subscription.max_groups || 5}</span>
              </div>
              <div className="user-stat-item">
                <span className="user-stat-value">{subscription.max_messages_per_day || 10}</span>
                <span className="user-stat-label">Msg/Tag</span>
              </div>
            </div>
          </div>
          <div className="user-info-actions">
            {subscription.plan_type === 'free_trial' && (
              <button 
                className="user-upgrade-btn"
                onClick={() => setActiveTab('subscriptions')}
                title="Upgrade verfügbar"
              >
                🚀 Upgrade
              </button>
            )}
            <button 
              className="user-logout-btn"
              onClick={logout}
              title="Abmelden"
            >
              Abmelden
            </button>
          </div>
        </div>
      )}

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

