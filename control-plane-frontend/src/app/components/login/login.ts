import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService, LoginCredentials } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  credentials: LoginCredentials = {
    username: '',
    password: ''
  };
  error: string = '';
  loading: boolean = false;
  returnUrl: string = '/dashboard';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    }
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
  }

  onSubmit(): void {
    if (!this.credentials.username || !this.credentials.password) {
      this.error = 'Please enter both username and password';
      return;
    }

    this.error = '';
    this.loading = true;

    this.authService.login(this.credentials).subscribe({
      next: () => {
        this.router.navigate([this.returnUrl]);
      },
      error: (err) => {
        this.loading = false;
        if (err.status === 401 || err.status === 400) {
          this.error = 'Invalid username or password';
        } else if (err.status === 0) {
          this.error = 'Unable to connect to server. Please try again later.';
        } else {
          this.error = 'An error occurred. Please try again.';
        }
      }
    });
  }
}
