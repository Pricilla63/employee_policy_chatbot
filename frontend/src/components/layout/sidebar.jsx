// import React, { useState, useEffect } from 'react';
// import { useAuth } from '../../context/authcontext';
// import { historyAPI } from '../../services/api';
// import { MessageSquare, Plus, LogOut, Trash2 } from 'lucide-react';

// const Sidebar = ({ onNewChat, onSelectHistory }) => {
//   const { user, logout } = useAuth();
//   const [history, setHistory] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     loadHistory();
//   }, []);

//   const loadHistory = async () => {
//     try {
//       const response = await historyAPI.getHistory(50, 0);
//       setHistory(response.data);
//     } catch (error) {
//       console.error('Error loading history:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleDeleteHistory = async (id, e) => {
//     e.stopPropagation();
//     if (window.confirm('Delete this conversation?')) {
//       try {
//         await historyAPI.deleteItem(id);
//         await loadHistory();
//       } catch (error) {
//         alert('Error deleting conversation');
//       }
//     }
//   };

//   const formatDate = (dateString) => {
//     const date = new Date(dateString);
//     const now = new Date();
//     const diffMs = now - date;
//     const diffMins = Math.floor(diffMs / 60000);
//     const diffHours = Math.floor(diffMs / 3600000);
//     const diffDays = Math.floor(diffMs / 86400000);

//     if (diffMins < 1) return 'Just now';
//     if (diffMins < 60) return `${diffMins}m ago`;
//     if (diffHours < 24) return `${diffHours}h ago`;
//     if (diffDays === 0) return 'Today';
//     if (diffDays === 1) return 'Yesterday';
//     if (diffDays < 7) return `${diffDays}d ago`;
//     return date.toLocaleDateString();
//   };

//   const groupHistoryByDate = () => {
//     const groups = {
//       today: [],
//       yesterday: [],
//       previous7Days: [],
//       older: [],
//     };

//     const now = new Date();
//     const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
//     const yesterday = new Date(today);
//     yesterday.setDate(yesterday.getDate() - 1);
//     const sevenDaysAgo = new Date(today);
//     sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

//     history.forEach((item) => {
//       const itemDate = new Date(item.timestamp);
//       const itemDay = new Date(
//         itemDate.getFullYear(),
//         itemDate.getMonth(),
//         itemDate.getDate()
//       );

//       if (itemDay.getTime() === today.getTime()) {
//         groups.today.push(item);
//       } else if (itemDay.getTime() === yesterday.getTime()) {
//         groups.yesterday.push(item);
//       } else if (itemDate >= sevenDaysAgo) {
//         groups.previous7Days.push(item);
//       } else {
//         groups.older.push(item);
//       }
//     });

//     return groups;
//   };

//   const groupedHistory = groupHistoryByDate();

//   const HistoryGroup = ({ title, items }) => {
//     if (items.length === 0) return null;

//     return (
//       <div className="mb-4">
//         <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">
//           {title}
//         </h3>
//         <div className="space-y-1">
//           {items.map((item) => (
//             <div
//               key={item._id}
//               onClick={() => onSelectHistory(item)}
//               className="w-full text-left p-3 hover:bg-gray-800 rounded-lg transition group relative cursor-pointer"
//             >
//               <div className="flex items-start gap-3">
//                 <MessageSquare
//                   size={16}
//                   className="text-gray-400 mt-1 flex-shrink-0"
//                 />
//                 <div className="flex-1 min-w-0">
//                   <p className="text-sm truncate pr-6">{item.question}</p>
//                 </div>
//                 {/* Changed from button to div with onClick */}
//                 <div
//                   onClick={(e) => handleDeleteHistory(item._id, e)}
//                   className="absolute right-2 top-3 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition cursor-pointer"
//                   role="button"
//                   aria-label="Delete conversation"
//                 >
//                   <Trash2 size={16} />
//                 </div>
//               </div>
//             </div>
//           ))}
//         </div>
//       </div>
//     );
//   };

//   return (
//     <div className="w-80 bg-gray-900 text-white flex flex-col h-screen">
//       {/* Header */}
//       <div className="p-4 border-b border-gray-800">
//         <button
//           onClick={onNewChat}
//           className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 py-3 rounded-lg transition font-medium"
//         >
//           <Plus size={20} />
//           New Chat
//         </button>
//       </div>

//       {/* Chat History */}
//       <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
//         {loading ? (
//           <div className="flex items-center justify-center py-8">
//             <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
//           </div>
//         ) : history.length === 0 ? (
//           <div className="text-center py-8 text-gray-500">
//             <MessageSquare className="mx-auto mb-2" size={32} />
//             <p className="text-sm">No conversations yet</p>
//           </div>
//         ) : (
//           <>
//             <HistoryGroup title="Today" items={groupedHistory.today} />
//             <HistoryGroup title="Yesterday" items={groupedHistory.yesterday} />
//             <HistoryGroup
//               title="Previous 7 Days"
//               items={groupedHistory.previous7Days}
//             />
//             <HistoryGroup title="Older" items={groupedHistory.older} />
//           </>
//         )}
//       </div>

//       {/* User Section - Bottom */}
//       <div className="p-4 border-t border-gray-800 bg-gray-900">
//         <div className="flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center font-semibold text-white">
//               {user?.username?.charAt(0).toUpperCase()}
//             </div>
//             <div>
//               <p className="text-sm font-medium">{user?.username}</p>
//               <p className="text-xs text-gray-400">Online</p>
//             </div>
//           </div>
//           <button
//             onClick={logout}
//             className="text-gray-400 hover:text-red-400 transition p-2 hover:bg-gray-800 rounded-lg"
//             title="Logout"
//           >
//             <LogOut size={20} />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Sidebar;



import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/authcontext';
import { historyAPI } from '../../services/api';
import { MessageSquare, Plus, LogOut, Trash2 } from 'lucide-react';

const Sidebar = ({ onNewChat, onSelectHistory }) => {
  const { user, logout } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await historyAPI.getHistory(50, 0);
      setHistory(response.data);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteHistory = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation?')) {
      try {
        await historyAPI.deleteItem(id);
        await loadHistory();
      } catch (error) {
        alert('Error deleting conversation');
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const groupHistoryByDate = () => {
    const groups = {
      today: [],
      yesterday: [],
      previous7Days: [],
      older: [],
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const sevenDaysAgo = new Date(today);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    history.forEach((item) => {
      const itemDate = new Date(item.timestamp);
      const itemDay = new Date(
        itemDate.getFullYear(),
        itemDate.getMonth(),
        itemDate.getDate()
      );

      if (itemDay.getTime() === today.getTime()) {
        groups.today.push(item);
      } else if (itemDay.getTime() === yesterday.getTime()) {
        groups.yesterday.push(item);
      } else if (itemDate >= sevenDaysAgo) {
        groups.previous7Days.push(item);
      } else {
        groups.older.push(item);
      }
    });

    return groups;
  };

  const groupedHistory = groupHistoryByDate();

  const HistoryGroup = ({ title, items }) => {
    if (items.length === 0) return null;

    return (
      <div className="mb-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">
          {title}
        </h3>
        <div className="space-y-1">
          {items.map((item) => (
            <div
              key={item._id}
              onClick={() => onSelectHistory(item)}
              className="w-full text-left p-3 hover:bg-gray-800 rounded-lg transition group relative cursor-pointer"
            >
              <div className="flex items-start gap-3">
                <MessageSquare
                  size={16}
                  className="text-gray-400 mt-1 flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate pr-6">{item.question}</p>
                </div>
                {/* Changed from button to div with onClick */}
                <div
                  onClick={(e) => handleDeleteHistory(item._id, e)}
                  className="absolute right-2 top-3 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition cursor-pointer"
                  role="button"
                  aria-label="Delete conversation"
                >
                  <Trash2 size={16} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-80 bg-gray-900 text-white flex flex-col h-screen">
      {/* Header with CA Logo */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center font-bold text-white text-lg">
            CA
          </div>
          <span className="font-bold text-lg">AI Assistant</span>
        </div>
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 py-3 rounded-lg transition font-medium"
        >
          <Plus size={20} />
          New Chat
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="mx-auto mb-2" size={32} />
            <p className="text-sm">No conversations yet</p>
          </div>
        ) : (
          <>
            <HistoryGroup title="Today" items={groupedHistory.today} />
            <HistoryGroup title="Yesterday" items={groupedHistory.yesterday} />
            <HistoryGroup
              title="Previous 7 Days"
              items={groupedHistory.previous7Days}
            />
            <HistoryGroup title="Older" items={groupedHistory.older} />
          </>
        )}
      </div>

      {/* User Section - Bottom */}
      <div className="p-4 border-t border-gray-800 bg-gray-900">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center font-semibold text-white">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-medium">{user?.username}</p>
              <p className="text-xs text-gray-400">Online</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-red-400 transition p-2 hover:bg-gray-800 rounded-lg"
            title="Logout"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;