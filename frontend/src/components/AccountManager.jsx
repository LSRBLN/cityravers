import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function AccountManager({ accounts, proxies = [], onUpdate }) {
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    account_type: 'user',  // 'user' oder 'bot'
    api_id: '',
    api_hash: '',
    bot_token: '',
    phone_number: '',
    session_name: '',
    proxy_id: ''
  })
  const [loginData, setLoginData] = useState({})
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [loginAccountId, setLoginAccountId] = useState(null)
  const [loginCode, setLoginCode] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginStep, setLoginStep] = useState('code') // 'code' oder 'password'
  const [loginLoading, setLoginLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [bulkBotsText, setBulkBotsText] = useState('')
  const [showSessionModal, setShowSessionModal] = useState(false)
  const [showTdataModal, setShowTdataModal] = useState(false)
  const [sessionFile, setSessionFile] = useState(null)
  const [sessionFilePath, setSessionFilePath] = useState('')
  const [tdataFiles, setTdataFiles] = useState([])
  const [tdataPath, setTdataPath] = useState('')
  const [sessionFormData, setSessionFormData] = useState({
    name: '',
    api_id: '',
    api_hash: ''
  })
  const [tdataFormData, setTdataFormData] = useState({
    name: '',
    api_id: '',
    api_hash: ''
  })
  const [showCreateBotModal, setShowCreateBotModal] = useState(false)
  const [createBotFormData, setCreateBotFormData] = useState({
    account_id: '',
    bot_name: '',
    bot_username: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // Prüfe ob Token vorhanden ist
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Fehler: Kein Token vorhanden. Bitte erneut einloggen.')
        setLoading(false)
        return
      }
      
      const submitData = {
        ...formData,
        proxy_id: formData.proxy_id ? parseInt(formData.proxy_id) : null
      }
      // Interceptor fügt Token automatisch hinzu
      const response = await axios.post(`${API_BASE}/accounts`, submitData)
      
      if (response.data.status === 'code_required') {
        // Code wurde automatisch angefordert beim Erstellen
        // Öffne Login-Modal für Code-Eingabe
        setLoginAccountId(response.data.account_id)
        setLoginStep('code')
        setLoginCode('')
        setLoginPassword('')
        setShowLoginModal(true)
        setShowModal(false) // Schließe Account-Erstellungs-Modal
        alert('✅ Code wurde an deine Telefonnummer gesendet. Prüfe Telegram!')
      } else if (response.data.status === 'password_required') {
        // 2FA erforderlich - öffne Login-Modal für Passwort
        setLoginAccountId(response.data.account_id)
        setLoginStep('password')
        setLoginCode('')
        setLoginPassword('')
        setShowLoginModal(true)
        setShowModal(false) // Schließe Account-Erstellungs-Modal
        alert('⚠️ Zwei-Faktor-Authentifizierung aktiviert. Bitte Passwort eingeben.')
      } else if (response.data.status === 'connected') {
        // Account wurde erfolgreich erstellt und ist bereits verbunden
        setShowModal(false)
        setFormData({ name: '', account_type: 'user', api_id: '', api_hash: '', bot_token: '', phone_number: '', session_name: '', proxy_id: '' })
        alert('✅ Account erfolgreich erstellt und verbunden!')
        onUpdate()
      } else {
        // Unbekannter Status
        setShowModal(false)
        setFormData({ name: '', account_type: 'user', api_id: '', api_hash: '', bot_token: '', phone_number: '', session_name: '', proxy_id: '' })
        onUpdate()
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleRequestCode = async (accountId) => {
    setLoginAccountId(accountId)
    setLoginStep('code')
    setLoginCode('')
    setLoginPassword('')
    setShowLoginModal(true)
    setLoginLoading(true)
    
    try {
      // Versuche Verbindung - wenn Session nicht autorisiert, wird Code angefordert
      const response = await axios.post(`${API_BASE}/accounts/${accountId}/request-code`)
      
      if (response.data.status === 'code_required') {
        // Code wurde angefordert, Modal ist bereits offen
        alert('✅ Code wurde an deine Telefonnummer gesendet. Prüfe Telegram!')
      } else if (response.data.status === 'connected') {
        alert('✅ Account ist bereits verbunden!')
        setShowLoginModal(false)
        onUpdate()
      }
    } catch (error) {
      // Wenn Endpunkt nicht existiert, versuche direkt Login
      if (error.response?.status === 404) {
        // Endpunkt existiert nicht, versuche direkt Login
        // Das Modal ist bereits offen, Benutzer kann Code eingeben
      } else {
        alert('Fehler: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoginLoading(false)
    }
  }

  const handleLogin = async (accountId) => {
    setLoginAccountId(accountId)
    setLoginStep('code')
    setLoginCode('')
    setLoginPassword('')
    setShowLoginModal(true)
    setLoginLoading(true)
    
    // Automatisch Code anfordern beim Öffnen des Modals
    try {
      const response = await axios.post(`${API_BASE}/accounts/${accountId}/request-code`)
      
      if (response.data.status === 'code_required') {
        // Code wurde angefordert
        // Kein Alert, da Modal bereits offen ist
      } else if (response.data.status === 'connected') {
        alert('✅ Account ist bereits verbunden!')
        setShowLoginModal(false)
        onUpdate()
      }
    } catch (error) {
      // Wenn Endpunkt nicht existiert oder Fehler, zeige Fehler
      if (error.response?.status !== 404) {
        alert('Fehler beim Anfordern des Codes: ' + (error.response?.data?.detail || error.message))
      }
      // Bei 404: Endpunkt existiert nicht, aber Modal bleibt offen für manuelle Eingabe
    } finally {
      setLoginLoading(false)
    }
  }

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    if (!loginAccountId) return
    
    setLoginLoading(true)
    
    try {
      const loginPayload = {
        account_id: loginAccountId
      }
      
      if (loginStep === 'code' && loginCode) {
        loginPayload.code = loginCode
      } else if (loginStep === 'password' && loginPassword) {
        loginPayload.password = loginPassword
      } else {
        // Wenn kein Code vorhanden ist, fordere einen an
        if (loginStep === 'code' && !loginCode) {
          try {
            const codeResponse = await axios.post(`${API_BASE}/accounts/${loginAccountId}/request-code`)
            if (codeResponse.data.status === 'code_required') {
              alert('✅ Code wurde an deine Telefonnummer gesendet. Prüfe Telegram!')
            }
          } catch (codeError) {
            alert('Fehler beim Anfordern des Codes: ' + (codeError.response?.data?.detail || codeError.message))
          }
        } else {
          alert('Bitte Code oder Passwort eingeben')
        }
        setLoginLoading(false)
        return
      }
      
      const response = await axios.post(`${API_BASE}/accounts/${loginAccountId}/login`, loginPayload)
      
      if (response.data.status === 'connected') {
        alert('✅ Erfolgreich eingeloggt!')
        setShowLoginModal(false)
        setLoginCode('')
        setLoginPassword('')
        setLoginAccountId(null)
        onUpdate()
      } else if (response.data.status === 'password_required') {
        setLoginStep('password')
        alert('⚠️ Zwei-Faktor-Authentifizierung aktiviert. Bitte Passwort eingeben.')
      } else if (response.data.status === 'code_required') {
        // Code wurde erneut angefordert (z.B. weil der alte Code ungültig war)
        setLoginCode('') // Lösche alten Code
        alert('⚠️ Code wurde erneut angefordert. Prüfe Telegram!')
      } else {
        alert('Fehler: ' + (response.data.error || response.data.status || 'Unbekannter Fehler'))
      }
    } catch (error) {
      // Wenn der Code ungültig ist, könnte das Backend einen Fehler zurückgeben
      // In diesem Fall fordern wir einen neuen Code an
      if (error.response?.status === 400 || error.response?.status === 401) {
        const errorDetail = error.response?.data?.detail || error.message
        if (errorDetail.toLowerCase().includes('code') || errorDetail.toLowerCase().includes('invalid')) {
          try {
            const codeResponse = await axios.post(`${API_BASE}/accounts/${loginAccountId}/request-code`)
            if (codeResponse.data.status === 'code_required') {
              setLoginCode('') // Lösche alten Code
              alert('⚠️ Code ungültig. Neuer Code wurde angefordert. Prüfe Telegram!')
            }
          } catch (codeError) {
            alert('Fehler: ' + errorDetail + '\n\nFehler beim Anfordern eines neuen Codes: ' + (codeError.response?.data?.detail || codeError.message))
          }
        } else {
          alert('Fehler: ' + errorDetail)
        }
      } else {
        alert('Fehler: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoginLoading(false)
    }
  }

  const handleDelete = async (accountId) => {
    if (!confirm('Account wirklich löschen?')) return
    
    try {
      await axios.delete(`${API_BASE}/accounts/${accountId}`)
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleLoadDialogs = async (accountId) => {
    try {
      const response = await axios.get(`${API_BASE}/accounts/${accountId}/dialogs`)
      console.log('Dialoge:', response.data)
      alert(`${response.data.length} Dialoge gefunden. Siehe Konsole für Details.`)
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleBulkImportBots = async () => {
    if (!bulkBotsText.trim()) {
      alert('Bitte Bot-Liste eingeben')
      return
    }
    
    setLoading(true)
    try {
      // Parse Text: Format: "Name:Token" oder "Name Token" pro Zeile
      const lines = bulkBotsText.split('\n').filter(line => line.trim())
      const bots = []
      
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed) continue
        
        // Versuche verschiedene Formate
        let name, token
        if (trimmed.includes(':')) {
          const parts = trimmed.split(':')
          name = parts[0].trim()
          token = parts.slice(1).join(':').trim()
        } else if (trimmed.includes(' ')) {
          const parts = trimmed.split(/\s+/)
          name = parts[0].trim()
          token = parts.slice(1).join(' ').trim()
        } else {
          // Nur Token, verwende Token als Name
          token = trimmed
          name = `Bot ${bots.length + 1}`
        }
        
        if (token) {
          bots.push({ name, bot_token: token })
        }
      }
      
      if (bots.length === 0) {
        alert('Keine gültigen Bot-Daten gefunden')
        return
      }
      
      const response = await axios.post(`${API_BASE}/accounts/bulk-bots`, { bots })
      
      alert(`Import abgeschlossen:\n✅ Erfolgreich: ${response.data.success}\n❌ Fehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.log('Fehler:', response.data.errors)
      }
      
      setShowBulkModal(false)
      setBulkBotsText('')
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleSessionFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    if (!file.name.endsWith('.session')) {
      alert('Nur .session Dateien sind erlaubt')
      return
    }
    
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_BASE}/upload/session`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setSessionFilePath(response.data.file_path)
      alert('Session-Datei erfolgreich hochgeladen!')
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFromSession = async (e) => {
    e.preventDefault()
    
    if (!sessionFilePath) {
      alert('Bitte Session-Datei hochladen')
      return
    }
    
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('name', sessionFormData.name)
      if (sessionFormData.api_id) {
        formData.append('api_id', sessionFormData.api_id)
      }
      if (sessionFormData.api_hash) {
        formData.append('api_hash', sessionFormData.api_hash)
      }
      formData.append('session_file_path', sessionFilePath)
      
      const response = await axios.post(`${API_BASE}/accounts/from-session`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.status === 'connected') {
        setShowSessionModal(false)
        setSessionFile(null)
        setSessionFilePath('')
        setSessionFormData({ name: '', api_id: '', api_hash: '' })
        onUpdate()
        alert('Account erfolgreich aus Session-Datei erstellt!')
      } else {
        alert('Fehler: ' + (response.data.error || 'Unbekannter Fehler'))
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleTdataUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return
    
    setLoading(true)
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })
      
      const response = await axios.post(`${API_BASE}/upload/tdata`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setTdataPath(response.data.tdata_path)
      setTdataFiles(response.data.files)
      alert(`tdata hochgeladen! ${response.data.files.length} Dateien. Hinweis: tdata-Konvertierung erfordert manuelle Konfiguration.`)
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
      <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Account-Verwaltung</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={() => setShowBulkModal(true)}>
            📋 Bulk-Import Bots
          </button>
          <button 
            className="btn btn-info" 
            onClick={() => {
              const userAccounts = accounts.filter(acc => acc.account_type === 'user' && acc.connected)
              if (userAccounts.length === 0) {
                alert('Keine verbundenen User-Accounts vorhanden. Bitte zuerst einen Account verbinden.')
                return
              }
              setCreateBotFormData({
                account_id: userAccounts[0].id.toString(),
                bot_name: '',
                bot_username: ''
              })
              setShowCreateBotModal(true)
            }}
            title="Erstelle einen neuen Bot über einen User-Account via BotFather"
          >
            🤖 Bot erstellen
          </button>
          <button className="btn btn-secondary" onClick={() => setShowSessionModal(true)}>
            📁 Session-Datei
          </button>
          <button className="btn btn-secondary" onClick={() => setShowTdataModal(true)}>
            📂 tdata
          </button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Neuer Account
          </button>
        </div>
      </div>

      {accounts.length === 0 ? (
        <div className="empty-state">
          <p>Keine Accounts vorhanden. Erstelle einen neuen Account.</p>
        </div>
      ) : (
        <table className="table">
          <thead>
              <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Telefonnummer</th>
                <th>Status</th>
                <th>Proxy</th>
                <th>Info</th>
                <th>Aktionen</th>
              </tr>
          </thead>
          <tbody>
            {accounts.map(account => (
              <tr key={account.id}>
                <td>{account.name}</td>
                <td>
                  <span className={`badge ${account.account_type === 'bot' ? 'badge-info' : 'badge-secondary'}`}>
                    {account.account_type === 'bot' ? 'Bot' : 'User'}
                  </span>
                </td>
                  <td>{account.phone_number || '-'}</td>
                  <td>
                    {account.connected ? (
                      <span className="badge badge-success">Verbunden</span>
                    ) : (
                      <span className="badge badge-warning">Nicht verbunden</span>
                    )}
                  </td>
                  <td>
                    {account.proxy ? (
                      <span className="badge badge-info" title={`${account.proxy.host}:${account.proxy.port}`}>
                        🔒 {account.proxy.name}
                      </span>
                    ) : (
                      <span style={{ color: '#999' }}>-</span>
                    )}
                  </td>
                  <td>
                    {account.info && (
                      <span>@{account.info.username || 'N/A'}</span>
                    )}
                  </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    {!account.connected && account.account_type === 'user' && (
                      <button
                        className="btn btn-success btn-small"
                        onClick={() => handleRequestCode(account.id)}
                      >
                        🔐 Login
                      </button>
                    )}
                    {account.account_type === 'user' && (
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={() => handleLoadDialogs(account.id)}
                      >
                        Dialoge
                      </button>
                    )}
                    <button
                      className="btn btn-danger btn-small"
                      onClick={() => handleDelete(account.id)}
                    >
                      Löschen
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
          <div className="modal-content">
            <div className="modal-header">
              <h3>Neuer Account</h3>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Account-Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="z.B. Mein Account"
                />
              </div>
              <div className="form-group">
                <label>Account-Typ</label>
                <select
                  value={formData.account_type}
                  onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                >
                  <option value="user">User Account (Telethon)</option>
                  <option value="bot">Bot (Bot API)</option>
                </select>
              </div>
              
              {formData.account_type === 'bot' ? (
                <>
                  <div className="form-group">
                    <label>Bot Token</label>
                    <input
                      type="text"
                      required={formData.account_type === 'bot'}
                      value={formData.bot_token}
                      onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
                      placeholder="Von @BotFather"
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label>API ID (optional wenn Session-Datei vorhanden)</label>
                    <input
                      type="text"
                      value={formData.api_id}
                      onChange={(e) => setFormData({ ...formData, api_id: e.target.value })}
                      placeholder="Von https://my.telegram.org/apps"
                    />
                    <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                      Optional: Wird aus Session-Datei oder Umgebungsvariablen geladen
                    </p>
                  </div>
                  <div className="form-group">
                    <label>API Hash (optional wenn Session-Datei vorhanden)</label>
                    <input
                      type="text"
                      value={formData.api_hash}
                      onChange={(e) => setFormData({ ...formData, api_hash: e.target.value })}
                      placeholder="Von https://my.telegram.org/apps"
                    />
                    <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                      Optional: Wird aus Session-Datei oder Umgebungsvariablen geladen
                    </p>
                  </div>
                  <div className="form-group">
                    <label>Telefonnummer</label>
                    <input
                      type="text"
                      required={formData.account_type === 'user'}
                      value={formData.phone_number}
                      onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                      placeholder="+491234567890"
                    />
                  </div>
                      <div className="form-group">
                        <label>Session-Name</label>
                        <input
                          type="text"
                          required={formData.account_type === 'user'}
                          value={formData.session_name}
                          onChange={(e) => setFormData({ ...formData, session_name: e.target.value })}
                          placeholder="z.B. account1_session"
                        />
                      </div>
                      <div className="form-group">
                        <label>Proxy (optional - zum Ban-Schutz)</label>
                        <select
                          value={formData.proxy_id}
                          onChange={(e) => setFormData({ ...formData, proxy_id: e.target.value || null })}
                        >
                          <option value="">Kein Proxy</option>
                          {proxies.filter(p => p.is_active).map(proxy => (
                            <option key={proxy.id} value={proxy.id}>
                              {proxy.name} ({proxy.proxy_type.toUpperCase()}) - {proxy.host}:{proxy.port}
                            </option>
                          ))}
                        </select>
                        {formData.proxy_id && (
                          <p style={{ fontSize: '0.85rem', color: '#667eea', marginTop: '5px' }}>
                            ℹ️ Account verbindet über Proxy, um Ban-Risiko zu reduzieren
                          </p>
                        )}
                      </div>
                    </>
                  )}
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Erstelle...' : 'Erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showBulkModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Bulk-Import Bot-APIs</h3>
              <button className="close-btn" onClick={() => setShowBulkModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>Bot-Liste (eine pro Zeile)</label>
              <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '10px' }}>
                Format: <code>Name:Token</code> oder <code>Name Token</code> oder nur <code>Token</code>
              </p>
              <textarea
                value={bulkBotsText}
                onChange={(e) => setBulkBotsText(e.target.value)}
                placeholder={`Bot1:123456:ABC-DEF...
Bot2 789012:GHI-JKL...
123456:MNO-PQR...`}
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
                onClick={handleBulkImportBots}
                disabled={loading}
              >
                {loading ? 'Importiere...' : 'Importieren'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showSessionModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Account aus Session-Datei importieren</h3>
              <button className="close-btn" onClick={() => setShowSessionModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreateFromSession}>
              <div className="form-group">
                <label>Account-Name</label>
                <input
                  type="text"
                  required
                  value={sessionFormData.name}
                  onChange={(e) => setSessionFormData({ ...sessionFormData, name: e.target.value })}
                  placeholder="z.B. Mein Account"
                />
              </div>
              <div className="form-group">
                <label>API ID (optional)</label>
                <input
                  type="text"
                  value={sessionFormData.api_id}
                  onChange={(e) => setSessionFormData({ ...sessionFormData, api_id: e.target.value })}
                  placeholder="Von https://my.telegram.org/apps"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Optional: Wird automatisch aus Session-Datei extrahiert oder aus Umgebungsvariablen geladen
                </p>
              </div>
              <div className="form-group">
                <label>API Hash (optional)</label>
                <input
                  type="text"
                  value={sessionFormData.api_hash}
                  onChange={(e) => setSessionFormData({ ...sessionFormData, api_hash: e.target.value })}
                  placeholder="Von https://my.telegram.org/apps"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Optional: Wird automatisch aus Session-Datei extrahiert oder aus Umgebungsvariablen geladen
                </p>
              </div>
              <div className="form-group">
                <label>Session-Datei (.session)</label>
                <input
                  type="file"
                  accept=".session"
                  onChange={handleSessionFileUpload}
                  style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                />
                {sessionFilePath && (
                  <p style={{ marginTop: '5px', fontSize: '0.9rem', color: '#27ae60' }}>
                    ✓ Datei hochgeladen: {sessionFilePath.split('/').pop()}
                  </p>
                )}
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Lade eine vorhandene Telethon .session Datei hoch
                </p>
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowSessionModal(false)}
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !sessionFilePath}
                >
                  {loading ? 'Erstelle...' : 'Account erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showTdataModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Account aus tdata importieren</h3>
              <button className="close-btn" onClick={() => setShowTdataModal(false)}>×</button>
            </div>
            <div className="alert alert-warning">
              <strong>Hinweis:</strong> tdata-Konvertierung ist komplex. 
              Verwende stattdessen Session-Dateien (.session) wenn möglich.
            </div>
            <div className="form-group">
              <label>Account-Name</label>
              <input
                type="text"
                value={tdataFormData.name}
                onChange={(e) => setTdataFormData({ ...tdataFormData, name: e.target.value })}
                placeholder="z.B. Mein Account"
              />
            </div>
            <div className="form-group">
              <label>API ID</label>
              <input
                type="text"
                value={tdataFormData.api_id}
                onChange={(e) => setTdataFormData({ ...tdataFormData, api_id: e.target.value })}
                placeholder="Von https://my.telegram.org/apps"
              />
            </div>
            <div className="form-group">
              <label>API Hash</label>
              <input
                type="text"
                value={tdataFormData.api_hash}
                onChange={(e) => setTdataFormData({ ...tdataFormData, api_hash: e.target.value })}
                placeholder="Von https://my.telegram.org/apps"
              />
            </div>
            <div className="form-group">
              <label>tdata-Dateien (alle Dateien aus dem tdata-Ordner)</label>
              <input
                type="file"
                multiple
                onChange={handleTdataUpload}
                style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
              />
              {tdataPath && (
                <div style={{ marginTop: '10px' }}>
                  <p style={{ fontSize: '0.9rem', color: '#27ae60' }}>
                    ✓ tdata hochgeladen: {tdataFiles.length} Dateien
                  </p>
                  <p style={{ fontSize: '0.85rem', color: '#666' }}>
                    Pfad: {tdataPath}
                  </p>
                </div>
              )}
              <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                Wähle alle Dateien aus dem tdata-Ordner deiner Telegram Desktop Installation
              </p>
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowTdataModal(false)}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="btn btn-primary"
                disabled={true}
                title="tdata-Konvertierung wird noch nicht vollständig unterstützt"
              >
                (Noch nicht verfügbar)
              </button>
            </div>
          </div>
        </div>
      )}

      {showCreateBotModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>🤖 Bot via BotFather erstellen</h3>
              <button className="close-btn" onClick={() => setShowCreateBotModal(false)}>×</button>
            </div>
            <div className="alert alert-info" style={{ marginBottom: '20px' }}>
              <strong>ℹ️ Info:</strong> Erstellt einen neuen Bot über einen verbundenen User-Account. 
              Der Account muss mit @BotFather kommunizieren können.
            </div>
            <form onSubmit={async (e) => {
              e.preventDefault()
              if (!createBotFormData.account_id || !createBotFormData.bot_name || !createBotFormData.bot_username) {
                alert('Bitte alle Felder ausfüllen')
                return
              }
              
              setLoading(true)
              try {
                const response = await axios.post(
                  `${API_BASE}/accounts/${createBotFormData.account_id}/create-bot`,
                  {
                    account_id: parseInt(createBotFormData.account_id),
                    bot_name: createBotFormData.bot_name,
                    bot_username: createBotFormData.bot_username
                  }
                )
                
                if (response.data.success) {
                  alert(`✅ Bot erfolgreich erstellt!\n\nBot-Token: ${response.data.bot_token}\nBot wurde automatisch zur Account-Liste hinzugefügt.`)
                  setShowCreateBotModal(false)
                  setCreateBotFormData({
                    account_id: '',
                    bot_name: '',
                    bot_username: ''
                  })
                  onUpdate()
                } else {
                  alert('Fehler: ' + (response.data.error || 'Unbekannter Fehler'))
                }
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
                  value={createBotFormData.account_id}
                  onChange={(e) => setCreateBotFormData({ ...createBotFormData, account_id: e.target.value })}
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
                <label>Bot-Name</label>
                <input
                  type="text"
                  required
                  value={createBotFormData.bot_name}
                  onChange={(e) => setCreateBotFormData({ ...createBotFormData, bot_name: e.target.value })}
                  placeholder="z.B. Mein Test Bot"
                />
              </div>
              <div className="form-group">
                <label>Bot-Username</label>
                <input
                  type="text"
                  required
                  value={createBotFormData.bot_username}
                  onChange={(e) => {
                    let username = e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '')
                    if (username && !username.endsWith('bot')) {
                      username = username + 'bot'
                    }
                    setCreateBotFormData({ ...createBotFormData, bot_username: username })
                  }}
                  placeholder="z.B. mein_test_bot"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Muss mit "bot" enden (wird automatisch hinzugefügt)
                </p>
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateBotModal(false)}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Erstelle Bot...' : 'Bot erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showLoginModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>🔐 Account einloggen</h3>
              <button className="close-btn" onClick={() => {
                setShowLoginModal(false)
                setLoginCode('')
                setLoginPassword('')
                setLoginAccountId(null)
                setLoginStep('code')
              }}>×</button>
            </div>
            <form onSubmit={handleLoginSubmit}>
              {loginStep === 'code' ? (
                <>
                  <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                    <strong>ℹ️ Schritt 1:</strong> Code eingeben
                    <br />
                    <small>Der Code wurde an deine Telefonnummer gesendet. Prüfe Telegram!</small>
                  </div>
                  <div className="form-group">
                    <label>Telegram-Code</label>
                    <input
                      type="text"
                      required
                      value={loginCode}
                      onChange={(e) => setLoginCode(e.target.value)}
                      placeholder="z.B. 12345"
                      autoFocus
                      maxLength={6}
                      style={{ fontSize: '1.2rem', textAlign: 'center', letterSpacing: '0.5rem' }}
                    />
                    <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                      Der Code wurde per Telegram an deine Telefonnummer gesendet
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        setShowLoginModal(false)
                        setLoginCode('')
                        setLoginPassword('')
                        setLoginAccountId(null)
                        setLoginStep('code')
                      }}
                    >
                      Abbrechen
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={async () => {
                        if (loginAccountId) {
                          setLoginLoading(true)
                          try {
                            await axios.post(`${API_BASE}/accounts/${loginAccountId}/request-code`)
                            alert('✅ Code wurde erneut angefordert. Prüfe Telegram!')
                          } catch (error) {
                            alert('Fehler: ' + (error.response?.data?.detail || error.message))
                          } finally {
                            setLoginLoading(false)
                          }
                        }
                      }}
                      disabled={loginLoading}
                    >
                      Code erneut anfordern
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loginLoading || !loginCode}>
                      {loginLoading ? 'Prüfe...' : 'Weiter'}
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
                    <strong>🔒 Schritt 2:</strong> Zwei-Faktor-Authentifizierung
                    <br />
                    <small>Dein Account hat 2FA aktiviert. Bitte Passwort eingeben.</small>
                  </div>
                  <div className="form-group">
                    <label>2FA-Passwort</label>
                    <input
                      type="password"
                      required
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder="Dein 2FA-Passwort"
                      autoFocus
                    />
                    <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                      Das Passwort für die Zwei-Faktor-Authentifizierung
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        setLoginStep('code')
                        setLoginPassword('')
                      }}
                    >
                      Zurück
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        setShowLoginModal(false)
                        setLoginCode('')
                        setLoginPassword('')
                        setLoginAccountId(null)
                        setLoginStep('code')
                      }}
                    >
                      Abbrechen
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loginLoading || !loginPassword}>
                      {loginLoading ? 'Logge ein...' : 'Einloggen'}
                    </button>
                  </div>
                </>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

