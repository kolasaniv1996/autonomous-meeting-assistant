import { useState, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { Dashboard } from './pages/Dashboard'
import { Configurations } from './pages/Configurations'
import { Agents } from './pages/Agents'
import { Meetings } from './pages/Meetings'
import { Settings } from './pages/Settings'
import { LoginPage } from './pages/Login'
import { RegisterPage } from './pages/Register'
import { HandleAuthTokenPage } from './pages/HandleAuthToken' // Import the new page
import './App.css'

const ProtectedRoute = ({ element }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return element;
};

function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard'); // This might need to be derived from useLocation now
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/handle-token" element={<HandleAuthTokenPage />} />
        <Route path="/auth/token/:token" element={<HandleAuthTokenPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        open={sidebarOpen}
        setOpen={setSidebarOpen}
        currentPage={currentPage} // Consider updating how currentPage is set
        setCurrentPage={setCurrentPage}
      />
      <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-16'}`}>
        <Header
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          currentPage={currentPage} // Consider updating
        />
        <main className="p-6">
          <Routes>
            <Route path="/" element={<ProtectedRoute element={<Navigate to="/dashboard" replace />} />} />
            <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
            <Route path="/configurations" element={<ProtectedRoute element={<Configurations />} />} />
            <Route path="/agents" element={<ProtectedRoute element={<Agents />} />} />
            <Route path="/meetings" element={<ProtectedRoute element={<Meetings />} />} />
            <Route path="/settings" element={<ProtectedRoute element={<Settings />} />} />
            {/* These are already defined above for non-authenticated users, but explicitly defining them here
                ensures they are available if the MainLayout is rendered while not authenticated,
                though the current structure makes that unlikely. This also ensures they are defined if
                the auth logic changes slightly. */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/auth/handle-token" element={<HandleAuthTokenPage />} />
            <Route path="/auth/token/:token" element={<HandleAuthTokenPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </Router>
  );
}

export default App;

