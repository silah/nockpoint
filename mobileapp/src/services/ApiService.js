import axios from 'axios';
import AuthService from './AuthService';

// Configure the base URL for your Flask API
const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  constructor() {
    // Create axios instance
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach auth token
    this.api.interceptors.request.use(async (config) => {
      const authHeaders = await AuthService.getAuthHeaders();
      config.headers = { ...config.headers, ...authHeaders };
      return config;
    });

    // Add response interceptor to handle token expiration
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, logout user
          await AuthService.logout();
          // You might want to navigate to login screen here
          // This would typically be handled by your navigation context
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get upcoming events
   * @returns {Promise<Array>}
   */
  async getUpcomingEvents() {
    try {
      const response = await this.api.get('/events', {
        params: { upcoming_only: true }
      });
      return response.data.events || [];
    } catch (error) {
      console.error('Error fetching events:', error);
      throw new Error('Failed to fetch events');
    }
  }

  /**
   * Get all events with optional filters
   * @param {Object} filters - Filter options (type, from_date, to_date, upcoming_only)
   * @returns {Promise<Array>}
   */
  async getEvents(filters = {}) {
    try {
      const response = await this.api.get('/events', { params: filters });
      return response.data.events || [];
    } catch (error) {
      console.error('Error fetching events:', error);
      throw new Error('Failed to fetch events');
    }
  }

  /**
   * Get event details by ID
   * @param {number} eventId 
   * @returns {Promise<Object>}
   */
  async getEvent(eventId) {
    try {
      const response = await this.api.get(`/events/${eventId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching event:', error);
      throw new Error('Failed to fetch event details');
    }
  }

  /**
   * Register for an event
   * @param {number} eventId 
   * @returns {Promise<Object>}
   */
  async registerForEvent(eventId) {
    try {
      const response = await this.api.post(`/events/${eventId}/register`);
      return response.data;
    } catch (error) {
      console.error('Error registering for event:', error);
      throw new Error(error.response?.data?.error || 'Failed to register for event');
    }
  }

  /**
   * Unregister from an event
   * @param {number} eventId 
   * @returns {Promise<Object>}
   */
  async unregisterFromEvent(eventId) {
    try {
      const response = await this.api.delete(`/events/${eventId}/unregister`);
      return response.data;
    } catch (error) {
      console.error('Error unregistering from event:', error);
      throw new Error(error.response?.data?.error || 'Failed to unregister from event');
    }
  }

  /**
   * Get competitions
   * @param {Object} filters - Filter options (upcoming_only)
   * @returns {Promise<Array>}
   */
  async getCompetitions(filters = {}) {
    try {
      const response = await this.api.get('/competitions', { params: filters });
      return response.data.competitions || [];
    } catch (error) {
      console.error('Error fetching competitions:', error);
      throw new Error('Failed to fetch competitions');
    }
  }

  /**
   * Get competition details by ID
   * @param {number} competitionId 
   * @returns {Promise<Object>}
   */
  async getCompetition(competitionId) {
    try {
      const response = await this.api.get(`/competitions/${competitionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching competition:', error);
      throw new Error('Failed to fetch competition details');
    }
  }

  /**
   * Submit a single score for a competition
   * @param {number} competitionId 
   * @param {Object} scoreData - {round_number, arrow_number, score, is_x}
   * @returns {Promise<Object>}
   */
  async submitScore(competitionId, scoreData) {
    try {
      const response = await this.api.post(`/competitions/${competitionId}/scores`, scoreData);
      return response.data;
    } catch (error) {
      console.error('Error submitting score:', error);
      throw new Error(error.response?.data?.error || 'Failed to submit score');
    }
  }

  /**
   * Submit multiple scores for a competition
   * @param {number} competitionId 
   * @param {Array} scores - Array of score objects
   * @returns {Promise<Object>}
   */
  async submitScoresBatch(competitionId, scores) {
    try {
      const response = await this.api.post(`/competitions/${competitionId}/scores/batch`, {
        scores
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting scores:', error);
      throw new Error(error.response?.data?.error || 'Failed to submit scores');
    }
  }
}

export default new ApiService();