import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';

// Hook genérico para chamadas de API
export function useApi(apiCall, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err.message);
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
}

// Hook específico para progresso geral
export function useProgress() {
  return useApi(() => apiService.getProgress());
}

// Hook para progresso do backend
export function useBackendProgress() {
  return useApi(() => apiService.getBackendProgress());
}

// Hook para progresso do frontend
export function useFrontendProgress() {
  return useApi(() => apiService.getFrontendProgress());
}

// Hook para funcionalidades
export function useFeaturesProgress() {
  return useApi(() => apiService.getFeaturesProgress());
}

// Hook para timeline
export function useProgressTimeline() {
  return useApi(() => apiService.getProgressTimeline());
}

// Hook para status dos serviços
export function useServicesStatus() {
  return useApi(() => apiService.getServicesStatus());
}

// Hook para atividade recente
export function useRecentActivity() {
  return useApi(() => apiService.getRecentActivity());
}

// Hook para repositórios GitHub
export function useRepositories() {
  return useApi(() => apiService.getRepositories());
}

// Hook para notificações
export function useNotifications() {
  return useApi(() => apiService.getNotifications());
}

// Hook para múltiplas APIs com estado combinado
export function useMultipleApis(apiCalls) {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const results = await Promise.allSettled(
          Object.entries(apiCalls).map(async ([key, apiCall]) => {
            const result = await apiCall();
            return [key, result];
          })
        );

        const newData = {};
        const errors = [];

        results.forEach((result, index) => {
          const [key] = Object.entries(apiCalls)[index];
          
          if (result.status === 'fulfilled') {
            const [, value] = result.value;
            newData[key] = value;
          } else {
            errors.push(`${key}: ${result.reason.message}`);
          }
        });

        setData(newData);
        
        if (errors.length > 0) {
          setError(errors.join(', '));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  return { data, loading, error };
}

