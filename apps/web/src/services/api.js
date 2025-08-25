const API_BASE_URL = 'http://localhost:3001/api';

class ApiService {
  async request(endpoint, options = {}) {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      };

      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Progress endpoints
  async getProgress() {
    return this.request('/progress');
  }

  async getBackendProgress() {
    return this.request('/progress/backend');
  }

  async getFrontendProgress() {
    return this.request('/progress/frontend');
  }

  async getFeaturesProgress() {
    return this.request('/progress/features');
  }

  async getProgressTimeline() {
    return this.request('/progress/timeline');
  }

  async getServicesStatus() {
    return this.request('/progress/services');
  }

  async getRecentActivity() {
    return this.request('/progress/activity');
  }

  // GitHub endpoints
  async getRepositories() {
    return this.request('/github/repos');
  }

  async getCommits(repo) {
    return this.request(`/github/commits/${repo}`);
  }

  async getRepositoryAnalysis(repo) {
    return this.request(`/github/analysis/${repo}`);
  }

  // Notifications endpoints
  async getNotifications() {
    return this.request('/notifications');
  }

  async createNotification(notification) {
    return this.request('/notifications', {
      method: 'POST',
      body: JSON.stringify(notification)
    });
  }

  async markNotificationAsRead(id) {
    return this.request(`/notifications/${id}/read`, {
      method: 'PUT'
    });
  }
}

export default new ApiService();

