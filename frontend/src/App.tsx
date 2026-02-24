/**
 * Main App component with routing and authentication.
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import SignUp from './pages/SignUp';
import SignIn from './pages/SignIn';
import Dashboard from './pages/DashboardNeo';
import Profile from './pages/Profile';
import OutreachEmail from './pages/OutreachEmail';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/signup" element={<SignUp />} />
          <Route path="/signin" element={<SignIn />} />
          
          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/outreach"
            element={
              <ProtectedRoute>
                <OutreachEmail />
              </ProtectedRoute>
            }
          />
          
          {/* Redirect root to dashboard (or signin if not authenticated) */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* 404 - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
