import { useState, useEffect, useCallback, useRef } from 'react';
import webSocketService from '../services/websocket';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const listenersRef = useRef(new Map());

  useEffect(() => {
    // Connect to WebSocket
    webSocketService.connect();
    
    // Connection status handlers
    const handleConnect = (data) => {
      setConnected(true);
      console.log('🔗 WebSocket conectado no React:', data?.id);
    };

    const handleDisconnect = () => {
      setConnected(false);
      console.log('❌ WebSocket desconectado no React');
    };

    // Subscribe to connection events
    webSocketService.on('connect', handleConnect);
    webSocketService.on('disconnect', handleDisconnect);

    // Check connection status periodically
    const connectionChecker = setInterval(() => {
      const isConnected = webSocketService.isConnected();
      setConnected(isConnected);
    }, 2000);
    
    // Initial check after a short delay
    setTimeout(() => {
      const isConnected = webSocketService.isConnected();
      setConnected(isConnected);
    }, 1000);

    return () => {
      clearInterval(connectionChecker);
      webSocketService.off('connect', handleConnect);
      webSocketService.off('disconnect', handleDisconnect);
    };
  }, []);

  const subscribe = useCallback((event, callback) => {
    if (!listenersRef.current.has(event)) {
      listenersRef.current.set(event, new Set());
    }
    listenersRef.current.get(event).add(callback);
    
    webSocketService.on(event, callback);

    // Return unsubscribe function
    return () => {
      webSocketService.off(event, callback);
      if (listenersRef.current.has(event)) {
        listenersRef.current.get(event).delete(callback);
      }
    };
  }, []);

  const subscribeToProgress = useCallback((repos) => {
    webSocketService.subscribeToProgress(repos);
  }, []);

  return {
    connected,
    lastUpdate,
    subscribe,
    subscribeToProgress
  };
}

// Hook específico para updates de progresso
export function useProgressUpdates(onUpdate) {
  const { subscribe } = useWebSocket();
  const [updates, setUpdates] = useState([]);

  useEffect(() => {
    const unsubscribe = subscribe('progress_update', (data) => {
      setUpdates(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 updates
      if (onUpdate) {
        onUpdate(data);
      }
    });

    return unsubscribe;
  }, [subscribe, onUpdate]);

  return updates;
}

// Hook para notificações em tempo real
export function useRealTimeNotifications(onNotification) {
  const { subscribe } = useWebSocket();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const unsubscribe = subscribe('notification', (data) => {
      setNotifications(prev => [data, ...prev]);
      if (onNotification) {
        onNotification(data);
      }
    });

    return unsubscribe;
  }, [subscribe, onNotification]);

  return notifications;
}

// Hook para status de builds
export function useBuildStatus(onBuildUpdate) {
  const { subscribe } = useWebSocket();
  const [buildStatus, setBuildStatus] = useState(null);

  useEffect(() => {
    const unsubscribe = subscribe('build_status', (data) => {
      setBuildStatus(data);
      if (onBuildUpdate) {
        onBuildUpdate(data);
      }
    });

    return unsubscribe;
  }, [subscribe, onBuildUpdate]);

  return buildStatus;
}

// Hook para estado inicial
export function useInitialState(onInitialState) {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe('initial_state', (data) => {
      if (onInitialState) {
        onInitialState(data);
      }
    });

    return unsubscribe;
  }, [subscribe, onInitialState]);
}

