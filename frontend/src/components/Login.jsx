import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import './Login.css'

export default function Login() {
  const { login, register } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  })

  const [registerData, setRegisterData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    const result = await login(loginData.username, loginData.password)
    
    if (!result.success) {
      setError(result.error)
    } else {
      setSuccess('Erfolgreich eingeloggt!')
    }
    
    setLoading(false)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validierung
    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwörter stimmen nicht überein')
      return
    }

    if (registerData.password.length < 6) {
      setError('Passwort muss mindestens 6 Zeichen lang sein')
      return
    }

    setLoading(true)

    const result = await register(
      registerData.email,
      registerData.username,
      registerData.password
    )
    
    if (!result.success) {
      setError(result.error)
    } else {
      setSuccess('Registrierung erfolgreich! Du erhältst 7 Tage kostenlosen Testzugang.')
    }
    
    setLoading(false)
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>🎵 Berlin City Raver</h1>
          <p>Marketing Tool</p>
        </div>

        <div className="login-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true)
              setError('')
              setSuccess('')
            }}
          >
            Login
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false)
              setError('')
              setSuccess('')
            }}
          >
            Registrieren
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {isLogin ? (
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label>Username oder Email</label>
              <input
                type="text"
                value={loginData.username}
                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                required
                placeholder="username oder email@example.com"
                disabled={loading}
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label>Passwort</label>
              <input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                required
                placeholder="Dein Passwort"
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Wird eingeloggt...' : 'Einloggen'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="login-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                required
                placeholder="email@example.com"
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                required
                placeholder="username"
                disabled={loading}
                minLength={3}
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label>Passwort</label>
              <input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                required
                placeholder="Mindestens 6 Zeichen"
                disabled={loading}
                minLength={6}
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label>Passwort bestätigen</label>
              <input
                type="password"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                required
                placeholder="Passwort wiederholen"
                disabled={loading}
                minLength={6}
                autoComplete="new-password"
              />
            </div>

            <div className="trial-info">
              <strong>🎁 Kostenloser Testzugang:</strong>
              <ul>
                <li>7 Tage kostenlos</li>
                <li>2 Accounts</li>
                <li>5 Gruppen</li>
                <li>10 Nachrichten/Tag</li>
              </ul>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Wird registriert...' : 'Registrieren'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

