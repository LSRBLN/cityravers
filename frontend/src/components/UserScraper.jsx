import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function UserScraper({ accounts, groups, onUpdate }) {
  const [scrapedUsers, setScrapedUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [inviting, setInviting] = useState(false)
  const [selectedUsers, setSelectedUsers] = useState([])
  const [scrapeAccountGroups, setScrapeAccountGroups] = useState([])  // Gruppen des ausgewählten Scraping-Accounts
  const [inviteAccountGroups, setInviteAccountGroups] = useState([])  // Gruppen des ausgewählten Einladungs-Accounts
  const [loadingScrapeGroups, setLoadingScrapeGroups] = useState(false)
  const [loadingInviteGroups, setLoadingInviteGroups] = useState(false)
  const [scrapeConfig, setScrapeConfig] = useState({
    account_id: '',
    group_id: '',
    limit: 1000
  })
  const [inviteConfig, setInviteConfig] = useState({
    account_id: '',
    target_group_id: '',
    delay: 2.0,
    invite_method: 'admin'  // 'admin' oder 'invite_link'
  })
  const [usernameList, setUsernameList] = useState('')  // Username-Liste (eine pro Zeile)

  const handleScrape = async () => {
    if (!scrapeConfig.account_id || !scrapeConfig.group_id) {
      alert('Bitte Account und Gruppe auswählen')
      return
    }
    
    setScraping(true)
    try {
      // Verwende chat_id direkt, wenn es aus accountGroups kommt
      const groupEntity = scrapeConfig.group_id
      
      const response = await axios.post(`${API_BASE}/scrape/group-members`, {
        account_id: parseInt(scrapeConfig.account_id),
        group_entity: groupEntity,  // Chat-ID oder Username
        limit: parseInt(scrapeConfig.limit)
      })
      
      alert(`Scraping abgeschlossen!\n✅ Gescrapt: ${response.data.scraped}\n💾 Gespeichert: ${response.data.saved}`)
      
      // Lade gescrapte User
      await loadScrapedUsers()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setScraping(false)
    }
  }

  const loadScrapedUsers = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/scraped-users`)
      setScrapedUsers(response.data)
    } catch (error) {
      console.error('Fehler beim Laden:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInvite = async () => {
    if (!inviteConfig.account_id || !inviteConfig.target_group_id) {
      alert('Bitte Account und Ziel-Gruppe auswählen')
      return
    }
    
    // Prüfe ob Username-Liste oder gescrapte User ausgewählt
    const hasUsernameList = usernameList.trim().length > 0
    const hasSelectedUsers = selectedUsers.length > 0
    
    if (!hasUsernameList && !hasSelectedUsers) {
      alert('Bitte mindestens einen User auswählen oder Username-Liste eingeben')
      return
    }
    
    let userCount = 0
    if (hasUsernameList) {
      const usernames = usernameList.split('\n').filter(u => u.trim().length > 0)
      userCount = usernames.length
    } else {
      userCount = selectedUsers.length
    }
    
    if (!confirm(`Wirklich ${userCount} User einladen?`)) {
      return
    }
    
    setInviting(true)
    try {
      let response
      
      if (hasUsernameList) {
        // Verwende Username-Liste
        const usernames = usernameList.split('\n')
          .map(u => u.trim())
          .filter(u => u.length > 0)
        
        // Verwende chat_id direkt, wenn es aus accountGroups kommt
        const groupEntity = inviteConfig.target_group_id
        
        response = await axios.post(`${API_BASE}/invite/users`, {
          account_id: parseInt(inviteConfig.account_id),
          group_entity: groupEntity,  // Chat-ID oder Username
          usernames: usernames,
          delay: parseFloat(inviteConfig.delay),
          invite_method: inviteConfig.invite_method
        })
      } else {
        // Verwende gescrapte User
        response = await axios.post(`${API_BASE}/invite/from-scraped`, {
          account_id: parseInt(inviteConfig.account_id),
          group_id: parseInt(inviteConfig.target_group_id),
          scraped_user_ids: selectedUsers,
          delay: parseFloat(inviteConfig.delay)
        })
      }
      
      // Prüfe ob die Antwort ein Error-Feld hat (bei Fehler)
      // Backend gibt bei Fehler: {"success": false, "error": "..."}
      // Backend gibt bei Erfolg: {"success": 0, "failed": 0, "total": X, ...}
      if (response.data.error || (response.data.success === false)) {
        alert(`Fehler: ${response.data.error || 'Unbekannter Fehler'}`)
        return
      }
      
      // Normale Antwort-Struktur (success ist hier eine Zahl, nicht Boolean)
      const successCount = typeof response.data.success === 'number' ? response.data.success : 0
      const failedCount = typeof response.data.failed === 'number' ? response.data.failed : 0
      const totalCount = typeof response.data.total === 'number' ? response.data.total : 0
      
      let message = `Einladungen abgeschlossen!\n✅ Erfolgreich: ${successCount}\n❌ Fehlgeschlagen: ${failedCount}`
      
      if (totalCount > 0) {
        message += `\n📊 Gesamt: ${totalCount}`
      }
      
      if (response.data.invite_link) {
        message += `\n\n🔗 Einladungslink: ${response.data.invite_link}`
      }
      
      if (response.data.errors && Array.isArray(response.data.errors) && response.data.errors.length > 0) {
        message += `\n\n⚠️ ${response.data.errors.length} Fehler aufgetreten (siehe Konsole)`
        console.log('Detaillierte Fehler:', response.data.errors)
      }
      
      alert(message)
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setInviting(false)
    }
  }

  const handleUserToggle = (userId) => {
    setSelectedUsers(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId)
      } else {
        return [...prev, userId]
      }
    })
  }

  const handleSelectAll = () => {
    if (selectedUsers.length === scrapedUsers.length) {
      setSelectedUsers([])
    } else {
      setSelectedUsers(scrapedUsers.map(u => u.id))
    }
  }

  // Lade Gruppen eines Accounts für Scraping
  const loadScrapeAccountGroups = async (accountId) => {
    if (!accountId) {
      setScrapeAccountGroups([])
      return
    }
    
    const account = accounts.find(acc => acc.id === parseInt(accountId))
    if (!account || !account.connected) {
      setScrapeAccountGroups([])
      return
    }
    
    setLoadingScrapeGroups(true)
    try {
      const response = await axios.get(`${API_BASE}/accounts/${accountId}/groups`)
      setScrapeAccountGroups(response.data)
    } catch (error) {
      console.error('Fehler beim Laden der Gruppen:', error)
      setScrapeAccountGroups([])
    } finally {
      setLoadingScrapeGroups(false)
    }
  }

  // Lade Gruppen eines Accounts für Einladung
  const loadInviteAccountGroups = async (accountId) => {
    if (!accountId) {
      setInviteAccountGroups([])
      return
    }
    
    const account = accounts.find(acc => acc.id === parseInt(accountId))
    if (!account || !account.connected) {
      setInviteAccountGroups([])
      return
    }
    
    setLoadingInviteGroups(true)
    try {
      const response = await axios.get(`${API_BASE}/accounts/${accountId}/groups`)
      setInviteAccountGroups(response.data)
    } catch (error) {
      console.error('Fehler beim Laden der Gruppen:', error)
      setInviteAccountGroups([])
    } finally {
      setLoadingInviteGroups(false)
    }
  }

  // Lade Gruppen, wenn Account für Scraping ausgewählt wird
  React.useEffect(() => {
    if (scrapeConfig.account_id) {
      loadScrapeAccountGroups(scrapeConfig.account_id)
    } else {
      setScrapeAccountGroups([])
    }
  }, [scrapeConfig.account_id])

  // Lade Gruppen, wenn Account für Einladung ausgewählt wird
  React.useEffect(() => {
    if (inviteConfig.account_id) {
      loadInviteAccountGroups(inviteConfig.account_id)
    } else {
      setInviteAccountGroups([])
    }
  }, [inviteConfig.account_id])

  React.useEffect(() => {
    loadScrapedUsers()
  }, [])

  const connectedUserAccounts = accounts.filter(acc => acc.connected && acc.account_type === 'user')

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>User-Scraping</h2>
          <button className="btn btn-secondary" onClick={loadScrapedUsers}>
            🔄 Aktualisieren
          </button>
        </div>

        <div className="alert alert-warning">
          <strong>⚠️ WARNUNG:</strong> User-Scraping und Masseneinladungen können gegen Telegram Nutzungsbedingungen verstoßen 
          und zu Account-Sperrungen führen. Nur für legitime Zwecke verwenden!
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
          <div>
            <h3 style={{ marginBottom: '15px', color: '#667eea' }}>Gruppe scrapen</h3>
            <div className="form-group">
              <label>Account</label>
              <select
                value={scrapeConfig.account_id}
                onChange={(e) => setScrapeConfig({ ...scrapeConfig, account_id: e.target.value })}
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
                value={scrapeConfig.group_id}
                onChange={(e) => setScrapeConfig({ ...scrapeConfig, group_id: e.target.value })}
                disabled={loadingScrapeGroups || !scrapeConfig.account_id}
              >
                <option value="">Bitte wählen...</option>
                {loadingScrapeGroups ? (
                  <option value="" disabled>Lade Gruppen...</option>
                ) : scrapeAccountGroups.length > 0 ? (
                  scrapeAccountGroups.map(group => (
                    <option key={group.id} value={group.chat_id}>
                      {group.name} {group.username ? `(@${group.username})` : ''}
                    </option>
                  ))
                ) : scrapeConfig.account_id ? (
                  <option value="" disabled>Keine Gruppen gefunden</option>
                ) : (
                  groups.map(group => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))
                )}
              </select>
              {scrapeConfig.account_id && !loadingScrapeGroups && scrapeAccountGroups.length === 0 && (
                <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                  Keine Gruppen für diesen Account gefunden. Stelle sicher, dass der Account verbunden ist.
                </small>
              )}
            </div>
            <div className="form-group">
              <label>Limit (max. User)</label>
              <input
                type="number"
                min="1"
                max="100000"
                value={scrapeConfig.limit}
                onChange={(e) => setScrapeConfig({ ...scrapeConfig, limit: e.target.value })}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={handleScrape}
              disabled={scraping || !scrapeConfig.account_id || !scrapeConfig.group_id}
            >
              {scraping ? 'Scrape läuft...' : '🚀 Gruppe scrapen'}
            </button>
          </div>

          <div>
            <h3 style={{ marginBottom: '15px', color: '#667eea' }}>User einladen</h3>
            <div className="form-group">
              <label>Account (muss Admin sein)</label>
              <select
                value={inviteConfig.account_id}
                onChange={(e) => setInviteConfig({ ...inviteConfig, account_id: e.target.value })}
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
              <label>Ziel-Gruppe</label>
              <select
                value={inviteConfig.target_group_id}
                onChange={(e) => setInviteConfig({ ...inviteConfig, target_group_id: e.target.value })}
                disabled={loadingInviteGroups || !inviteConfig.account_id}
              >
                <option value="">Bitte wählen...</option>
                {loadingInviteGroups ? (
                  <option value="" disabled>Lade Gruppen...</option>
                ) : inviteAccountGroups.length > 0 ? (
                  inviteAccountGroups.map(group => (
                    <option key={group.id} value={group.chat_id}>
                      {group.name} {group.username ? `(@${group.username})` : ''}
                    </option>
                  ))
                ) : inviteConfig.account_id ? (
                  <option value="" disabled>Keine Gruppen gefunden</option>
                ) : (
                  groups.map(group => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))
                )}
              </select>
              {inviteConfig.account_id && !loadingInviteGroups && inviteAccountGroups.length === 0 && (
                <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                  Keine Gruppen für diesen Account gefunden. Stelle sicher, dass der Account verbunden ist.
                </small>
              )}
            </div>
            <div className="form-group">
              <label>Einladungsmethode</label>
              <select
                value={inviteConfig.invite_method}
                onChange={(e) => setInviteConfig({ ...inviteConfig, invite_method: e.target.value })}
              >
                <option value="admin">Als Admin einladen (direkt)</option>
                <option value="invite_link">Invite-Link erstellen und per DM senden</option>
              </select>
              <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                {inviteConfig.invite_method === 'admin' 
                  ? 'Direkte Einladung als Admin (Account muss Admin-Rechte haben)'
                  : 'Erstellt einen Einladungslink und sendet diesen per DM an alle User'}
              </small>
            </div>
            <div className="form-group">
              <label>Username-Liste (eine pro Zeile, mit oder ohne @)</label>
              <textarea
                rows="5"
                placeholder="username1&#10;username2&#10;@username3&#10;..."
                value={usernameList}
                onChange={(e) => setUsernameList(e.target.value)}
                style={{ width: '100%', fontFamily: 'monospace', fontSize: '14px' }}
              />
              <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                Alternativ: Wähle gescrapte User aus der Liste unten aus
              </small>
            </div>
            <div className="form-group">
              <label>Delay zwischen Einladungen (Sekunden)</label>
              <input
                type="number"
                min="1"
                max="60"
                step="0.1"
                value={inviteConfig.delay}
                onChange={(e) => setInviteConfig({ ...inviteConfig, delay: e.target.value })}
              />
            </div>
            <button
              className="btn btn-success"
              onClick={handleInvite}
              disabled={
                inviting || 
                (!usernameList.trim() && selectedUsers.length === 0) || 
                !inviteConfig.account_id || 
                !inviteConfig.target_group_id
              }
            >
              {inviting ? 'Lade ein...' : (
                `📨 ${usernameList.trim() 
                  ? usernameList.split('\n').filter(u => u.trim()).length 
                  : selectedUsers.length} User einladen`
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Gescrapte User ({scrapedUsers.length})</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className="btn btn-secondary btn-small"
              onClick={handleSelectAll}
            >
              {selectedUsers.length === scrapedUsers.length ? 'Alle abwählen' : 'Alle auswählen'}
            </button>
            <span className="badge badge-info">
              {selectedUsers.length} ausgewählt
            </span>
          </div>
        </div>

        {loading ? (
          <div className="loading">Lade User...</div>
        ) : scrapedUsers.length === 0 ? (
          <div className="empty-state">
            <p>Keine gescrapten User vorhanden. Scrape zuerst eine Gruppe.</p>
          </div>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={selectedUsers.length === scrapedUsers.length && scrapedUsers.length > 0}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th>Username</th>
                  <th>Name</th>
                  <th>Telefon</th>
                  <th>Quelle</th>
                  <th>Gescrapt</th>
                </tr>
              </thead>
              <tbody>
                {scrapedUsers.map(user => (
                  <tr key={user.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.id)}
                        onChange={() => handleUserToggle(user.id)}
                      />
                    </td>
                    <td>@{user.username || 'N/A'}</td>
                    <td>{user.first_name} {user.last_name || ''}</td>
                    <td>{user.phone || '-'}</td>
                    <td>{user.source_group_name || '-'}</td>
                    <td>
                      {user.scraped_at ? new Date(user.scraped_at).toLocaleDateString('de-DE') : '-'}
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

