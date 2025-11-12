import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './AdminDashboard.css'
import { API_BASE } from '../config/api'

function AdminSettings() {
  const [settings, setSettings] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [editingKey, setEditingKey] = useState(null)
  const [editValue, setEditValue] = useState('')

  useEffect(() => {
    fetchSettings()
  }, [category])

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setLoading(false)
        return
      }
      const params = category ? { category } : {}
      // Interceptor fügt Token automatisch hinzu
      const response = await axios.get(`${API_BASE}/admin/settings`, { params })
      setSettings(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Einstellungen:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (setting) => {
    setEditingKey(setting.key)
    setEditValue(setting.value)
  }

  const handleSave = async (key) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Kein Token vorhanden')
        return
      }
      // Interceptor fügt Token automatisch hinzu
      await axios.put(`${API_BASE}/admin/settings/${key}`, { value: editValue })
      alert('Einstellung erfolgreich aktualisiert')
      setEditingKey(null)
      fetchSettings()
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Speichern:', error)
        alert(error.response?.data?.detail || 'Fehler beim Speichern')
      }
    }
  }

  const handleDelete = async (key) => {
    if (!confirm(`Möchten Sie die Einstellung "${key}" wirklich löschen?`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Kein Token vorhanden')
        return
      }
      // Interceptor fügt Token automatisch hinzu
      await axios.delete(`${API_BASE}/admin/settings/${key}`)
      alert('Einstellung erfolgreich gelöscht')
      fetchSettings()
    } catch (error) {
      console.error('Fehler beim Löschen:', error)
      alert(error.response?.data?.detail || 'Fehler beim Löschen')
    }
  }

  const categories = ['general', 'api', 'security', 'features']
  const groupedSettings = settings.reduce((acc, setting) => {
    if (!acc[setting.category]) {
      acc[setting.category] = []
    }
    acc[setting.category].push(setting)
    return acc
  }, {})

  if (loading) {
    return <div className="admin-loading">Lade Einstellungen...</div>
  }

  return (
    <div className="admin-settings">
      <h2>System-Einstellungen</h2>
      
      <div className="category-filter">
        <label>Kategorie filtern:</label>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Alle</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {Object.entries(groupedSettings).map(([cat, catSettings]) => (
        <div key={cat} className="settings-category">
          <h3>{cat}</h3>
          <table>
            <thead>
              <tr>
                <th>Key</th>
                <th>Wert</th>
                <th>Typ</th>
                <th>Beschreibung</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {catSettings.map((setting) => (
                <tr key={setting.id}>
                  <td><code>{setting.key}</code></td>
                  <td>
                    {editingKey === setting.key ? (
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        style={{ width: '100%' }}
                      />
                    ) : (
                      <code>{setting.value}</code>
                    )}
                  </td>
                  <td>{setting.value_type}</td>
                  <td>{setting.description || '-'}</td>
                  <td>
                    {editingKey === setting.key ? (
                      <>
                        <button onClick={() => handleSave(setting.key)} className="btn-small">✅ Speichern</button>
                        <button onClick={() => setEditingKey(null)} className="btn-small">❌ Abbrechen</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => handleEdit(setting)} className="btn-small">✏️ Bearbeiten</button>
                        <button onClick={() => handleDelete(setting.key)} className="btn-small btn-danger">🗑️ Löschen</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {settings.length === 0 && (
        <p className="no-data">Keine Einstellungen gefunden</p>
      )}
    </div>
  )
}

export default AdminSettings

