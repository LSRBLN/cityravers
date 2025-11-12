import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import './UserProfile.css'

export default function UserProfile() {
  const { user, logout } = useAuth()

  if (!user) return null

  const subscription = user.subscription || {}
  const stats = user.stats || {}

  const getPlanName = (planType) => {
    const plans = {
      'free_trial': '🎁 Kostenloser Test',
      'basic': '📦 Basis',
      'pro': '⭐ Pro',
      'enterprise': '🚀 Enterprise'
    }
    return plans[planType] || planType
  }

  const getExpiryDate = () => {
    if (!subscription.expires_at) return 'Unbegrenzt'
    const date = new Date(subscription.expires_at)
    return date.toLocaleDateString('de-DE')
  }

  return (
    <div style={{ 
      background: 'rgba(255, 255, 255, 0.15)', 
      backdropFilter: 'blur(10px)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--spacing-lg)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      minWidth: '280px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'white' }}>👤 {user.username}</h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.875rem', opacity: 0.9, color: 'white' }}>{user.email}</p>
        </div>
        <button 
          onClick={logout} 
          className="btn-modern btn-modern-secondary" 
          style={{ 
            background: 'rgba(255, 255, 255, 0.2)', 
            color: 'white', 
            border: '1px solid rgba(255, 255, 255, 0.3)',
            padding: 'var(--spacing-sm) var(--spacing-md)',
            fontSize: '0.875rem'
          }}
        >
          Abmelden
        </button>
      </div>

      <div className="stats-grid-modern" style={{ marginTop: 'var(--spacing-md)', gap: 'var(--spacing-sm)' }}>
        <div className="stat-card" style={{ padding: 'var(--spacing-md)' }}>
          <div className="stat-card-value" style={{ fontSize: '1.75rem' }}>{stats.account_count || 0}</div>
          <div className="stat-card-label" style={{ fontSize: '0.75rem' }}>Accounts</div>
          <div className="stat-card-max" style={{ fontSize: '0.7rem' }}>Max: {subscription.max_accounts || 1}</div>
        </div>
        <div className="stat-card" style={{ padding: 'var(--spacing-md)' }}>
          <div className="stat-card-value" style={{ fontSize: '1.75rem' }}>{stats.group_count || 0}</div>
          <div className="stat-card-label" style={{ fontSize: '0.75rem' }}>Gruppen</div>
          <div className="stat-card-max" style={{ fontSize: '0.7rem' }}>Max: {subscription.max_groups || 5}</div>
        </div>
        <div className="stat-card" style={{ padding: 'var(--spacing-md)' }}>
          <div className="stat-card-value" style={{ fontSize: '1.75rem' }}>{subscription.max_messages_per_day || 10}</div>
          <div className="stat-card-label" style={{ fontSize: '0.75rem' }}>Nachrichten/Tag</div>
        </div>
      </div>

      {subscription.plan_type === 'free_trial' && (
        <div style={{ marginTop: 'var(--spacing-md)', textAlign: 'center' }}>
          <button 
            className="btn-modern btn-modern-primary" 
            style={{ 
              background: 'rgba(255, 255, 255, 0.25)', 
              color: 'white', 
              border: '1px solid rgba(255, 255, 255, 0.4)',
              width: '100%',
              fontSize: '0.875rem',
              padding: 'var(--spacing-sm) var(--spacing-md)'
            }}
            onClick={() => window.location.hash = '#subscriptions'}
          >
            🚀 Upgrade verfügbar
          </button>
        </div>
      )}
    </div>
  )
}

