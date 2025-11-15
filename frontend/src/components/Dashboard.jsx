import React from 'react'
import { useDevice } from '../hooks/useDevice'
import './Dashboard.css'

export default function Dashboard({ accounts, groups, scheduledMessages }) {
  const { isMobile } = useDevice()

  // Berechne Statistiken
  const totalAccounts = accounts?.length || 0
  const connectedAccounts = accounts?.filter(acc => acc.connected)?.length || 0
  const totalGroups = groups?.length || 0
  const totalScheduled = scheduledMessages?.length || 0

  const stats = [
    {
      label: 'Accounts',
      value: totalAccounts,
      subValue: `${connectedAccounts} verbunden`,
      icon: '👤',
      color: 'primary',
      gradient: 'linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%)'
    },
    {
      label: 'Gruppen',
      value: totalGroups,
      subValue: 'Gesamt',
      icon: '👥',
      color: 'secondary',
      gradient: 'linear-gradient(135deg, var(--secondary-500) 0%, var(--secondary-600) 100%)'
    },
    {
      label: 'Geplante Nachrichten',
      value: totalScheduled,
      subValue: 'Aktiv',
      icon: '📅',
      color: 'info',
      gradient: 'linear-gradient(135deg, var(--info) 0%, #2563eb 100%)'
    },
    {
      label: 'Nachrichten/Tag',
      value: '9999',
      subValue: 'Limit',
      icon: '📊',
      color: 'success',
      gradient: 'linear-gradient(135deg, var(--success) 0%, #059669 100%)'
    }
  ]

  return (
    <div className="dashboard-container">
      <div className="dashboard-grid">
        {stats.map((stat, index) => (
          <div 
            key={index} 
            className="dashboard-stat-card"
            style={{ 
              background: stat.gradient,
              animationDelay: `${index * 0.1}s`
            }}
          >
            <div className="dashboard-stat-icon">{stat.icon}</div>
            <div className="dashboard-stat-content">
              <div className="dashboard-stat-value">{stat.value}</div>
              <div className="dashboard-stat-label">{stat.label}</div>
              <div className="dashboard-stat-subvalue">{stat.subValue}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

