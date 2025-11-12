import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import './SubscriptionPlans.css'
import { API_BASE } from '../config/api'

export default function SubscriptionPlans() {
  const { user, refreshUser } = useAuth()
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [showPayment, setShowPayment] = useState(false)

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${API_BASE}/subscriptions/plans`)
      setPlans(response.data.filter(p => p.plan_type !== 'free_trial')) // Free Trial nicht anzeigen
    } catch (error) {
      console.error('Fehler beim Laden der Pakete:', error)
    }
  }

  const handlePurchase = async (plan) => {
    setSelectedPlan(plan)
    setError('')
    setSuccess('')
    
    // TODO: Stripe/PayPal Integration
    // Für jetzt: Direkter Kauf ohne Payment
    setLoading(true)
    
    try {
      const response = await axios.post(`${API_BASE}/subscriptions/purchase`, {
        plan_type: plan.plan_type,
        payment_method: 'stripe', // TODO: Echte Payment-Methode
        payment_token: 'demo_token' // TODO: Echter Payment Token
      })
      
      if (response.data.success) {
        setSuccess('Paket erfolgreich gekauft!')
        // User-Daten aktualisieren
        await refreshUser()
        setTimeout(() => {
          window.location.reload()
        }, 2000)
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Fehler beim Kauf')
    } finally {
      setLoading(false)
    }
  }

  const currentPlan = user?.subscription?.plan_type || 'free_trial'

  return (
    <div className="subscription-plans">
      <div className="plans-header">
        <h2>📦 Pakete & Preise</h2>
        <p>Wähle das passende Paket für deine Bedürfnisse</p>
        {currentPlan !== 'free_trial' && (
          <div className="current-plan-badge">
            Aktuelles Paket: {plans.find(p => p.plan_type === currentPlan)?.name || currentPlan}
          </div>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="plans-grid">
        {plans.map((plan) => {
          const isCurrentPlan = plan.plan_type === currentPlan
          const isUpgrade = currentPlan === 'free_trial' || 
            (plan.plan_type === 'pro' && currentPlan === 'basic') ||
            (plan.plan_type === 'enterprise' && ['free_trial', 'basic', 'pro'].includes(currentPlan))
          
          return (
            <div 
              key={plan.plan_type} 
              className={`plan-card ${isCurrentPlan ? 'current' : ''} ${isUpgrade ? 'upgrade' : ''}`}
            >
              {isCurrentPlan && (
                <div className="plan-badge">Aktuell</div>
              )}
              
              <div className="plan-header">
                <h3>{plan.name}</h3>
                <div className="plan-price">
                  <span className="price-amount">€{plan.price.toFixed(2)}</span>
                  <span className="price-period">/Monat</span>
                </div>
              </div>

              <p className="plan-description">{plan.description}</p>

              <div className="plan-features">
                <div className="feature-item">
                  <strong>{plan.max_accounts}</strong> Accounts
                </div>
                <div className="feature-item">
                  <strong>{plan.max_groups}</strong> Gruppen
                </div>
                <div className="feature-item">
                  <strong>{plan.max_messages_per_day}</strong> Nachrichten/Tag
                </div>
                {plan.features.auto_number_purchase && (
                  <div className="feature-item highlight">
                    ✅ Automatischer Nummernkauf
                  </div>
                )}
              </div>

              <button
                className={`btn ${isCurrentPlan ? 'btn-secondary' : 'btn-primary'}`}
                onClick={() => handlePurchase(plan)}
                disabled={isCurrentPlan || loading}
              >
                {isCurrentPlan 
                  ? 'Aktuelles Paket' 
                  : loading 
                    ? 'Wird verarbeitet...' 
                    : isUpgrade 
                      ? 'Upgraden' 
                      : 'Kaufen'
                }
              </button>
            </div>
          )
        })}
      </div>

      <div className="payment-info">
        <h4>💳 Zahlungsmethoden</h4>
        <p>Wir akzeptieren Kreditkarten, PayPal und weitere Zahlungsmethoden.</p>
        <p className="note">⚠️ Hinweis: Zahlungsintegration wird aktuell implementiert. Für Tests wird der Kauf simuliert.</p>
      </div>
    </div>
  )
}

