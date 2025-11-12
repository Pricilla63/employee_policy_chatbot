// import React, { useState } from 'react';
// import {
//   BrowserRouter as Router,
//   Routes,
//   Route,
//   Navigate,
// } from 'react-router-dom';
// import { AuthProvider, useAuth } from './context/authcontext';
// import Login from './components/auth/login';
// import Register from './components/auth/register';
// import Sidebar from './components/layout/sidebar';
// import ChatArea from './components/layout/chatarea';
// import Loader from './components/common/loader';
// import ErrorBoundary from './components/common/errorboundary';

// const PrivateRoute = ({ children }) => {
//   const { user, loading } = useAuth();

//   if (loading) {
//     return <Loader />;
//   }

//   return user ? children : <Navigate to="/login" />;
// };

// const ChatPage = () => {
//   const [selectedHistory, setSelectedHistory] = useState(null);
//   const [refreshKey, setRefreshKey] = useState(0);

//   const handleNewChat = () => {
//     setSelectedHistory(null);
//     setRefreshKey((prev) => prev + 1);
//   };

//   const handleNewMessage = () => {
//     setRefreshKey((prev) => prev + 1);
//   };

//   return (
//     <div className="flex h-screen overflow-hidden bg-gray-50">
//       <Sidebar
//         key={refreshKey}
//         onNewChat={handleNewChat}
//         onSelectHistory={setSelectedHistory}
//         selectedHistory={selectedHistory} // Add this line
//       />
//       <ChatArea
//         selectedHistory={selectedHistory}
//         onNewMessage={handleNewMessage}
//       />
//     </div>
//   );
// };

// function App() {
//   return (
//     <ErrorBoundary>
//       <AuthProvider>
//         <Router>
//           <Routes>
//             <Route path="/login" element={<Login />} />
//             <Route path="/register" element={<Register />} />
//             <Route
//               path="/chat"
//               element={
//                 <PrivateRoute>
//                   <ChatPage />
//                 </PrivateRoute>
//               }
//             />
//             <Route path="/" element={<Navigate to="/chat" />} />
//             <Route path="*" element={<Navigate to="/chat" />} />
//           </Routes>
//         </Router>
//       </AuthProvider>
//     </ErrorBoundary>
//   );
// }

// export default App;



// import React, { useState } from 'react';
// import {
//   BrowserRouter as Router,
//   Routes,
//   Route,
//   Navigate,
// } from 'react-router-dom';
// import { AuthProvider, useAuth } from './context/authcontext';
// import Login from './components/auth/login';
// import Register from './components/auth/register';
// import Sidebar from './components/layout/sidebar';
// import ChatArea from './components/layout/chatarea';
// import Loader from './components/common/loader';
// import ErrorBoundary from './components/common/errorboundary';

// const PrivateRoute = ({ children }) => {
//   const { user, loading } = useAuth();

//   if (loading) {
//     return <Loader />;
//   }

//   return user ? children : <Navigate to="/login" />;
// };

// const ChatPage = () => {
//   const [selectedHistory, setSelectedHistory] = useState(null);
//   const [refreshKey, setRefreshKey] = useState(0);
//   const [currentMessages, setCurrentMessages] = useState([]);

//   // Handle new chat - Reset all states
//   const handleNewChat = () => {
//     setSelectedHistory(null);  // Clear selected history
//     setCurrentMessages([]);    // Clear current messages
//     setRefreshKey((prev) => prev + 1);  // Force refresh
//   };

//   // Handle selecting a history item
//   const handleSelectHistory = (historyItem) => {
//     setSelectedHistory(historyItem);
//     setRefreshKey((prev) => prev + 1);  // Force refresh when selecting history
//   };

//   // Handle new message sent
//   const handleNewMessage = () => {
//     setRefreshKey((prev) => prev + 1);  // This will trigger sidebar to reload history
//   };

//   // Handle messages update from ChatArea
//   const handleMessagesUpdate = (messages) => {
//     setCurrentMessages(messages);
//   };

//   return (
//     <div className="flex h-screen overflow-hidden bg-gray-50">
//       <Sidebar
//         onNewChat={handleNewChat}
//         onSelectHistory={handleSelectHistory}
//         selectedHistory={selectedHistory}
//         refreshTrigger={refreshKey}
//       />
//       <ChatArea
//         key={`chatarea-${refreshKey}`}  // Add key to force re-render
//         selectedHistory={selectedHistory}
//         onNewMessage={handleNewMessage}
//         onMessagesUpdate={handleMessagesUpdate}
//         currentMessages={currentMessages}
//       />
//     </div>
//   );
// };

// function App() {
//   return (
//     <ErrorBoundary>
//       <AuthProvider>
//         <Router>
//           <Routes>
//             <Route path="/login" element={<Login />} />
//             <Route path="/register" element={<Register />} />
//             <Route
//               path="/chat"
//               element={
//                 <PrivateRoute>
//                   <ChatPage />
//                 </PrivateRoute>
//               }
//             />
//             <Route path="/" element={<Navigate to="/chat" />} />
//             <Route path="*" element={<Navigate to="/chat" />} />
//           </Routes>
//         </Router>
//       </AuthProvider>
//     </ErrorBoundary>
//   );
// }

// export default App;



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
  const [currentMessages, setCurrentMessages] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  // Handle new chat - Reset all states and create new conversation
  const handleNewChat = async () => {
    try {
      // Save current conversation if it exists and has messages
      if (currentConversationId && currentMessages.length > 0) {
        // Conversation is already saved, just deactivate it by starting new one
        // This will make the backend deactivate current and prepare for new
      }
      
      // Explicitly start new conversation
      // await conversationsAPI.startNewConversation();
      
      setSelectedHistory(null);
      setCurrentMessages([]);
      setCurrentConversationId(null);
      setRefreshKey((prev) => prev + 1);
    } catch (error) {
      console.error('Error starting new chat:', error);
    }
  };

  // Handle selecting a history item
  const handleSelectHistory = (historyItem) => {
    setSelectedHistory(historyItem);
    setCurrentConversationId(historyItem._id);
    setRefreshKey((prev) => prev + 1);
  };

  // Handle new message sent
  const handleNewMessage = () => {
    setRefreshKey((prev) => prev + 1);  // This will trigger sidebar to reload history
  };

  // Handle messages update from ChatArea
  const handleMessagesUpdate = (messages) => {
    setCurrentMessages(messages);
  };

  // Handle conversation ID change
  const handleConversationIdChange = (conversationId) => {
    setCurrentConversationId(conversationId);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar
        onNewChat={handleNewChat}
        onSelectHistory={handleSelectHistory}
        selectedHistory={selectedHistory}
        refreshTrigger={refreshKey}
      />
      <ChatArea
        key={`chatarea-${refreshKey}`}  // Add key to force re-render
        selectedHistory={selectedHistory}
        onNewMessage={handleNewMessage}
        onMessagesUpdate={handleMessagesUpdate}
        currentMessages={currentMessages}
        currentConversationId={currentConversationId}
        onConversationIdChange={handleConversationIdChange}
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