import React, { useState } from 'react'
import axios from 'axios'
import { format } from 'date-fns'
import MessageTemplates from './MessageTemplates'
import { API_BASE } from '../config/api'

export default function ScheduledMessages({ scheduledMessages, accounts, groups, onUpdate }) {
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    account_id: '',
    group_ids: [],  // Array für mehrere Gruppen
    message: '',
    scheduled_time: '',
    delay: 1.0,
    batch_size: 10,
    batch_delay: 5.0,
    repeat_count: 1,
    group_delay: 2.0  // Delay zwischen Gruppen
  })
  const [loading, setLoading] = useState(false)
  const [showTemplates, setShowTemplates] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await axios.post(`${API_BASE}/scheduled-messages`, {
        ...formData,
        account_id: parseInt(formData.account_id),
        group_ids: formData.group_ids.map(id => parseInt(id)),  // Array von IDs
        scheduled_time: new Date(formData.scheduled_time).toISOString(),
        delay: parseFloat(formData.delay),
        batch_size: parseInt(formData.batch_size),
        batch_delay: parseFloat(formData.batch_delay),
        repeat_count: parseInt(formData.repeat_count),
        group_delay: parseFloat(formData.group_delay)
      })
      setShowModal(false)
      setFormData({
        account_id: '',
        group_ids: [],
        message: '',
        scheduled_time: '',
        delay: 1.0,
        batch_size: 10,
        batch_delay: 5.0,
        repeat_count: 1,
        group_delay: 2.0
      })
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (messageId) => {
    if (!confirm('Geplante Nachricht wirklich abbrechen?')) return
    
    try {
      await axios.delete(`${API_BASE}/scheduled-messages/${messageId}`)
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleTest = async (accountId, groupId, message) => {
    if (!confirm('Testnachricht jetzt senden?')) return
    
    try {
      await axios.post(`${API_BASE}/send-test?account_id=${accountId}&group_id=${groupId}&message=${encodeURIComponent(message)}`)
      alert('Testnachricht gesendet!')
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      running: 'badge-info',
      completed: 'badge-success',
      failed: 'badge-danger',
      cancelled: 'badge-secondary'
    }
    return badges[status] || 'badge-secondary'
  }

  const getAccountName = (accountId) => {
    const account = accounts.find(a => a.id === accountId)
    return account ? account.name : `Account #${accountId}`
  }

  const getGroupName = (groupId) => {
    const group = groups.find(g => g.id === groupId)
    return group ? group.name : `Gruppe #${groupId}`
  }

  const getGroupNames = (groupIds) => {
    if (!Array.isArray(groupIds)) return 'N/A'
    return groupIds.map(id => getGroupName(id)).join(', ')
  }

  const handleGroupToggle = (groupId) => {
    const groupIdStr = groupId.toString()
    setFormData(prev => {
      const currentIds = prev.group_ids.map(id => id.toString())
      if (currentIds.includes(groupIdStr)) {
        return {
          ...prev,
          group_ids: prev.group_ids.filter(id => id.toString() !== groupIdStr)
        }
      } else {
        return {
          ...prev,
          group_ids: [...prev.group_ids, groupId]
        }
      }
    })
  }

  const connectedAccounts = accounts.filter(acc => acc.connected)

  // Setze Standard-Zeit auf jetzt + 1 Minute
  const getDefaultTime = () => {
    const now = new Date()
    now.setMinutes(now.getMinutes() + 1)
    return now.toISOString().slice(0, 16)
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Geplante Nachrichten</h2>
        <button
          className="btn btn-primary"
          onClick={() => {
            setFormData({
              ...formData,
              scheduled_time: getDefaultTime()
            })
            setShowModal(true)
          }}
          disabled={connectedAccounts.length === 0 || groups.length === 0}
        >
          + Neue geplante Nachricht
        </button>
      </div>

      {connectedAccounts.length === 0 && (
        <div className="alert alert-warning">
          Keine verbundenen Accounts vorhanden. Bitte zuerst einen Account verbinden.
        </div>
      )}

      {groups.length === 0 && (
        <div className="alert alert-warning">
          Keine Gruppen vorhanden. Bitte zuerst Gruppen hinzufügen.
        </div>
      )}

      {scheduledMessages.length === 0 ? (
        <div className="empty-state">
          <p>Keine geplanten Nachrichten. Erstelle eine neue geplante Nachricht.</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Gruppe</th>
              <th>Nachricht</th>
              <th>Geplant für</th>
              <th>Wiederholungen</th>
              <th>Status</th>
              <th>Ergebnis</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {scheduledMessages.map(msg => (
              <tr key={msg.id}>
                <td>{getAccountName(msg.account_id)}</td>
                <td>
                  {Array.isArray(msg.group_ids) ? (
                    <span title={getGroupNames(msg.group_ids)}>
                      {msg.group_ids.length} Gruppe(n)
                    </span>
                  ) : (
                    getGroupName(msg.group_id || msg.group_ids)
                  )}
                </td>
                <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {msg.message.substring(0, 50)}{msg.message.length > 50 ? '...' : ''}
                </td>
                <td>
                  {format(new Date(msg.scheduled_time), 'dd.MM.yyyy HH:mm')}
                </td>
                <td>{msg.repeat_count}x</td>
                <td>
                  <span className={`badge ${getStatusBadge(msg.status)}`}>
                    {msg.status}
                  </span>
                </td>
                <td>
                  {msg.status === 'completed' && (
                    <span className="badge badge-success">
                      {msg.sent_count} gesendet
                    </span>
                  )}
                  {msg.status === 'failed' && (
                    <span className="badge badge-danger">
                      {msg.failed_count} fehlgeschlagen
                    </span>
                  )}
                  {msg.status === 'running' && (
                    <span className="badge badge-info">
                      Läuft...
                    </span>
                  )}
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    {msg.status === 'pending' && (
                      <button
                        className="btn btn-danger btn-small"
                        onClick={() => handleCancel(msg.id)}
                      >
                        Abbrechen
                      </button>
                    )}
                    <button
                      className="btn btn-secondary btn-small"
                      onClick={() => {
                        const firstGroupId = Array.isArray(msg.group_ids) ? msg.group_ids[0] : (msg.group_id || msg.group_ids)
                        handleTest(msg.account_id, firstGroupId, msg.message)
                      }}
                    >
                      Test
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Neue geplante Nachricht</h3>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Account</label>
                <select
                  required
                  value={formData.account_id}
                  onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                >
                  <option value="">Bitte wählen...</option>
                  {connectedAccounts.map(acc => (
                    <option key={acc.id} value={acc.id}>
                      {acc.name} 
                      {acc.account_type === 'bot' ? ' [BOT]' : ''}
                      {acc.info && ` (@${acc.info.username || 'N/A'})`}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Gruppen (mehrere auswählbar)</label>
                <div style={{ 
                  border: '2px solid #e0e0e0', 
                  borderRadius: '5px', 
                  padding: '10px', 
                  maxHeight: '200px', 
                  overflowY: 'auto',
                  backgroundColor: '#f8f9fa'
                }}>
                  {groups.length === 0 ? (
                    <p style={{ color: '#999', margin: 0 }}>Keine Gruppen verfügbar</p>
                  ) : (
                    groups.map(group => (
                      <label key={group.id} style={{ 
                        display: 'block', 
                        padding: '8px',
                        cursor: 'pointer',
                        borderRadius: '3px',
                        marginBottom: '5px',
                        backgroundColor: formData.group_ids.includes(group.id) ? '#e3f2fd' : 'transparent'
                      }}>
                        <input
                          type="checkbox"
                          checked={formData.group_ids.includes(group.id)}
                          onChange={() => handleGroupToggle(group.id)}
                          style={{ marginRight: '8px' }}
                        />
                        {group.name} ({group.chat_type})
                      </label>
                    ))
                  )}
                </div>
                {formData.group_ids.length > 0 && (
                  <p style={{ marginTop: '5px', fontSize: '0.9rem', color: '#667eea' }}>
                    {formData.group_ids.length} Gruppe(n) ausgewählt
                  </p>
                )}
              </div>
              <div className="form-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                  <label>Nachricht</label>
                  <button
                    type="button"
                    className="btn btn-secondary btn-small"
                    onClick={() => setShowTemplates(true)}
                  >
                    📋 Vorlagen
                  </button>
                </div>
                <textarea
                  required
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Nachrichtentext..."
                  rows="4"
                />
              </div>
              <div className="form-group">
                <label>Geplant für</label>
                <input
                  type="datetime-local"
                  required
                  value={formData.scheduled_time}
                  onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                  min={new Date().toISOString().slice(0, 16)}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Wiederholungen</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="1000"
                    value={formData.repeat_count}
                    onChange={(e) => setFormData({ ...formData, repeat_count: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Delay (Sekunden)</label>
                  <input
                    type="number"
                    required
                    min="0.1"
                    max="60"
                    step="0.1"
                    value={formData.delay}
                    onChange={(e) => setFormData({ ...formData, delay: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Batch-Größe</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="100"
                    value={formData.batch_size}
                    onChange={(e) => setFormData({ ...formData, batch_size: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Batch-Delay (Sekunden)</label>
                  <input
                    type="number"
                    required
                    min="0"
                    max="300"
                    step="0.1"
                    value={formData.batch_delay}
                    onChange={(e) => setFormData({ ...formData, batch_delay: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Gruppen-Delay (Sekunden zwischen verschiedenen Gruppen)</label>
                <input
                  type="number"
                  required
                  min="0"
                  max="300"
                  step="0.1"
                  value={formData.group_delay}
                  onChange={(e) => setFormData({ ...formData, group_delay: e.target.value })}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading || formData.group_ids.length === 0}>
                  {loading ? 'Erstelle...' : 'Erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showTemplates && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content" style={{ maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>Nachrichtenvorlagen</h3>
              <button className="close-btn" onClick={() => setShowTemplates(false)}>×</button>
            </div>
            <MessageTemplates
              onTemplateSelect={(template) => {
                setFormData({ ...formData, message: template.message })
                setShowTemplates(false)
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

