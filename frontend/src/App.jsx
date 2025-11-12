import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from './contexts/AuthContext'
import { useDevice } from './hooks/useDevice'
import Login from './components/Login'
import UserProfile from './components/UserProfile'
import DropdownMenu from './components/DropdownMenu'
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

import { API_BASE } from './config/api'

function App() {
  const { isAuthenticated, loading: authLoading, user } = useAuth()
  const { isMobile, isTablet, isDesktop } = useDevice()
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
    <div className={`container ${isMobile ? 'mobile' : ''} ${isTablet ? 'tablet' : ''}`}>
      <div className="professional-header">
        <div className="professional-header-content">
          <div className={`header-content ${isMobile ? 'mobile' : ''}`}>
            <div className="header-title">
              <h1 style={{ margin: 0 }}>Berlin City Raver - Marketing Tool</h1>
              {!isMobile && <p>Verwaltung für Accountauswahl, Gruppenauswahl und Zeitplanung</p>}
              {/* Logo unter dem Tool-Namen */}
              <div style={{ 
                marginTop: 'var(--spacing-md)',
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: 'center'
              }}>
                <img 
                  src="/logo.png" 
                  alt="Berlin City Raver Logo" 
                  style={{ 
                    height: isMobile ? '288px' : '384px',
                    width: 'auto',
                    borderRadius: 'var(--radius-md)',
                    boxShadow: 'var(--shadow-lg)',
                    background: 'rgba(255, 255, 255, 0.95)',
                    padding: '8px',
                    display: 'block'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              </div>
            </div>
            <UserProfile />
          </div>
        </div>
      </div>

      <div className="warning-banner-modern">
        <svg fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        <div>
          <strong>Warnung:</strong> Spam verstößt gegen Telegram Nutzungsbedingungen. 
          Vorsichtig verwenden. Kann zu Account-Sperrungen führen.
        </div>
      </div>

      {/* Dropdown Menu */}
      <div style={{ marginBottom: 'var(--spacing-2xl)' }}>
        <DropdownMenu 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          isAdmin={isAdmin}
        />
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

      {/* Copyright Footer */}
      <div style={{
        marginTop: 'var(--spacing-3xl)',
        padding: 'var(--spacing-lg)',
        textAlign: 'center',
        color: 'var(--gray-600)',
        fontSize: '0.875rem',
        borderTop: '1px solid var(--gray-200)'
      }}>
        <p style={{ margin: 0 }}>
          Programmiert von der{' '}
          <a 
            href="https://www.phnxvision.de" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              color: 'var(--primary-600)',
              textDecoration: 'none',
              fontWeight: 600
            }}
          >
            PhnxVision Marketing Agentur
          </a>
        </p>
      </div>
    </div>
  )
}

export default App

