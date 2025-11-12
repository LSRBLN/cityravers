import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import UserProfile from './components/UserProfile'
import AccountManager from './components/AccountManager'
import GroupManager from './components/GroupManager'
import ScheduledMessages from './components/ScheduledMessages'
import UserScraper from './components/UserScraper'
import MessageForwarder from './components/MessageForwarder'
import AccountWarmer from './components/AccountWarmer'
import MessageTemplates from './components/MessageTemplates'
import ProxyManager from './components/ProxyManager'
import AccountToGroups from './components/AccountToGroups'
import SubscriptionPlans from './components/SubscriptionPlans'
import AdminDashboard from './components/AdminDashboard'
import './App.css'

const API_BASE = '/api'

function App() {
  const { isAuthenticated, loading: authLoading, user } = useAuth()
  const [activeTab, setActiveTab] = useState('accounts')
  const isAdmin = user?.is_admin || false
  const [accounts, setAccounts] = useState([])
  const [groups, setGroups] = useState([])
  const [scheduledMessages, setScheduledMessages] = useState([])
  const [proxies, setProxies] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchAccounts = async () => {
    try {
      // Prüfe ob Token vorhanden ist
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('Kein Token vorhanden, überspringe fetchAccounts')
        return
      }
      const response = await axios.get(`${API_BASE}/accounts`)
      setAccounts(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Accounts:', error)
      }
    }
  }

  const fetchGroups = async () => {
    try {
      // Prüfe ob Token vorhanden ist
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('Kein Token vorhanden, überspringe fetchGroups')
        return
      }
      const response = await axios.get(`${API_BASE}/groups`)
      setGroups(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Gruppen:', error)
      }
    }
  }

  const fetchProxies = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return
      const response = await axios.get(`${API_BASE}/proxies`)
      setProxies(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der Proxies:', error)
      }
    }
  }

  const fetchScheduledMessages = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return
      const response = await axios.get(`${API_BASE}/scheduled-messages`)
      setScheduledMessages(response.data)
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Fehler beim Laden der geplanten Nachrichten:', error)
      }
    }
  }

  useEffect(() => {
    // Nur laden wenn authentifiziert UND nicht mehr im Loading-State UND Token vorhanden
    const token = localStorage.getItem('token')
    if (isAuthenticated && !authLoading && user && token) {
      // Kurze Verzögerung, um sicherzustellen, dass Token in Headers gesetzt ist
      const timer = setTimeout(() => {
        fetchAccounts()
        fetchGroups()
        fetchScheduledMessages()
        fetchProxies()
      }, 200)
      
      // Auto-Refresh alle 5 Sekunden
      const interval = setInterval(() => {
        fetchScheduledMessages()
      }, 5000)
      
      return () => {
        clearTimeout(timer)
        clearInterval(interval)
      }
    }
  }, [isAuthenticated, authLoading, user])

  // Zeige Login wenn nicht authentifiziert
  if (authLoading) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <p>Lädt...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <div className="container">
      <div className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h1>🎵 Berlin City Raver - Marketing Tool</h1>
            <p>Verwaltung für Accountauswahl, Gruppenauswahl und Zeitplanung</p>
          </div>
          <UserProfile />
        </div>
        <div className="warning">
          ⚠️ <strong>Warnung:</strong> Spam verstößt gegen Telegram Nutzungsbedingungen. 
          Nur für legitime Zwecke verwenden. Kann zu Account-Sperrungen führen.
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('accounts')}
        >
          👤 Accounts
        </button>
        <button
          className={`tab ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('groups')}
        >
          👥 Gruppen
        </button>
        <button
          className={`tab ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => setActiveTab('messages')}
        >
          📅 Geplante Nachrichten
        </button>
        <button
          className={`tab ${activeTab === 'scraper' ? 'active' : ''}`}
          onClick={() => setActiveTab('scraper')}
        >
          👥 User-Scraping
        </button>
        <button
          className={`tab ${activeTab === 'forwarder' ? 'active' : ''}`}
          onClick={() => setActiveTab('forwarder')}
        >
          📤 Weiterleiten
        </button>
        <button
          className={`tab ${activeTab === 'warmer' ? 'active' : ''}`}
          onClick={() => setActiveTab('warmer')}
        >
          🔥 Account-Warmer
        </button>
        <button
          className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          📝 Vorlagen
        </button>
        <button
          className={`tab ${activeTab === 'proxies' ? 'active' : ''}`}
          onClick={() => setActiveTab('proxies')}
        >
          🔒 Proxies
        </button>
        <button
          className={`tab ${activeTab === 'account-to-groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('account-to-groups')}
        >
          👤→👥 Account zu Gruppen
        </button>
        <button
          className={`tab ${activeTab === 'subscriptions' ? 'active' : ''}`}
          onClick={() => setActiveTab('subscriptions')}
        >
          📦 Pakete
        </button>
        {isAdmin && (
          <button
            className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
            style={{ background: '#ffc107', color: '#333', fontWeight: 'bold' }}
          >
            🔐 Admin Console
          </button>
        )}
      </div>

      {activeTab === 'accounts' && (
        <AccountManager
          accounts={accounts}
          proxies={proxies}
          onUpdate={() => {
            fetchAccounts()
            fetchProxies()
          }}
        />
      )}

      {activeTab === 'groups' && (
        <GroupManager
          groups={groups}
          accounts={accounts}
          onUpdate={fetchGroups}
        />
      )}

      {activeTab === 'messages' && (
        <ScheduledMessages
          scheduledMessages={scheduledMessages}
          accounts={accounts}
          groups={groups}
          onUpdate={fetchScheduledMessages}
        />
      )}

      {activeTab === 'scraper' && (
        <UserScraper
          accounts={accounts}
          groups={groups}
          onUpdate={() => {
            fetchAccounts()
            fetchGroups()
          }}
        />
      )}

      {activeTab === 'forwarder' && (
        <MessageForwarder
          accounts={accounts}
          groups={groups}
          onUpdate={() => {
            fetchAccounts()
            fetchGroups()
          }}
        />
      )}

      {activeTab === 'warmer' && (
        <AccountWarmer
          accounts={accounts}
          onUpdate={fetchAccounts}
        />
      )}

      {activeTab === 'templates' && (
        <MessageTemplates />
      )}

      {activeTab === 'proxies' && (
        <ProxyManager
          accounts={accounts}
          onUpdate={() => {
            fetchAccounts()
            fetchProxies()
          }}
        />
      )}

      {activeTab === 'account-to-groups' && (
        <AccountToGroups
          accounts={accounts}
          groups={groups}
          onUpdate={() => {
            fetchAccounts()
            fetchGroups()
          }}
        />
      )}

      {activeTab === 'subscriptions' && (
        <SubscriptionPlans />
      )}

      {activeTab === 'admin' && isAdmin && (
        <AdminDashboard />
      )}
    </div>
  )
}

export default App

