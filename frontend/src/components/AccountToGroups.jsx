import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function AccountToGroups({ accounts = [], groups = [], onUpdate }) {
  const [selectedAccountId, setSelectedAccountId] = useState('')
  const [selectedGroupIds, setSelectedGroupIds] = useState([])
  const [delay, setDelay] = useState(3.0)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedAccountId || selectedGroupIds.length === 0) {
      alert('Bitte Account und mindestens eine Gruppe auswählen')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await axios.post(`${API_BASE}/accounts/add-to-groups`, {
        account_id: parseInt(selectedAccountId),
        group_ids: selectedGroupIds.map(id => parseInt(id)),
        delay: delay
      })

      setResult(response.data)
      
      if (response.data.success) {
        alert(`✅ Erfolgreich!\n\nHinzugefügt: ${response.data.added}\nFehlgeschlagen: ${response.data.failed}\nGesamt: ${response.data.total}`)
        if (onUpdate) {
          onUpdate()
        }
      } else {
        alert(`❌ Fehler: ${response.data.error || 'Unbekannter Fehler'}`)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleGroupToggle = (groupId) => {
    setSelectedGroupIds(prev => {
      if (prev.includes(groupId)) {
        return prev.filter(id => id !== groupId)
      } else {
        return [...prev, groupId]
      }
    })
  }

  const handleSelectAll = () => {
    if (selectedGroupIds.length === groups.filter(g => g.is_active).length) {
      setSelectedGroupIds([])
    } else {
      setSelectedGroupIds(groups.filter(g => g.is_active).map(g => g.id))
    }
  }

  const connectedAccounts = accounts.filter(acc => acc.account_type === 'user' && acc.connected)
  const activeGroups = groups.filter(g => g.is_active)

  return (
    <div className="section">
      <h2>👤 Account zu Gruppen hinzufügen</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Wähle einen Account aus und füge ihn zu mehreren Gruppen hinzu.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Account auswählen *</label>
          <select
            required
            value={selectedAccountId}
            onChange={(e) => setSelectedAccountId(e.target.value)}
            disabled={loading}
          >
            <option value="">Account auswählen...</option>
            {connectedAccounts.map(acc => (
              <option key={acc.id} value={acc.id}>
                {acc.name} {acc.info?.username ? `(@${acc.info.username})` : ''} {acc.info?.first_name ? `- ${acc.info.first_name}` : ''}
              </option>
            ))}
          </select>
          {connectedAccounts.length === 0 && (
            <p style={{ fontSize: '0.85rem', color: '#e74c3c', marginTop: '5px' }}>
              ⚠️ Keine verbundenen User-Accounts verfügbar. Bitte zuerst einen Account verbinden.
            </p>
          )}
        </div>

        <div className="form-group">
          <label>Gruppen auswählen *</label>
          <div style={{ marginBottom: '10px' }}>
            <button
              type="button"
              className="btn btn-secondary btn-small"
              onClick={handleSelectAll}
              disabled={loading || activeGroups.length === 0}
            >
              {selectedGroupIds.length === activeGroups.length ? 'Alle abwählen' : 'Alle auswählen'}
            </button>
            <span style={{ marginLeft: '10px', fontSize: '0.9rem', color: '#666' }}>
              {selectedGroupIds.length} von {activeGroups.length} Gruppen ausgewählt
            </span>
          </div>
          <div style={{ 
            maxHeight: '300px', 
            overflowY: 'auto', 
            border: '1px solid #e0e0e0', 
            borderRadius: '5px', 
            padding: '10px',
            backgroundColor: '#f9f9f9'
          }}>
            {activeGroups.length === 0 ? (
              <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                Keine Gruppen verfügbar. Bitte zuerst Gruppen hinzufügen.
              </p>
            ) : (
              activeGroups.map(group => (
                <label
                  key={group.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '8px',
                    marginBottom: '5px',
                    cursor: 'pointer',
                    backgroundColor: selectedGroupIds.includes(group.id) ? '#e8f5e9' : 'white',
                    borderRadius: '3px',
                    border: selectedGroupIds.includes(group.id) ? '2px solid #4caf50' : '1px solid #e0e0e0'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedGroupIds.includes(group.id)}
                    onChange={() => handleGroupToggle(group.id)}
                    disabled={loading}
                    style={{ marginRight: '10px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 'bold' }}>{group.name}</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>
                      {group.chat_type || 'group'} • 
                      {group.member_count ? ` ${group.member_count} Mitglieder` : ' Mitglieder unbekannt'} • 
                      {group.is_public ? ' Öffentlich' : ' Privat'} • 
                      {group.bot_invite_allowed ? ' Bots erlaubt' : ' Bots nicht erlaubt'}
                      {group.username && ` • @${group.username}`}
                    </div>
                  </div>
                </label>
              ))
            )}
          </div>
        </div>

        <div className="form-group">
          <label>Verzögerung zwischen Gruppen (Sekunden)</label>
          <input
            type="number"
            min="1"
            max="60"
            step="0.5"
            value={delay}
            onChange={(e) => setDelay(parseFloat(e.target.value))}
            disabled={loading}
          />
          <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
            Empfohlen: 3-5 Sekunden zwischen Gruppen-Einladungen
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setSelectedAccountId('')
              setSelectedGroupIds([])
              setResult(null)
            }}
            disabled={loading}
          >
            Zurücksetzen
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !selectedAccountId || selectedGroupIds.length === 0}
          >
            {loading ? 'Füge hinzu...' : `Account zu ${selectedGroupIds.length} Gruppe(n) hinzufügen`}
          </button>
        </div>
      </form>

      {result && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: result.success ? '#e8f5e9' : '#ffebee', borderRadius: '5px' }}>
          <h3 style={{ marginTop: 0 }}>Ergebnis:</h3>
          <p><strong>Gesamt:</strong> {result.total}</p>
          <p><strong>Hinzugefügt:</strong> {result.added}</p>
          <p><strong>Fehlgeschlagen:</strong> {result.failed}</p>
          
          {result.errors && result.errors.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong>Fehlerdetails:</strong>
              <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                {result.errors.slice(0, 10).map((error, idx) => (
                  <li key={idx} style={{ fontSize: '0.9rem' }}>
                    {error.group || error.user_id}: {error.error || error.message || error.status}
                  </li>
                ))}
                {result.errors.length > 10 && (
                  <li style={{ fontSize: '0.9rem', color: '#666' }}>
                    ... und {result.errors.length - 10} weitere Fehler
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

