import React, { useState, useEffect } from 'react'
import axios from 'axios'
import AdminUserManagement from './AdminUserManagement'
import AdminSettings from './AdminSettings'
import AdminAPI from './AdminAPI'
import './AdminDashboard.css'

const API_BASE = '/api'

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('stats')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Warte bis Token vorhanden ist
    const token = localStorage.getItem('token')
    if (token) {
      // Kurze Verzögerung, damit Interceptor Token setzen kann
      const timer = setTimeout(() => {
        fetchStats()
      }, 100)
      return () => clearTimeout(timer)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('Kein Token vorhanden, überspringe fetchStats')
        setLoading(false)
        return
      }
      // Interceptor fügt Token automatisch hinzu
      const response = await axios.get(`${API_BASE}/admin/stats`)
      setStats(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Statistiken:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="admin-loading">Lade Dashboard...</div>
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>🔐 Admin Console</h1>
        <p>System-Verwaltung und Konfiguration</p>
      </div>

      <div className="admin-tabs">
        <button
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          📊 Statistiken
        </button>
        <button
          className={activeTab === 'users' ? 'active' : ''}
          onClick={() => setActiveTab('users')}
        >
          👥 Benutzerverwaltung
        </button>
        <button
          className={activeTab === 'api' ? 'active' : ''}
          onClick={() => setActiveTab('api')}
        >
          🔑 API-Einstellungen
        </button>
        <button
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ System-Einstellungen
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'stats' && (
          <div className="admin-stats">
            <h2>System-Statistiken</h2>
            {stats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Benutzer</h3>
                  <div className="stat-value">{stats.users.total}</div>
                  <div className="stat-details">
                    <span>✅ Aktiv: {stats.users.active}</span>
                    <span>👑 Admins: {stats.users.admins}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <h3>Accounts</h3>
                  <div className="stat-value">{stats.accounts.total}</div>
                  <div className="stat-details">
                    <span>✅ Aktiv: {stats.accounts.active}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <h3>Gruppen</h3>
                  <div className="stat-value">{stats.groups.total}</div>
                </div>
                <div className="stat-card">
                  <h3>Proxies</h3>
                  <div className="stat-value">{stats.proxies.total}</div>
                  <div className="stat-details">
                    <span>✅ Aktiv: {stats.proxies.active}</span>
                  </div>
                </div>
                <div className="stat-card">
                  <h3>Geplante Nachrichten</h3>
                  <div className="stat-value">{stats.scheduled_messages.total}</div>
                  <div className="stat-details">
                    <span>⏳ Ausstehend: {stats.scheduled_messages.pending}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && <AdminUserManagement />}
        {activeTab === 'api' && <AdminAPI />}
        {activeTab === 'settings' && <AdminSettings />}
      </div>
    </div>
  )
}

export default AdminDashboard

