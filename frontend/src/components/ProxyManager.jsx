import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = '/api'

export default function ProxyManager({ accounts, onUpdate }) {
  const [proxies, setProxies] = useState([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [showBulkModal, setShowBulkModal] = useState(false)
  const [selectedProxy, setSelectedProxy] = useState(null)
  const [bulkProxiesText, setBulkProxiesText] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    proxy_type: 'socks5',
    host: '',
    port: '',
    username: '',
    password: '',
    secret: '',
    country: '',
    notes: ''
  })
  const [filterType, setFilterType] = useState('')

  useEffect(() => {
    loadProxies()
  }, [filterType])

  const loadProxies = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterType) params.proxy_type = filterType
      const response = await axios.get(`${API_BASE}/proxies`, { params })
      setProxies(response.data)
    } catch (error) {
      console.error('Fehler beim Laden:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = {
        ...formData,
        port: parseInt(formData.port)
      }
      
      if (selectedProxy) {
        await axios.put(`${API_BASE}/proxies/${selectedProxy.id}`, data)
      } else {
        await axios.post(`${API_BASE}/proxies`, data)
      }
      
      setShowModal(false)
      setSelectedProxy(null)
      setFormData({
        name: '',
        proxy_type: 'socks5',
        host: '',
        port: '',
        username: '',
        password: '',
        secret: '',
        country: '',
        notes: ''
      })
      loadProxies()
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (proxy) => {
    setSelectedProxy(proxy)
    setFormData({
      name: proxy.name,
      proxy_type: proxy.proxy_type,
      host: proxy.host,
      port: proxy.port.toString(),
      username: proxy.username || '',
      password: proxy.password || '',
      secret: proxy.secret || '',
      country: proxy.country || '',
      notes: proxy.notes || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Wirklich löschen?')) return
    
    try {
      await axios.delete(`${API_BASE}/proxies/${id}`)
      loadProxies()
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleTest = async (id) => {
    try {
      const response = await axios.post(`${API_BASE}/proxies/${id}/test`)
      if (response.data.success) {
        alert('✅ Proxy erreichbar!')
        loadProxies()
      } else {
        alert('❌ Proxy nicht erreichbar: ' + (response.data.message || response.data.error))
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleToggleActive = async (proxy) => {
    try {
      await axios.put(`${API_BASE}/proxies/${proxy.id}`, {
        is_active: !proxy.is_active
      })
      loadProxies()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleBulkImport = async () => {
    if (!bulkProxiesText.trim()) {
      alert('Bitte Proxy-Liste eingeben')
      return
    }
    
    setLoading(true)
    try {
      // Parse Text: verschiedene Formate unterstützen
      const lines = bulkProxiesText.split('\n').filter(line => line.trim())
      const proxies = []
      
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed) continue
        
        // Format: type://username:password@host:port oder host:port:type oder host:port
        let proxy_data = {}
        
        if (trimmed.includes('://')) {
          // Format: socks5://user:pass@host:port
          const parts = trimmed.split('://')
          proxy_data.proxy_type = parts[0].toLowerCase()
          const rest = parts[1]
          
          if (rest.includes('@')) {
            const [auth, addr] = rest.split('@')
            const [username, password] = auth.split(':')
            const [host, port] = addr.split(':')
            proxy_data.username = username
            proxy_data.password = password
            proxy_data.host = host
            proxy_data.port = parseInt(port)
          } else {
            const [host, port] = rest.split(':')
            proxy_data.host = host
            proxy_data.port = parseInt(port)
          }
        } else if (trimmed.includes(':')) {
          const parts = trimmed.split(':')
          if (parts.length >= 2) {
            proxy_data.host = parts[0].trim()
            proxy_data.port = parseInt(parts[1].trim())
            proxy_data.proxy_type = parts[2] ? parts[2].trim().toLowerCase() : 'socks5'
            
            if (parts.length >= 4) {
              proxy_data.username = parts[2].trim()
              proxy_data.password = parts[3].trim()
            }
          }
        }
        
        if (proxy_data.host && proxy_data.port) {
          proxy_data.name = proxy_data.name || `Proxy ${proxies.length + 1}`
          proxies.push(proxy_data)
        }
      }
      
      if (proxies.length === 0) {
        alert('Keine gültigen Proxy-Daten gefunden')
        return
      }
      
      const response = await axios.post(`${API_BASE}/proxies/bulk`, { proxies })
      
      alert(`Import abgeschlossen:\n✅ Erfolgreich: ${response.data.success}\n❌ Fehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.log('Fehler:', response.data.errors)
      }
      
      setShowBulkModal(false)
      setBulkProxiesText('')
      loadProxies()
      onUpdate()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const getAccountsUsingProxy = (proxyId) => {
    return accounts.filter(acc => acc.proxy_id === proxyId).length
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Proxy-Verwaltung</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{ padding: '8px', borderRadius: '5px', border: '2px solid #e0e0e0' }}
            >
              <option value="">Alle Typen</option>
              <option value="socks5">SOCKS5</option>
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="mtproto">MTProto</option>
            </select>
            <button className="btn btn-secondary" onClick={() => setShowBulkModal(true)}>
              📋 Bulk-Import
            </button>
            <button className="btn btn-primary" onClick={() => {
              setSelectedProxy(null)
              setFormData({
                name: '',
                proxy_type: 'socks5',
                host: '',
                port: '',
                username: '',
                password: '',
                secret: '',
                country: '',
                notes: ''
              })
              setShowModal(true)
            }}>
              + Neuer Proxy
            </button>
          </div>
        </div>

        <div className="alert alert-info">
          <strong>ℹ️ Info:</strong> Proxies helfen, Bans zu vermeiden, indem jeder Account über eine andere IP verbindet. 
          Unterstützt: SOCKS5, HTTP, HTTPS und MTProto.
        </div>

        {loading ? (
          <div className="loading">Lade Proxies...</div>
        ) : proxies.length === 0 ? (
          <div className="empty-state">
            <p>Keine Proxies vorhanden. Erstelle einen neuen Proxy.</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Host:Port</th>
                <th>Land</th>
                <th>Status</th>
                <th>Verwendet</th>
                <th>Verwendung</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {proxies.map(proxy => (
                <tr key={proxy.id}>
                  <td>{proxy.name}</td>
                  <td>
                    <span className={`badge ${proxy.proxy_type === 'mtproto' ? 'badge-info' : 'badge-secondary'}`}>
                      {proxy.proxy_type.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <code>{proxy.host}:{proxy.port}</code>
                    {proxy.username && <span style={{ color: '#999', fontSize: '0.9rem' }}> (Auth)</span>}
                  </td>
                  <td>{proxy.country || '-'}</td>
                  <td>
                    {proxy.is_active ? (
                      <span className="badge badge-success">Aktiv</span>
                    ) : (
                      <span className="badge badge-secondary">Inaktiv</span>
                    )}
                    {proxy.is_verified && (
                      <span className="badge badge-info" style={{ marginLeft: '5px' }}>✓ Verifiziert</span>
                    )}
                  </td>
                  <td>{getAccountsUsingProxy(proxy.id)} Account(s)</td>
                  <td>{proxy.usage_count}x</td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button
                        className="btn btn-info btn-small"
                        onClick={() => handleTest(proxy.id)}
                      >
                        Test
                      </button>
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={() => handleEdit(proxy)}
                      >
                        Bearbeiten
                      </button>
                      <button
                        className="btn btn-warning btn-small"
                        onClick={() => handleToggleActive(proxy)}
                      >
                        {proxy.is_active ? 'Deaktivieren' : 'Aktivieren'}
                      </button>
                      <button
                        className="btn btn-danger btn-small"
                        onClick={() => handleDelete(proxy.id)}
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
      </div>

      {showModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>{selectedProxy ? 'Proxy bearbeiten' : 'Neuer Proxy'}</h3>
              <button className="close-btn" onClick={() => {
                setShowModal(false)
                setSelectedProxy(null)
              }}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="z.B. Proxy DE 1"
                />
              </div>
              <div className="form-group">
                <label>Proxy-Typ</label>
                <select
                  required
                  value={formData.proxy_type}
                  onChange={(e) => setFormData({ ...formData, proxy_type: e.target.value })}
                >
                  <option value="socks5">SOCKS5</option>
                  <option value="http">HTTP</option>
                  <option value="https">HTTPS</option>
                  <option value="mtproto">MTProto</option>
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Host</label>
                  <input
                    type="text"
                    required
                    value={formData.host}
                    onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                    placeholder="z.B. 192.168.1.1"
                  />
                </div>
                <div className="form-group">
                  <label>Port</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="65535"
                    value={formData.port}
                    onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                    placeholder="1080"
                  />
                </div>
              </div>
              {formData.proxy_type !== 'mtproto' && (
                <div className="form-row">
                  <div className="form-group">
                    <label>Username (optional)</label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Password (optional)</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    />
                  </div>
                </div>
              )}
              {formData.proxy_type === 'mtproto' && (
                <div className="form-group">
                  <label>Secret (MTProto)</label>
                  <input
                    type="text"
                    required
                    value={formData.secret}
                    onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                    placeholder="MTProto Secret"
                  />
                </div>
              )}
              <div className="form-group">
                <label>Land (optional)</label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  placeholder="z.B. DE, US"
                />
              </div>
              <div className="form-group">
                <label>Notizen (optional)</label>
                <textarea
                  rows="3"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Notizen zum Proxy..."
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowModal(false)
                    setSelectedProxy(null)
                  }}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Speichere...' : 'Speichern'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showBulkModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h3>Bulk-Import Proxies</h3>
              <button className="close-btn" onClick={() => setShowBulkModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>Proxy-Liste (eine pro Zeile)</label>
              <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '10px' }}>
                Formate:<br/>
                • <code>socks5://user:pass@host:port</code><br/>
                • <code>host:port:type</code><br/>
                • <code>host:port</code> (Standard: SOCKS5)
              </p>
              <textarea
                value={bulkProxiesText}
                onChange={(e) => setBulkProxiesText(e.target.value)}
                placeholder={`socks5://user:pass@192.168.1.1:1080
192.168.1.2:1080
http://proxy.example.com:8080
host:port:mtproto`}
                rows="12"
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
                onClick={handleBulkImport}
                disabled={loading}
              >
                {loading ? 'Importiere...' : 'Importieren'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

