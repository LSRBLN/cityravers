import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'
import './DialogViewer.css'

export default function DialogViewer({ accountId, onClose }) {
  const [dialogs, setDialogs] = useState([])
  const [selectedDialog, setSelectedDialog] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const messagesEndRef = useRef(null)
  const messagesContainerRef = useRef(null)

  useEffect(() => {
    loadDialogs()
  }, [accountId])

  useEffect(() => {
    if (selectedDialog) {
      loadMessages(selectedDialog.id)
    }
  }, [selectedDialog])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadDialogs = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/accounts/${accountId}/dialogs`)
      setDialogs(response.data)
    } catch (error) {
      alert('Fehler beim Laden der Dialoge: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const loadMessages = async (dialogId) => {
    setLoading(true)
    try {
      const response = await axios.get(
        `${API_BASE}/accounts/${accountId}/dialogs/${dialogId}/messages?limit=100`
      )
      setMessages(response.data.messages || [])
    } catch (error) {
      alert('Fehler beim Laden der Nachrichten: ' + (error.response?.data?.detail || error.message))
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !selectedDialog) return

    setSending(true)
    try {
      await axios.post(
        `${API_BASE}/accounts/${accountId}/dialogs/${selectedDialog.id}/send`,
        { message: newMessage.trim() }
      )
      setNewMessage('')
      // Nachrichten neu laden
      await loadMessages(selectedDialog.id)
    } catch (error) {
      alert('Fehler beim Senden: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSending(false)
    }
  }

  const getDialogTypeIcon = (type) => {
    switch (type) {
      case 'private':
        return '👤'
      case 'group':
        return '👥'
      case 'channel':
        return '📢'
      case 'supergroup':
        return '💬'
      default:
        return '💬'
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'gerade eben'
    if (minutes < 60) return `vor ${minutes} Min`
    if (hours < 24) return `vor ${hours} Std`
    if (days < 7) return `vor ${days} Tag${days > 1 ? 'en' : ''}`
    return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  const filteredDialogs = dialogs.filter(dialog =>
    dialog.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dialog.username?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="dialog-viewer-overlay" onClick={onClose}>
      <div className="dialog-viewer-container" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-viewer-header">
          <h2>💬 Dialoge</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="dialog-viewer-content">
          {/* Dialog-Liste */}
          <div className="dialog-list-panel">
            <div className="dialog-search">
              <input
                type="text"
                placeholder="🔍 Dialoge durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="dialog-search-input"
              />
            </div>
            <div className="dialog-list">
              {loading && !selectedDialog ? (
                <div className="loading">Lädt Dialoge...</div>
              ) : filteredDialogs.length === 0 ? (
                <div className="empty-state">Keine Dialoge gefunden</div>
              ) : (
                filteredDialogs.map((dialog) => (
                  <div
                    key={dialog.id}
                    className={`dialog-item ${selectedDialog?.id === dialog.id ? 'active' : ''}`}
                    onClick={() => setSelectedDialog(dialog)}
                  >
                    <div className="dialog-item-icon">
                      {getDialogTypeIcon(dialog.type)}
                    </div>
                    <div className="dialog-item-content">
                      <div className="dialog-item-name">{dialog.name || 'Unbekannt'}</div>
                      <div className="dialog-item-meta">
                        {dialog.type === 'private' && dialog.username && `@${dialog.username}`}
                        {dialog.type === 'group' && dialog.participants_count && `${dialog.participants_count} Mitglieder`}
                        {dialog.type === 'channel' && dialog.username && `@${dialog.username}`}
                        {dialog.type === 'supergroup' && dialog.username && `@${dialog.username}`}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Nachrichten-Panel */}
          <div className="messages-panel">
            {selectedDialog ? (
              <>
                <div className="messages-header">
                  <div className="messages-header-info">
                    <span className="messages-header-icon">
                      {getDialogTypeIcon(selectedDialog.type)}
                    </span>
                    <div>
                      <div className="messages-header-name">{selectedDialog.name || 'Unbekannt'}</div>
                      <div className="messages-header-meta">
                        {selectedDialog.type === 'private' && selectedDialog.username && `@${selectedDialog.username}`}
                        {selectedDialog.type === 'group' && selectedDialog.participants_count && `${selectedDialog.participants_count} Mitglieder`}
                        {selectedDialog.type === 'channel' && selectedDialog.username && `@${selectedDialog.username}`}
                        {selectedDialog.type === 'supergroup' && selectedDialog.username && `@${selectedDialog.username}`}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="messages-container" ref={messagesContainerRef}>
                  {loading ? (
                    <div className="loading">Lädt Nachrichten...</div>
                  ) : messages.length === 0 ? (
                    <div className="empty-state">Keine Nachrichten</div>
                  ) : (
                    messages.map((msg) => (
                      <div key={msg.id} className="message-item">
                        <div className="message-content">
                          <div className="message-text">{msg.text || '(Medien)'}</div>
                          <div className="message-meta">
                            {msg.date && formatDate(msg.date)}
                            {msg.media && ' 📎'}
                            {msg.is_reply && ' ↩️'}
                            {msg.is_forward && ' 🔄'}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>

                <form className="message-input-form" onSubmit={handleSendMessage}>
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Nachricht schreiben..."
                    className="message-input"
                    disabled={sending}
                  />
                  <button
                    type="submit"
                    className="btn btn-primary send-btn"
                    disabled={sending || !newMessage.trim()}
                  >
                    {sending ? '⏳' : '📤'}
                  </button>
                </form>
              </>
            ) : (
              <div className="messages-placeholder">
                <div className="placeholder-icon">💬</div>
                <div className="placeholder-text">Wähle einen Dialog aus</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

