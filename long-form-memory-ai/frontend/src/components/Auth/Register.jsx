import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { MoonIcon, SunIcon, SparklesIcon } from '@heroicons/react/24/outline'
import useAuth from '../../hooks/useAuth'
import useTheme from '../../hooks/useTheme'

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [validationError, setValidationError] = useState('')
  const { register, error } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setValidationError('')

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setValidationError('Password must be at least 6 characters')
      return
    }

    try {
      await register(formData.email, formData.username, formData.password)
      navigate('/chat')
    } catch {
      // Error handled in context
    }
  }

  return (
    <div className="min-h-screen px-4 py-8 sm:py-12">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-end mb-6">
          <button
            onClick={toggleTheme}
            className="neutral-button p-2"
            aria-label="Toggle theme"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          </button>
        </div>

        <div className="max-w-md mx-auto surface-panel rounded-3xl p-7 sm:p-9">
          <div className="text-center">
            <div className="h-14 w-14 mx-auto rounded-2xl surface-strong flex items-center justify-center glow-ring">
              <SparklesIcon className="h-7 w-7 text-[var(--accent)]" />
            </div>
            <h2 className="mt-5 text-3xl font-semibold">Create Account</h2>
            <p className="mt-2 text-secondary">Join MemoryAI and keep context across chats</p>
          </div>

          <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            {(error || validationError) && (
              <div className="rounded-xl border border-red-400/40 bg-red-500/10 text-red-300 px-4 py-3 text-sm">
                {validationError || error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1.5">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="input-field px-4 py-2.5"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-1.5">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="input-field px-4 py-2.5"
                placeholder="Choose a username"
                value={formData.username}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1.5">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input-field px-4 py-2.5"
                placeholder="Create a password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1.5">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="input-field px-4 py-2.5"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>

            <button type="submit" className="accent-button w-full py-2.5 font-semibold">
              Create account
            </button>
          </form>

          <p className="text-center mt-6 text-sm text-secondary">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-[var(--accent)] hover:underline">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register
