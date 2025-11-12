import React, { useState } from 'react'
import axios from 'axios'

const API_BASE = '/api'

export default function UserScraper({ accounts, groups, onUpdate }) {
  const [scrapedUsers, setScrapedUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [inviting, setInviting] = useState(false)
  const [selectedUsers, setSelectedUsers] = useState([])
  const [scrapeConfig, setScrapeConfig] = useState({
    account_id: '',
    group_id: '',
    limit: 1000
  })
  const [inviteConfig, setInviteConfig] = useState({
    account_id: '',
    target_group_id: '',
    delay: 2.0
  })

  const handleScrape = async () => {
    if (!scrapeConfig.account_id || !scrapeConfig.group_id) {
      alert('Bitte Account und Gruppe auswählen')
      return
    }
    
    setScraping(true)
    try {
      const response = await axios.post(`${API_BASE}/scrape/group-members`, {
        account_id: parseInt(scrapeConfig.account_id),
        group_id: parseInt(scrapeConfig.group_id),
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
    
    if (selectedUsers.length === 0) {
      alert('Bitte mindestens einen User auswählen')
      return
    }
    
    if (!confirm(`Wirklich ${selectedUsers.length} User einladen?`)) {
      return
    }
    
    setInviting(true)
    try {
      const response = await axios.post(`${API_BASE}/invite/from-scraped`, {
        account_id: parseInt(inviteConfig.account_id),
        group_id: parseInt(inviteConfig.target_group_id),
        scraped_user_ids: selectedUsers,
        delay: parseFloat(inviteConfig.delay)
      })
      
      alert(`Einladungen abgeschlossen!\n✅ Erfolgreich: ${response.data.success}\n❌ Fehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.log('Fehler:', response.data.errors)
      }
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
              disabled={inviting || selectedUsers.length === 0 || !inviteConfig.account_id || !inviteConfig.target_group_id}
            >
              {inviting ? 'Lade ein...' : `📨 ${selectedUsers.length} User einladen`}
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

