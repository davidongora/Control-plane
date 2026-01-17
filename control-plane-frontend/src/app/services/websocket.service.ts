import { Injectable } from '@angular/core';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root',
})
export class WebSocketService {
  private sockets: Map<string, WebSocket> = new Map();
  private messageSubjects: Map<string, Subject<WebSocketMessage>> = new Map();
  private connectionStatusSubjects: Map<string, BehaviorSubject<boolean>> = new Map();
  private reconnectTimeouts: Map<string, any> = new Map();
  private readonly RECONNECT_INTERVAL = 5000; // 5 seconds
  private readonly MAX_RECONNECT_ATTEMPTS = 5;
  private reconnectAttempts: Map<string, number> = new Map();

  private getWebSocketUrl(path: string): string {
    const wsProtocol = environment.apiUrl.startsWith('https') ? 'wss' : 'ws';
    const baseUrl = environment.apiUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${baseUrl}/${path}`;
  }

  /**
   * Connect to a WebSocket endpoint
   */
  connect(endpoint: string): Observable<WebSocketMessage> {
    if (this.messageSubjects.has(endpoint)) {
      return this.messageSubjects.get(endpoint)!.asObservable();
    }

    const subject = new Subject<WebSocketMessage>();
    const statusSubject = new BehaviorSubject<boolean>(false);
    this.messageSubjects.set(endpoint, subject);
    this.connectionStatusSubjects.set(endpoint, statusSubject);
    this.reconnectAttempts.set(endpoint, 0);

    this.createWebSocket(endpoint);

    return subject.asObservable();
  }

  /**
   * Get connection status for an endpoint
   */
  getConnectionStatus(endpoint: string): Observable<boolean> {
    if (!this.connectionStatusSubjects.has(endpoint)) {
      const statusSubject = new BehaviorSubject<boolean>(false);
      this.connectionStatusSubjects.set(endpoint, statusSubject);
      return statusSubject.asObservable();
    }
    return this.connectionStatusSubjects.get(endpoint)!.asObservable();
  }

  /**
   * Create WebSocket connection
   */
  private createWebSocket(endpoint: string): void {
    const url = this.getWebSocketUrl(endpoint);
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log(`WebSocket connected: ${endpoint}`);
      this.reconnectAttempts.set(endpoint, 0);
      this.connectionStatusSubjects.get(endpoint)?.next(true);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.messageSubjects.get(endpoint)?.next(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
      this.connectionStatusSubjects.get(endpoint)?.next(false);
    };

    ws.onclose = () => {
      console.log(`WebSocket closed: ${endpoint}`);
      this.connectionStatusSubjects.get(endpoint)?.next(false);
      this.sockets.delete(endpoint);
      
      // Attempt to reconnect
      this.attemptReconnect(endpoint);
    };

    this.sockets.set(endpoint, ws);
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  private attemptReconnect(endpoint: string): void {
    const attempts = this.reconnectAttempts.get(endpoint) || 0;
    
    if (attempts >= this.MAX_RECONNECT_ATTEMPTS) {
      console.log(`Max reconnect attempts reached for ${endpoint}`);
      this.messageSubjects.get(endpoint)?.next({
        type: 'error',
        message: 'Unable to connect to server. Please refresh the page.'
      });
      return;
    }

    this.reconnectAttempts.set(endpoint, attempts + 1);
    
    const timeout = setTimeout(() => {
      console.log(`Attempting to reconnect to ${endpoint} (attempt ${attempts + 1})`);
      this.createWebSocket(endpoint);
    }, this.RECONNECT_INTERVAL);

    this.reconnectTimeouts.set(endpoint, timeout);
  }

  /**
   * Send message to WebSocket
   */
  send(endpoint: string, message: any): void {
    const ws = this.sockets.get(endpoint);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.warn(`WebSocket not connected: ${endpoint}`);
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(endpoint: string): void {
    const ws = this.sockets.get(endpoint);
    if (ws) {
      ws.close();
      this.sockets.delete(endpoint);
    }

    const timeout = this.reconnectTimeouts.get(endpoint);
    if (timeout) {
      clearTimeout(timeout);
      this.reconnectTimeouts.delete(endpoint);
    }

    this.messageSubjects.get(endpoint)?.complete();
    this.messageSubjects.delete(endpoint);
    
    this.connectionStatusSubjects.get(endpoint)?.complete();
    this.connectionStatusSubjects.delete(endpoint);
    
    this.reconnectAttempts.delete(endpoint);
  }

  /**
   * Disconnect all WebSocket connections
   */
  disconnectAll(): void {
    this.sockets.forEach((ws, endpoint) => {
      this.disconnect(endpoint);
    });
  }

  /**
   * Check if connected to endpoint
   */
  isConnected(endpoint: string): boolean {
    const ws = this.sockets.get(endpoint);
    return ws !== undefined && ws.readyState === WebSocket.OPEN;
  }
}
