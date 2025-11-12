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
    <div className="user-profile">
      <div className="profile-header">
        <div className="profile-info">
          <h3>👤 {user.username}</h3>
          <p>{user.email}</p>
        </div>
        <button onClick={logout} className="btn btn-secondary">
          Abmelden
        </button>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h4>📦 Abonnement</h4>
          <div className="subscription-card">
            <div className="subscription-plan">
              <strong>{getPlanName(subscription.plan_type)}</strong>
              <span className={`status ${subscription.is_active ? 'active' : 'inactive'}`}>
                {subscription.is_active ? '✅ Aktiv' : '❌ Inaktiv'}
              </span>
            </div>
            {subscription.expires_at && (
              <p className="expiry">Läuft ab: {getExpiryDate()}</p>
            )}
          </div>
        </div>

        <div className="profile-section">
          <h4>📊 Statistiken</h4>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{stats.account_count || 0}</div>
              <div className="stat-label">Accounts</div>
              <div className="stat-limit">Max: {subscription.max_accounts || 1}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.group_count || 0}</div>
              <div className="stat-label">Gruppen</div>
              <div className="stat-limit">Max: {subscription.max_groups || 5}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{subscription.max_messages_per_day || 10}</div>
              <div className="stat-label">Nachrichten/Tag</div>
            </div>
          </div>
        </div>

        {subscription.features && Object.keys(subscription.features).length > 0 && (
          <div className="profile-section">
            <h4>✨ Features</h4>
            <div className="features-list">
              {Object.entries(subscription.features).map(([key, value]) => (
                <div key={key} className="feature-item">
                  {value ? '✅' : '❌'} {key.replace(/_/g, ' ')}
                </div>
              ))}
            </div>
          </div>
        )}

        {subscription.plan_type === 'free_trial' && (
          <div className="upgrade-banner">
            <h4>🚀 Upgrade verfügbar!</h4>
            <p>Dein kostenloser Testzugang läuft bald ab. Upgrade jetzt für mehr Features!</p>
            <button className="btn btn-primary">Paket auswählen</button>
          </div>
        )}
      </div>
    </div>
  )
}

