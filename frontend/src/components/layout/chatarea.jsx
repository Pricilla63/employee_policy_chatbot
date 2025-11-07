// import React, { useState, useRef, useEffect } from 'react';
// import { useAuth } from '../../context/authcontext';
// import { queryAPI } from '../../services/api';
// import { Send, Loader2, Sparkles, Copy, Check } from 'lucide-react';

// const ChatArea = ({ selectedHistory, onNewMessage }) => {
//   const { user } = useAuth();
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [copiedIndex, setCopiedIndex] = useState(null);
//   const messagesEndRef = useRef(null);

//   useEffect(() => {
//     if (selectedHistory) {
//       setMessages([
//         {
//           type: 'user',
//           content: selectedHistory.question,
//           timestamp: selectedHistory.timestamp,
//         },
//         {
//           type: 'assistant',
//           content: selectedHistory.answer,
//           sources: selectedHistory.sources,
//           timestamp: selectedHistory.timestamp,
//           responseTime: selectedHistory.response_time,
//         },
//       ]);
//     } else {
//       setMessages([]);
//     }
//   }, [selectedHistory]);

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   const copyToClipboard = (text, index) => {
//     navigator.clipboard.writeText(text);
//     setCopiedIndex(index);
//     setTimeout(() => setCopiedIndex(null), 2000);
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!input.trim() || loading) return;

//     const userMessage = {
//       type: 'user',
//       content: input,
//       timestamp: new Date().toISOString(),
//     };

//     setMessages((prev) => [...prev, userMessage]);
//     setInput('');
//     setLoading(true);

//     try {
//       const response = await queryAPI.ask(input);
//       const assistantMessage = {
//         type: 'assistant',
//         content: response.data.answer,
//         sources: response.data.sources,
//         responseTime: response.data.response_time,
//         documentsQueried: response.data.documents_queried,
//         timestamp: new Date().toISOString(),
//       };
//       setMessages((prev) => [...prev, assistantMessage]);
//       onNewMessage?.();
//     } catch (error) {
//       const errorMessage = {
//         type: 'assistant',
//         content:
//           error.response?.data?.detail ||
//           'Sorry, I encountered an error. Please make sure you have documents uploaded.',
//         timestamp: new Date().toISOString(),
//         isError: true,
//       };
//       setMessages((prev) => [...prev, errorMessage]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const suggestedPrompts = [
//     {
//       icon: '📄',
//       title: 'Summarize',
//       description: 'Get a quick summary of the documents',
//       prompt: 'Can you provide a summary of the key points in the documents?',
//     },
//     {
//       icon: '🔍',
//       title: 'Search',
//       description: 'Find specific information',
//       prompt: 'What are the main topics covered in the documents?',
//     },
//     {
//       icon: '💡',
//       title: 'Explain',
//       description: 'Get detailed explanations',
//       prompt: 'Can you explain the key concepts mentioned?',
//     },
//     {
//       icon: '📊',
//       title: 'Analyze',
//       description: 'Deep dive into the content',
//       prompt: 'What insights can you provide from the documents?',
//     },
//   ];

//   const handlePromptClick = (prompt) => {
//     setInput(prompt);
//   };

//   return (
//     <div className="flex-1 flex flex-col h-screen bg-white">
//       {/* Messages Area */}
//       <div className="flex-1 overflow-y-auto">
//         {messages.length === 0 ? (
//           <div className="h-full flex items-center justify-center">
//             <div className="text-center max-w-3xl px-4">
//               {/* Welcome Header */}
//               <div className="mb-8">
//                 <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
//                   <Sparkles className="w-10 h-10 text-white" />
//                 </div>
//                 <h1 className="text-4xl font-bold text-gray-800 mb-3">
//                   Hi {user?.username}!
//                 </h1>
//                 <p className="text-xl text-gray-600">How can I help you today?</p>
//               </div>

//               {/* Suggested Prompts */}
//               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
//                 {suggestedPrompts.map((prompt, index) => (
//                   <button
//                     key={index}
//                     onClick={() => handlePromptClick(prompt.prompt)}
//                     className="p-5 border-2 border-gray-200 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all text-left group"
//                   >
//                     <div className="text-3xl mb-2">{prompt.icon}</div>
//                     <h3 className="font-semibold text-gray-800 mb-1 group-hover:text-blue-600">
//                       {prompt.title}
//                     </h3>
//                     <p className="text-sm text-gray-600">
//                       {prompt.description}
//                     </p>
//                   </button>
//                 ))}
//               </div>
//             </div>
//           </div>
//         ) : (
//           <div className="max-w-4xl mx-auto px-4 py-8">
//             {messages.map((message, index) => (
//               <div
//                 key={index}
//                 className={`mb-8 animate-fadeIn ${
//                   message.type === 'user' ? 'flex justify-end' : ''
//                 }`}
//               >
//                 <div
//                   className={`flex gap-4 max-w-3xl ${
//                     message.type === 'user' ? 'flex-row-reverse' : ''
//                   }`}
//                 >
//                   {/* Avatar */}
//                   <div className="flex-shrink-0">
//                     <div
//                       className={`w-10 h-10 rounded-full flex items-center justify-center ${
//                         message.type === 'user'
//                           ? 'bg-gradient-to-br from-blue-500 to-blue-600'
//                           : message.isError
//                           ? 'bg-gradient-to-br from-red-500 to-pink-600'
//                           : 'bg-gradient-to-br from-purple-500 to-pink-600'
//                       }`}
//                     >
//                       {message.type === 'user' ? (
//                         <span className="text-white font-semibold text-sm">
//                           {user?.username?.charAt(0).toUpperCase()}
//                         </span>
//                       ) : (
//                         <Sparkles className="text-white" size={20} />
//                       )}
//                     </div>
//                   </div>

//                   {/* Message Content */}
//                   <div className="flex-1 min-w-0">
//                     <div className="flex items-center gap-2 mb-2">
//                       <span className="font-semibold text-sm text-gray-900">
//                         {message.type === 'user'
//                           ? user?.username
//                           : 'DocuChat AI'}
//                       </span>
//                     </div>

//                     <div
//                       className={`prose max-w-none ${
//                         message.type === 'user'
//                           ? 'bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm'
//                           : message.isError
//                           ? 'bg-red-50 text-red-800 px-4 py-3 rounded-2xl'
//                           : 'text-gray-800'
//                       }`}
//                     >
//                       <p className="whitespace-pre-wrap leading-relaxed">
//                         {message.content}
//                       </p>
//                     </div>

//                     {/* Copy Button for Assistant Messages */}
//                     {message.type === 'assistant' && !message.isError && (
//                       <div className="flex items-center gap-2 mt-2">
//                         <button
//                           onClick={() => copyToClipboard(message.content, index)}
//                           className="text-gray-500 hover:text-gray-700 text-xs flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition"
//                         >
//                           {copiedIndex === index ? (
//                             <>
//                               <Check size={14} />
//                               Copied!
//                             </>
//                           ) : (
//                             <>
//                               <Copy size={14} />
//                               Copy
//                             </>
//                           )}
//                         </button>
//                         {message.responseTime && (
//                           <span className="text-xs text-gray-400">
//                             ⚡ {message.responseTime.toFixed(2)}s
//                           </span>
//                         )}
//                       </div>
//                     )}

//                     {/* Sources */}
//                     {message.sources && message.sources.length > 0 && (
//                       <div className="mt-4 space-y-2">
//                         <p className="text-sm font-semibold text-gray-700 flex items-center gap-1">
//                           📚 Sources used:
//                         </p>
//                         <div className="space-y-2">
//                           {message.sources.slice(0, 3).map((source, idx) => (
//                             <div
//                               key={idx}
//                               className="text-sm bg-gray-50 p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition"
//                             >
//                               <p className="text-gray-700 text-xs leading-relaxed line-clamp-3">
//                                 {source}
//                               </p>
//                             </div>
//                           ))}
//                         </div>
//                       </div>
//                     )}

//                     {/* Documents Queried */}
//                     {message.documentsQueried &&
//                       message.documentsQueried.length > 0 && (
//                         <div className="mt-2">
//                           <p className="text-xs text-gray-500">
//                             📄 Searched in:{' '}
//                             {message.documentsQueried.join(', ')}
//                           </p>
//                         </div>
//                       )}
//                   </div>
//                 </div>
//               </div>
//             ))}

//             {/* Loading State */}
//             {loading && (
//               <div className="flex gap-4 mb-8">
//                 <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center flex-shrink-0">
//                   <Sparkles className="text-white" size={20} />
//                 </div>
//                 <div className="flex items-center gap-2 text-gray-500">
//                   <Loader2 className="animate-spin" size={20} />
//                   <span className="text-sm">Searching through documents...</span>
//                 </div>
//               </div>
//             )}

//             <div ref={messagesEndRef} />
//           </div>
//         )}
//       </div>

//       {/* Input Area */}
//       <div className="border-t border-gray-200 bg-white">
//         <div className="max-w-4xl mx-auto p-4">
//           <form onSubmit={handleSubmit} className="flex gap-3">
//             <input
//               type="text"
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               placeholder="Message DocuChat AI..."
//               className="flex-1 px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-800 placeholder-gray-400 shadow-sm"
//               disabled={loading}
//             />
//             <button
//               type="submit"
//               disabled={loading || !input.trim()}
//               className="px-6 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md"
//             >
//               <Send size={20} />
//             </button>
//           </form>
//           <p className="text-xs text-center text-gray-500 mt-3">
//             DocuChat AI can make mistakes. Verify important information.
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatArea;



import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/authcontext';
import { queryAPI } from '../../services/api';
import { Send, Loader2, Sparkles, Copy, Check } from 'lucide-react';

const ChatArea = ({ selectedHistory, onNewMessage }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (selectedHistory) {
      setMessages([
        {
          type: 'user',
          content: selectedHistory.question,
          timestamp: selectedHistory.timestamp,
        },
        {
          type: 'assistant',
          content: selectedHistory.answer,
          sources: selectedHistory.sources,
          timestamp: selectedHistory.timestamp,
          responseTime: selectedHistory.response_time,
        },
      ]);
    } else {
      setMessages([]);
    }
  }, [selectedHistory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryAPI.ask(input);
      const assistantMessage = {
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        responseTime: response.data.response_time,
        documentsQueried: response.data.documents_queried,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      onNewMessage?.();
    } catch (error) {
      const errorMessage = {
        type: 'assistant',
        content:
          error.response?.data?.detail ||
          'Sorry, I encountered an error. Please make sure you have documents uploaded.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* Header with loanDNA */}
      <div className="border-b border-gray-200 bg-white py-4 px-6">
        <h1 className="text-xl font-bold text-gray-800">loanDNA</h1>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-3xl px-4">
              {/* Simplified Welcome Message */}
              <div className="mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-4xl font-bold text-gray-800 mb-3">
                  Hi {user?.username}!
                </h1>
                <p className="text-xl text-gray-600">How can I help you today?</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-8">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-8 animate-fadeIn ${
                  message.type === 'user' ? 'flex justify-end' : ''
                }`}
              >
                <div
                  className={`flex gap-4 max-w-3xl ${
                    message.type === 'user' ? 'flex-row-reverse' : ''
                  }`}
                >
                  {/* Avatar */}
                  <div className="flex-shrink-0">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        message.type === 'user'
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600'
                          : message.isError
                          ? 'bg-gradient-to-br from-red-500 to-pink-600'
                          : 'bg-gradient-to-br from-purple-500 to-pink-600'
                      }`}
                    >
                      {message.type === 'user' ? (
                        <span className="text-white font-semibold text-sm">
                          {user?.username?.charAt(0).toUpperCase()}
                        </span>
                      ) : (
                        <Sparkles className="text-white" size={20} />
                      )}
                    </div>
                  </div>

                  {/* Message Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-sm text-gray-900">
                        {/* {message.type === ''
                          ? user?.username
                          : ''} */}
                      </span>
                    </div>

                    <div
                      className={`prose max-w-none ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm'
                          : message.isError
                          ? 'bg-red-50 text-red-800 px-4 py-3 rounded-2xl'
                          : 'text-gray-800'
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                    </div>

                    {/* Copy Button for Assistant Messages */}
                    {message.type === 'assistant' && !message.isError && (
                      <div className="flex items-center gap-2 mt-2">
                        <button
                          onClick={() => copyToClipboard(message.content, index)}
                          className="text-gray-500 hover:text-gray-700 text-xs flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition"
                        >
                          {copiedIndex === index ? (
                            <>
                              <Check size={14} />
                              Copied!
                            </>
                          ) : (
                            <>
                              <Copy size={14} />
                              Copy
                            </>
                          )}
                        </button>
                        {/* {message.responseTime && (
                          <span className="text-xs text-gray-400">
                            ⚡ {message.responseTime.toFixed(2)}s
                          </span>
                        )} */}
                      </div>
                    )}

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <p className="text-sm font-semibold text-gray-700 flex items-center gap-1">
                          📚 Sources used:
                        </p>
                        <div className="space-y-2">
                          {message.sources.slice(0, 3).map((source, idx) => (
                            <div
                              key={idx}
                              className="text-sm bg-gray-50 p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition"
                            >
                              <p className="text-gray-700 text-xs leading-relaxed line-clamp-3">
                                {source}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Documents Queried
                    {message.documentsQueried &&
                      message.documentsQueried.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500">
                            📄 Searched in:{' '}
                            {message.documentsQueried.join(', ')}
                          </p>
                        </div>
                      )} */}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading State */}
            {loading && (
              <div className="flex gap-4 mb-8">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="text-white" size={20} />
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="animate-spin" size={20} />
                  <span className="text-sm">Searching through documents...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto p-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message DocuChat AI..."
              className="flex-1 px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-800 placeholder-gray-400 shadow-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md"
            >
              <Send size={20} />
            </button>
          </form>
          <p className="text-xs text-center text-gray-500 mt-3">
            LoanDNA AI can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;