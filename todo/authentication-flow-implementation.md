# Authentication Flow Implementatie Plan

**Project**: Digital Resupplying Tool  
**Versie**: 1.4.0  
**Doel**: Complete frontend authentication flow implementeren  
**Status**: 🔄 In Planning  
**Laatst Bijgewerkt**: 2 november 2025

---

## 📋 Executive Summary

Gisteren is het volledige backend authentication systeem gebouwd (JWT, bcrypt, RBAC). Vandaag implementeren we de frontend zodat gebruikers kunnen inloggen en de app wordt beveiligd met route protection en permission-based UI rendering.

### Huidige Situatie
- ✅ Backend JWT auth compleet (`backend/auth.py`, `backend/routers/auth.py`)
- ✅ User/Role/Permission database models
- ✅ Password hashing en validatie
- ❌ Geen login pagina
- ❌ Geen auth state management
- ❌ Geen route protection
- ❌ Geen API authentication

### Eindresultaat
- ✅ Professional login pagina met MC Company branding
- ✅ Complete auth state management met React Context
- ✅ Alle routes protected (redirect naar login als niet ingelogd)
- ✅ User menu in sidebar met logout functionaliteit
- ✅ API calls authenticated met Bearer tokens
- ✅ Auto token refresh (seamless UX)
- ✅ Remember Me functionaliteit (7 of 30 dagen)
- ✅ Permission-based UI rendering

---

## 🎯 Implementatie Volgorde & Tijdsinschatting

### FASE 1: Foundation (Dag 1 - ~2 uur) 🏗️
**Doel**: Basis infrastructure voor authentication

#### 1.1 TypeScript Types & Interfaces (15 min)
- [ ] **Bestand**: `frontend/types/auth.ts` (nieuw)
- [ ] User interface
- [ ] AuthState interface  
- [ ] LoginCredentials interface
- [ ] TokenResponse interface
- [ ] AuthContextType interface

#### 1.2 Token Storage Utility (30 min)
- [ ] **Bestand**: `frontend/lib/token-storage.ts` (nieuw)
- [ ] LocalStorage/SessionStorage abstraction
- [ ] Token encryption (basis, voor later uitbreiden)
- [ ] Expiry checking helpers
- [ ] Clear all tokens functie

#### 1.3 Auth Context & Provider (60 min)
- [ ] **Bestand**: `frontend/contexts/auth-context.tsx` (nieuw)
- [ ] React Context setup
- [ ] User state management
- [ ] Login functie
- [ ] Logout functie
- [ ] Token refresh logic
- [ ] Permission check helpers
- [ ] Loading states
- [ ] Error handling

#### 1.4 API Client Updates (30 min)
- [ ] **Bestand**: `frontend/lib/api.ts` (update)
- [ ] Auth endpoints toevoegen (login, refresh, me)
- [ ] Bearer token injection in headers
- [ ] 401 interceptor met auto-refresh
- [ ] 403 handler (logout)
- [ ] Error response typing

**Checkpoint**: Backend en frontend kunnen nu communiceren voor auth

---

### FASE 2: UI Core (Dag 1 - ~2 uur) 🎨
**Doel**: User-facing authentication UI

#### 2.1 Login Pagina (75 min)
- [ ] **Bestand**: `frontend/app/login/page.tsx` (nieuw)
- [ ] **Bestand**: `frontend/app/login/layout.tsx` (nieuw - geen sidebar op login)
- [ ] Page structure met centered card
- [ ] MC Company logo integratie
- [ ] Username input met icon
- [ ] Password input met show/hide toggle
- [ ] Remember Me checkbox
- [ ] Submit button met loading state
- [ ] Error message display
- [ ] Form validation
- [ ] Success redirect naar dashboard
- [ ] Responsive design (mobile friendly)
- [ ] Dark mode compatible

**Shadcn/ui Components Nodig**:
```bash
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add button
npx shadcn-ui@latest add label
npx shadcn-ui@latest add checkbox
```

#### 2.2 Protected Route Wrapper (30 min)
- [ ] **Bestand**: `frontend/components/auth/protected-route.tsx` (nieuw)
- [ ] Auth check logic
- [ ] Loading state tijdens check
- [ ] Redirect naar /login als not authenticated
- [ ] Permission-based rendering (optioneel prop)
- [ ] Children rendering als authenticated

#### 2.3 Layout Integration (15 min)
- [ ] **Bestand**: `frontend/app/layout.tsx` (update)
- [ ] Wrap met AuthProvider
- [ ] Conditional sidebar rendering (niet op /login)
- [ ] Hydration error prevention

**Checkpoint**: Gebruikers kunnen nu inloggen en worden doorgestuurd naar dashboard

---

### FASE 3: User Experience (Dag 2 - ~1.5 uur) 👤
**Doel**: User identity en navigatie

#### 3.1 User Menu Component (45 min)
- [ ] **Bestand**: `frontend/components/auth/user-menu.tsx` (nieuw)
- [ ] Avatar met initialen
- [ ] Dropdown menu (shadcn/ui DropdownMenu)
- [ ] User info display (naam, rol)
- [ ] Menu items:
  - [ ] Mijn Profiel (link)
  - [ ] Instellingen (link)
  - [ ] Divider
  - [ ] Uitloggen (button)
- [ ] Logout confirmation (optioneel)
- [ ] Smooth animations

**Shadcn/ui Components Nodig**:
```bash
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add separator
```

#### 3.2 Sidebar Integration (20 min)
- [ ] **Bestand**: `frontend/components/app-sidebar.tsx` (update)
- [ ] UserMenu component onderaan sidebar
- [ ] Collapsed state handling (alleen avatar, geen tekst)
- [ ] Hover effects
- [ ] Positie fix (sticky bottom)

#### 3.3 Dashboard Personalisatie (15 min)
- [ ] **Bestand**: `frontend/app/page.tsx` (update)
- [ ] "Welkom terug, [Naam]!" greeting
- [ ] Laatste login tijd tonen
- [ ] User-specific stats (optioneel)

#### 3.4 Permission-based UI (30 min)
- [ ] **Bestand**: `frontend/components/auth/permission-gate.tsx` (nieuw)
- [ ] Component voor conditional rendering
- [ ] Hook: `usePermission(permission: string)`
- [ ] Implementatie in bestaande components:
  - [ ] Approve/Reject buttons (alleen met permission)
  - [ ] Settings menu item (alleen admins)
  - [ ] User management link (alleen admins)

**Checkpoint**: Complete user experience met identity en permissions

---

### FASE 4: Advanced Features (Dag 2 - ~1 uur) 🚀
**Doel**: Professional touches en edge cases

#### 4.1 Auto Token Refresh (30 min)
- [ ] **Bestand**: `frontend/contexts/auth-context.tsx` (update)
- [ ] Timer setup voor refresh
- [ ] Refresh 5 minuten voor expiry
- [ ] Silent refresh (geen UI blocking)
- [ ] Failure handling (logout)

#### 4.2 Session Expired Modal (20 min)
- [ ] **Bestand**: `frontend/components/auth/session-expired-modal.tsx` (nieuw)
- [ ] Modal component (shadcn/ui Dialog)
- [ ] "Je sessie is verlopen" message
- [ ] "Opnieuw inloggen" button
- [ ] Redirect naar login met return URL
- [ ] Auto-show bij auth failure

**Shadcn/ui Components Nodig**:
```bash
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add alert-dialog
```

#### 4.3 Remember Me Implementation (10 min)
- [ ] **Bestand**: `frontend/lib/token-storage.ts` (update)
- [ ] Conditional storage (localStorage vs sessionStorage)
- [ ] Restore session on page load
- [ ] Clear logic bij logout

**Checkpoint**: Production-ready authentication met alle edge cases

---

### FASE 5: Testing & Polish (Dag 2-3 - ~1 uur) ✅
**Doel**: Verify everything works en polish UX

#### 5.1 Manual Testing (30 min)
- [ ] Login flow werkt
- [ ] Verkeerde credentials tonen error
- [ ] Remember Me persisteert sessie
- [ ] Logout werkt correct
- [ ] Protected routes redirecten
- [ ] Token refresh werkt
- [ ] API calls authenticated
- [ ] Permission checks werken
- [ ] Dark mode werkt
- [ ] Mobile responsive
- [ ] Error states tonen correct

#### 5.2 Edge Cases (20 min)
- [ ] Network errors tijdens login
- [ ] Token expired tijdens gebruik
- [ ] Multiple tabs sync (optioneel)
- [ ] Browser back button gedrag
- [ ] Direct URL access naar protected routes
- [ ] Refresh during loading states

#### 5.3 Final Polish (10 min)
- [ ] Animations smooth
- [ ] Loading states consistent
- [ ] Error messages user-friendly (Nederlands)
- [ ] Focus states accessible
- [ ] Tab navigation werkt

**Checkpoint**: Complete, tested, production-ready auth systeem!

---

## 📁 Bestanden Overzicht

### Nieuwe Bestanden (15 totaal)

#### Core Auth (7 bestanden)
1. `frontend/types/auth.ts` - TypeScript interfaces
2. `frontend/lib/token-storage.ts` - Token storage utility
3. `frontend/contexts/auth-context.tsx` - Auth state management
4. `frontend/components/auth/protected-route.tsx` - Route protection
5. `frontend/components/auth/permission-gate.tsx` - Permission checks
6. `frontend/components/auth/user-menu.tsx` - User dropdown menu
7. `frontend/components/auth/session-expired-modal.tsx` - Session modal

#### UI Components (2 bestanden)
8. `frontend/app/login/page.tsx` - Login pagina
9. `frontend/app/login/layout.tsx` - Login layout (zonder sidebar)

### Te Updaten Bestanden (4 totaal)
1. `frontend/lib/api.ts` - Auth endpoints + token injection
2. `frontend/app/layout.tsx` - AuthProvider wrapper
3. `frontend/components/app-sidebar.tsx` - User menu integratie
4. `frontend/app/page.tsx` - User greeting

---

## 🔧 Technische Specificaties

### 1. TypeScript Types (`frontend/types/auth.ts`)

```typescript
// User interface matching backend
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_name: string;
  role_display_name: string;
  permissions: string[];
  is_active: boolean;
  last_login: string | null;
}

// Auth state
export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Login credentials
export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

// Token response from API
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Auth context type
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}
```

### 2. Token Storage (`frontend/lib/token-storage.ts`)

```typescript
// Storage keys
const ACCESS_TOKEN_KEY = 'drt_access_token';
const REFRESH_TOKEN_KEY = 'drt_refresh_token';
const USER_KEY = 'drt_user';
const REMEMBER_ME_KEY = 'drt_remember_me';

// Storage interface
export const tokenStorage = {
  // Get storage type based on remember me
  getStorage: (rememberMe: boolean = false): Storage => {
    const remembered = rememberMe || localStorage.getItem(REMEMBER_ME_KEY) === 'true';
    return remembered ? localStorage : sessionStorage;
  },

  // Save tokens
  setTokens: (accessToken: string, refreshToken: string, rememberMe: boolean = false) => {
    const storage = tokenStorage.getStorage(rememberMe);
    storage.setItem(ACCESS_TOKEN_KEY, accessToken);
    storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(REMEMBER_ME_KEY, rememberMe.toString());
  },

  // Get access token
  getAccessToken: (): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY) || sessionStorage.getItem(ACCESS_TOKEN_KEY);
  },

  // Get refresh token
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  // Save user data
  setUser: (user: User) => {
    const storage = tokenStorage.getStorage();
    storage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Get user data
  getUser: (): User | null => {
    const userStr = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  // Clear all auth data
  clear: () => {
    [localStorage, sessionStorage].forEach(storage => {
      storage.removeItem(ACCESS_TOKEN_KEY);
      storage.removeItem(REFRESH_TOKEN_KEY);
      storage.removeItem(USER_KEY);
    });
    localStorage.removeItem(REMEMBER_ME_KEY);
  }
};
```

### 3. Auth Context (`frontend/contexts/auth-context.tsx`)

**Key Features**:
- React Context voor app-wide auth state
- Login/logout functies
- Auto token refresh met timer
- Permission checks
- Loading en error states

**Implementation Notes**:
- Use `useEffect` voor initial auth check on mount
- Set up refresh timer (5 min voor expiry)
- Handle refresh failures gracefully (logout)
- Provide context met `<AuthProvider>` in layout

**State Management**:
```typescript
const [state, setState] = useState<AuthState>({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true, // Start als true voor initial check
  error: null
});
```

### 4. API Client Updates (`frontend/lib/api.ts`)

**Toevoegen**:

```typescript
// Auth endpoints
export const api = {
  // ...existing code...
  
  auth: {
    /**
     * Login met username en password
     */
    async login(credentials: LoginCredentials): Promise<TokenResponse> {
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login?remember_me=${credentials.remember_me || false}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      return response.json();
    },

    /**
     * Refresh access token
     */
    async refresh(refreshToken: string): Promise<TokenResponse> {
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      return response.json();
    },

    /**
     * Get current user info
     */
    async me(accessToken: string): Promise<User> {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get user info');
      }

      return response.json();
    },

    /**
     * Logout (client-side cleanup)
     */
    async logout(accessToken: string): Promise<void> {
      try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });
      } catch {
        // Ignore errors, cleanup locally anyway
      }
    }
  }
};
```

**Modify fetchAPI**:
```typescript
async function fetchAPI<T>(endpoint: string, accessToken?: string): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add authorization header if token provided
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });

  // Handle 401 - token expired (trigger refresh in context)
  if (response.status === 401) {
    throw new Error('UNAUTHORIZED');
  }

  // Handle 403 - forbidden
  if (response.status === 403) {
    throw new Error('FORBIDDEN');
  }

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}
```

### 5. Login Pagina Design (`frontend/app/login/page.tsx`)

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│                                         │
│              [MC Logo]                  │
│                                         │
│     Digital Resupplying Tool           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │  [🔑] Gebruikersnaam            │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │                         │   │   │
│  │  └─────────────────────────┘   │   │
│  │                                 │   │
│  │  [🔒] Wachtwoord               │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │                     [👁] │   │   │
│  │  └─────────────────────────┘   │   │
│  │                                 │   │
│  │  [▢] Onthoud mij                │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │    INLOGGEN   [→]       │   │   │
│  │  └─────────────────────────┘   │   │
│  │                                 │   │
│  │  ⓘ Error message hier           │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│     Hulp nodig? Contact IT support     │
│                                         │
└─────────────────────────────────────────┘
```

**Tailwind Classes Reference**:
```typescript
// Container
"min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800"

// Card
"w-full max-w-md p-8"

// Logo container
"flex flex-col items-center mb-8"

// Inputs
"w-full"

// Button
"w-full bg-primary hover:bg-primary/90"

// Error message
"text-sm text-red-500 mt-2"

// Remember me
"flex items-center space-x-2"
```

### 6. Protected Route (`frontend/components/auth/protected-route.tsx`)

**Implementation**:
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  permission?: string; // Optionele permission check
  fallback?: React.ReactNode; // Custom fallback component
}

export function ProtectedRoute({ children, permission, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasPermission } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect naar login met return URL
      router.push(`/login?returnUrl=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isAuthenticated, isLoading, router]);

  // Loading state
  if (isLoading) {
    return fallback || <div>Authenticatie controleren...</div>;
  }

  // Not authenticated
  if (!isAuthenticated) {
    return null; // Redirect happens in useEffect
  }

  // Check permission if specified
  if (permission && !hasPermission(permission)) {
    return <div>Je hebt geen toegang tot deze pagina.</div>;
  }

  return <>{children}</>;
}
```

### 7. User Menu (`frontend/components/auth/user-menu.tsx`)

**Features**:
- Avatar met initialen (eerste letter voornaam + achternaam)
- Dropdown menu met opties
- Role badge
- Logout met confirmation (optioneel)

**Shadcn/ui Components**:
- `DropdownMenu` voor menu
- `Avatar` voor user icon
- `Separator` voor scheidingslijn in menu

---

## 🎨 Design Guidelines

### Color Scheme
- **Primary**: Blue/Indigo (consistent met MC Company)
- **Success**: Green (na login)
- **Error**: Red (validation errors)
- **Neutral**: Gray (borders, text)

### Typography
- **Headings**: Font weight 600-700
- **Body**: Font weight 400
- **Labels**: Font weight 500

### Spacing
- **Card padding**: 2rem (p-8)
- **Input spacing**: 1rem between (gap-4)
- **Section spacing**: 1.5rem (gap-6)

### Animations
- **Fade in**: 200ms ease
- **Button hover**: 150ms ease
- **Dropdown**: 200ms ease with slide

### Responsive Breakpoints
- **Mobile**: < 640px (col-span-1)
- **Tablet**: 640px - 1024px (col-span-2)
- **Desktop**: > 1024px (full layout)

---

## 🔐 Security Considerations

### Token Management
- ✅ Access token: In memory (React state)
- ✅ Refresh token: localStorage/sessionStorage
- ✅ Never log tokens
- ⚠️ Future: HttpOnly cookies (more secure)

### XSS Protection
- ✅ React escapes by default
- ✅ No `dangerouslySetInnerHTML` met user input
- ✅ Validate all inputs

### CSRF Protection
- ✅ JWT in Authorization header (niet in cookies)
- ✅ Geen CSRF nodig voor Bearer tokens

### Password Security
- ✅ Backend: bcrypt hashing (cost 12)
- ✅ Frontend: HTTPS in productie
- ✅ No password in logs
- ✅ Strong password policy enforced

---

## 📊 Testing Checklist

### Functional Tests
- [ ] **Login Flow**
  - [ ] Correct credentials → Success
  - [ ] Wrong username → Error
  - [ ] Wrong password → Error
  - [ ] Empty fields → Validation error
  - [ ] Network error → User-friendly message

- [ ] **Token Management**
  - [ ] Token stored after login
  - [ ] Token sent in API calls
  - [ ] Token refresh works automatically
  - [ ] Expired token handled gracefully
  - [ ] Logout clears tokens

- [ ] **Route Protection**
  - [ ] Protected routes redirect to login
  - [ ] Login required message shown
  - [ ] Return URL works after login
  - [ ] Direct URL access blocked
  - [ ] Back button doesn't break auth

- [ ] **Remember Me**
  - [ ] LocalStorage used if checked
  - [ ] SessionStorage used if not checked
  - [ ] Page refresh keeps session (if remembered)
  - [ ] Page refresh loses session (if not remembered)

- [ ] **User Menu**
  - [ ] Shows correct user name
  - [ ] Shows correct role
  - [ ] Logout button works
  - [ ] Menu closes after action

- [ ] **Permissions**
  - [ ] Admin sees all features
  - [ ] User sees limited features
  - [ ] Store sees only relevant features
  - [ ] Permission checks work in UI

### UI/UX Tests
- [ ] **Login Page**
  - [ ] Dark mode works
  - [ ] Light mode works
  - [ ] Mobile responsive
  - [ ] Tablet responsive
  - [ ] Desktop layout correct
  - [ ] Logo visible
  - [ ] Form centered
  - [ ] Error messages clear

- [ ] **Loading States**
  - [ ] Login button shows spinner
  - [ ] Initial auth check shows loading
  - [ ] Token refresh silent (no UI blocking)
  - [ ] Protected route shows loading placeholder

- [ ] **Error States**
  - [ ] Network errors shown
  - [ ] Auth errors shown
  - [ ] Session expired modal appears
  - [ ] Clear error messages (Nederlands)

- [ ] **Animations**
  - [ ] Smooth transitions
  - [ ] No flashing content
  - [ ] Loading spinners smooth
  - [ ] Dropdown animations smooth

### Edge Cases
- [ ] **Browser**
  - [ ] Works in Chrome
  - [ ] Works in Firefox
  - [ ] Works in Safari
  - [ ] Works in Edge

- [ ] **Network**
  - [ ] Handles slow connection
  - [ ] Handles offline mode
  - [ ] Recovers from network failure
  - [ ] Timeout handling

- [ ] **Multiple Tabs**
  - [ ] Logout in one tab logs out others
  - [ ] Token refresh syncs across tabs
  - [ ] State consistency

- [ ] **Edge Scenarios**
  - [ ] Backend down during login
  - [ ] Token expired mid-request
  - [ ] Corrupted storage data
  - [ ] Browser back/forward navigation
  - [ ] Page refresh during login
  - [ ] Session timeout during form fill

---

## 🚀 Quick Start Guide

### Stap 1: Installeer Benodigde Packages

```bash
cd frontend

# Shadcn/ui components (als nog niet geïnstalleerd)
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input  
npx shadcn-ui@latest add button
npx shadcn-ui@latest add label
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add alert-dialog

# Iconen voor UI (als nog niet geïnstalleerd)
npm install lucide-react
```

### Stap 2: Maak Directory Structuur

```bash
# Vanuit frontend directory
mkdir -p types
mkdir -p contexts
mkdir -p components/auth
mkdir -p app/login
```

### Stap 3: Start met FASE 1 - Foundation

Begin met de basis types en utilities:
1. `frontend/types/auth.ts` - TypeScript interfaces
2. `frontend/lib/token-storage.ts` - Token storage
3. `frontend/contexts/auth-context.tsx` - Auth context
4. Update `frontend/lib/api.ts` - Auth endpoints

### Stap 4: Bouw FASE 2 - UI Core

Maak de login UI:
1. `frontend/app/login/layout.tsx` - Login layout
2. `frontend/app/login/page.tsx` - Login pagina
3. `frontend/components/auth/protected-route.tsx` - Route protection
4. Update `frontend/app/layout.tsx` - Integratie

### Stap 5: Test de Basis Flow

```bash
# Start dev server
npm run dev

# Test:
# 1. Ga naar http://localhost:3000
# 2. Wordt doorgestuurd naar /login
# 3. Log in met test credentials
# 4. Wordt doorgestuurd naar dashboard
```

### Stap 6: Voltooi FASE 3 & 4

Add user experience en advanced features volgens plan.

---

## 📝 Implementation Notes

### Backend Test Credentials

Na het seeden van de database zijn deze test users beschikbaar:

**Admin Account**:
- Username: `admin`
- Password: `Admin123!@#` (of zoals gedefinieerd in seed_database.py)
- Rol: Admin (volledige toegang)

**User Account**:
- Username: `user`
- Password: `User123!@#`
- Rol: User (beperkte toegang)

**Store Account**:
- Username: `store`
- Password: `Store123!@#`
- Rol: Store (winkel-specifiek)

### Development Tips

1. **Token Expiry Testing**
   - Access token: 15 minuten
   - Force expiry: Verander tijd in browser DevTools
   - Test refresh flow

2. **Permission Testing**
   - Log in als verschillende rollen
   - Verify UI changes per rol
   - Check console voor permission logs

3. **Error Testing**
   - Stop backend server → Test network errors
   - Wrong credentials → Test error messages
   - Clear storage → Test auth recovery

4. **Mobile Testing**
   - Chrome DevTools responsive mode
   - Test all breakpoints
   - Check touch interactions

### Common Pitfalls

❌ **Hydration Errors**
- Probleem: Server/client mismatch bij auth check
- Oplossing: Use `useEffect` voor auth check, niet in render

❌ **Token in URL**
- Probleem: Never put tokens in URLs
- Oplossing: Always use headers for Bearer tokens

❌ **Infinite Redirect Loop**
- Probleem: Login page redirects to login
- Oplossing: Exclude /login from route protection

❌ **CORS Errors**
- Probleem: Backend blocks requests
- Oplossing: Check CORS config in `backend/main.py`

❌ **Storage Quota**
- Probleem: localStorage can be full
- Oplossing: Add try/catch around storage operations

---

## 🔄 Migration Path

### Van Huidige Situatie → Met Auth

**Stap 1: Backward Compatibility**
- Implementeer auth zonder oude functionaliteit te breken
- Keep existing pages werkend
- Add auth layer gradually

**Stap 2: Toggle Auth (Development)**
```typescript
// Voor development: maak auth optioneel
const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true';

if (!AUTH_ENABLED) {
  // Skip auth checks tijdens development
}
```

**Stap 3: Test Thoroughly**
- Test alle bestaande flows
- Verify geen breaking changes
- Check API calls still work

**Stap 4: Enable Auth**
- Set `AUTH_ENABLED=true`
- Deploy to staging
- Full testing cycle
- Deploy to production

---

## 📦 Dependencies

### Required
- `react` (al geïnstalleerd)
- `next` (al geïnstalleerd)
- `@radix-ui/*` (via shadcn/ui)
- `lucide-react` (iconen)

### Optional (Future)
- `react-hook-form` - Form validation
- `zod` - Schema validation
- `jose` - JWT decoding (if needed client-side)
- `@tanstack/react-query` - Better API state management

---

## 🎓 Learning Resources

### JWT & Authentication
- [JWT.io](https://jwt.io/) - JWT debugging
- [OAuth 2.0](https://oauth.net/2/) - OAuth reference
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### React Patterns
- [React Context](https://react.dev/learn/passing-data-deeply-with-context)
- [Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Next.js Authentication](https://nextjs.org/docs/app/building-your-application/authentication)

### UI/UX
- [Shadcn/ui Docs](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/) - Headless components

---

## 🐛 Debugging Guide

### Auth Not Working?

**Check 1: Backend Running?**
```bash
# Start backend
cd backend
.venv\Scripts\python.exe main.py

# Check health
curl http://localhost:8000/health
```

**Check 2: CORS Configured?**
```python
# backend/main.py should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check 3: Tokens in Storage?**
```javascript
// Browser console:
console.log(localStorage.getItem('drt_access_token'));
console.log(localStorage.getItem('drt_refresh_token'));
```

**Check 4: API Calls have Token?**
```javascript
// Browser DevTools → Network tab
// Check request headers:
// Authorization: Bearer <token>
```

### Login Errors?

**401 Unauthorized**
- Wrong username/password
- Check backend logs
- Verify user exists in database

**403 Forbidden**
- User not active
- Missing permissions
- Check role assignment

**500 Server Error**
- Backend error
- Check backend logs
- Database connection issue?

**Network Error**
- Backend not running
- Wrong URL/port
- Firewall blocking?

---

## 📊 Progress Tracking

Use deze checklist om voortgang bij te houden:

### Overall Progress
- [ ] FASE 1: Foundation (0/4 taken)
- [ ] FASE 2: UI Core (0/3 taken)
- [ ] FASE 3: User Experience (0/4 taken)
- [ ] FASE 4: Advanced Features (0/3 taken)
- [ ] FASE 5: Testing & Polish (0/3 taken)

### Quick Status
- **Status**: 🟡 In Progress / 🟢 Voltooid / 🔴 Geblokkeerd
- **Huidige Fase**: FASE 1
- **Geschatte Resterende Tijd**: ~6-7 uur
- **Blokkerende Issues**: Geen

### Latest Updates
- **2 november 2025 - 11:24**: Plan aangemaakt, klaar voor implementatie
- **[Datum]**: [Update hier]
- **[Datum]**: [Update hier]

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
✅ MVP is bereikt wanneer:
- [ ] Users kunnen inloggen met username/password
- [ ] Remember Me functionaliteit werkt
- [ ] Protected routes redirecten naar login
- [ ] API calls zijn authenticated
- [ ] User kan uitloggen
- [ ] Basis error handling werkt

### Production Ready
✅ Production ready wanneer:
- [ ] All MVP criteria
- [ ] User menu in sidebar
- [ ] Permission-based UI rendering
- [ ] Auto token refresh werkt
- [ ] Session expired handling
- [ ] Mobile responsive
- [ ] Dark/light mode support
- [ ] All tests passing
- [ ] Error messages user-friendly
- [ ] Loading states polished

### Feature Complete
✅ Feature complete wanneer:
- [ ] All Production Ready criteria
- [ ] Dashboard personalisatie
- [ ] Permission gates overal
- [ ] Advanced error recovery
- [ ] Multiple tabs sync
- [ ] Full accessibility
- [ ] Performance optimized
- [ ] Security audit passed

---

## 🎉 Conclusie

Dit plan biedt een complete roadmap voor het implementeren van een production-ready authentication systeem in DRT. Met het gisteren gebouwde backend systeem als fundament, kunnen we nu een professionele en veilige frontend auth flow bouwen.

### Verwachte Tijdlijn
- **FASE 1-2**: Dag 1 (4 uur) - Core functionaliteit
- **FASE 3-4**: Dag 2 (2.5 uur) - UX en advanced features  
- **FASE 5**: Dag 2-3 (1 uur) - Testing en polish
- **Totaal**: 6-7.5 uur werk

### Volgende Stappen
1. ✅ Review dit plan
2. ⏩ Start met FASE 1.1 - TypeScript Types
3. 🔄 Work through checklist systematisch
4. ✅ Test na elke fase
5. 🎯 MVP first, dan polish

**Status**: 🟢 Plan Complete - Ready for Implementation!

---

**Laatste Update**: 2 november 2025 - 11:25  
**Document Versie**: 1.0  
**Eigenaar**: Digital Resupplying Tool Team
