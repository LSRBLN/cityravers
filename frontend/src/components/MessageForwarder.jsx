import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function MessageForwarder({ accounts, groups, onUpdate }) {
  const [activeTab, setActiveTab] = useState('simple') // simple, advanced, bulk, scheduled
  const [loading, setLoading] = useState(false)
  const [forwarding, setForwarding] = useState(false)
  
  // Simple Forwarder State
  const [simpleConfig, setSimpleConfig] = useState({
    account_id: '',
    source_group_entity: '',
    source_group_id: '',
    use_manual_source: false,
    message_id: '',
    target_group_ids: [],
    delay: 2.0
  })
  const [jsonInput, setJsonInput] = useState('')
  const [showJsonParser, setShowJsonParser] = useState(false)
  
  // Advanced Forwarder State
  const [advancedConfig, setAdvancedConfig] = useState({
    account_id: '',
    source_group_id: '',
    manual_group_entity: '',
    use_manual_input: false,
    limit: 100
  })
  const [messages, setMessages] = useState([])
  const [selectedMessages, setSelectedMessages] = useState([])
  const [forwardConfig, setForwardConfig] = useState({
    target_group_ids: [],
    delay: 2.0
  })
  const [filterText, setFilterText] = useState('')
  const [filterDateFrom, setFilterDateFrom] = useState('')
  const [filterDateTo, setFilterDateTo] = useState('')
  const [showPreview, setShowPreview] = useState(false)
  const [previewMessage, setPreviewMessage] = useState(null)
  
  // Bulk Forwarder State
  const [bulkConfig, setBulkConfig] = useState({
    account_id: '',
    source_group_entity: '',
    source_group_id: '',
    use_manual_source: false,
    message_ids: '', // Komma-getrennte IDs
    target_group_ids: [],
    delay: 2.0
  })
  
  // Statistics
  const [stats, setStats] = useState({
    total_forwarded: 0,
    total_failed: 0,
    last_forward: null
  })

  const connectedUserAccounts = accounts.filter(acc => acc.connected && acc.account_type === 'user')

  // JSON Parser
  const parseJsonMessage = () => {
    try {
      const data = JSON.parse(jsonInput)
      
      let msgId = null
      if (data.message?.message_id) {
        msgId = data.message.message_id.toString()
      } else if (data.message_id) {
        msgId = data.message_id.toString()
      }
      
      let chatId = null
      let chatType = null
      let chatName = null
      
      if (data.message?.chat?.id) {
        chatId = data.message.chat.id.toString()
        chatType = data.message.chat.type || 'unknown'
        chatName = data.message.chat.title || data.message.chat.first_name || data.message.chat.username || null
      } else if (data.chat?.id) {
        chatId = data.chat.id.toString()
        chatType = data.chat.type || 'unknown'
        chatName = data.chat.title || data.chat.first_name || data.chat.username || null
      }
      
      if (msgId && chatId) {
        setSimpleConfig({
          ...simpleConfig,
          use_manual_source: true,
          source_group_entity: chatId,
          message_id: msgId
        })
        setShowJsonParser(false)
        setJsonInput('')
        alert(`✅ Daten erfolgreich eingefügt!\n\nQuell-Chat: ${chatId}\nTyp: ${chatType}\nMessage-ID: ${msgId}`)
      } else {
        alert('❌ Konnte Message-ID oder Chat-ID nicht aus JSON extrahieren')
      }
    } catch (error) {
      alert('❌ Ungültiges JSON-Format: ' + error.message)
    }
  }

  // Simple Forwarder
  const handleSimpleForward = async () => {
    if (!simpleConfig.account_id) {
      alert('Bitte Account auswählen')
      return
    }
    
    if (!simpleConfig.use_manual_source && !simpleConfig.source_group_id) {
      alert('Bitte Quell-Gruppe auswählen oder manuelle Eingabe verwenden')
      return
    }
    
    if (simpleConfig.use_manual_source && !simpleConfig.source_group_entity) {
      alert('Bitte Quell-Gruppe eingeben')
      return
    }
    
    if (!simpleConfig.message_id) {
      alert('Bitte Message-ID eingeben')
      return
    }
    
    if (simpleConfig.target_group_ids.length === 0) {
      alert('Bitte mindestens eine Ziel-Gruppe auswählen')
      return
    }
    
    if (!confirm(`Wirklich Nachricht ${simpleConfig.message_id} an ${simpleConfig.target_group_ids.length} Gruppe(n) weiterleiten?`)) {
      return
    }
    
    setForwarding(true)
    try {
      const requestData = {
        account_id: parseInt(simpleConfig.account_id),
        message_id: simpleConfig.message_id.toString(),
        target_group_ids: simpleConfig.target_group_ids.map(id => parseInt(id)),
        delay: parseFloat(simpleConfig.delay)
      }
      
      if (simpleConfig.use_manual_source) {
        requestData.source_group_entity = simpleConfig.source_group_entity.trim()
      } else {
        requestData.source_group_id = parseInt(simpleConfig.source_group_id)
      }
      
      const response = await axios.post(`${API_BASE}/messages/forward-by-id`, requestData)
      
      setStats({
        total_forwarded: stats.total_forwarded + response.data.forwarded,
        total_failed: stats.total_failed + response.data.failed,
        last_forward: new Date().toISOString()
      })
      
      alert(`✅ Weiterleitung abgeschlossen!\n\nErfolgreich: ${response.data.forwarded}\nFehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        const errorList = response.data.errors.map(e => `- ${e.target}: ${e.error}`).join('\n')
        alert(`Fehler bei einigen Weiterleitungen:\n\n${errorList}`)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setForwarding(false)
    }
  }

  // Advanced Forwarder - Load Messages
  const handleLoadMessages = async () => {
    if (!advancedConfig.account_id) {
      alert('Bitte Account auswählen')
      return
    }
    
    if (!advancedConfig.use_manual_input && !advancedConfig.source_group_id) {
      alert('Bitte Quell-Gruppe auswählen oder manuelle Eingabe verwenden')
      return
    }
    
    if (advancedConfig.use_manual_input && !advancedConfig.manual_group_entity) {
      alert('Bitte Chat-ID, Username oder Einladungslink eingeben')
      return
    }
    
    setLoading(true)
    try {
      const requestData = {
        account_id: parseInt(advancedConfig.account_id),
        limit: parseInt(advancedConfig.limit)
      }
      
      if (advancedConfig.use_manual_input) {
        requestData.manual_group_entity = advancedConfig.manual_group_entity.trim()
      } else {
        requestData.group_id = parseInt(advancedConfig.source_group_id)
      }
      
      const response = await axios.post(`${API_BASE}/messages/get-group-messages`, requestData)
      
      if (Array.isArray(response.data)) {
        setMessages(response.data)
        setSelectedMessages([])
        
        if (response.data.length === 0) {
          alert('⚠️ Keine Nachrichten gefunden')
        }
      } else {
        setMessages(response.data.messages || [])
        setSelectedMessages([])
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message
      alert('❌ Fehler beim Laden der Nachrichten:\n\n' + errorMsg)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  // Advanced Forwarder - Forward Selected
  const handleAdvancedForward = async () => {
    if (!advancedConfig.account_id) {
      alert('Bitte Account auswählen')
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
      const sourceGroupId = advancedConfig.use_manual_input ? null : parseInt(advancedConfig.source_group_id)
      
      const response = await axios.post(`${API_BASE}/messages/forward`, {
        account_id: parseInt(advancedConfig.account_id),
        source_group_id: sourceGroupId,
        message_ids: selectedMessages,
        target_group_ids: forwardConfig.target_group_ids.map(id => parseInt(id)),
        delay: parseFloat(forwardConfig.delay)
      })
      
      setStats({
        total_forwarded: stats.total_forwarded + response.data.success,
        total_failed: stats.total_failed + response.data.failed,
        last_forward: new Date().toISOString()
      })
      
      alert(`✅ Weiterleitung abgeschlossen!\n\nErfolgreich: ${response.data.success}\nFehlgeschlagen: ${response.data.failed}`)
      
      if (response.data.errors && response.data.errors.length > 0) {
        console.log('Fehler:', response.data.errors)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setForwarding(false)
    }
  }

  // Bulk Forwarder
  const handleBulkForward = async () => {
    if (!bulkConfig.account_id) {
      alert('Bitte Account auswählen')
      return
    }
    
    if (!bulkConfig.message_ids.trim()) {
      alert('Bitte Message-IDs eingeben (komma-getrennt)')
      return
    }
    
    if (bulkConfig.target_group_ids.length === 0) {
      alert('Bitte mindestens eine Ziel-Gruppe auswählen')
      return
    }
    
    const messageIds = bulkConfig.message_ids.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
    
    if (messageIds.length === 0) {
      alert('Keine gültigen Message-IDs gefunden')
      return
    }
    
    if (!confirm(`Wirklich ${messageIds.length} Nachricht(en) an ${bulkConfig.target_group_ids.length} Gruppe(n) weiterleiten?`)) {
      return
    }
    
    setForwarding(true)
    try {
      const sourceGroupId = bulkConfig.use_manual_source ? null : parseInt(bulkConfig.source_group_id)
      const sourceGroupEntity = bulkConfig.use_manual_source ? bulkConfig.source_group_entity : null
      
      // Weiterleite jede Nachricht einzeln
      let totalForwarded = 0
      let totalFailed = 0
      const errors = []
      
      for (const msgId of messageIds) {
        try {
          const requestData = {
            account_id: parseInt(bulkConfig.account_id),
            message_id: msgId.toString(),
            target_group_ids: bulkConfig.target_group_ids.map(id => parseInt(id)),
            delay: parseFloat(bulkConfig.delay)
          }
          
          if (bulkConfig.use_manual_source) {
            requestData.source_group_entity = sourceGroupEntity
          } else {
            requestData.source_group_id = sourceGroupId
          }
          
          const response = await axios.post(`${API_BASE}/messages/forward-by-id`, requestData)
          totalForwarded += response.data.forwarded || 0
          totalFailed += response.data.failed || 0
          
          if (response.data.errors) {
            errors.push(...response.data.errors)
          }
          
          // Delay zwischen Nachrichten
          if (msgId !== messageIds[messageIds.length - 1]) {
            await new Promise(resolve => setTimeout(resolve, parseFloat(bulkConfig.delay) * 1000))
          }
        } catch (error) {
          totalFailed++
          errors.push({
            message_id: msgId,
            error: error.response?.data?.detail || error.message
          })
        }
      }
      
      setStats({
        total_forwarded: stats.total_forwarded + totalForwarded,
        total_failed: stats.total_failed + totalFailed,
        last_forward: new Date().toISOString()
      })
      
      alert(`✅ Bulk-Weiterleitung abgeschlossen!\n\nErfolgreich: ${totalForwarded}\nFehlgeschlagen: ${totalFailed}`)
      
      if (errors.length > 0) {
        const errorList = errors.slice(0, 10).map(e => `- ${e.message_id || e.target}: ${e.error}`).join('\n')
        alert(`Fehler bei einigen Weiterleitungen:\n\n${errorList}${errors.length > 10 ? '\n...' : ''}`)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setForwarding(false)
    }
  }

  // Filter Messages
  const filteredMessages = messages.filter(msg => {
    if (filterText && !msg.text?.toLowerCase().includes(filterText.toLowerCase())) {
      return false
    }
    
    if (filterDateFrom) {
      const msgDate = new Date(msg.date)
      const fromDate = new Date(filterDateFrom)
      if (msgDate < fromDate) return false
    }
    
    if (filterDateTo) {
      const msgDate = new Date(msg.date)
      const toDate = new Date(filterDateTo)
      toDate.setHours(23, 59, 59, 999)
      if (msgDate > toDate) return false
    }
    
    return true
  })

  // Message Preview
  const showMessagePreview = (message) => {
    setPreviewMessage(message)
    setShowPreview(true)
  }

  // Select/Deselect Helpers
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
    if (selectedMessages.length === filteredMessages.length) {
      setSelectedMessages([])
    } else {
      setSelectedMessages(filteredMessages.map(m => m.id))
    }
  }

  const handleSelectFiltered = () => {
    const filteredIds = filteredMessages.map(m => m.id)
    setSelectedMessages(prev => {
      const newSelection = [...new Set([...prev, ...filteredIds])]
      return newSelection
    })
  }

  return (
    <div>
      {/* Header mit Statistiken */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2>📤 Nachrichten-Weiterleitung</h2>
          <div style={{ display: 'flex', gap: '20px', fontSize: '0.9rem' }}>
            <div>
              <strong>✅ Erfolgreich:</strong> {stats.total_forwarded}
            </div>
            <div>
              <strong>❌ Fehlgeschlagen:</strong> {stats.total_failed}
            </div>
            {stats.last_forward && (
              <div>
                <strong>🕐 Letzte:</strong> {new Date(stats.last_forward).toLocaleString('de-DE')}
              </div>
            )}
          </div>
        </div>

        <div className="alert alert-warning">
          <strong>⚠️ WARNUNG:</strong> Massenweiterleitungen können gegen Telegram Nutzungsbedingungen verstoßen 
          und zu Account-Sperrungen führen. Nur für legitime Zwecke verwenden!
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '20px', borderBottom: '2px solid #e0e0e0' }}>
          <button
            className={`btn ${activeTab === 'simple' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('simple')}
            style={{ borderRadius: '5px 5px 0 0', marginBottom: '-2px' }}
          >
            🎯 Einfach
          </button>
          <button
            className={`btn ${activeTab === 'advanced' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('advanced')}
            style={{ borderRadius: '5px 5px 0 0', marginBottom: '-2px' }}
          >
            📋 Erweitert
          </button>
          <button
            className={`btn ${activeTab === 'bulk' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('bulk')}
            style={{ borderRadius: '5px 5px 0 0', marginBottom: '-2px' }}
          >
            📦 Bulk
          </button>
        </div>
      </div>

      {/* Simple Forwarder Tab */}
      {activeTab === 'simple' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>🎯 Einfacher Forwarder</h3>
            <button
              className="btn btn-secondary btn-small"
              onClick={() => setShowJsonParser(!showJsonParser)}
            >
              {showJsonParser ? '✖️ JSON-Parser schließen' : '📋 Aus JSON einfügen'}
            </button>
          </div>

          {showJsonParser && (
            <div className="alert alert-info" style={{ marginBottom: '20px' }}>
              <strong>📋 JSON-Parser:</strong> Füge hier ein Telegram Update-JSON ein.
              <textarea
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                placeholder='Füge hier das JSON ein...'
                style={{
                  width: '100%',
                  minHeight: '150px',
                  marginTop: '10px',
                  padding: '10px',
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                  borderRadius: '5px',
                  border: '1px solid #ddd'
                }}
              />
              <button
                className="btn btn-primary"
                onClick={parseJsonMessage}
                disabled={!jsonInput.trim()}
                style={{ marginTop: '10px' }}
              >
                📥 Aus JSON extrahieren
              </button>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Quell-Nachricht</h4>
              
              <div className="form-group">
                <label>Account</label>
                <select
                  value={simpleConfig.account_id}
                  onChange={(e) => setSimpleConfig({ ...simpleConfig, account_id: e.target.value })}
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
                <label>
                  <input
                    type="checkbox"
                    checked={simpleConfig.use_manual_source}
                    onChange={(e) => setSimpleConfig({ ...simpleConfig, use_manual_source: e.target.checked, source_group_id: '', source_group_entity: '' })}
                    style={{ marginRight: '8px' }}
                  />
                  Manuelle Quell-Gruppe eingeben
                </label>
              </div>
              
              {!simpleConfig.use_manual_source ? (
                <div className="form-group">
                  <label>Quell-Gruppe</label>
                  <select
                    value={simpleConfig.source_group_id}
                    onChange={(e) => setSimpleConfig({ ...simpleConfig, source_group_id: e.target.value })}
                  >
                    <option value="">Bitte wählen...</option>
                    {groups.map(group => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="form-group">
                  <label>Quell-Gruppe (Chat-ID, @username oder Einladungslink)</label>
                  <input
                    type="text"
                    value={simpleConfig.source_group_entity}
                    onChange={(e) => setSimpleConfig({ ...simpleConfig, source_group_entity: e.target.value })}
                    placeholder="z.B. -1001234567890, @gruppenname oder https://t.me/joinchat/..."
                    style={{ width: '100%' }}
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Message-ID</label>
                <input
                  type="text"
                  value={simpleConfig.message_id}
                  onChange={(e) => setSimpleConfig({ ...simpleConfig, message_id: e.target.value })}
                  placeholder="z.B. 4053119"
                  style={{ width: '100%' }}
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Die Message-ID findest du in der Nachricht oder im JSON
                </p>
              </div>
            </div>

            <div>
              <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Ziel-Gruppen</h4>
              
              <div className="form-group">
                <label>Ziel-Gruppen (mehrere auswählbar)</label>
                <div style={{
                  border: '2px solid #e0e0e0',
                  borderRadius: '5px',
                  padding: '10px',
                  maxHeight: '250px',
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
                        backgroundColor: simpleConfig.target_group_ids.includes(group.id) ? '#e3f2fd' : 'transparent'
                      }}>
                        <input
                          type="checkbox"
                          checked={simpleConfig.target_group_ids.includes(group.id)}
                          onChange={() => {
                            const currentIds = simpleConfig.target_group_ids
                            if (currentIds.includes(group.id)) {
                              setSimpleConfig({
                                ...simpleConfig,
                                target_group_ids: currentIds.filter(id => id !== group.id)
                              })
                            } else {
                              setSimpleConfig({
                                ...simpleConfig,
                                target_group_ids: [...currentIds, group.id]
                              })
                            }
                          }}
                          style={{ marginRight: '8px' }}
                        />
                        {group.name}
                      </label>
                    ))
                  )}
                </div>
                {simpleConfig.target_group_ids.length > 0 && (
                  <p style={{ marginTop: '5px', fontSize: '0.9rem', color: '#667eea' }}>
                    {simpleConfig.target_group_ids.length} Gruppe(n) ausgewählt
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
                  value={simpleConfig.delay}
                  onChange={(e) => setSimpleConfig({ ...simpleConfig, delay: e.target.value })}
                />
              </div>
              
              <button
                className="btn btn-success"
                onClick={handleSimpleForward}
                disabled={forwarding || !simpleConfig.account_id || !simpleConfig.message_id || simpleConfig.target_group_ids.length === 0}
                style={{ width: '100%', marginTop: '10px', padding: '12px' }}
              >
                {forwarding ? '⏳ Leite weiter...' : `📤 Nachricht ${simpleConfig.message_id || '?'} weiterleiten`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Advanced Forwarder Tab */}
      {activeTab === 'advanced' && (
        <div>
          <div className="card" style={{ marginBottom: '20px' }}>
            <h3>📋 Erweiterter Forwarder</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
              <div>
                <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Nachrichten laden</h4>
                
                <div className="form-group">
                  <label>Account</label>
                  <select
                    value={advancedConfig.account_id}
                    onChange={(e) => setAdvancedConfig({ ...advancedConfig, account_id: e.target.value })}
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
                  <label>
                    <input
                      type="checkbox"
                      checked={advancedConfig.use_manual_input}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, use_manual_input: e.target.checked, source_group_id: '', manual_group_entity: '' })}
                      style={{ marginRight: '8px' }}
                    />
                    Manuelle Eingabe
                  </label>
                </div>
                
                {!advancedConfig.use_manual_input ? (
                  <div className="form-group">
                    <label>Quell-Gruppe</label>
                    <select
                      value={advancedConfig.source_group_id}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, source_group_id: e.target.value })}
                    >
                      <option value="">Bitte wählen...</option>
                      {groups.map(group => (
                        <option key={group.id} value={group.id}>
                          {group.name}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : (
                  <div className="form-group">
                    <label>Gruppe (Chat-ID, @username oder Einladungslink)</label>
                    <input
                      type="text"
                      value={advancedConfig.manual_group_entity}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, manual_group_entity: e.target.value })}
                      placeholder="z.B. -1001234567890, @gruppenname oder https://t.me/joinchat/..."
                      style={{ width: '100%' }}
                    />
                  </div>
                )}
                
                <div className="form-group">
                  <label>Limit (max. Nachrichten)</label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={advancedConfig.limit}
                    onChange={(e) => setAdvancedConfig({ ...advancedConfig, limit: e.target.value })}
                  />
                </div>
                
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    className="btn btn-primary"
                    onClick={handleLoadMessages}
                    disabled={loading || !advancedConfig.account_id || (!advancedConfig.source_group_id && !advancedConfig.manual_group_entity)}
                  >
                    {loading ? '⏳ Lade...' : '📥 Nachrichten laden'}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={async () => {
                      if (!advancedConfig.account_id || (!advancedConfig.source_group_id && !advancedConfig.manual_group_entity)) {
                        alert('Bitte Account und Quell-Gruppe auswählen')
                        return
                      }
                      
                      setLoading(true)
                      try {
                        const groupId = advancedConfig.use_manual_input ? null : parseInt(advancedConfig.source_group_id)
                        const groupEntity = advancedConfig.use_manual_input ? advancedConfig.manual_group_entity : null
                        
                        if (groupId) {
                          const response = await axios.post(
                            `${API_BASE}/groups/${groupId}/update-chat-id?account_id=${advancedConfig.account_id}`
                          )
                          alert(`✅ ${response.data.message}`)
                        } else {
                          alert('Chat-ID-Aktualisierung nur für Gruppen aus Dropdown möglich')
                        }
                      } catch (error) {
                        alert('Fehler: ' + (error.response?.data?.detail || error.message))
                      } finally {
                        setLoading(false)
                      }
                    }}
                    disabled={loading || advancedConfig.use_manual_input}
                    title="Aktualisiert die Chat-ID der Gruppe"
                  >
                    🔄 Chat-ID aktualisieren
                  </button>
                </div>
              </div>

              <div>
                <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Weiterleiten</h4>
                
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
                            onChange={() => {
                              const currentIds = forwardConfig.target_group_ids
                              if (currentIds.includes(group.id)) {
                                setForwardConfig({
                                  ...forwardConfig,
                                  target_group_ids: currentIds.filter(id => id !== group.id)
                                })
                              } else {
                                setForwardConfig({
                                  ...forwardConfig,
                                  target_group_ids: [...currentIds, group.id]
                                })
                              }
                            }}
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
                  onClick={handleAdvancedForward}
                  disabled={forwarding || selectedMessages.length === 0 || forwardConfig.target_group_ids.length === 0}
                  style={{ width: '100%', marginTop: '10px' }}
                >
                  {forwarding ? '⏳ Leite weiter...' : `📤 ${selectedMessages.length} Nachricht(en) weiterleiten`}
                </button>
              </div>
            </div>
          </div>

          {/* Messages List mit Filtern */}
          {messages.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>Nachrichten ({filteredMessages.length} von {messages.length})</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={handleSelectAll}
                  >
                    {selectedMessages.length === filteredMessages.length ? 'Alle abwählen' : 'Alle auswählen'}
                  </button>
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={handleSelectFiltered}
                  >
                    Gefilterte auswählen
                  </button>
                  <span className="badge badge-info">
                    {selectedMessages.length} ausgewählt
                  </span>
                </div>
              </div>

              {/* Filter */}
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '10px', marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label style={{ fontSize: '0.85rem' }}>Text-Filter</label>
                  <input
                    type="text"
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    placeholder="Nachricht enthält..."
                    style={{ width: '100%' }}
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label style={{ fontSize: '0.85rem' }}>Von Datum</label>
                  <input
                    type="date"
                    value={filterDateFrom}
                    onChange={(e) => setFilterDateFrom(e.target.value)}
                    style={{ width: '100%' }}
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label style={{ fontSize: '0.85rem' }}>Bis Datum</label>
                  <input
                    type="date"
                    value={filterDateTo}
                    onChange={(e) => setFilterDateTo(e.target.value)}
                    style={{ width: '100%' }}
                  />
                </div>
              </div>

              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th style={{ width: '40px' }}>
                        <input
                          type="checkbox"
                          checked={selectedMessages.length === filteredMessages.length && filteredMessages.length > 0}
                          onChange={handleSelectAll}
                        />
                      </th>
                      <th style={{ width: '80px' }}>ID</th>
                      <th>Text (Vorschau)</th>
                      <th style={{ width: '150px' }}>Datum</th>
                      <th style={{ width: '100px' }}>Typ</th>
                      <th style={{ width: '80px' }}>Aktion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredMessages.map(msg => (
                      <tr key={msg.id} style={{ backgroundColor: selectedMessages.includes(msg.id) ? '#e3f2fd' : 'transparent' }}>
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
                        <td>
                          <button
                            className="btn btn-secondary btn-small"
                            onClick={() => showMessagePreview(msg)}
                            style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                          >
                            👁️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Bulk Forwarder Tab */}
      {activeTab === 'bulk' && (
        <div className="card">
          <h3>📦 Bulk-Forwarder</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Leite mehrere Nachrichten auf einmal weiter. Gib die Message-IDs komma-getrennt ein.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Quell-Nachrichten</h4>
              
              <div className="form-group">
                <label>Account</label>
                <select
                  value={bulkConfig.account_id}
                  onChange={(e) => setBulkConfig({ ...bulkConfig, account_id: e.target.value })}
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
                <label>
                  <input
                    type="checkbox"
                    checked={bulkConfig.use_manual_source}
                    onChange={(e) => setBulkConfig({ ...bulkConfig, use_manual_source: e.target.checked, source_group_id: '', source_group_entity: '' })}
                    style={{ marginRight: '8px' }}
                  />
                  Manuelle Quell-Gruppe eingeben
                </label>
              </div>
              
              {!bulkConfig.use_manual_source ? (
                <div className="form-group">
                  <label>Quell-Gruppe</label>
                  <select
                    value={bulkConfig.source_group_id}
                    onChange={(e) => setBulkConfig({ ...bulkConfig, source_group_id: e.target.value })}
                  >
                    <option value="">Bitte wählen...</option>
                    {groups.map(group => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <div className="form-group">
                  <label>Quell-Gruppe (Chat-ID, @username oder Einladungslink)</label>
                  <input
                    type="text"
                    value={bulkConfig.source_group_entity}
                    onChange={(e) => setBulkConfig({ ...bulkConfig, source_group_entity: e.target.value })}
                    placeholder="z.B. -1001234567890, @gruppenname"
                    style={{ width: '100%' }}
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Message-IDs (komma-getrennt)</label>
                <textarea
                  value={bulkConfig.message_ids}
                  onChange={(e) => setBulkConfig({ ...bulkConfig, message_ids: e.target.value })}
                  placeholder="z.B. 4053090, 4053119, 4053120"
                  style={{ width: '100%', minHeight: '100px', fontFamily: 'monospace' }}
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Mehrere Message-IDs durch Komma trennen
                </p>
              </div>
            </div>

            <div>
              <h4 style={{ marginBottom: '15px', color: '#667eea' }}>Ziel-Gruppen</h4>
              
              <div className="form-group">
                <label>Ziel-Gruppen (mehrere auswählbar)</label>
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
                        padding: '5px',
                        cursor: 'pointer',
                        borderRadius: '3px',
                        marginBottom: '3px',
                        backgroundColor: bulkConfig.target_group_ids.includes(group.id) ? '#e3f2fd' : 'transparent'
                      }}>
                        <input
                          type="checkbox"
                          checked={bulkConfig.target_group_ids.includes(group.id)}
                          onChange={() => {
                            const currentIds = bulkConfig.target_group_ids
                            if (currentIds.includes(group.id)) {
                              setBulkConfig({
                                ...bulkConfig,
                                target_group_ids: currentIds.filter(id => id !== group.id)
                              })
                            } else {
                              setBulkConfig({
                                ...bulkConfig,
                                target_group_ids: [...currentIds, group.id]
                              })
                            }
                          }}
                          style={{ marginRight: '8px' }}
                        />
                        {group.name}
                      </label>
                    ))
                  )}
                </div>
                {bulkConfig.target_group_ids.length > 0 && (
                  <p style={{ marginTop: '5px', fontSize: '0.9rem', color: '#667eea' }}>
                    {bulkConfig.target_group_ids.length} Gruppe(n) ausgewählt
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
                  value={bulkConfig.delay}
                  onChange={(e) => setBulkConfig({ ...bulkConfig, delay: e.target.value })}
                />
              </div>
              
              <button
                className="btn btn-success"
                onClick={handleBulkForward}
                disabled={forwarding || !bulkConfig.account_id || !bulkConfig.message_ids.trim() || bulkConfig.target_group_ids.length === 0}
                style={{ width: '100%', marginTop: '10px', padding: '12px' }}
              >
                {forwarding ? '⏳ Leite weiter...' : `📤 Bulk-Weiterleitung starten`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Message Preview Modal */}
      {showPreview && previewMessage && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Nachricht-Vorschau</h3>
              <button className="close-btn" onClick={() => setShowPreview(false)}>×</button>
            </div>
            <div style={{ padding: '20px' }}>
              <p><strong>Message-ID:</strong> <code>{previewMessage.id}</code></p>
              <p><strong>Datum:</strong> {previewMessage.date ? new Date(previewMessage.date).toLocaleString('de-DE') : '-'}</p>
              <p><strong>Typ:</strong> 
                {previewMessage.is_reply && ' ↩️ Antwort'}
                {previewMessage.is_forward && ' ↪️ Weitergeleitet'}
                {previewMessage.media && ' 📎 Medien'}
                {!previewMessage.is_reply && !previewMessage.is_forward && !previewMessage.media && ' 💬 Text'}
              </p>
              <div style={{ marginTop: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                <strong>Text:</strong>
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', marginTop: '10px' }}>
                  {previewMessage.text || '(kein Text)'}
                </pre>
              </div>
              <button
                className="btn btn-primary"
                style={{ marginTop: '20px', width: '100%' }}
                onClick={() => setShowPreview(false)}
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
