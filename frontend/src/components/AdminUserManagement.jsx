import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './AdminDashboard.css'

import { API_BASE } from '../config/api'

function AdminUserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState(null)
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    is_active: true,
    is_admin: false
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setLoading(false)
        return
      }
      // Interceptor fügt Token automatisch hinzu
      const response = await axios.get(`${API_BASE}/admin/users`)
      setUsers(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Benutzer:', error)
        alert('Fehler beim Laden der Benutzer')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (user) => {
    setSelectedUser(user)
    setFormData({
      email: user.email,
      username: user.username,
      password: '',
      is_active: user.is_active,
      is_admin: user.is_admin
    })
    setEditMode(true)
  }

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Kein Token vorhanden')
        return
      }
      const updateData = { ...formData }
      if (!updateData.password) {
        delete updateData.password
      }
      // Interceptor fügt Token automatisch hinzu
      await axios.put(`${API_BASE}/admin/users/${selectedUser.id}`, updateData)
      alert('Benutzer erfolgreich aktualisiert')
      setEditMode(false)
      setSelectedUser(null)
      fetchUsers()
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Aktualisieren:', error)
        alert(error.response?.data?.detail || 'Fehler beim Aktualisieren')
      }
    }
  }

  const handleDelete = async (userId) => {
    if (!confirm('Möchten Sie diesen Benutzer wirklich löschen?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Kein Token vorhanden')
        return
      }
      // Interceptor fügt Token automatisch hinzu
      await axios.delete(`${API_BASE}/admin/users/${userId}`)
      alert('Benutzer erfolgreich gelöscht')
      fetchUsers()
    } catch (error) {
      console.error('Fehler beim Löschen:', error)
      alert(error.response?.data?.detail || 'Fehler beim Löschen')
    }
  }

  if (loading) {
    return <div className="admin-loading">Lade Benutzer...</div>
  }

  return (
    <div className="admin-user-management">
      <h2>Benutzerverwaltung</h2>
      
      {editMode && selectedUser ? (
        <div className="edit-user-form">
          <h3>Benutzer bearbeiten: {selectedUser.username}</h3>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Username:</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Neues Passwort (leer lassen zum Beibehalten):</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              Aktiv
            </label>
          </div>
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_admin}
                onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
              />
              Admin
            </label>
          </div>
          <div className="form-actions">
            <button onClick={handleSave} className="btn-primary">Speichern</button>
            <button onClick={() => { setEditMode(false); setSelectedUser(null) }} className="btn-secondary">Abbrechen</button>
          </div>
        </div>
      ) : (
        <div className="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Username</th>
                <th>Status</th>
                <th>Rolle</th>
                <th>Accounts</th>
                <th>Gruppen</th>
                <th>Erstellt</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.email}</td>
                  <td>{user.username}</td>
                  <td>
                    <span className={user.is_active ? 'badge-active' : 'badge-inactive'}>
                      {user.is_active ? '✅ Aktiv' : '❌ Inaktiv'}
                    </span>
                  </td>
                  <td>
                    {user.is_admin && <span className="badge-admin">👑 Admin</span>}
                  </td>
                  <td>{user.account_count}</td>
                  <td>{user.group_count}</td>
                  <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
                  <td>
                    <button onClick={() => handleEdit(user)} className="btn-small">✏️ Bearbeiten</button>
                    <button onClick={() => handleDelete(user.id)} className="btn-small btn-danger">🗑️ Löschen</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default AdminUserManagement

