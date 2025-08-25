import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io('http://localhost:3001', {
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log('🔗 WebSocket conectado:', this.socket.id);
      this.emit('connect', { id: this.socket.id });
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket desconectado');
      this.emit('disconnect', {});
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ Erro de conexão WebSocket:', error);
      this.emit('connect_error', error);
    });

    // Handle real-time updates
    this.socket.on('progress_update', (data) => {
      console.log('📊 Update de progresso:', data);
      this.emit('progress_update', data);
    });

    this.socket.on('build_status', (data) => {
      console.log('🔧 Status de build:', data);
      this.emit('build_status', data);
    });

    this.socket.on('notification', (data) => {
      console.log('🔔 Nova notificação:', data);
      this.emit('notification', data);
    });

    this.socket.on('initial_state', (data) => {
      console.log('🎯 Estado inicial:', data);
      this.emit('initial_state', data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribeToProgress(repos) {
    if (this.socket?.connected) {
      this.socket.emit('subscribe_progress', repos);
    }
  }

  // Check connection status
  isConnected() {
    return this.socket?.connected || false;
  }

  // Get connection ID
  getConnectionId() {
    return this.socket?.id || null;
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} listener:`, error);
        }
      });
    }
  }
}

export default new WebSocketService();

