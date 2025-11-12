import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function AccountWarmer({ accounts, onUpdate }) {
  const [warmings, setWarmings] = useState([])
  const [loading, setLoading] = useState(false)
  const [showConfigModal, setShowConfigModal] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [config, setConfig] = useState({
    account_id: '',
    read_messages_per_day: 20,
    scroll_dialogs_per_day: 10,
    reactions_per_day: 5,
    small_messages_per_day: 3,
    start_time: '09:00',
    end_time: '22:00',
    min_delay: 30.0,
    max_delay: 300.0,
    max_warming_days: 14
  })
  const [activities, setActivities] = useState({})

  useEffect(() => {
    loadWarmings()
    const interval = setInterval(loadWarmings, 10000) // Alle 10 Sekunden aktualisieren
    return () => clearInterval(interval)
  }, [])

  const loadWarmings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/warming/stats`)
      setWarmings(response.data)
    } catch (error) {
      console.error('Fehler beim Laden:', error)
    }
  }

  const loadConfig = async (accountId) => {
    try {
      const response = await axios.get(`${API_BASE}/warming/config/${accountId}`)
      setConfig(response.data)
      setSelectedAccount(accountId)
      setShowConfigModal(true)
    } catch (error) {
      if (error.response?.status === 404) {
        // Keine Konfiguration vorhanden, erstelle neue
        setConfig({
          account_id: accountId,
          read_messages_per_day: 20,
          scroll_dialogs_per_day: 10,
          reactions_per_day: 5,
          small_messages_per_day: 3,
          start_time: '09:00',
          end_time: '22:00',
          min_delay: 30.0,
          max_delay: 300.0,
          max_warming_days: 14
        })
        setSelectedAccount(accountId)
        setShowConfigModal(true)
      } else {
        alert('Fehler: ' + (error.response?.data?.detail || error.message))
      }
    }
  }

  const handleSaveConfig = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/warming/config`, config)
      setShowConfigModal(false)
      loadWarmings()
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (accountId, currentStatus) => {
    setLoading(true)
    try {
      await axios.put(`${API_BASE}/warming/config/${accountId}`, {
        is_active: !currentStatus
      })
      loadWarmings()
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const loadActivities = async (accountId) => {
    try {
      const response = await axios.get(`${API_BASE}/warming/activities/${accountId}`)
      setActivities(prev => ({ ...prev, [accountId]: response.data }))
    } catch (error) {
      console.error('Fehler beim Laden der Aktivitäten:', error)
    }
  }

  const userAccounts = accounts.filter(acc => acc.account_type === 'user')

  const getAccountName = (accountId) => {
    const account = accounts.find(a => a.id === accountId)
    return account ? account.name : `Account ${accountId}`
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Account-Warmer</h2>
          <button className="btn btn-primary" onClick={loadWarmings}>
            🔄 Aktualisieren
          </button>
        </div>

        <div className="alert alert-info">
          <strong>ℹ️ Info:</strong> Account-Warming simuliert natürliche Aktivitäten, um Accounts "aufzuwärmen" 
          und das Risiko von Sperrungen zu reduzieren. Schrittweise Erhöhung der Aktivität über 10-14 Tage.
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Status</th>
              <th>Fortschritt</th>
              <th>Tage</th>
              <th>Aktionen</th>
              <th>Letzte Aktion</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {warmings.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', color: '#999' }}>
                  Keine Warming-Konfigurationen vorhanden. Erstelle eine neue Konfiguration.
                </td>
              </tr>
            ) : (
              warmings.map(warming => (
                <tr key={warming.account_id}>
                  <td>{warming.account_name}</td>
                  <td>
                    {warming.is_active ? (
                      <span className="badge badge-success">Aktiv</span>
                    ) : (
                      <span className="badge badge-secondary">Inaktiv</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        flex: 1,
                        height: '20px',
                        backgroundColor: '#e0e0e0',
                        borderRadius: '10px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${warming.progress * 100}%`,
                          height: '100%',
                          backgroundColor: warming.progress >= 1 ? '#4caf50' : '#667eea',
                          transition: 'width 0.3s'
                        }} />
                      </div>
                      <span style={{ fontSize: '0.9rem', color: '#666' }}>
                        {Math.round(warming.progress * 100)}%
                      </span>
                    </div>
                  </td>
                  <td>
                    {warming.warming_days} / {warming.max_warming_days}
                  </td>
                  <td>{warming.total_actions}</td>
                  <td>
                    {warming.last_action_at
                      ? new Date(warming.last_action_at).toLocaleString('de-DE')
                      : 'Nie'}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={() => loadConfig(warming.account_id)}
                      >
                        ⚙️ Konfigurieren
                      </button>
                      <button
                        className={`btn btn-small ${warming.is_active ? 'btn-warning' : 'btn-success'}`}
                        onClick={() => handleToggleActive(warming.account_id, warming.is_active)}
                        disabled={loading}
                      >
                        {warming.is_active ? '⏸️ Pausieren' : '▶️ Starten'}
                      </button>
                      <button
                        className="btn btn-info btn-small"
                        onClick={() => loadActivities(warming.account_id)}
                      >
                        📊 Aktivitäten
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        <div style={{ marginTop: '20px' }}>
          <h3>Neue Konfiguration erstellen</h3>
          <select
            onChange={(e) => {
              if (e.target.value) {
                loadConfig(parseInt(e.target.value))
              }
            }}
            style={{ padding: '10px', borderRadius: '5px', border: '2px solid #e0e0e0', minWidth: '200px' }}
          >
            <option value="">Account auswählen...</option>
            {userAccounts.map(acc => (
              <option key={acc.id} value={acc.id}>
                {acc.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Aktivitäten-Modals */}
      {Object.entries(activities).map(([accountId, acts]) => (
        <div key={accountId} className="modal" style={{ display: acts.length > 0 ? 'block' : 'none' }}>
          <div className="modal-content" style={{ maxWidth: '800px' }}>
            <div className="modal-header">
              <h3>Aktivitäten: {getAccountName(parseInt(accountId))}</h3>
              <button className="close-btn" onClick={() => setActivities(prev => {
                const newActs = { ...prev }
                delete newActs[accountId]
                return newActs
              })}>×</button>
            </div>
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Typ</th>
                    <th>Ziel</th>
                    <th>Erfolg</th>
                    <th>Zeit</th>
                  </tr>
                </thead>
                <tbody>
                  {acts.map(act => (
                    <tr key={act.id}>
                      <td>
                        {act.activity_type === 'read' && '📖 Lesen'}
                        {act.activity_type === 'scroll' && '📜 Scrollen'}
                        {act.activity_type === 'reaction' && '👍 Reaktion'}
                        {act.activity_type === 'message' && '💬 Nachricht'}
                      </td>
                      <td>{act.target_chat_name || '-'}</td>
                      <td>
                        {act.success ? (
                          <span className="badge badge-success">✓</span>
                        ) : (
                          <span className="badge badge-danger" title={act.error_message}>✗</span>
                        )}
                      </td>
                      <td>
                        {act.executed_at
                          ? new Date(act.executed_at).toLocaleString('de-DE')
                          : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ))}

      {/* Konfigurations-Modal */}
      {showConfigModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Warming-Konfiguration</h3>
              <button className="close-btn" onClick={() => setShowConfigModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>Aktivitäten pro Tag</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Nachrichten lesen</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={config.read_messages_per_day}
                    onChange={(e) => setConfig({ ...config, read_messages_per_day: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Dialoge scrollen</label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    value={config.scroll_dialogs_per_day}
                    onChange={(e) => setConfig({ ...config, scroll_dialogs_per_day: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Reaktionen</label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={config.reactions_per_day}
                    onChange={(e) => setConfig({ ...config, reactions_per_day: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Kleine Nachrichten</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={config.small_messages_per_day}
                    onChange={(e) => setConfig({ ...config, small_messages_per_day: parseInt(e.target.value) })}
                  />
                </div>
              </div>
            </div>
            <div className="form-group">
              <label>Zeitfenster</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Startzeit (HH:MM)</label>
                  <input
                    type="time"
                    value={config.start_time}
                    onChange={(e) => setConfig({ ...config, start_time: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Endzeit (HH:MM)</label>
                  <input
                    type="time"
                    value={config.end_time}
                    onChange={(e) => setConfig({ ...config, end_time: e.target.value })}
                  />
                </div>
              </div>
            </div>
            <div className="form-group">
              <label>Delays (Sekunden)</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Min. Delay</label>
                  <input
                    type="number"
                    min="10"
                    max="600"
                    step="1"
                    value={config.min_delay}
                    onChange={(e) => setConfig({ ...config, min_delay: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.9rem' }}>Max. Delay</label>
                  <input
                    type="number"
                    min="30"
                    max="3600"
                    step="1"
                    value={config.max_delay}
                    onChange={(e) => setConfig({ ...config, max_delay: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
            </div>
            <div className="form-group">
              <label>Warming-Dauer (Tage)</label>
              <input
                type="number"
                min="1"
                max="30"
                value={config.max_warming_days}
                onChange={(e) => setConfig({ ...config, max_warming_days: parseInt(e.target.value) })}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowConfigModal(false)}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSaveConfig}
                disabled={loading}
              >
                {loading ? 'Speichere...' : 'Speichern'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

