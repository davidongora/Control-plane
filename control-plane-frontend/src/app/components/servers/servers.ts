import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Api, Server } from '../../services/api';

@Component({
  selector: 'app-servers',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './servers.html',
  styleUrl: './servers.css',
})
export class Servers implements OnInit {
  servers: Server[] = [];
  loading = true;
  showAddForm = false;
  serverForm!: FormGroup;
  submitting = false;
  errorMessage = '';
  successMessage = '';

  constructor(private api: Api, private fb: FormBuilder) {}

  ngOnInit() {
    this.loadServers();
    this.initForm();
  }

  initForm() {
    this.serverForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(255)]],
      hostname: ['', [Validators.required, Validators.maxLength(255)]],
      ip_address: ['', [Validators.required, Validators.pattern(/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/)]],
      port: [22, [Validators.required, Validators.min(1), Validators.max(65535)]],
      username: ['', [Validators.required, Validators.maxLength(100)]],
      password: [''],
      ssh_key: [''],
      description: [''],
      is_active: [true]
    }, { validators: Servers.atLeastOneAuthMethod });
  }

  static atLeastOneAuthMethod(form: FormGroup) {
    const password = form.get('password')?.value;
    const ssh_key = form.get('ssh_key')?.value;
    return password || ssh_key ? null : { noAuthMethod: true };
  }

  loadServers() {
    this.loading = true;
    this.api.getServers().subscribe({
      next: (response) => {
        this.servers = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading servers:', err);
        this.loading = false;
      }
    });
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (this.showAddForm) {
      this.initForm();
      this.errorMessage = '';
      this.successMessage = '';
    }
  }

  addServer() {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.serverForm.invalid) {
      this.markFormGroupTouched(this.serverForm);
      return;
    }

    this.submitting = true;
    const serverData = this.serverForm.value;

    this.api.createServer(serverData).subscribe({
      next: (server) => {
        this.successMessage = 'Server added successfully!';
        this.loadServers();
        setTimeout(() => {
          this.showAddForm = false;
          this.successMessage = '';
        }, 2000);
      },
      error: (err) => {
        console.error('Error creating server:', err);
        this.errorMessage = err.error?.detail || err.error?.message || 'Failed to create server. Please check your input.';
        this.submitting = false;
      },
      complete: () => {
        this.submitting = false;
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  testConnection(server: Server) {
    if (!server.id) return;
    
    this.api.testConnection(server.id).subscribe({
      next: (response) => {
        alert(response.message);
      },
      error: (err) => {
        alert('Connection test failed');
        console.error('Error testing connection:', err);
      }
    });
  }

  deleteServer(server: Server) {
    if (!server.id || !confirm(`Are you sure you want to delete ${server.name}?`)) return;
    
    this.api.deleteServer(server.id).subscribe({
      next: () => {
        this.servers = this.servers.filter(s => s.id !== server.id);
      },
      error: (err) => {
        console.error('Error deleting server:', err);
        alert('Failed to delete server');
      }
    });
  }
}
