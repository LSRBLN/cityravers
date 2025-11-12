import React, { useState } from 'react'
import axios from 'axios'

const API_BASE = '/api'

export default function MessageForwarder({ accounts, groups, onUpdate }) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [forwarding, setForwarding] = useState(false)
  const [selectedMessages, setSelectedMessages] = useState([])
  const [config, setConfig] = useState({
    account_id: '',
    source_group_id: '',
    limit: 100
  })
  const [forwardConfig, setForwardConfig] = useState({
    target_group_ids: [],
    delay: 2.0
  })

  const handleLoadMessages = async () => {
    if (!config.account_id || !config.source_group_id) {
      alert('Bitte Account und Quell-Gruppe auswählen')
      return
    }
    
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/messages/get-group-messages`, {
        account_id: parseInt(config.account_id),
        group_id: parseInt(config.source_group_id),
        limit: parseInt(config.limit)
      })
      
      setMessages(response.data)
      setSelectedMessages([])
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleForward = async () => {
    if (!config.account_id || !config.source_group_id) {
      alert('Bitte Account und Quell-Gruppe auswählen')
      return
    }
    
    if (selectedMessages.length === 0) {
      alert('Bitte mindestens eine Nachricht auswählen')
      return
    }
    
    if (forwardConfig.target_group_ids.length === 0) {
      alert('Bitte mindestens eine Ziel-Gruppe auswählen')
      return
    }
    
    if (!confirm(`Wirklich ${selectedMessages.length} Nachricht(en) an ${forwardConfig.target_group_ids.length} Gruppe(n) weiterleiten?`)) {
      return
    }
    
    setForwarding(true)
    try {
      const response = await axios.post(`${API_BASE}/messages/forward`, {
        account_id: parseInt(config.account_id),
        source_group_id: parseInt(config.source_group_id),
        message_ids: selectedMessages,
        target_group_ids: forwardConfig.target_group_ids.map(id => parseInt(id)),
        delay: parseFloat(forwardConfig.delay)
      })
      
      alert(`Weiterleitung abgeschlossen!\n✅ Erfolgreich: ${response.data.success}\n❌ Fehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.log('Fehler:', response.data.errors)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setForwarding(false)
    }
  }

  const handleMessageToggle = (messageId) => {
    setSelectedMessages(prev => {
      if (prev.includes(messageId)) {
        return prev.filter(id => id !== messageId)
      } else {
        return [...prev, messageId]
      }
    })
  }

  const handleSelectAll = () => {
    if (selectedMessages.length === messages.length) {
      setSelectedMessages([])
    } else {
      setSelectedMessages(messages.map(m => m.id))
    }
  }

  const handleTargetGroupToggle = (groupId) => {
    const groupIdStr = groupId.toString()
    setForwardConfig(prev => {
      const currentIds = prev.target_group_ids.map(id => id.toString())
      if (currentIds.includes(groupIdStr)) {
        return {
          ...prev,
          target_group_ids: prev.target_group_ids.filter(id => id.toString() !== groupIdStr)
        }
      } else {
        return {
          ...prev,
          target_group_ids: [...prev.target_group_ids, groupId]
        }
      }
    })
  }

  const connectedUserAccounts = accounts.filter(acc => acc.connected && acc.account_type === 'user')

  const getGroupName = (groupId) => {
    const group = groups.find(g => g.id === groupId)
    return group ? group.name : `ID: ${groupId}`
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Nachrichten-Weiterleitung</h2>
        </div>

        <div className="alert alert-warning">
          <strong>⚠️ WARNUNG:</strong> Massenweiterleitungen können gegen Telegram Nutzungsbedingungen verstoßen 
          und zu Account-Sperrungen führen. Nur für legitime Zwecke verwenden!
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
          <div>
            <h3 style={{ marginBottom: '15px', color: '#667eea' }}>Nachrichten laden</h3>
            <div className="form-group">
              <label>Account</label>
              <select
                value={config.account_id}
                onChange={(e) => setConfig({ ...config, account_id: e.target.value })}
              >
                <option value="">Bitte wählen...</option>
                {connectedUserAccounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Quell-Gruppe</label>
              <select
                value={config.source_group_id}
                onChange={(e) => setConfig({ ...config, source_group_id: e.target.value })}
              >
                <option value="">Bitte wählen...</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Limit (max. Nachrichten)</label>
              <input
                type="number"
                min="1"
                max="1000"
                value={config.limit}
                onChange={(e) => setConfig({ ...config, limit: e.target.value })}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={handleLoadMessages}
              disabled={loading || !config.account_id || !config.source_group_id}
            >
              {loading ? 'Lade...' : '📥 Nachrichten laden'}
            </button>
          </div>

          <div>
            <h3 style={{ marginBottom: '15px', color: '#667eea' }}>Weiterleiten</h3>
            <div className="form-group">
              <label>Ziel-Gruppen (mehrere auswählbar)</label>
              <div style={{
                border: '2px solid #e0e0e0',
                borderRadius: '5px',
                padding: '10px',
                maxHeight: '150px',
                overflowY: 'auto',
                backgroundColor: '#f8f9fa'
              }}>
                {groups.length === 0 ? (
                  <p style={{ color: '#999', margin: 0 }}>Keine Gruppen verfügbar</p>
                ) : (
                  groups.map(group => (
                    <label key={group.id} style={{
                      display: 'block',
                      padding: '5px',
                      cursor: 'pointer',
                      borderRadius: '3px',
                      marginBottom: '3px',
                      backgroundColor: forwardConfig.target_group_ids.includes(group.id) ? '#e3f2fd' : 'transparent'
                    }}>
                      <input
                        type="checkbox"
                        checked={forwardConfig.target_group_ids.includes(group.id)}
                        onChange={() => handleTargetGroupToggle(group.id)}
                        style={{ marginRight: '8px' }}
                      />
                      {group.name}
                    </label>
                  ))
                )}
              </div>
              {forwardConfig.target_group_ids.length > 0 && (
                <p style={{ marginTop: '5px', fontSize: '0.9rem', color: '#667eea' }}>
                  {forwardConfig.target_group_ids.length} Gruppe(n) ausgewählt
                </p>
              )}
            </div>
            <div className="form-group">
              <label>Delay zwischen Weiterleitungen (Sekunden)</label>
              <input
                type="number"
                min="1"
                max="60"
                step="0.1"
                value={forwardConfig.delay}
                onChange={(e) => setForwardConfig({ ...forwardConfig, delay: e.target.value })}
              />
            </div>
            <button
              className="btn btn-success"
              onClick={handleForward}
              disabled={forwarding || selectedMessages.length === 0 || forwardConfig.target_group_ids.length === 0}
            >
              {forwarding ? 'Leite weiter...' : `📤 ${selectedMessages.length} Nachricht(en) weiterleiten`}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Nachrichten ({messages.length})</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            {messages.length > 0 && (
              <>
                <button
                  className="btn btn-secondary btn-small"
                  onClick={handleSelectAll}
                >
                  {selectedMessages.length === messages.length ? 'Alle abwählen' : 'Alle auswählen'}
                </button>
                <span className="badge badge-info">
                  {selectedMessages.length} ausgewählt
                </span>
              </>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading">Lade Nachrichten...</div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <p>Keine Nachrichten geladen. Wähle Account und Gruppe aus und klicke auf "Nachrichten laden".</p>
          </div>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={selectedMessages.length === messages.length && messages.length > 0}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th>ID</th>
                  <th>Text (Vorschau)</th>
                  <th>Datum</th>
                  <th>Typ</th>
                </tr>
              </thead>
              <tbody>
                {messages.map(msg => (
                  <tr key={msg.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedMessages.includes(msg.id)}
                        onChange={() => handleMessageToggle(msg.id)}
                      />
                    </td>
                    <td><code>{msg.id}</code></td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {msg.text ? (msg.text.substring(0, 100) + (msg.text.length > 100 ? '...' : '')) : '(kein Text)'}
                      {msg.media && ' 📎'}
                    </td>
                    <td>
                      {msg.date ? new Date(msg.date).toLocaleString('de-DE') : '-'}
                    </td>
                    <td>
                      {msg.is_reply && '↩️ '}
                      {msg.is_forward && '↪️ '}
                      {msg.media && '📎'}
                      {!msg.is_reply && !msg.is_forward && !msg.media && '💬'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

