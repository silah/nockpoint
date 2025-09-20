import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

// Configure the base URL for your Flask API
const API_BASE_URL = 'http://localhost:5000/api';

class AuthService {
  constructor() {
    this.TOKEN_KEY = 'nockpoint_auth_token';
    this.USER_KEY = 'nockpoint_user_data';
  }

  /**
   * Login user with username and password
   * @param {string} username 
   * @param {string} password 
   * @returns {Promise<{success: boolean, user?: object, error?: string}>}
   */
  async login(username, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        username,
        password,
      });

      if (response.status === 200) {
        const { token, user } = response.data;
        
        // Store token and user data
        await AsyncStorage.setItem(this.TOKEN_KEY, token);
        await AsyncStorage.setItem(this.USER_KEY, JSON.stringify(user));
        
        return {
          success: true,
          user,
          token
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      
      if (error.response?.status === 401) {
        return {
          success: false,
          error: 'Invalid username or password'
        };
      }
      
      return {
        success: false,
        error: 'Network error. Please check your connection.'
      };
    }
  }

  /**
   * Get stored token from AsyncStorage
   * @returns {Promise<string|null>}
   */
  async getStoredToken() {
    try {
      return await AsyncStorage.getItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Error getting stored token:', error);
      return null;
    }
  }

  /**
   * Get stored user data from AsyncStorage
   * @returns {Promise<object|null>}
   */
  async getStoredUser() {
    try {
      const userData = await AsyncStorage.getItem(this.USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting stored user:', error);
      return null;
    }
  }

  /**
   * Validate token with the server
   * @param {string} token 
   * @returns {Promise<{valid: boolean, user?: object}>}
   */
  async validateToken(token) {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 200) {
        const { user } = response.data;
        // Update stored user data in case it changed
        await AsyncStorage.setItem(this.USER_KEY, JSON.stringify(user));
        
        return {
          valid: true,
          user
        };
      }
    } catch (error) {
      console.error('Token validation error:', error);
      
      if (error.response?.status === 401) {
        // Token is invalid or expired, clear stored data
        await this.logout();
      }
      
      return {
        valid: false
      };
    }
  }

  /**
   * Check if user has valid authentication
   * @returns {Promise<{isAuthenticated: boolean, user?: object}>}
   */
  async checkAuthentication() {
    const token = await this.getStoredToken();
    
    if (!token) {
      return { isAuthenticated: false };
    }

    const validation = await this.validateToken(token);
    
    return {
      isAuthenticated: validation.valid,
      user: validation.user
    };
  }

  /**
   * Logout user and clear stored data
   */
  async logout() {
    try {
      await AsyncStorage.removeItem(this.TOKEN_KEY);
      await AsyncStorage.removeItem(this.USER_KEY);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }

  /**
   * Get authorization header for API requests
   * @returns {Promise<{Authorization: string}|{}>}
   */
  async getAuthHeaders() {
    const token = await this.getStoredToken();
    if (token) {
      return {
        'Authorization': `Bearer ${token}`
      };
    }
    return {};
  }
}

export default new AuthService();