import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

export default function MessageTemplates({ onTemplateSelect, accounts, groups }) {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [showLoadFromMessageModal, setShowLoadFromMessageModal] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    message: '',
    category: '',
    tags: ''
  })
  const [loadFromMessageData, setLoadFromMessageData] = useState({
    account_id: '',
    source_group: '',
    message_id: '',
    template_name: '',
    category: '',
    tags: ''
  })
  const [loadingFromMessage, setLoadingFromMessage] = useState(false)
  const [filterCategory, setFilterCategory] = useState('')

  useEffect(() => {
    loadTemplates()
  }, [filterCategory])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterCategory) params.category = filterCategory
      const response = await axios.get(`${API_BASE}/message-templates`, { params })
      setTemplates(response.data)
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
      const tags = formData.tags.split(',').map(t => t.trim()).filter(t => t)
      
      if (selectedTemplate) {
        await axios.put(`${API_BASE}/message-templates/${selectedTemplate.id}`, {
          name: formData.name,
          message: formData.message,
          category: formData.category || null,
          tags: tags.length > 0 ? tags : null
        })
      } else {
        await axios.post(`${API_BASE}/message-templates`, {
          name: formData.name,
          message: formData.message,
          category: formData.category || null,
          tags: tags.length > 0 ? tags : null
        })
      }
      
      setShowModal(false)
      setSelectedTemplate(null)
      setFormData({ name: '', message: '', category: '', tags: '' })
      loadTemplates()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (template) => {
    setSelectedTemplate(template)
    setFormData({
      name: template.name,
      message: template.message,
      category: template.category || '',
      tags: (template.tags || []).join(', ')
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Wirklich löschen?')) return
    
    try {
      await axios.delete(`${API_BASE}/message-templates/${id}`)
      loadTemplates()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleToggleActive = async (template) => {
    try {
      await axios.put(`${API_BASE}/message-templates/${template.id}`, {
        is_active: !template.is_active
      })
      loadTemplates()
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    }
  }

  const categories = [...new Set(templates.map(t => t.category).filter(Boolean))]

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Nachrichtenvorlagen</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              style={{ padding: '8px', borderRadius: '5px', border: '2px solid #e0e0e0' }}
            >
              <option value="">Alle Kategorien</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <button className="btn btn-secondary" onClick={() => {
              setLoadFromMessageData({
                account_id: '',
                source_group: '',
                message_id: '',
                template_name: '',
                category: '',
                tags: ''
              })
              setShowLoadFromMessageModal(true)
            }}>
              📥 Aus Nachricht laden
            </button>
            <button className="btn btn-primary" onClick={() => {
              setSelectedTemplate(null)
              setFormData({ name: '', message: '', category: '', tags: '' })
              setShowModal(true)
            }}>
              + Neue Vorlage
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading">Lade Vorlagen...</div>
        ) : templates.length === 0 ? (
          <div className="empty-state">
            <p>Keine Vorlagen vorhanden. Erstelle eine neue Vorlage.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
            {templates.map(template => (
              <div key={template.id} className="card" style={{ padding: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{template.name}</h3>
                    {template.category && (
                      <span className="badge badge-info" style={{ marginTop: '5px' }}>
                        {template.category}
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    {template.is_active ? (
                      <span className="badge badge-success">Aktiv</span>
                    ) : (
                      <span className="badge badge-secondary">Inaktiv</span>
                    )}
                  </div>
                </div>
                
                <p style={{ 
                  margin: '10px 0', 
                  fontSize: '0.9rem', 
                  color: '#666',
                  maxHeight: '100px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {template.message}
                </p>
                
                {template.tags && template.tags.length > 0 && (
                  <div style={{ marginBottom: '10px' }}>
                    {template.tags.map((tag, idx) => (
                      <span key={idx} className="badge badge-secondary" style={{ marginRight: '5px', fontSize: '0.75rem' }}>
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '0.85rem', color: '#999' }}>
                  <span>Verwendet: {template.usage_count}x</span>
                  <span>{new Date(template.created_at).toLocaleDateString('de-DE')}</span>
                </div>
                
                <div style={{ display: 'flex', gap: '5px', marginTop: '10px' }}>
                  {onTemplateSelect && (
                    <button
                      className="btn btn-success btn-small"
                      onClick={() => onTemplateSelect(template)}
                    >
                      Verwenden
                    </button>
                  )}
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => handleEdit(template)}
                  >
                    Bearbeiten
                  </button>
                  <button
                    className="btn btn-warning btn-small"
                    onClick={() => handleToggleActive(template)}
                  >
                    {template.is_active ? 'Deaktivieren' : 'Aktivieren'}
                  </button>
                  <button
                    className="btn btn-danger btn-small"
                    onClick={() => handleDelete(template.id)}
                  >
                    Löschen
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal: Vorlage aus Nachricht laden */}
      {showLoadFromMessageModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>Vorlage aus Nachricht erstellen</h3>
              <button className="close-btn" onClick={() => {
                setShowLoadFromMessageModal(false)
                setLoadFromMessageData({
                  account_id: '',
                  source_group: '',
                  message_id: '',
                  template_name: '',
                  category: '',
                  tags: ''
                })
              }}>×</button>
            </div>
            <form onSubmit={async (e) => {
              e.preventDefault()
              if (!loadFromMessageData.account_id || !loadFromMessageData.source_group || !loadFromMessageData.message_id || !loadFromMessageData.template_name) {
                alert('Bitte alle Pflichtfelder ausfüllen')
                return
              }
              
              setLoadingFromMessage(true)
              try {
                const tags = loadFromMessageData.tags.split(',').map(t => t.trim()).filter(t => t)
                
                const response = await axios.post(`${API_BASE}/message-templates/from-message`, {
                  account_id: parseInt(loadFromMessageData.account_id),
                  source_group: loadFromMessageData.source_group,
                  message_id: loadFromMessageData.message_id,
                  template_name: loadFromMessageData.template_name,
                  category: loadFromMessageData.category || null,
                  tags: tags.length > 0 ? tags : null
                })
                
                alert(`✅ Vorlage erfolgreich erstellt!\n\nVorschau:\n${response.data.message_preview}`)
                setShowLoadFromMessageModal(false)
                setLoadFromMessageData({
                  account_id: '',
                  source_group: '',
                  message_id: '',
                  template_name: '',
                  category: '',
                  tags: ''
                })
                loadTemplates()
              } catch (error) {
                alert('Fehler: ' + (error.response?.data?.detail || error.message))
              } finally {
                setLoadingFromMessage(false)
              }
            }}>
              <div className="form-group">
                <label>Account *</label>
                <select
                  required
                  value={loadFromMessageData.account_id}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, account_id: e.target.value })}
                >
                  <option value="">Bitte wählen...</option>
                  {accounts && accounts.filter(acc => acc.connected && acc.account_type === 'user').map(acc => (
                    <option key={acc.id} value={acc.id}>{acc.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Quell-Gruppe (Chat-ID oder Username) *</label>
                <input
                  type="text"
                  required
                  value={loadFromMessageData.source_group}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, source_group: e.target.value })}
                  placeholder="z.B. -1001234567890 oder @gruppenname"
                />
                {groups && groups.length > 0 && (
                  <select
                    style={{ marginTop: '5px' }}
                    onChange={(e) => {
                      if (e.target.value) {
                        const group = groups.find(g => g.id === parseInt(e.target.value))
                        if (group) {
                          setLoadFromMessageData({ ...loadFromMessageData, source_group: group.chat_id || group.username || e.target.value })
                        }
                      }
                    }}
                  >
                    <option value="">Oder aus Liste wählen...</option>
                    {groups.map(group => (
                      <option key={group.id} value={group.id}>
                        {group.name} ({group.chat_id || group.username || 'N/A'})
                      </option>
                    ))}
                  </select>
                )}
              </div>
              <div className="form-group">
                <label>Message ID *</label>
                <input
                  type="text"
                  required
                  value={loadFromMessageData.message_id}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, message_id: e.target.value })}
                  placeholder="z.B. 12345 oder 4053090"
                />
                <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                  Die Message ID findest du in der Telegram-App (Rechtsklick → Nachricht kopieren → Link)
                </small>
              </div>
              <div className="form-group">
                <label>Vorlagen-Name *</label>
                <input
                  type="text"
                  required
                  value={loadFromMessageData.template_name}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, template_name: e.target.value })}
                  placeholder="z.B. Willkommensnachricht"
                />
              </div>
              <div className="form-group">
                <label>Kategorie (optional)</label>
                <input
                  type="text"
                  value={loadFromMessageData.category}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, category: e.target.value })}
                  placeholder="z.B. marketing, info, announcement"
                />
              </div>
              <div className="form-group">
                <label>Tags (kommagetrennt, optional)</label>
                <input
                  type="text"
                  value={loadFromMessageData.tags}
                  onChange={(e) => setLoadFromMessageData({ ...loadFromMessageData, tags: e.target.value })}
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowLoadFromMessageModal(false)
                    setLoadFromMessageData({
                      account_id: '',
                      source_group: '',
                      message_id: '',
                      template_name: '',
                      category: '',
                      tags: ''
                    })
                  }}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={loadingFromMessage}>
                  {loadingFromMessage ? 'Lade...' : 'Vorlage erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>{selectedTemplate ? 'Vorlage bearbeiten' : 'Neue Vorlage'}</h3>
              <button className="close-btn" onClick={() => {
                setShowModal(false)
                setSelectedTemplate(null)
                setFormData({ name: '', message: '', category: '', tags: '' })
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
                  placeholder="z.B. Willkommensnachricht"
                />
              </div>
              <div className="form-group">
                <label>Nachricht</label>
                <textarea
                  required
                  rows="6"
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Nachrichtentext..."
                />
              </div>
              <div className="form-group">
                <label>Kategorie (optional)</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="z.B. marketing, info, announcement"
                />
              </div>
              <div className="form-group">
                <label>Tags (kommagetrennt, optional)</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowModal(false)
                    setSelectedTemplate(null)
                    setFormData({ name: '', message: '', category: '', tags: '' })
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
    </div>
  )
}

