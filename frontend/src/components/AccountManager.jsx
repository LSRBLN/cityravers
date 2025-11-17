import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'
import DialogViewer from './DialogViewer'

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
  const [phoneCodeHash, setPhoneCodeHash] = useState(null) // Speichere phone_code_hash
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
  const [showCompletePackageModal, setShowCompletePackageModal] = useState(false)
  const [packageFormData, setPackageFormData] = useState({
    name: '',
    api_id: '',
    api_hash: '',
    two_factor_password: ''
  })
  const [packageFiles, setPackageFiles] = useState({
    session: null,
    tdata: null,
    json: null
  })
  const [showCreateBotModal, setShowCreateBotModal] = useState(false)
  const [createBotFormData, setCreateBotFormData] = useState({
    account_id: '',
    bot_name: '',
    bot_username: ''
  })
  const [showBulkCreateBotsModal, setShowBulkCreateBotsModal] = useState(false)
  const [bulkCreateBotsFormData, setBulkCreateBotsFormData] = useState({
    account_id: '',
    count: 10,
    name_prefix: 'Group Bot',
    username_prefix: 'group_bot',
    delay_between_bots: 3.0
  })
  const [bulkCreateBotsProgress, setBulkCreateBotsProgress] = useState(null)
  const [showAutoCreateModal, setShowAutoCreateModal] = useState(false)
  const [autoCreateFormData, setAutoCreateFormData] = useState({
    provider: '5sim',
    country: 'germany',
    service: 'telegram',
    max_accounts: 5,
    min_balance: ''
  })
  const [autoCreateProgress, setAutoCreateProgress] = useState(null)
  const [showSingleCreateModal, setShowSingleCreateModal] = useState(false)
  const [showDialogViewer, setShowDialogViewer] = useState(false)
  const [dialogAccountId, setDialogAccountId] = useState(null)
  const [singleCreateFormData, setSingleCreateFormData] = useState({
    provider: 'onlinesim',
    country: '',
    service: 'telegram'
  })
  const [countriesPrices, setCountriesPrices] = useState([])
  const [loadingPrices, setLoadingPrices] = useState(false)
  const [selectedPrice, setSelectedPrice] = useState(null)

  // Lade Länder und Preise
  const loadCountriesPrices = async (provider = 'onlinesim') => {
    setLoadingPrices(true)
    try {
      const response = await axios.get(`${API_BASE}/phone/countries-prices?provider=${provider}`)
      if (response.data.success) {
        setCountriesPrices(response.data.countries || [])
      }
    } catch (error) {
      console.error('Fehler beim Laden der Länder/Preise:', error)
      alert('Fehler beim Laden der Länder/Preise: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoadingPrices(false)
    }
  }

  // Öffne Single-Create-Modal und lade Preise
  const openSingleCreateModal = () => {
    setShowSingleCreateModal(true)
    setSingleCreateFormData({
      provider: 'onlinesim',
      country: '',
      service: 'telegram'
    })
    setSelectedPrice(null)
    loadCountriesPrices('onlinesim')
  }

  // Berechne Preis basierend auf Auswahl
  const calculatePrice = () => {
    if (!singleCreateFormData.country || !singleCreateFormData.service) return null
    const country = countriesPrices.find(c => c.country_code === singleCreateFormData.country || 
      c.country_name.toLowerCase() === singleCreateFormData.country.toLowerCase())
    if (!country) return null
    
    if (singleCreateFormData.service === 'telegram') {
      return country.telegram_price
    } else if (singleCreateFormData.service === 'whatsapp') {
      return country.whatsapp_price
    }
    return null
  }

  // Handle Single Account Creation
  const handleSingleCreate = async (e) => {
    e.preventDefault()
    if (!singleCreateFormData.country) {
      alert('Bitte wähle ein Land aus')
      return
    }
    
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/accounts/create-single`, singleCreateFormData)
      
      if (response.data.success) {
        alert(response.data.message || '✅ Account erfolgreich erstellt!')
        setShowSingleCreateModal(false)
        setSingleCreateFormData({ provider: 'onlinesim', country: '', service: 'telegram' })
        setSelectedPrice(null)
        onUpdate()
      } else {
        alert(response.data.error || response.data.message || 'Fehler bei der Account-Erstellung')
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

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
        const message = response.data.message || '✅ Code wurde über Telegram gesendet. Prüfe deine Telegram-App!'
        alert(message)
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
        // Speichere phone_code_hash für späteren Login
        if (response.data.phone_code_hash) {
          setPhoneCodeHash(response.data.phone_code_hash)
        }
        const message = response.data.message || '✅ Code wurde über Telegram gesendet. Prüfe deine Telegram-App!'
        alert(message)
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
        // Speichere phone_code_hash für späteren Login
        if (response.data.phone_code_hash) {
          setPhoneCodeHash(response.data.phone_code_hash)
        }
        const message = response.data.message || '✅ Code wurde über Telegram gesendet. Prüfe deine Telegram-App!'
        alert(message)
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
        // Füge phone_code_hash hinzu, falls vorhanden
        if (phoneCodeHash) {
          loginPayload.phone_code_hash = phoneCodeHash
        }
      } else if (loginStep === 'password' && loginPassword) {
        loginPayload.password = loginPassword
      } else {
        // Wenn kein Code vorhanden ist, fordere einen an
        if (loginStep === 'code' && !loginCode) {
          try {
            const codeResponse = await axios.post(`${API_BASE}/accounts/${loginAccountId}/request-code`)
            if (codeResponse.data.status === 'code_required') {
              // Speichere phone_code_hash
              if (codeResponse.data.phone_code_hash) {
                setPhoneCodeHash(codeResponse.data.phone_code_hash)
              }
              const message = codeResponse.data.message || '✅ Code wurde über Telegram gesendet. Prüfe deine Telegram-App!'
              alert(message)
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
        setPhoneCodeHash(null) // Lösche Hash nach erfolgreichem Login
        onUpdate()
      } else if (response.data.status === 'password_required') {
        setLoginStep('password')
        alert('⚠️ Zwei-Faktor-Authentifizierung aktiviert. Bitte Passwort eingeben.')
      } else if (response.data.status === 'code_required') {
        // Code wurde erneut angefordert (z.B. weil der alte Code ungültig war)
        setLoginCode('') // Lösche alten Code
        const message = response.data.message || '⚠️ Code wurde erneut angefordert. Prüfe deine Telegram-App!'
        alert(message)
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
              // Speichere neuen phone_code_hash
              if (codeResponse.data.phone_code_hash) {
                setPhoneCodeHash(codeResponse.data.phone_code_hash)
              }
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
      if (response.data.length === 0) {
        alert('Keine Dialoge gefunden.')
        return
      }
      setDialogAccountId(accountId)
      setShowDialogViewer(true)
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
      
      // Prüfe ob es eine ZIP-Datei ist
      const zipFile = files.find(f => f.name.endsWith('.zip'))
      if (zipFile && files.length === 1) {
        // ZIP-Datei hochladen
        formData.append('file', zipFile)
      } else {
        // Einzelne Dateien hochladen
        files.forEach(file => {
          formData.append('files', file)
        })
      }
      
      const response = await axios.post(`${API_BASE}/upload/tdata`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.success) {
        setTdataPath(response.data.tdata_path)
        setTdataFiles(response.data.files || [])
        alert(response.data.message || `✅ tdata erfolgreich hochgeladen! ${response.data.file_count || response.data.files.length} Dateien.`)
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCompletePackageSubmit = async (e) => {
    e.preventDefault()
    if (!packageFormData.name) {
      alert('Bitte Account-Namen eingeben')
      return
    }
    
    if (!packageFiles.session && !packageFiles.tdata && !packageFiles.json) {
      alert('Bitte mindestens eine Datei hochladen (SESSION empfohlen)')
      return
    }
    
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('name', packageFormData.name)
      
      if (packageFiles.session) {
        formData.append('session_file', packageFiles.session)
      }
      if (packageFiles.tdata) {
        formData.append('tdata_zip', packageFiles.tdata)
      }
      if (packageFiles.json) {
        formData.append('json_file', packageFiles.json)
      }
      if (packageFormData.two_factor_password) {
        formData.append('two_factor_password', packageFormData.two_factor_password)
      }
      if (packageFormData.api_id) {
        formData.append('api_id', packageFormData.api_id)
      }
      if (packageFormData.api_hash) {
        formData.append('api_hash', packageFormData.api_hash)
      }
      
      const response = await axios.post(`${API_BASE}/accounts/from-complete-package`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.success) {
        let message = response.data.message || '✅ Account erfolgreich importiert!'
        if (response.data.connection_status === 'connected') {
          message += '\n✅ Account wurde automatisch verbunden!'
        } else if (response.data.connection_status) {
          message += `\n⚠️ Verbindungsstatus: ${response.data.connection_status}`
        }
        if (response.data.has_2fa) {
          message += '\n🔒 2FA-Passwort wurde gespeichert'
        }
        alert(message)
        setShowCompletePackageModal(false)
        setPackageFormData({ name: '', api_id: '', api_hash: '', two_factor_password: '' })
        setPackageFiles({ session: null, tdata: null, json: null })
        onUpdate()
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleTdataSubmit = async (e) => {
    e.preventDefault()
    if (!tdataPath) {
      alert('Bitte zuerst tdata-Dateien hochladen')
      return
    }
    
    if (!tdataFormData.name) {
      alert('Bitte Account-Namen eingeben')
      return
    }
    
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('name', tdataFormData.name)
      formData.append('tdata_path', tdataPath)
      if (tdataFormData.api_id) {
        formData.append('api_id', tdataFormData.api_id)
      }
      if (tdataFormData.api_hash) {
        formData.append('api_hash', tdataFormData.api_hash)
      }
      
      const response = await axios.post(`${API_BASE}/accounts/from-tdata`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.success) {
        alert(response.data.message || '✅ Account aus tdata erstellt!')
        setShowTdataModal(false)
        setTdataPath('')
        setTdataFiles([])
        setTdataFormData({ name: '', api_id: '', api_hash: '' })
        onUpdate()
      }
    } catch (error) {
      alert('Fehler: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
      <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <h2 style={{ margin: 0, color: 'var(--gray-900)' }}>Account-Verwaltung</h2>
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
          <button 
            className="btn btn-success" 
            onClick={() => {
              const userAccounts = accounts.filter(acc => acc.account_type === 'user' && acc.connected)
              if (userAccounts.length === 0) {
                alert('Keine verbundenen User-Accounts vorhanden. Bitte zuerst einen Account verbinden.')
                return
              }
              setBulkCreateBotsFormData({
                account_id: userAccounts[0].id.toString(),
                count: 10,
                name_prefix: 'Group Bot',
                username_prefix: 'group_bot',
                delay_between_bots: 3.0
              })
              setShowBulkCreateBotsModal(true)
            }}
            title="Erstelle mehrere Bots mit automatisch generierten Namen"
          >
            🤖🤖 Mehrere Bots erstellen
          </button>
          <button className="btn btn-secondary" onClick={() => setShowSessionModal(true)}>
            📁 Session-Datei
          </button>
          <button className="btn btn-secondary" onClick={() => setShowTdataModal(true)}>
            📂 tdata
          </button>
          <button 
            className="btn btn-success" 
            onClick={() => setShowCompletePackageModal(true)}
            title="Importiere komplettes Paket (TDATA + SESSION + JSON + 2FA)"
          >
            📦 Komplettes Paket
          </button>
          <button 
            className="btn btn-success" 
            onClick={openSingleCreateModal}
            title="Erstelle einen einzelnen Account mit automatischem Nummernkauf"
          >
            ➕ Account erstellen
          </button>
          <button 
            className="btn btn-info" 
            onClick={() => setShowAutoCreateModal(true)}
            title="Automatisch mehrere Accounts erstellen (kauft Nummern und erstellt Accounts)"
          >
            ⚡ Bulk-Erstellung
          </button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Manuell
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
              <tr 
                key={account.id}
                style={{
                  backgroundColor: account.connected ? 'rgba(76, 175, 80, 0.05)' : 'transparent',
                  borderLeft: account.connected ? '4px solid #4CAF50' : '4px solid transparent'
                }}
              >
                <td style={{ color: 'var(--gray-900)', fontWeight: account.connected ? '600' : 'normal' }}>
                  {account.connected && <span style={{ marginRight: '8px', fontSize: '1.2em' }}>✅</span>}
                  {account.name}
                </td>
                <td>
                  <span className={`badge ${account.account_type === 'bot' ? 'badge-info' : 'badge-secondary'}`}>
                    {account.account_type === 'bot' ? 'Bot' : 'User'}
                  </span>
                </td>
                  <td style={{ color: 'var(--gray-900)' }}>{account.phone_number || '-'}</td>
                  <td>
                    {account.connected ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <span className="badge badge-success" style={{ fontSize: '0.9em', padding: '6px 12px' }}>
                          ✅ Verbunden
                        </span>
                        <span style={{ fontSize: '0.75em', color: 'var(--gray-600)', fontStyle: 'italic' }}>
                          Bereit zur Nutzung
                        </span>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <span className="badge badge-warning" style={{ fontSize: '0.9em', padding: '6px 12px' }}>
                          ⚠️ Nicht verbunden
                        </span>
                        <span style={{ fontSize: '0.75em', color: 'var(--gray-600)', fontStyle: 'italic' }}>
                          Login erforderlich
                        </span>
                      </div>
                    )}
                  </td>
                  <td>
                    {account.proxy ? (
                      <span className="badge badge-info" title={`${account.proxy.host}:${account.proxy.port}`}>
                        🔒 {account.proxy.name}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--gray-500)' }}>-</span>
                    )}
                  </td>
                  <td>
                    {account.info ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ color: 'var(--gray-900)', fontWeight: '500' }}>
                          @{account.info.username || 'N/A'}
                        </span>
                        {account.info.first_name && (
                          <span style={{ fontSize: '0.85em', color: 'var(--gray-600)' }}>
                            {account.info.first_name} {account.info.last_name || ''}
                          </span>
                        )}
                      </div>
                    ) : account.connected ? (
                      <span style={{ color: 'var(--gray-500)', fontStyle: 'italic' }}>Info wird geladen...</span>
                    ) : (
                      <span style={{ color: 'var(--gray-400)' }}>-</span>
                    )}
                  </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                    {account.connected ? (
                      <>
                        <span 
                          className="badge badge-success" 
                          style={{ 
                            padding: '6px 10px', 
                            fontSize: '0.85em',
                            cursor: 'default',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                          title="Account ist bereits verbunden - kein Login nötig"
                        >
                          ✅ Bereit
                        </span>
                        {account.account_type === 'user' && (
                          <button
                            className="btn btn-secondary btn-small"
                            onClick={() => handleLoadDialogs(account.id)}
                            title="Dialoge anzeigen"
                          >
                            💬 Dialoge
                          </button>
                        )}
                      </>
                    ) : (
                      account.account_type === 'user' && (
                        <button
                          className="btn btn-success btn-small"
                          onClick={() => handleRequestCode(account.id)}
                          title="Account verbinden"
                        >
                          🔐 Login
                        </button>
                      )
                    )}
                    <button
                      className="btn btn-danger btn-small"
                      onClick={() => handleDelete(account.id)}
                      title="Account löschen"
                    >
                      🗑️ Löschen
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
          <div className="modal-content" style={{ maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>📂 Account aus tdata importieren</h3>
              <button className="close-btn" onClick={() => {
                setShowTdataModal(false)
                setTdataPath('')
                setTdataFiles([])
                setTdataFormData({ name: '', api_id: '', api_hash: '' })
              }}>×</button>
            </div>
            
            <form onSubmit={handleTdataSubmit}>
              <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                <strong>ℹ️ Anleitung:</strong>
                <ol style={{ marginTop: '10px', paddingLeft: '20px', fontSize: '0.9rem' }}>
                  <li>Lade den tdata-Ordner hoch (als ZIP oder einzelne Dateien)</li>
                  <li>Der tdata-Ordner sollte mindestens 3 Dateien enthalten</li>
                  <li>Der Account wird erstellt, aber für die Verwendung muss die tdata zu einer Telethon-Session konvertiert werden</li>
                </ol>
              </div>
              
              <div className="form-group">
                <label>Account-Name</label>
                <input
                  type="text"
                  required
                  value={tdataFormData.name}
                  onChange={(e) => setTdataFormData({ ...tdataFormData, name: e.target.value })}
                  placeholder="z.B. Mein Account"
                />
              </div>
              
              <div className="form-group">
                <label>API ID (optional)</label>
                <input
                  type="text"
                  value={tdataFormData.api_id}
                  onChange={(e) => setTdataFormData({ ...tdataFormData, api_id: e.target.value })}
                  placeholder="Von https://my.telegram.org/apps (wird aus Umgebungsvariablen geladen falls leer)"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Optional: Wird automatisch aus Umgebungsvariablen geladen falls nicht angegeben
                </p>
              </div>
              
              <div className="form-group">
                <label>API Hash (optional)</label>
                <input
                  type="text"
                  value={tdataFormData.api_hash}
                  onChange={(e) => setTdataFormData({ ...tdataFormData, api_hash: e.target.value })}
                  placeholder="Von https://my.telegram.org/apps (wird aus Umgebungsvariablen geladen falls leer)"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Optional: Wird automatisch aus Umgebungsvariablen geladen falls nicht angegeben
                </p>
              </div>
              
              <div className="form-group">
                <label>tdata hochladen</label>
                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                    Option 1: ZIP-Datei (empfohlen)
                  </label>
                  <input
                    type="file"
                    accept=".zip,application/zip"
                    onChange={handleTdataUpload}
                    style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                  />
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                    Option 2: Einzelne Dateien (alle Dateien aus dem tdata-Ordner)
                  </label>
                  <input
                    type="file"
                    multiple
                    onChange={handleTdataUpload}
                    style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                  />
                </div>
                {tdataPath && (
                  <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#e8f5e9', borderRadius: '5px' }}>
                    <p style={{ fontSize: '0.9rem', color: '#27ae60', fontWeight: 'bold', margin: '0 0 5px 0' }}>
                      ✓ tdata erfolgreich hochgeladen
                    </p>
                    <p style={{ fontSize: '0.85rem', color: '#666', margin: '5px 0' }}>
                      <strong>Dateien:</strong> {tdataFiles.length} Dateien
                    </p>
                    <p style={{ fontSize: '0.85rem', color: '#666', margin: '5px 0' }}>
                      <strong>Pfad:</strong> {tdataPath}
                    </p>
                  </div>
                )}
                <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#fff3cd', borderRadius: '5px', fontSize: '0.85rem' }}>
                  <strong>📋 Optionen:</strong>
                  <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                    <li><strong>ZIP-Datei:</strong> Lade den gesamten tdata-Ordner als ZIP hoch (empfohlen)</li>
                    <li><strong>Einzelne Dateien:</strong> Wähle alle Dateien aus dem tdata-Ordner aus</li>
                  </ul>
                  <p style={{ margin: '10px 0 0 0', fontSize: '0.85rem', color: '#856404' }}>
                    <strong>⚠️ Wichtig:</strong> Der tdata-Ordner sollte mindestens 3 Dateien enthalten. 
                    Stelle sicher, dass alle Dateien aus dem tdata-Ordner hochgeladen werden.
                  </p>
                </div>
              </div>
              
              <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
                <strong>⚠️ Hinweis zur Verwendung:</strong>
                <p style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                  Nach dem Import wird der Account erstellt, aber die tdata muss zu einer Telethon-Session konvertiert werden, 
                  um mit diesem Tool verwendet zu werden. Du kannst die tdata auch mit Telegram Desktop verwenden.
                </p>
                <p style={{ marginTop: '10px', fontSize: '0.85rem' }}>
                  <strong>Alternative:</strong> Verwende Session-Dateien (.session) wenn möglich, da diese direkt mit Telethon funktionieren.
                </p>
              </div>
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowTdataModal(false)
                    setTdataPath('')
                    setTdataFiles([])
                    setTdataFormData({ name: '', api_id: '', api_hash: '' })
                  }}
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !tdataPath || !tdataFormData.name}
                >
                  {loading ? 'Erstelle...' : '✅ Account erstellen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCompletePackageModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>📦 Komplettes Paket importieren</h3>
              <button className="close-btn" onClick={() => {
                setShowCompletePackageModal(false)
                setPackageFormData({ name: '', api_id: '', api_hash: '', two_factor_password: '' })
                setPackageFiles({ session: null, tdata: null, json: null })
              }}>×</button>
            </div>
            
            <form onSubmit={handleCompletePackageSubmit}>
              <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                <strong>ℹ️ Komplettes Paket:</strong>
                <p style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                  Importiere Accounts mit allen verfügbaren Formaten:
                </p>
                <ul style={{ marginTop: '10px', paddingLeft: '20px', fontSize: '0.9rem' }}>
                  <li><strong>TDATA</strong> - Telegram Desktop Daten (ZIP-Datei)</li>
                  <li><strong>SESSION</strong> - Telethon Session-Datei (.session)</li>
                  <li><strong>JSON</strong> - Metadaten-Datei mit Account-Informationen</li>
                  <li><strong>2FA</strong> - Zwei-Faktor-Authentifizierung Passwort</li>
                </ul>
                <p style={{ marginTop: '10px', fontSize: '0.85rem', color: '#666' }}>
                  <strong>Hinweis:</strong> Alle Felder sind optional. Lade mindestens eine Datei hoch (SESSION empfohlen).
                </p>
              </div>
              
              <div className="form-group">
                <label>Account-Name *</label>
                <input
                  type="text"
                  required
                  value={packageFormData.name}
                  onChange={(e) => setPackageFormData({ ...packageFormData, name: e.target.value })}
                  placeholder="z.B. Mein Account"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Wird automatisch aus JSON extrahiert falls vorhanden
                </p>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                <div className="form-group">
                  <label>API ID (optional)</label>
                  <input
                    type="text"
                    value={packageFormData.api_id}
                    onChange={(e) => setPackageFormData({ ...packageFormData, api_id: e.target.value })}
                    placeholder="Von https://my.telegram.org/apps"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Wird aus JSON oder Umgebungsvariablen geladen
                  </p>
                </div>
                
                <div className="form-group">
                  <label>API Hash (optional)</label>
                  <input
                    type="text"
                    value={packageFormData.api_hash}
                    onChange={(e) => setPackageFormData({ ...packageFormData, api_hash: e.target.value })}
                    placeholder="Von https://my.telegram.org/apps"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Wird aus JSON oder Umgebungsvariablen geladen
                  </p>
                </div>
              </div>
              
              <div className="form-group">
                <label>2FA-Passwort (optional)</label>
                <input
                  type="password"
                  value={packageFormData.two_factor_password}
                  onChange={(e) => setPackageFormData({ ...packageFormData, two_factor_password: e.target.value })}
                  placeholder="Zwei-Faktor-Authentifizierung Passwort"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Wird verschlüsselt gespeichert und automatisch beim Login verwendet
                </p>
              </div>
              
              <div style={{ borderTop: '2px solid #e0e0e0', paddingTop: '20px', marginTop: '20px' }}>
                <h4 style={{ marginBottom: '15px' }}>📁 Dateien hochladen</h4>
                
                <div className="form-group">
                  <label>SESSION-Datei (.session) - Empfohlen</label>
                  <input
                    type="file"
                    accept=".session"
                    onChange={(e) => setPackageFiles({ ...packageFiles, session: e.target.files[0] || null })}
                    style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                  />
                  {packageFiles.session && (
                    <p style={{ fontSize: '0.9rem', color: '#27ae60', marginTop: '5px' }}>
                      ✓ {packageFiles.session.name}
                    </p>
                  )}
                </div>
                
                <div className="form-group">
                  <label>TDATA (ZIP-Datei)</label>
                  <input
                    type="file"
                    accept=".zip,application/zip"
                    onChange={(e) => setPackageFiles({ ...packageFiles, tdata: e.target.files[0] || null })}
                    style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                  />
                  {packageFiles.tdata && (
                    <p style={{ fontSize: '0.9rem', color: '#27ae60', marginTop: '5px' }}>
                      ✓ {packageFiles.tdata.name}
                    </p>
                  )}
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Telegram Desktop tdata-Ordner als ZIP-Datei
                  </p>
                </div>
                
                <div className="form-group">
                  <label>JSON-Metadaten</label>
                  <input
                    type="file"
                    accept=".json,application/json"
                    onChange={(e) => setPackageFiles({ ...packageFiles, json: e.target.files[0] || null })}
                    style={{ padding: '10px', border: '2px solid #e0e0e0', borderRadius: '5px', width: '100%' }}
                  />
                  {packageFiles.json && (
                    <p style={{ fontSize: '0.9rem', color: '#27ae60', marginTop: '5px' }}>
                      ✓ {packageFiles.json.name}
                    </p>
                  )}
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Metadaten-Datei mit Account-Informationen (Telefonnummer, API Credentials, etc.)
                  </p>
                </div>
              </div>
              
              <div className="alert alert-success" style={{ marginBottom: '20px' }}>
                <strong>✅ Vorteile des kompletten Pakets:</strong>
                <ul style={{ marginTop: '10px', paddingLeft: '20px', fontSize: '0.9rem' }}>
                  <li>Automatische Extraktion von Account-Informationen aus JSON</li>
                  <li>2FA-Passwort wird verschlüsselt gespeichert und automatisch verwendet</li>
                  <li>Unterstützung für alle Formate (TDATA, SESSION, JSON)</li>
                  <li>Automatische Verbindung wenn Session vorhanden</li>
                </ul>
              </div>
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowCompletePackageModal(false)
                    setPackageFormData({ name: '', api_id: '', api_hash: '', two_factor_password: '' })
                    setPackageFiles({ session: null, tdata: null, json: null })
                  }}
                >
                  Abbrechen
                </button>
                <button
                  type="submit"
                  className="btn btn-success"
                  disabled={loading || !packageFormData.name || (!packageFiles.session && !packageFiles.tdata && !packageFiles.json)}
                >
                  {loading ? 'Importiere...' : '✅ Account importieren'}
                </button>
              </div>
            </form>
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
                    if (username && !username.endsWith('_bot')) {
                      // Entferne "bot" oder "_bot" falls bereits vorhanden
                      username = username.replace(/_?bot$/, '')
                      username = username + '_bot'
                    }
                    setCreateBotFormData({ ...createBotFormData, bot_username: username })
                  }}
                  placeholder="z.B. mein_test_bot"
                />
                <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                  Muss auf "_bot" enden (wird automatisch hinzugefügt)
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

      {showBulkCreateBotsModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>🤖 Mehrere Bots erstellen</h3>
              <button className="close-btn" onClick={() => {
                setShowBulkCreateBotsModal(false)
                setBulkCreateBotsProgress(null)
                setBulkCreateBotsFormData({
                  account_id: '',
                  count: 10,
                  name_prefix: 'Group Bot',
                  username_prefix: 'group_bot',
                  delay_between_bots: 3.0
                })
              }}>×</button>
            </div>
            
            {!bulkCreateBotsProgress ? (
              <form onSubmit={async (e) => {
                e.preventDefault()
                if (!bulkCreateBotsFormData.account_id) {
                  alert('Bitte einen User-Account auswählen')
                  return
                }
                
                setLoading(true)
                setBulkCreateBotsProgress({ status: 'creating', message: 'Erstelle Bots...', current: 0, total: bulkCreateBotsFormData.count })
                
                try {
                  const response = await axios.post(
                    `${API_BASE}/accounts/${bulkCreateBotsFormData.account_id}/bulk-create-bots`,
                    {
                      account_id: parseInt(bulkCreateBotsFormData.account_id),
                      count: parseInt(bulkCreateBotsFormData.count),
                      name_prefix: bulkCreateBotsFormData.name_prefix,
                      username_prefix: bulkCreateBotsFormData.username_prefix,
                      delay_between_bots: parseFloat(bulkCreateBotsFormData.delay_between_bots)
                    }
                  )
                  
                  setBulkCreateBotsProgress({
                    status: 'completed',
                    message: 'Bot-Erstellung abgeschlossen',
                    result: response.data
                  })
                  
                  if (response.data.created > 0) {
                    setTimeout(() => {
                      onUpdate()
                    }, 2000)
                  }
                } catch (error) {
                  setBulkCreateBotsProgress({
                    status: 'error',
                    message: 'Fehler bei der Bot-Erstellung',
                    error: error.response?.data?.detail || error.message
                  })
                } finally {
                  setLoading(false)
                }
              }}>
                <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                  <strong>ℹ️ Info:</strong> Erstellt mehrere Bots über einen verbundenen User-Account via BotFather. 
                  Namen werden automatisch generiert. Bots werden automatisch in der Datenbank gespeichert.
                </div>
                
                <div className="form-group">
                  <label>User-Account (muss verbunden sein)</label>
                  <select
                    required
                    value={bulkCreateBotsFormData.account_id}
                    onChange={(e) => setBulkCreateBotsFormData({ ...bulkCreateBotsFormData, account_id: e.target.value })}
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
                  <label>Anzahl Bots</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="50"
                    value={bulkCreateBotsFormData.count}
                    onChange={(e) => setBulkCreateBotsFormData({ ...bulkCreateBotsFormData, count: parseInt(e.target.value) || 1 })}
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Anzahl der zu erstellenden Bots (1-50)
                  </p>
                </div>
                
                <div className="form-group">
                  <label>Name-Präfix</label>
                  <input
                    type="text"
                    required
                    value={bulkCreateBotsFormData.name_prefix}
                    onChange={(e) => setBulkCreateBotsFormData({ ...bulkCreateBotsFormData, name_prefix: e.target.value })}
                    placeholder="z.B. Group Bot"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Bots werden benannt als: "{bulkCreateBotsFormData.name_prefix} 1", "{bulkCreateBotsFormData.name_prefix} 2", etc.
                  </p>
                </div>
                
                <div className="form-group">
                  <label>Username-Präfix</label>
                  <input
                    type="text"
                    required
                    value={bulkCreateBotsFormData.username_prefix}
                    onChange={(e) => {
                      let prefix = e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '')
                      setBulkCreateBotsFormData({ ...bulkCreateBotsFormData, username_prefix: prefix })
                    }}
                    placeholder="z.B. group_bot"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Usernames werden generiert als: "{bulkCreateBotsFormData.username_prefix}_1_bot", "{bulkCreateBotsFormData.username_prefix}_2_bot", etc.
                  </p>
                </div>
                
                <div className="form-group">
                  <label>Delay zwischen Bots (Sekunden)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="60"
                    step="0.5"
                    value={bulkCreateBotsFormData.delay_between_bots}
                    onChange={(e) => setBulkCreateBotsFormData({ ...bulkCreateBotsFormData, delay_between_bots: parseFloat(e.target.value) || 3.0 })}
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Wartezeit zwischen Bot-Erstellungen (empfohlen: 3 Sekunden)
                  </p>
                </div>
                
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowBulkCreateBotsModal(false)
                      setBulkCreateBotsProgress(null)
                    }}
                  >
                    Abbrechen
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Erstelle Bots...' : `${bulkCreateBotsFormData.count} Bots erstellen`}
                  </button>
                </div>
              </form>
            ) : (
              <div>
                {bulkCreateBotsProgress.status === 'creating' && (
                  <div>
                    <p>{bulkCreateBotsProgress.message}</p>
                    <div className="progress-bar" style={{ width: '100%', height: '20px', backgroundColor: '#f0f0f0', borderRadius: '10px', overflow: 'hidden', marginTop: '10px' }}>
                      <div style={{ 
                        width: `${(bulkCreateBotsProgress.current / bulkCreateBotsProgress.total) * 100}%`, 
                        height: '100%', 
                        backgroundColor: '#4CAF50',
                        transition: 'width 0.3s'
                      }}></div>
                    </div>
                    <p style={{ marginTop: '10px', fontSize: '0.9rem', color: '#666' }}>
                      {bulkCreateBotsProgress.current} / {bulkCreateBotsProgress.total} Bots
                    </p>
                  </div>
                )}
                
                {bulkCreateBotsProgress.status === 'completed' && (
                  <div>
                    <div className="alert alert-success">
                      <strong>✅ Erfolgreich!</strong> {bulkCreateBotsProgress.result.message}
                    </div>
                    <p><strong>Erstellt:</strong> {bulkCreateBotsProgress.result.created} / {bulkCreateBotsProgress.result.total}</p>
                    <p><strong>Fehlgeschlagen:</strong> {bulkCreateBotsProgress.result.failed}</p>
                    
                    {bulkCreateBotsProgress.result.bots && bulkCreateBotsProgress.result.bots.length > 0 && (
                      <div style={{ marginTop: '20px' }}>
                        <strong>Erstellte Bots:</strong>
                        <ul style={{ marginTop: '10px', maxHeight: '200px', overflowY: 'auto' }}>
                          {bulkCreateBotsProgress.result.bots.map((bot, idx) => (
                            <li key={idx}>
                              {bot.name} (ID: {bot.id}, @{bot.username})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {bulkCreateBotsProgress.result.errors && bulkCreateBotsProgress.result.errors.length > 0 && (
                      <div style={{ marginTop: '20px' }}>
                        <strong>Fehler:</strong>
                        <ul style={{ marginTop: '10px', maxHeight: '200px', overflowY: 'auto', color: '#d32f2f' }}>
                          {bulkCreateBotsProgress.result.errors.map((error, idx) => (
                            <li key={idx}>
                              {error.bot}: {error.error}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <button
                      className="btn btn-primary"
                      style={{ marginTop: '20px', width: '100%' }}
                      onClick={() => {
                        setShowBulkCreateBotsModal(false)
                        setBulkCreateBotsProgress(null)
                        onUpdate()
                      }}
                    >
                      Schließen
                    </button>
                  </div>
                )}
                
                {bulkCreateBotsProgress.status === 'error' && (
                  <div>
                    <div className="alert alert-danger">
                      <strong>❌ Fehler:</strong> {bulkCreateBotsProgress.error}
                    </div>
                    <button
                      className="btn btn-secondary"
                      style={{ marginTop: '20px', width: '100%' }}
                      onClick={() => {
                        setShowBulkCreateBotsModal(false)
                        setBulkCreateBotsProgress(null)
                      }}
                    >
                      Schließen
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {showAutoCreateModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>⚡ Automatische Account-Erstellung</h3>
              <button className="close-btn" onClick={() => {
                setShowAutoCreateModal(false)
                setAutoCreateProgress(null)
                setAutoCreateFormData({
                  provider: '5sim',
                  country: 'germany',
                  service: 'telegram',
                  max_accounts: 5,
                  min_balance: ''
                })
              }}>×</button>
            </div>
            
            {!autoCreateProgress ? (
              <form onSubmit={async (e) => {
                e.preventDefault()
                setLoading(true)
                setAutoCreateProgress({ status: 'starting', message: 'Starte automatische Account-Erstellung...' })
                
                try {
                  const requestData = {
                    provider: autoCreateFormData.provider,
                    country: autoCreateFormData.country,
                    service: autoCreateFormData.service,
                    max_accounts: parseInt(autoCreateFormData.max_accounts) || 5,
                    min_balance: autoCreateFormData.min_balance ? parseFloat(autoCreateFormData.min_balance) : null
                  }
                  
                  const response = await axios.post(`${API_BASE}/accounts/auto-create`, requestData)
                  
                  setAutoCreateProgress({
                    status: 'completed',
                    message: 'Account-Erstellung abgeschlossen',
                    result: response.data
                  })
                  
                  if (response.data.created > 0) {
                    setTimeout(() => {
                      onUpdate()
                    }, 2000)
                  }
                } catch (error) {
                  setAutoCreateProgress({
                    status: 'error',
                    message: 'Fehler bei der Account-Erstellung',
                    error: error.response?.data?.detail || error.message
                  })
                } finally {
                  setLoading(false)
                }
              }}>
                <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                  <strong>ℹ️ Info:</strong> Diese Funktion kauft automatisch Telefonnummern beim gewählten Provider, 
                  wartet auf SMS-Codes und erstellt vollständig konfigurierte Telegram-Accounts. 
                  Alle Daten (ID, Nummer, Hash, API) werden automatisch gespeichert.
                </div>
                
                <div className="form-group">
                  <label>Provider</label>
                  <select
                    required
                    value={autoCreateFormData.provider}
                    onChange={(e) => setAutoCreateFormData({ ...autoCreateFormData, provider: e.target.value })}
                  >
                    <option value="5sim">5sim.net</option>
                    <option value="sms-activate">SMS-Activate.org</option>
                    <option value="onlinesim">OnlineSim.io</option>
                    <option value="sms-manager">SMS-Manager.com</option>
                    <option value="getsmscode">GetSMSCode.com</option>
                  </select>
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Wähle den SMS-Provider. Stelle sicher, dass der API-Key konfiguriert ist.
                  </p>
                </div>
                
                <div className="form-group">
                  <label>Land</label>
                  <select
                    required
                    value={autoCreateFormData.country}
                    onChange={(e) => setAutoCreateFormData({ ...autoCreateFormData, country: e.target.value })}
                  >
                    <option value="germany">Deutschland</option>
                    <option value="usa">USA</option>
                    <option value="russia">Russland</option>
                    <option value="ukraine">Ukraine</option>
                    <option value="poland">Polen</option>
                    <option value="vietnam">Vietnam</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Service</label>
                  <select
                    required
                    value={autoCreateFormData.service}
                    onChange={(e) => setAutoCreateFormData({ ...autoCreateFormData, service: e.target.value })}
                  >
                    <option value="telegram">Telegram</option>
                    <option value="whatsapp">WhatsApp</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Anzahl Accounts</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="50"
                    value={autoCreateFormData.max_accounts}
                    onChange={(e) => setAutoCreateFormData({ ...autoCreateFormData, max_accounts: e.target.value })}
                    placeholder="5"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Maximale Anzahl zu erstellender Accounts (begrenzt durch Account-Limit und Guthaben)
                  </p>
                </div>
                
                <div className="form-group">
                  <label>Mindest-Guthaben (optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={autoCreateFormData.min_balance}
                    onChange={(e) => setAutoCreateFormData({ ...autoCreateFormData, min_balance: e.target.value })}
                    placeholder="z.B. 10.00"
                  />
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Optional: Mindest-Guthaben beim Provider (verhindert Erstellung wenn Guthaben zu niedrig)
                  </p>
                </div>
                
                <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowAutoCreateModal(false)
                      setAutoCreateProgress(null)
                    }}
                  >
                    Abbrechen
                  </button>
                  <button type="submit" className="btn btn-success" disabled={loading}>
                    {loading ? 'Starte...' : '⚡ Accounts erstellen'}
                  </button>
                </div>
              </form>
            ) : (
              <div>
                {autoCreateProgress.status === 'starting' && (
                  <div className="alert alert-info">
                    <p><strong>⏳ {autoCreateProgress.message}</strong></p>
                    <p>Bitte warten... Dies kann einige Minuten dauern.</p>
                  </div>
                )}
                
                {autoCreateProgress.status === 'completed' && autoCreateProgress.result && (
                  <div>
                    <div className={`alert ${autoCreateProgress.result.created > 0 ? 'alert-success' : 'alert-warning'}`}>
                      <h4>✅ Account-Erstellung abgeschlossen</h4>
                      <p><strong>Angefragt:</strong> {autoCreateProgress.result.requested} Accounts</p>
                      <p><strong>Erstellt:</strong> {autoCreateProgress.result.created} Accounts</p>
                      <p><strong>Fehlgeschlagen:</strong> {autoCreateProgress.result.failed} Accounts</p>
                      {autoCreateProgress.result.balance_before !== undefined && (
                        <p><strong>Guthaben vorher:</strong> {autoCreateProgress.result.balance_before} {autoCreateProgress.result.balance_after !== undefined ? `→ ${autoCreateProgress.result.balance_after}` : ''}</p>
                      )}
                    </div>
                    
                    {autoCreateProgress.result.accounts && autoCreateProgress.result.accounts.length > 0 && (
                      <div style={{ marginTop: '20px' }}>
                        <h4>Erstellte Accounts:</h4>
                        <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid #e0e0e0', borderRadius: '5px', padding: '10px' }}>
                          {autoCreateProgress.result.accounts.map((acc, idx) => (
                            <div key={idx} style={{ padding: '10px', borderBottom: '1px solid #f0f0f0', marginBottom: '5px' }}>
                              <p><strong>{acc.name}</strong></p>
                              <p style={{ fontSize: '0.9rem', color: '#666' }}>
                                📱 {acc.phone_number}<br/>
                                {acc.username && <>👤 @{acc.username}<br/></>}
                                {acc.first_name && <>👨 {acc.first_name} {acc.last_name || ''}<br/></>}
                                <span className="badge badge-success">✅ Verbunden</span>
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {autoCreateProgress.result.errors && autoCreateProgress.result.errors.length > 0 && (
                      <div style={{ marginTop: '20px' }}>
                        <h4>Fehler:</h4>
                        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #e0e0e0', borderRadius: '5px', padding: '10px', backgroundColor: '#fff5f5' }}>
                          {autoCreateProgress.result.errors.map((error, idx) => (
                            <p key={idx} style={{ fontSize: '0.9rem', color: '#c33', marginBottom: '5px' }}>
                              ❌ {error}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => {
                          setShowAutoCreateModal(false)
                          setAutoCreateProgress(null)
                          onUpdate()
                        }}
                      >
                        Schließen
                      </button>
                    </div>
                  </div>
                )}
                
                {autoCreateProgress.status === 'error' && (
                  <div className="alert alert-danger">
                    <h4>❌ Fehler</h4>
                    <p><strong>{autoCreateProgress.message}</strong></p>
                    <p>{autoCreateProgress.error}</p>
                    <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => {
                          setShowAutoCreateModal(false)
                          setAutoCreateProgress(null)
                        }}
                      >
                        Schließen
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {showSingleCreateModal && (
        <div className="modal">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3>➕ Einzelnen Account erstellen</h3>
              <button className="close-btn" onClick={() => {
                setShowSingleCreateModal(false)
                setSingleCreateFormData({ provider: 'onlinesim', country: '', service: 'telegram' })
                setSelectedPrice(null)
              }}>×</button>
            </div>
            
            <form onSubmit={handleSingleCreate}>
              <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                <strong>ℹ️ Info:</strong> Diese Funktion kauft automatisch eine Telefonnummer beim gewählten Provider, 
                wartet auf den SMS-Code und erstellt einen vollständig konfigurierten Telegram-Account.
              </div>
              
              <div className="form-group">
                <label>Provider</label>
                <select
                  required
                  value={singleCreateFormData.provider}
                  onChange={(e) => {
                    setSingleCreateFormData({ ...singleCreateFormData, provider: e.target.value })
                    loadCountriesPrices(e.target.value)
                  }}
                >
                  <option value="onlinesim">OnlineSim.io</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Service</label>
                <select
                  required
                  value={singleCreateFormData.service}
                  onChange={(e) => setSingleCreateFormData({ ...singleCreateFormData, service: e.target.value })}
                >
                  <option value="telegram">Telegram</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Land {loadingPrices && <span style={{ fontSize: '0.85rem', color: '#666' }}>(Lade Preise...)</span>}</label>
                {loadingPrices ? (
                  <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                    Lade verfügbare Länder...
                  </div>
                ) : (
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
                    gap: '10px',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    padding: '10px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '5px',
                    backgroundColor: '#f9f9f9'
                  }}>
                    {countriesPrices.map((country) => {
                      const price = singleCreateFormData.service === 'telegram' ? country.telegram_price : country.whatsapp_price
                      const isSelected = singleCreateFormData.country === country.country_code
                      const isAvailable = price !== null && price !== undefined
                      
                      return (
                        <div
                          key={country.country_code}
                          onClick={() => {
                            if (isAvailable) {
                              setSingleCreateFormData({ ...singleCreateFormData, country: country.country_code })
                              setSelectedPrice(price)
                            }
                          }}
                          style={{
                            padding: '12px',
                            border: `2px solid ${isSelected ? '#28a745' : isAvailable ? '#ddd' : '#ffc107'}`,
                            borderRadius: '5px',
                            cursor: isAvailable ? 'pointer' : 'not-allowed',
                            backgroundColor: isSelected ? '#e8f5e9' : isAvailable ? '#fff' : '#fff3cd',
                            transition: 'all 0.2s',
                            opacity: isAvailable ? 1 : 0.6
                          }}
                          onMouseEnter={(e) => {
                            if (isAvailable) {
                              e.currentTarget.style.transform = 'scale(1.02)'
                              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (isAvailable) {
                              e.currentTarget.style.transform = 'scale(1)'
                              e.currentTarget.style.boxShadow = 'none'
                            }
                          }}
                        >
                          <div style={{ fontWeight: 'bold', marginBottom: '5px', color: isSelected ? '#28a745' : '#333' }}>
                            {country.country_name}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '5px' }}>
                            {country.iso_code}
                          </div>
                          {isAvailable ? (
                            <div style={{ fontSize: '1rem', fontWeight: 'bold', color: '#28a745' }}>
                              ${price.toFixed(2)}
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.85rem', color: '#ff9800' }}>
                              Nicht verfügbar
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
                {!loadingPrices && countriesPrices.length === 0 && (
                  <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                    Keine Länder verfügbar
                  </div>
                )}
              </div>
              
              {/* Kostenübersicht */}
              {singleCreateFormData.country && calculatePrice() !== null && (
                <div className="alert alert-success" style={{ marginBottom: '20px', padding: '15px' }}>
                  <h4 style={{ margin: '0 0 10px 0' }}>💰 Kostenübersicht</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                        <strong>Land:</strong> {countriesPrices.find(c => c.country_code === singleCreateFormData.country)?.country_name || singleCreateFormData.country}
                      </p>
                      <p style={{ margin: '5px 0', fontSize: '0.9rem' }}>
                        <strong>Service:</strong> {singleCreateFormData.service === 'telegram' ? 'Telegram' : 'WhatsApp'}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ margin: '5px 0', fontSize: '1.2rem', fontWeight: 'bold', color: '#28a745' }}>
                        ${calculatePrice().toFixed(2)}
                      </p>
                      <p style={{ margin: '5px 0', fontSize: '0.85rem', color: '#666' }}>
                        pro Account
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {singleCreateFormData.country && calculatePrice() === null && (
                <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
                  ⚠️ Preis für diese Kombination nicht verfügbar. Bitte ein anderes Land wählen.
                </div>
              )}
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowSingleCreateModal(false)
                    setSingleCreateFormData({ provider: 'onlinesim', country: '', service: 'telegram' })
                    setSelectedPrice(null)
                  }}
                >
                  Abbrechen
                </button>
                <button 
                  type="submit" 
                  className="btn btn-success" 
                  disabled={loading || !singleCreateFormData.country || calculatePrice() === null}
                >
                  {loading ? 'Erstelle...' : '✅ Account erstellen'}
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
                setPhoneCodeHash(null)
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
                        setPhoneCodeHash(null)
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
                            const codeResponse = await axios.post(`${API_BASE}/accounts/${loginAccountId}/request-code`)
                            // Speichere neuen phone_code_hash
                            if (codeResponse.data.phone_code_hash) {
                              setPhoneCodeHash(codeResponse.data.phone_code_hash)
                            }
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
                        setPhoneCodeHash(null)
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

      {showDialogViewer && dialogAccountId && (
        <DialogViewer
          accountId={dialogAccountId}
          onClose={() => {
            setShowDialogViewer(false)
            setDialogAccountId(null)
          }}
        />
      )}
    </div>
  )
}

