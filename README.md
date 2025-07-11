# SRM College Timetable Management System

A comprehensive, production-ready AI-powered timetable management system built for SRM College Ramapuram. This full-stack application automates timetable allocation for staff and students with intelligent conflict resolution and optimization, powered by Supabase.

## 🚀 Features

### Core Functionality
- **Staff Registration & Authentication** - Secure login using SRM email domains (@srmist.edu.in)
- **Dual Admin System** - Main Admin and Department Admin portals with role-based access
- **Role-Based Subject Allocation** - Assistant Professors (2 subjects), Professors/HODs (1 subject)
- **AI-Powered Timetable Generation** - Intelligent scheduling with conflict detection
- **Dynamic Classroom Allocation** - Automated room assignment based on availability
- **Real-time Updates** - Live notifications and data synchronization

### AI Features
- **Conflict Detection** - Automatically identifies scheduling conflicts
- **Load Balancing** - Optimally distributes teaching hours across staff
- **Smart Suggestions** - AI recommendations for optimal scheduling
- **Constraint Optimization** - Respects all institutional rules and preferences

### Security & Performance
- **Supabase Authentication** - Secure authentication with Row Level Security
- **Real-time Database** - PostgreSQL with real-time subscriptions
- **Input Validation** - Comprehensive data validation
- **Database Integrity** - Foreign key constraints and data consistency

## 🛠 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Router** for navigation

### Backend
- **Supabase** - Backend-as-a-Service
- **PostgreSQL** database with structured schema
- **Row Level Security** for data protection
- **Real-time subscriptions** for live updates

### AI & Algorithms
- **Custom optimization algorithms** for timetable generation
- **Constraint satisfaction** for conflict resolution
- **Heuristic scheduling** for load balancing

## 📁 Project Structure

```
srm-timetable-system/
├── src/
│   ├── components/           # React components
│   │   ├── Dashboard.tsx     # Main dashboard
│   │   ├── LoginForm.tsx     # Authentication
│   │   ├── RegisterForm.tsx  # Staff registration
│   │   ├── DepartmentManagement.tsx
│   │   ├── StaffManagement.tsx
│   │   ├── SubjectManagement.tsx
│   │   └── TimetableManagement.tsx
│   ├── lib/
│   │   └── supabase.ts       # Supabase client configuration
│   ├── services/
│   │   └── supabaseService.ts # API service layer
│   └── App.tsx               # Main application
├── supabase/
│   └── migrations/           # Database migrations
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd srm-timetable-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up Supabase**
   - Create a new project at [supabase.com](https://supabase.com)
   - Copy your project URL and anon key
   - Update `.env` file:
   ```env
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

4. **Run database migrations**
   - Go to your Supabase dashboard
   - Navigate to SQL Editor
   - Run the migration file from `supabase/migrations/`

5. **Start the development server**
   ```bash
   npm run dev
   ```

The application will be available at: http://localhost:5173

### Default Credentials
- **Main Admin**: admin@srmist.edu.in / admin123

## 📋 API Documentation

### Authentication
- Supabase Auth handles user authentication
- Custom authentication for staff/admin roles
- Row Level Security policies for data protection

### Database Tables
- **main_admin** - Main administrator accounts
- **departments** - Department information
- **staff** - Staff members and their roles
- **subjects** - Course subjects and assignments
- **timetable** - Generated schedules
- **classrooms** - Room information and availability
- **time_slots** - Available time periods
- **system_rules** - Dynamic configuration rules

## 🤖 AI Algorithm Details

### Timetable Generation Process
1. **Data Collection** - Gather all constraints and requirements
2. **Conflict Detection** - Identify potential scheduling conflicts
3. **Optimization** - Apply heuristic algorithms for optimal placement
4. **Validation** - Ensure all constraints are satisfied
5. **Refinement** - Iterative improvement of the schedule

### Constraints Handled
- Staff availability and maximum hours
- Classroom capacity and availability
- Subject requirements and prerequisites
- Lunch breaks and institutional policies
- Department-specific rules and preferences

## 🔒 Security Features

- **Row Level Security** - Database-level access control
- **Email Domain Validation** - Only @srmist.edu.in emails allowed
- **Password Hashing** - bcrypt with salt rounds
- **Real-time Policies** - Dynamic security rules
- **Input Sanitization** - XSS and injection protection

## 📱 User Roles & Permissions

### Main Admin
- Manage all departments and staff
- Set system-wide rules and policies
- Generate and export timetables
- Access comprehensive analytics

### Department Admin
- Manage department staff and subjects
- Generate department timetables
- Assign subjects to staff
- Monitor department activities

### Staff
- View personal timetable
- View assigned subjects
- Update personal information
- Access department resources

## 🎨 UI/UX Features

- **Responsive Design** - Works on all devices
- **Modern Interface** - Clean, professional design
- **Accessibility** - WCAG 2.1 compliant
- **Interactive Elements** - Hover states and animations
- **Loading States** - Progress indicators
- **Error Handling** - User-friendly error messages

## 📈 Performance Optimizations

- **Database Indexing** - Optimized queries
- **Real-time Updates** - Efficient data synchronization
- **Lazy Loading** - Component optimization
- **Bundle Splitting** - Reduced initial load
- **Caching** - Optimized data fetching

## 🚢 Deployment

### Production Build
```bash
npm run build
```

### Environment Variables
```env
# Production environment
VITE_SUPABASE_URL=your_production_supabase_url
VITE_SUPABASE_ANON_KEY=your_production_anon_key
```

### Netlify Deployment
The application is optimized for Netlify deployment with automatic builds from Git.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the migration files for database setup

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic timetable generation
- ✅ Staff and department management
- ✅ Supabase integration
- ✅ Real-time updates

### Phase 2 (Next)
- 🔄 Excel export functionality
- 🔄 Advanced AI features
- 🔄 Mobile responsiveness improvements

### Phase 3 (Future)
- 📋 Student portal
- 📋 Attendance tracking
- 📋 Performance analytics

---

Built with ❤️ for SRM College Ramapuram using React, TypeScript, Tailwind CSS, and Supabase.#   S R M _ T I M E T A B L E _ T E S T I N G 1  
 