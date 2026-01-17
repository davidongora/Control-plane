import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, catchError, of } from 'rxjs';
import { Router } from '@angular/router';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private baseUrl = 'http://localhost:8000';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.loadUserFromStorage();
    this.initCsrf();
  }

  private initCsrf(): void {
    this.http.get(`${this.baseUrl}/api/auth/csrf/`).subscribe();
  }

  private loadUserFromStorage(): void {
    const userJson = localStorage.getItem('currentUser');
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        this.currentUserSubject.next(user);
      } catch (e) {
        localStorage.removeItem('currentUser');
      }
    }
  }

  private saveUserToStorage(user: User | null): void {
    if (user) {
      localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('currentUser');
    }
  }

  login(credentials: LoginCredentials): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/api/auth/login/`, credentials).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
        this.saveUserToStorage(user);
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/auth/logout/`, {}).pipe(
      tap(() => {
        this.currentUserSubject.next(null);
        this.saveUserToStorage(null);
        this.router.navigate(['/login']);
      }),
      catchError(() => {
        this.currentUserSubject.next(null);
        this.saveUserToStorage(null);
        this.router.navigate(['/login']);
        return of(null);
      })
    );
  }

  checkAuth(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/api/auth/user/`).pipe(
      tap(user => {
        this.currentUserSubject.next(user);
        this.saveUserToStorage(user);
      }),
      catchError(() => {
        this.currentUserSubject.next(null);
        this.saveUserToStorage(null);
        return of(null as any);
      })
    );
  }

  isAuthenticated(): boolean {
    return this.currentUserSubject.value !== null;
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}
