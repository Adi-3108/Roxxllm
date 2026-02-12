import api from './api'

export const authService = {
  login: async (email, password) => {
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    } catch (error) {
      // Handle network errors gracefully
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password. Please check your credentials and try again.')
      } else if (error.response?.status === 404) {
        throw new Error('User not found. Please check your email or register for a new account.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Login failed. Please try again later.')
      }
    }
  },

  register: async (email, username, password) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        username,
        password
      })
      return response.data
    } catch (error) {
      // Handle network errors gracefully
      if (error.response?.status === 400) {
        throw new Error('Invalid registration details. Please check your email, username, and password.')
      } else if (error.response?.status === 409) {
        throw new Error('Email or username already taken. Please choose a different email or username.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Registration failed. Please try again later.')
      }
    }
  },

  loginWithGoogle: async (googleData) => {
    try {
      const response = await api.post('/auth/google', googleData)
      return response.data
    } catch (error) {
      if (error.response?.status === 400) {
        throw new Error('Google authentication failed. Please try again.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Google login failed. Please try again later.')
      }
    }
  },

  getMe: async () => {
    try {
      const response = await api.get('/auth/me')
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Authentication expired. Please log in again.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Failed to get user information. Please try again.')
      }
    }
  },

  refreshToken: async (refreshToken) => {
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      })
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Refresh token expired. Please log in again.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Token refresh failed. Please log in again.')
      }
    }
  },

  deleteAccount: async () => {
    try {
      return await api.delete('/user/delete')
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Authentication required. Please log in again.')
      } else if (error.response?.status === 404) {
        throw new Error('User not found.')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network connection failed. Please check your internet connection and try again.')
      } else {
        throw new Error('Account deletion failed. Please try again.')
      }
    }
  }
}