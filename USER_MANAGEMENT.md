# User Management Feature

This document describes the User Management feature implemented in the Control Plane application.

## Overview

The User Management interface allows administrators to manage user accounts, including creating, editing, deleting users, and changing passwords. This feature is protected by admin-only permissions on the backend.

## Backend Implementation

### API Endpoints

All user management endpoints are located under `/api/users/`:

- **GET /api/users/** - List all users (admin only)
- **POST /api/users/** - Create a new user (admin only)
- **GET /api/users/{id}/** - Get user details (admin only)
- **PUT /api/users/{id}/** - Update user (admin only)
- **DELETE /api/users/{id}/** - Delete user (admin only)
- **PATCH /api/users/{id}/change_password/** - Change user password (admin only)
- **GET /api/users/me/** - Get current user info (authenticated users)

### Serializers

#### UserManagementSerializer
Location: `servers/serializers.py`

Fields:
- `id` (read-only)
- `username` (required, unique)
- `email` (optional)
- `first_name` (optional)
- `last_name` (optional)
- `is_staff` (boolean)
- `is_active` (boolean)
- `date_joined` (read-only)
- `password` (write-only, required for creation, optional for updates)

### ViewSet

#### UserViewSet
Location: `servers/views.py`

- Inherits from `viewsets.ModelViewSet`
- Uses Django's built-in `User` model
- Permissions: `IsAuthenticated` + `IsAdminUser` for all actions except `/me/`
- Special action: `change_password` - allows admins to change any user's password

### URL Configuration

Location: `servers/urls.py`

The UserViewSet is registered with the Django REST Framework router:
```python
router.register(r'users', views.UserViewSet)
```

## Frontend Implementation

### Component

**Location**: `control-plane-frontend/src/app/components/user-management/`

Files:
- `user-management.ts` - Component logic
- `user-management.html` - Template
- `user-management.css` - Styles

### Features

1. **User List Table**
   - Displays: username, email, first name, last name, is_staff, is_active, date_joined
   - Real-time toggle switches for is_staff and is_active
   - Action buttons: Edit, Change Password, Delete

2. **Add User Form**
   - Fields: username (required), email, first name, last name, password (required), is_staff checkbox, is_active checkbox
   - Form validation with error messages
   - Success/error notifications

3. **Edit User Modal**
   - Update user information except password
   - Same validation as add form

4. **Change Password Modal**
   - New password with confirmation
   - Password matching validation
   - Minimum 8 characters requirement

5. **Search/Filter**
   - Search by username, email, first name, or last name
   - Real-time filtering

6. **User Management**
   - Toggle staff status with checkbox
   - Toggle active status with checkbox
   - Delete with confirmation dialog

### API Service

**Location**: `control-plane-frontend/src/app/services/api.ts`

New methods added:
- `getUsers()` - List all users
- `getUser(id)` - Get user details
- `createUser(user)` - Create new user
- `updateUser(id, user)` - Update user
- `deleteUser(id)` - Delete user
- `changeUserPassword(id, newPassword)` - Change password
- `getCurrentUserProfile()` - Get current user profile

### Routes

**Location**: `control-plane-frontend/src/app/app.routes.ts`

Added route:
```typescript
{ path: 'user-management', component: UserManagementComponent, canActivate: [authGuard] }
```

### Navigation

**Location**: `control-plane-frontend/src/app/app.html`

Added navigation link in the navbar (visible to authenticated users):
```html
<a routerLink="/user-management" routerLinkActive="active">User Management</a>
```

## Security

### Backend Security
- All endpoints require authentication
- Most endpoints require admin privileges (`IsAdminUser`)
- Only `/api/users/me/` is accessible to all authenticated users
- Passwords are hashed using Django's password hashing
- CSRF protection is enabled for all state-changing operations

### Frontend Security
- Route protected by `authGuard`
- Navigation link only visible to authenticated users
- Password fields use `type="password"`
- Delete operations require confirmation

## Testing

### Backend Tests

Run the test script to verify all endpoints:

```bash
cd /home/runner/work/Control-plane/Control-plane
source venv/bin/activate
python /tmp/test_user_api3.py
```

Expected output:
- ✅ User Created Successfully
- ✅ User Updated Successfully
- ✅ Password Changed Successfully
- ✅ User Deleted Successfully

### Frontend Build

```bash
cd control-plane-frontend
npm install
npm run build
```

## Usage

### For Administrators

1. **Access User Management**
   - Navigate to `/user-management` in the application
   - Or click "User Management" in the navigation bar

2. **Create a New User**
   - Click "Add User" button
   - Fill in the form (username and password are required)
   - Check "Is Staff" to make the user an admin
   - Check "Is Active" to enable the account (default: true)
   - Click "Create User"

3. **Edit a User**
   - Click the edit icon (✏️) next to any user
   - Update the fields in the modal
   - Click "Update User"

4. **Change Password**
   - Click the key icon (🔑) next to any user
   - Enter new password and confirmation
   - Click "Change Password"

5. **Toggle Staff/Active Status**
   - Use the toggle switches in the table
   - Changes are applied immediately

6. **Delete a User**
   - Click the delete icon (🗑️) next to any user
   - Confirm the deletion in the dialog

7. **Search Users**
   - Use the search bar to filter by username, email, or name
   - Results update in real-time

## Data Model

The feature uses Django's built-in User model from `django.contrib.auth.models.User`:

```python
class User:
    username: str (unique, required)
    email: str (optional)
    first_name: str (optional)
    last_name: str (optional)
    password: str (hashed)
    is_staff: bool (default: False)
    is_active: bool (default: True)
    date_joined: datetime (auto-generated)
```

## Future Enhancements

Potential improvements for future versions:

1. **User Groups & Permissions** - Add support for Django groups and custom permissions
2. **Password Reset** - Email-based password reset functionality
3. **User Profile** - Extended user profile with avatar, bio, etc.
4. **Activity Log** - Track user actions and login history
5. **Bulk Operations** - Import/export users, bulk activate/deactivate
6. **Advanced Filtering** - Filter by staff status, active status, date joined
7. **Pagination** - Add pagination for large user lists
8. **User Roles** - Custom role-based access control beyond is_staff

## Notes

- Only superusers/staff members can access user management features
- Password must be at least 8 characters long
- Usernames must be unique
- Deleting a user cannot be undone
- The current logged-in user can be viewed via the `/me/` endpoint
