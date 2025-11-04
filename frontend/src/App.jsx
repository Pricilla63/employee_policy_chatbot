import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { AuthProvider, useAuth } from './context/authcontext';
import Login from './components/auth/login';
import Register from './components/auth/register';
import Sidebar from './components/layout/sidebar';
import ChatArea from './components/layout/chatarea';
import Loader from './components/common/loader';
import ErrorBoundary from './components/common/errorboundary';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <Loader />;
  }

  return user ? children : <Navigate to="/login" />;
};

const ChatPage = () => {
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleNewChat = () => {
    setSelectedHistory(null);
    setRefreshKey((prev) => prev + 1);
  };

  const handleNewMessage = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar
        key={refreshKey}
        onNewChat={handleNewChat}
        onSelectHistory={setSelectedHistory}
      />
      <ChatArea
        selectedHistory={selectedHistory}
        onNewMessage={handleNewMessage}
      />
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/chat"
              element={
                <PrivateRoute>
                  <ChatPage />
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/chat" />} />
            <Route path="*" element={<Navigate to="/chat" />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;