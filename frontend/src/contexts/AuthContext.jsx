import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config/api'

const AuthContext = createContext(null)

// Axios Request Interceptor - fügt Token automatisch hinzu
// Wird beim Import registriert (nur einmal)
let requestInterceptorId = null
let responseInterceptorId = null

if (!requestInterceptorId) {
  requestInterceptorId = axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token')
      if (token) {
        // Stelle sicher, dass headers existiert
        if (!config.headers) {
          config.headers = {}
        }
        // Überschreibe Authorization Header immer mit aktuellem Token
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )
}

// Axios Response Interceptor - behandelt 401 Fehler
if (!responseInterceptorId) {
  responseInterceptorId = axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Token ungültig - aber nur löschen wenn es wirklich ein Token gibt
        // Nicht löschen bei Login/Register Requests (die haben kein Token)
        const requestUrl = error.config?.url || ''
        const isAuthEndpoint = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')
        
        if (!isAuthEndpoint) {
          // Nur löschen wenn es nicht ein Auth-Endpoint ist
          const currentToken = localStorage.getItem('token')
          if (currentToken) {
            console.log('401 Fehler erkannt, Token wird gelöscht')
            localStorage.removeItem('token')
          }
        }
      }
      return Promise.reject(error)
    }
  )
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // Setze Token in Axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      localStorage.setItem('token', token)
    } else {
      delete axios.defaults.headers.common['Authorization']
      localStorage.removeItem('token')
    }
  }, [token])

  // Prüfe ob User eingeloggt ist beim Start
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      // Warte kurz, damit Interceptor registriert ist
      setTimeout(() => {
        checkAuth()
      }, 100)
    } else {
      setLoading(false)
    }
  }, []) // Nur beim Mount

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/auth/me`)
      setUser(response.data)
      setToken(localStorage.getItem('token')) // Aktualisiere Token-State
    } catch (error) {
      // Token ungültig oder User nicht gefunden
      console.log('Auth check failed, clearing session')
      logout()
    } finally {
      setLoading(false)
    }
  }

  // Exportiere checkAuth für externe Nutzung
  const refreshUser = async () => {
    await checkAuth()
  }

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        username,
        password
      })
      const data = response.data
      const access_token = data.access_token
      
      if (!access_token) {
        return {
          success: false,
          error: 'Kein Token erhalten'
        }
      }
      
      // Setze Token zuerst in localStorage
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Setze User-Daten direkt aus Response (ohne access_token)
      setUser({
        user_id: data.user_id,
        username: data.username,
        email: data.email,
        subscription: data.subscription,
        is_admin: data.is_admin || false
      })
      
      // Warte kurz, damit State-Updates verarbeitet werden
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Verifiziere dass Token noch vorhanden ist
      const verifyToken = localStorage.getItem('token')
      if (!verifyToken || verifyToken !== access_token) {
        console.error('Token wurde nach Login gelöscht oder geändert!', {
          expected: access_token,
          actual: verifyToken
        })
        return {
          success: false,
          error: 'Token konnte nicht gespeichert werden'
        }
      }
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login fehlgeschlagen'
      }
    }
  }

  const register = async (email, username, password) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, {
        email,
        username,
        password
      })
      const data = response.data
      const access_token = data.access_token
      
      if (!access_token) {
        return {
          success: false,
          error: 'Kein Token erhalten'
        }
      }
      
      // Setze Token zuerst in localStorage
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Setze User-Daten direkt aus Response (ohne access_token)
      setUser({
        user_id: data.user_id,
        username: data.username,
        email: data.email,
        subscription: data.subscription,
        is_admin: data.is_admin || false
      })
      
      // Warte kurz, damit State-Updates verarbeitet werden
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Verifiziere dass Token noch vorhanden ist
      const verifyToken = localStorage.getItem('token')
      if (!verifyToken || verifyToken !== access_token) {
        console.error('Token wurde nach Register gelöscht oder geändert!', {
          expected: access_token,
          actual: verifyToken
        })
        return {
          success: false,
          error: 'Token konnte nicht gespeichert werden'
        }
      }
      
      return { success: true }
    } catch (error) {
      console.error('Register error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Registrierung fehlgeschlagen'
      }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    refreshUser: checkAuth,
    isAuthenticated: !!token && !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

