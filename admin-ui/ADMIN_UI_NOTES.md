# Attendee Admin UI

Admin dashboard được xây dựng với **Qwik + TypeScript + Tailwind CSS**.

## 🎯 Tính năng đã hoàn thành

### 📱 **Mobile-First Responsive Design**
- ✅ **Mobile Layout**: Hamburger menu, overlay sidebar, mobile navigation
- ✅ **Responsive Tables**: `MobileTable` (cards) + `DesktopTable` (hidden trên mobile) 
- ✅ **Responsive Cards**: `CardGrid` với responsive columns
- ✅ **Mobile Components**: Touch-friendly buttons, responsive spacing

### 🎨 **UI Components System** 
- ✅ **FontAwesome Icons**: Toàn bộ hệ thống sử dụng `@fortawesome/free-solid-svg-icons`
- ✅ **Table Components**: Comprehensive table system với responsive support
- ✅ **Form Components**: SearchInput, StatusBadge, Filters
- ✅ **Layout Components**: Sidebar, Navbar, Cards với mobile support

### 📄 **Admin Pages**
- ✅ **Dashboard**: System stats, activity feed, quick actions
- ✅ **Users**: User management với search/filter/CRUD
- ✅ **Organizations**: Credits management, webhooks, status tracking
- ✅ **Projects**: Project management, API keys, status monitoring  
- ✅ **Bots**: Real-time bot monitoring, platform badges, controls
- ✅ **Transcriptions**: Job processing, provider stats, downloads
- ✅ **Webhooks**: Subscription management, delivery tracking
- ✅ **Settings**: System configuration, provider settings

### 🔗 **API Integration**
- ✅ **Axios Client**: Timeout, auth tokens, error handling
- ✅ **TypeScript Types**: Complete type definitions
- ✅ **Service Layer**: 8 API modules (auth, users, projects, bots, etc.)
- ✅ **Environment Config**: `VITE_API_BASE_URL` default localhost:8000

## 🚀 **Dev Setup**

```bash
# Install & Run
npm install
npm run dev    # http://localhost:5174

# Build & Preview  
npm run build
npm run preview
```

## 📱 **Mobile Features**

### Responsive Breakpoints
- **xs**: < 640px (Mobile)
- **sm**: 640px+ (Large mobile)  
- **md**: 768px+ (Tablet)
- **lg**: 1024px+ (Desktop)

### Mobile Components
- **MobileTable**: Card-based layout
- **DesktopTable**: Hidden below lg breakpoint
- **CardGrid**: Responsive grid (1 col mobile → 4 cols desktop)
- **Sidebar**: Overlay menu với backdrop

### Mobile UX
- Touch-friendly button sizes (min-height 44px)
- Horizontal scroll tables với `overflow-x-auto`
- Responsive text sizing (`text-xs sm:text-sm`)
- Mobile-first spacing (`px-3 sm:px-6`)

## 🎨 **Icon System**

**FontAwesome Integration:**
```tsx
import { FaIcon } from '../components/ui/fa-icon';
import { faUsers, faPlus } from '@fortawesome/free-solid-svg-icons';

<FaIcon icon={faUsers} class="h-5 w-5" />
```

**Available Icons:**
- Navigation: `faHome`, `faUsers`, `faBuilding`, `faFolder`, `faRobot`
- Actions: `faPlus`, `faEye`, `faPencil`, `faTrash`, `faCog` 
- Status: `faBell`, `faCheck`, `faXmark`, `faClock`
- Media: `faMicrophone`, `faDownload`, `faStop`

## 📊 **Data Flow**

```
FastAPI Backend ← → Admin UI (Qwik)
    ↓                   ↓
PostgreSQL         Axios Client
    ↓                   ↓  
Celery Jobs       API Services
```

## 🔄 **Next Steps**

1. **Backend Integration**: Connect to real FastAPI endpoints
2. **Authentication**: JWT token management, protected routes
3. **Real-time**: WebSocket cho bot status updates  
4. **Testing**: Component testing với Vitest
5. **Deployment**: Docker + production build optimization
