import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function GroupManager({ groups, accounts, onUpdate }) {
  const [showModal, setShowModal] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [dialogs, setDialogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    chat_id: '',
    chat_type: 'group',
    username: ''
  })
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [bulkGroupNames, setBulkGroupNames] = useState('')
  const [bulkAccountId, setBulkAccountId] = useState('')
  const [showCheckModal, setShowCheckModal] = useState(false)
  const [checkFormData, setCheckFormData] = useState({
    account_id: '',
    group_entity: '',
    bot_username: ''
  })
  const [checkResult, setCheckResult] = useState(null)

  const handleLoadDialogs = async (accountId) => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/accounts/${accountId}/dialogs`)
      setDialogs(response.data)
      setSelectedAccount(accountId)
      setShowModal(true)
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleAddFromDialog = async (dialog) => {
    try {
      await axios.post(`${API_BASE}/groups`, {
        name: dialog.name,
        chat_id: dialog.id.toString(),
        chat_type: dialog.type,
        username: dialog.username
      })
      setShowModal(false)
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleManualAdd = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await axios.post(`${API_BASE}/groups`, formData)
      setShowModal(false)
      setFormData({ name: '', chat_id: '', chat_type: 'group', username: '' })
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (groupId) => {
    if (!confirm('Gruppe wirklich löschen?')) return
    
    try {
      await axios.delete(`${API_BASE}/groups/${groupId}`)
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleBulkImportGroups = async () => {
    if (!bulkGroupNames.trim()) {
      alert('Bitte Gruppennamen eingeben')
      return
    }
    
    if (!bulkAccountId) {
      alert('Bitte Account auswählen')
      return
    }
    
    setLoading(true)
    try {
      // Parse Text: eine Gruppe pro Zeile
      const groupNames = bulkGroupNames
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
      
      if (groupNames.length === 0) {
        alert('Keine Gruppennamen gefunden')
        return
      }
      
      const response = await axios.post(`${API_BASE}/groups/search-by-name`, {
        account_id: parseInt(bulkAccountId),
        group_names: groupNames
      })
      
      const added = response.data.filter(r => r.status === 'added').length
      const exists = response.data.filter(r => r.status === 'exists').length
      const notFound = response.data.filter(r => r.status === 'not_found').length
      
      alert(`Import abgeschlossen:\n✅ Neu hinzugefügt: ${added}\n⚠️ Bereits vorhanden: ${exists}\n❌ Nicht gefunden: ${notFound}`)
      
      if (notFound > 0) {
        const notFoundNames = response.data
          .filter(r => r.status === 'not_found')
          .map(r => r.name)
          .join(', ')
        console.log('Nicht gefundene Gruppen:', notFoundNames)
      }
      
      setShowBulkModal(false)
      setBulkGroupNames('')
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const connectedAccounts = accounts.filter(acc => acc.connected)

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Gruppen-Verwaltung</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            {connectedAccounts.filter(acc => acc.account_type === 'user').length > 0 && (
              <button 
                className="btn btn-info" 
                onClick={() => {
                  const userAccounts = accounts.filter(acc => acc.account_type === 'user' && acc.connected)
                  if (userAccounts.length === 0) {
                    alert('Keine verbundenen User-Accounts vorhanden.')
                    return
                  }
                  setCheckFormData({
                    account_id: userAccounts[0].id.toString(),
                    group_entity: '',
                    bot_username: ''
                  })
                  setCheckResult(null)
                  setShowCheckModal(true)
                }}
                title="Prüfe Gruppen-Existenz und Bot-Hinzufügungs-Möglichkeit"
              >
                🔍 Prüfen
              </button>
            )}
            {connectedAccounts.length > 0 && (
              <>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    if (connectedAccounts.length > 0) {
                      setBulkAccountId(connectedAccounts[0].id.toString())
                    }
                    setShowBulkModal(true)
                  }}
                >
                  📋 Bulk-Import (Namen)
                </button>
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    handleLoadDialogs(parseInt(e.target.value))
                  }
                }}
                style={{ padding: '10px', borderRadius: '5px', border: '2px solid #e0e0e0' }}
              >
                <option value="">Dialoge laden von...</option>
                {connectedAccounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name}
                  </option>
                ))}
              </select>
            </>
          )}
          <button
            className="btn btn-primary"
            onClick={() => {
              setShowModal(true)
              setDialogs([])
            }}
          >
            + Manuell hinzufügen
          </button>
        </div>
      </div>

      {groups.length === 0 ? (
        <div className="empty-state">
          <p>Keine Gruppen vorhanden. Lade Dialoge von einem Account oder füge manuell hinzu.</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Chat-ID</th>
              <th>Typ</th>
              <th>Username</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {groups.map(group => (
              <tr key={group.id}>
                <td>{group.name}</td>
                <td>{group.chat_id}</td>
                <td>
                  <span className="badge badge-info">{group.chat_type || 'group'}</span>
                </td>
                <td>@{group.username || '-'}</td>
                <td>
                  <button
                    className="btn btn-danger btn-small"
                    onClick={() => handleDelete(group.id)}
                  >
                    Löschen
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h3>{dialogs.length > 0 ? 'Dialoge auswählen' : 'Gruppe manuell hinzufügen'}</h3>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>

            {dialogs.length > 0 ? (
              <div>
                <p style={{ marginBottom: '15px' }}>Wähle eine Gruppe aus:</p>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Typ</th>
                        <th>ID</th>
                        <th>Aktion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dialogs.map(dialog => (
                        <tr key={dialog.id}>
                          <td>{dialog.name}</td>
                          <td>
                            <span className="badge badge-info">{dialog.type}</span>
                          </td>
                          <td>{dialog.id}</td>
                          <td>
                            <button
                              className="btn btn-success btn-small"
                              onClick={() => handleAddFromDialog(dialog)}
                            >
                              Hinzufügen
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <form onSubmit={handleManualAdd}>
                <div className="form-group">
                  <label>Gruppen-Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="z.B. Meine Gruppe"
                  />
                </div>
                <div className="form-group">
                  <label>Chat-ID</label>
                  <input
                    type="text"
                    required
                    value={formData.chat_id}
                    onChange={(e) => setFormData({ ...formData, chat_id: e.target.value })}
                    placeholder="z.B. -1001234567890 oder @username"
                  />
                </div>
                <div className="form-group">
                  <label>Typ</label>
                  <select
                    value={formData.chat_type}
                    onChange={(e) => setFormData({ ...formData, chat_type: e.target.value })}
                  >
                    <option value="group">Gruppe</option>
                    <option value="channel">Kanal</option>
                    <option value="supergroup">Supergruppe</option>
                    <option value="private">Privat</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Username (optional)</label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="@username"
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
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Hinzufügen...' : 'Hinzufügen'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {showBulkModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Bulk-Import Gruppen (nach Namen)</h3>
              <button className="close-btn" onClick={() => setShowBulkModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>Account</label>
              <select
                value={bulkAccountId}
                onChange={(e) => setBulkAccountId(e.target.value)}
                required
              >
                <option value="">Bitte wählen...</option>
                {connectedAccounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} {acc.account_type === 'bot' ? '[BOT]' : ''}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Gruppennamen (eine pro Zeile)</label>
              <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '10px' }}>
                Gib Gruppennamen oder Usernames ein (z.B. "Meine Gruppe" oder "@channelname")
              </p>
              <textarea
                value={bulkGroupNames}
                onChange={(e) => setBulkGroupNames(e.target.value)}
                placeholder={`Meine Gruppe
@channelname
Gruppe 2
@anotherchannel`}
                rows="10"
                style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
              />
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowBulkModal(false)}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleBulkImportGroups}
                disabled={loading || !bulkAccountId}
              >
                {loading ? 'Suche...' : 'Suchen & Hinzufügen'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showCheckModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h3>🔍 Gruppen-Prüfung</h3>
              <button className="close-btn" onClick={() => {
                setShowCheckModal(false)
                setCheckResult(null)
              }}>×</button>
            </div>
            <form onSubmit={async (e) => {
              e.preventDefault()
              if (!checkFormData.account_id || !checkFormData.group_entity) {
                alert('Bitte Account und Gruppe angeben')
                return
              }
              
              setLoading(true)
              setCheckResult(null)
              
              try {
                // Prüfe zuerst Gruppen-Existenz
                const existsResponse = await axios.post(`${API_BASE}/groups/check-exists`, {
                  account_id: parseInt(checkFormData.account_id),
                  group_entity: checkFormData.group_entity
                })
                
                let botCheckResult = null
                if (existsResponse.data.exists && checkFormData.bot_username) {
                  // Prüfe Bot-Hinzufügung
                  botCheckResult = await axios.post(`${API_BASE}/groups/check-bot-can-be-added`, {
                    account_id: parseInt(checkFormData.account_id),
                    group_entity: checkFormData.group_entity,
                    bot_username: checkFormData.bot_username
                  })
                }
                
                setCheckResult({
                  exists: existsResponse.data,
                  botCheck: botCheckResult?.data || null
                })
              } catch (error) {
                alert('Fehler: ' + (error.response?.data?.detail || error.message))
              } finally {
                setLoading(false)
              }
            }}>
              <div className="form-group">
                <label>User-Account (muss verbunden sein)</label>
                <select
                  required
                  value={checkFormData.account_id}
                  onChange={(e) => setCheckFormData({ ...checkFormData, account_id: e.target.value })}
                >
                  <option value="">Account auswählen...</option>
                  {accounts
                    .filter(acc => acc.account_type === 'user' && acc.connected)
                    .map(acc => (
                      <option key={acc.id} value={acc.id}>
                        {acc.name} {acc.info?.username ? `(@${acc.info.username})` : ''}
                      </option>
                    ))}
                </select>
              </div>
              <div className="form-group">
                <label>Gruppe (Chat-ID oder Username)</label>
                <input
                  type="text"
                  required
                  value={checkFormData.group_entity}
                  onChange={(e) => setCheckFormData({ ...checkFormData, group_entity: e.target.value })}
                  placeholder="z.B. @groupname oder -1001234567890"
                />
              </div>
              <div className="form-group">
                <label>Bot-Username (optional - für Bot-Prüfung)</label>
                <input
                  type="text"
                  value={checkFormData.bot_username}
                  onChange={(e) => setCheckFormData({ ...checkFormData, bot_username: e.target.value })}
                  placeholder="z.B. @mybot"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Optional: Prüft ob dieser Bot zur Gruppe hinzugefügt werden kann
                </p>
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowCheckModal(false)
                    setCheckResult(null)
                  }}
                >
                  Schließen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Prüfe...' : 'Prüfen'}
                </button>
              </div>
            </form>

            {checkResult && (
              <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
                <h4>Prüf-Ergebnisse:</h4>
                
                <div style={{ marginTop: '15px' }}>
                  <h5>Gruppen-Existenz:</h5>
                  {checkResult.exists.exists ? (
                    <div style={{ padding: '10px', backgroundColor: '#d4edda', borderRadius: '5px', marginTop: '10px' }}>
                      <p><strong>✅ Gruppe existiert</strong></p>
                      <p><strong>Name:</strong> {checkResult.exists.title || 'N/A'}</p>
                      <p><strong>Typ:</strong> {checkResult.exists.type}</p>
                      {checkResult.exists.username && <p><strong>Username:</strong> @{checkResult.exists.username}</p>}
                      {checkResult.exists.members_count && <p><strong>Mitglieder:</strong> {checkResult.exists.members_count}</p>}
                      <p><strong>ID:</strong> {checkResult.exists.id}</p>
                    </div>
                  ) : (
                    <div style={{ padding: '10px', backgroundColor: '#f8d7da', borderRadius: '5px', marginTop: '10px' }}>
                      <p><strong>❌ Gruppe nicht gefunden</strong></p>
                      <p>{checkResult.exists.error}</p>
                    </div>
                  )}
                </div>

                {checkResult.botCheck && (
                  <div style={{ marginTop: '15px' }}>
                    <h5>Bot-Hinzufügungs-Prüfung:</h5>
                    <div style={{ padding: '10px', backgroundColor: checkResult.botCheck.can_add ? '#d4edda' : '#fff3cd', borderRadius: '5px', marginTop: '10px' }}>
                      <p><strong>{checkResult.botCheck.can_add ? '✅' : '⚠️'} Bot kann {checkResult.botCheck.can_add ? '' : 'nicht '}hinzugefügt werden</strong></p>
                      <p><strong>Gruppe existiert:</strong> {checkResult.botCheck.group_exists ? '✅' : '❌'}</p>
                      <p><strong>Account ist Admin:</strong> {checkResult.botCheck.is_admin ? '✅' : '❌'}</p>
                      {checkResult.botCheck.bot_username && (
                        <>
                          <p><strong>Bot existiert:</strong> {checkResult.botCheck.bot_exists ? '✅' : '❌'}</p>
                          <p><strong>Bot bereits in Gruppe:</strong> {checkResult.botCheck.bot_already_in_group ? '⚠️ Ja' : '✅ Nein'}</p>
                        </>
                      )}
                      {checkResult.botCheck.errors && checkResult.botCheck.errors.length > 0 && (
                        <div style={{ marginTop: '10px' }}>
                          <strong>Fehler:</strong>
                          <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                            {checkResult.botCheck.errors.map((error, idx) => (
                              <li key={idx} style={{ color: '#dc3545' }}>{error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {checkResult.botCheck.message && (
                        <p style={{ marginTop: '10px', color: '#28a745' }}>{checkResult.botCheck.message}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

