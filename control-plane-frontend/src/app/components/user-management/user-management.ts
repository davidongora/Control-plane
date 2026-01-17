import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { Api, UserManagement } from '../../services/api';

@Component({
  selector: 'app-user-management',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css',
})
export class UserManagementComponent implements OnInit {
  users: UserManagement[] = [];
  loading = true;
  showAddForm = false;
  showEditForm = false;
  showPasswordForm = false;
  userForm!: FormGroup;
  editForm!: FormGroup;
  passwordForm!: FormGroup;
  submitting = false;
  errorMessage = '';
  successMessage = '';
  selectedUser: UserManagement | null = null;
  searchQuery = '';

  constructor(private api: Api, private fb: FormBuilder) {}

  ngOnInit() {
    this.loadUsers();
    this.initForms();
  }

  initForms() {
    this.userForm = this.fb.group({
      username: ['', [Validators.required, Validators.maxLength(150)]],
      email: ['', [Validators.email]],
      first_name: ['', [Validators.maxLength(150)]],
      last_name: ['', [Validators.maxLength(150)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      is_staff: [false],
      is_active: [true]
    });

    this.editForm = this.fb.group({
      username: ['', [Validators.required, Validators.maxLength(150)]],
      email: ['', [Validators.email]],
      first_name: ['', [Validators.maxLength(150)]],
      last_name: ['', [Validators.maxLength(150)]],
      is_staff: [false],
      is_active: [true]
    });

    this.passwordForm = this.fb.group({
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('new_password')?.value;
    const confirm = form.get('confirm_password')?.value;
    return password === confirm ? null : { passwordMismatch: true };
  }

  loadUsers() {
    this.loading = true;
    this.api.getUsers().subscribe({
      next: (response) => {
        this.users = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.errorMessage = 'Failed to load users';
        this.loading = false;
      }
    });
  }

  get filteredUsers(): UserManagement[] {
    if (!this.searchQuery.trim()) {
      return this.users;
    }
    const query = this.searchQuery.toLowerCase();
    return this.users.filter(user =>
      user.username.toLowerCase().includes(query) ||
      (user.email && user.email.toLowerCase().includes(query)) ||
      (user.first_name && user.first_name.toLowerCase().includes(query)) ||
      (user.last_name && user.last_name.toLowerCase().includes(query))
    );
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (this.showAddForm) {
      this.userForm.reset({ is_staff: false, is_active: true });
      this.errorMessage = '';
      this.successMessage = '';
    }
  }

  addUser() {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.userForm.invalid) {
      this.markFormGroupTouched(this.userForm);
      return;
    }

    this.submitting = true;
    const userData = this.userForm.value;

    this.api.createUser(userData).subscribe({
      next: (user) => {
        this.successMessage = 'User created successfully!';
        this.loadUsers();
        setTimeout(() => {
          this.showAddForm = false;
          this.successMessage = '';
        }, 2000);
      },
      error: (err) => {
        console.error('Error creating user:', err);
        this.errorMessage = err.error?.username?.[0] || err.error?.detail || 'Failed to create user';
        this.submitting = false;
      },
      complete: () => {
        this.submitting = false;
      }
    });
  }

  editUser(user: UserManagement) {
    this.selectedUser = user;
    this.showEditForm = true;
    this.editForm.patchValue({
      username: user.username,
      email: user.email || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      is_staff: user.is_staff,
      is_active: user.is_active
    });
    this.errorMessage = '';
    this.successMessage = '';
  }

  updateUser() {
    if (!this.selectedUser) return;

    this.errorMessage = '';
    this.successMessage = '';

    if (this.editForm.invalid) {
      this.markFormGroupTouched(this.editForm);
      return;
    }

    this.submitting = true;
    const userData = this.editForm.value;

    this.api.updateUser(this.selectedUser.id!, userData).subscribe({
      next: (user) => {
        this.successMessage = 'User updated successfully!';
        this.loadUsers();
        setTimeout(() => {
          this.showEditForm = false;
          this.successMessage = '';
          this.selectedUser = null;
        }, 2000);
      },
      error: (err) => {
        console.error('Error updating user:', err);
        this.errorMessage = err.error?.username?.[0] || err.error?.detail || 'Failed to update user';
        this.submitting = false;
      },
      complete: () => {
        this.submitting = false;
      }
    });
  }

  cancelEdit() {
    this.showEditForm = false;
    this.selectedUser = null;
    this.errorMessage = '';
    this.successMessage = '';
  }

  deleteUser(user: UserManagement) {
    if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
      return;
    }

    this.api.deleteUser(user.id!).subscribe({
      next: () => {
        this.successMessage = 'User deleted successfully!';
        this.loadUsers();
        setTimeout(() => {
          this.successMessage = '';
        }, 3000);
      },
      error: (err) => {
        console.error('Error deleting user:', err);
        this.errorMessage = err.error?.detail || 'Failed to delete user';
        setTimeout(() => {
          this.errorMessage = '';
        }, 5000);
      }
    });
  }

  openPasswordForm(user: UserManagement) {
    this.selectedUser = user;
    this.showPasswordForm = true;
    this.passwordForm.reset();
    this.errorMessage = '';
    this.successMessage = '';
  }

  changePassword() {
    if (!this.selectedUser) return;

    this.errorMessage = '';
    this.successMessage = '';

    if (this.passwordForm.invalid) {
      this.markFormGroupTouched(this.passwordForm);
      return;
    }

    this.submitting = true;
    const newPassword = this.passwordForm.value.new_password;

    this.api.changeUserPassword(this.selectedUser.id!, newPassword).subscribe({
      next: () => {
        this.successMessage = 'Password changed successfully!';
        setTimeout(() => {
          this.showPasswordForm = false;
          this.successMessage = '';
          this.selectedUser = null;
        }, 2000);
      },
      error: (err) => {
        console.error('Error changing password:', err);
        this.errorMessage = err.error?.error || err.error?.detail || 'Failed to change password';
        this.submitting = false;
      },
      complete: () => {
        this.submitting = false;
      }
    });
  }

  cancelPasswordForm() {
    this.showPasswordForm = false;
    this.selectedUser = null;
    this.errorMessage = '';
    this.successMessage = '';
  }

  toggleStaff(user: UserManagement) {
    const updatedUser = { ...user, is_staff: !user.is_staff };
    this.api.updateUser(user.id!, updatedUser).subscribe({
      next: () => {
        this.loadUsers();
      },
      error: (err) => {
        console.error('Error updating user:', err);
        this.errorMessage = 'Failed to update user status';
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
      }
    });
  }

  toggleActive(user: UserManagement) {
    const updatedUser = { ...user, is_active: !user.is_active };
    this.api.updateUser(user.id!, updatedUser).subscribe({
      next: () => {
        this.loadUsers();
      },
      error: (err) => {
        console.error('Error updating user:', err);
        this.errorMessage = 'Failed to update user status';
        setTimeout(() => {
          this.errorMessage = '';
        }, 3000);
      }
    });
  }

  markFormGroupTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  formatDate(date: string | undefined): string {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString();
  }
}
