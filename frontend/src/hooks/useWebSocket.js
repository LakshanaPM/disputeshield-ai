import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * useWebSocket Hook
 * Connects to /ws/disputes via native WebSocket with exponential backoff reconnection.
 * Exposes connection state, last received payload, and sending capability.
 */
export function useWebSocket(path = '/ws/disputes') {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // 'connecting' | 'connected' | 'disconnected' | 'reconnecting'
  const wsRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      const customWsUrl = import.meta.env.VITE_WS_URL;
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const url = customWsUrl
        ? `${customWsUrl.replace(/\/$/, '')}${path}`
        : `${protocol}//${host}${path}`;

      setConnectionStatus(reconnectAttemptsRef.current > 0 ? 'reconnecting' : 'connecting');

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;

        // Periodic heartbeat ping every 30s
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.type !== 'pong') {
            setLastMessage(data);
          }
        } catch (err) {
          setLastMessage({ type: 'raw', data: event.data });
        }
      };

      ws.onerror = (err) => {
        console.warn('[useWebSocket] Socket encountered error:', err);
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(1000 * Math.pow(1.5, reconnectAttemptsRef.current), 10000);
          setConnectionStatus('reconnecting');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          setConnectionStatus('disconnected');
        }
      };
    } catch (err) {
      console.error('[useWebSocket] Failed to establish connection:', err);
      setConnectionStatus('disconnected');
    }
  }, [path]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((msg) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  }, []);

  return { isConnected, lastMessage, connectionStatus, sendMessage };
}

export default useWebSocket;
