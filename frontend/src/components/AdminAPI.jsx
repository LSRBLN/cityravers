import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './AdminDashboard.css'

const API_BASE = '/api'

function AdminAPI() {
  const [apiSettings, setApiSettings] = useState({
    telegram: { api_id: '', api_hash: '', source: '' },
    '5sim': { api_key: '', source: '' },
    sms_activate: { api_key: '', source: '' },
    sms_manager: { api_key: '', source: '' },
    getsmscode: { api_key: '', source: '' }
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchApiSettings()
  }, [])

  const fetchApiSettings = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setLoading(false)
        return
      }
      // Interceptor fügt Token automatisch hinzu
      const response = await axios.get(`${API_BASE}/admin/api-settings`)
      setApiSettings(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der API-Einstellungen:', error)
        alert('Fehler beim Laden der API-Einstellungen')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Kein Token vorhanden')
        setSaving(false)
        return
      }
      // Interceptor fügt Token automatisch hinzu
      await axios.put(`${API_BASE}/admin/api-settings`, apiSettings)
      alert('API-Einstellungen erfolgreich gespeichert')
      fetchApiSettings()
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
      alert(error.response?.data?.detail || 'Fehler beim Speichern')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="admin-loading">Lade API-Einstellungen...</div>
  }

  return (
    <div className="admin-api">
      <h2>API-Einstellungen</h2>
      <p className="info-text">
        Hier können Sie die API-Keys für verschiedene Dienste verwalten.
        Änderungen werden in der Datenbank gespeichert.
      </p>

      <div className="api-settings-form">
        <div className="api-section">
          <h3>📱 Telegram API</h3>
          <div className="form-group">
            <label>API ID:</label>
            <input
              type="text"
              value={apiSettings.telegram.api_id}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                telegram: { ...apiSettings.telegram, api_id: e.target.value }
              })}
              placeholder="Telegram API ID"
            />
            <small>Quelle: {apiSettings.telegram.source === 'database' ? 'Datenbank' : 'Umgebungsvariable'}</small>
          </div>
          <div className="form-group">
            <label>API Hash:</label>
            <input
              type="text"
              value={apiSettings.telegram.api_hash}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                telegram: { ...apiSettings.telegram, api_hash: e.target.value }
              })}
              placeholder="Telegram API Hash"
            />
          </div>
        </div>

        <div className="api-section">
          <h3>📞 5sim.net API</h3>
          <div className="form-group">
            <label>API Key:</label>
            <input
              type="password"
              value={apiSettings['5sim'].api_key}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                '5sim': { ...apiSettings['5sim'], api_key: e.target.value }
              })}
              placeholder="5sim.net API Key"
            />
            <small>Quelle: {apiSettings['5sim'].source === 'database' ? 'Datenbank' : 'Umgebungsvariable'}</small>
          </div>
        </div>

        <div className="api-section">
          <h3>📲 SMS-Activate API</h3>
          <div className="form-group">
            <label>API Key:</label>
            <input
              type="password"
              value={apiSettings.sms_activate.api_key}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                sms_activate: { ...apiSettings.sms_activate, api_key: e.target.value }
              })}
              placeholder="SMS-Activate API Key"
            />
            <small>Quelle: {apiSettings.sms_activate.source === 'database' ? 'Datenbank' : 'Umgebungsvariable'}</small>
          </div>
        </div>

        <div className="api-section">
          <h3>📱 SMS-Manager.com API</h3>
          <div className="form-group">
            <label>API Key:</label>
            <input
              type="password"
              value={apiSettings.sms_manager.api_key}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                sms_manager: { ...apiSettings.sms_manager, api_key: e.target.value }
              })}
              placeholder="SMS-Manager.com API Key"
            />
            <small>Quelle: {apiSettings.sms_manager.source === 'database' ? 'Datenbank' : 'Umgebungsvariable'}</small>
          </div>
        </div>

        <div className="api-section">
          <h3>📞 GetSMSCode.com API</h3>
          <div className="form-group">
            <label>API Key (Format: username:token):</label>
            <input
              type="password"
              value={apiSettings.getsmscode.api_key}
              onChange={(e) => setApiSettings({
                ...apiSettings,
                getsmscode: { ...apiSettings.getsmscode, api_key: e.target.value }
              })}
              placeholder="GetSMSCode API Key (username:token)"
            />
            <small>Quelle: {apiSettings.getsmscode.source === 'database' ? 'Datenbank' : 'Umgebungsvariable'}</small>
            <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
              Format: username:token (z.B. myuser:abc123def456)
            </small>
          </div>
        </div>

        <div className="form-actions">
          <button onClick={handleSave} className="btn-primary" disabled={saving}>
            {saving ? 'Speichere...' : '💾 Speichern'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminAPI

