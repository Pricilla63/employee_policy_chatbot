import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/authcontext';
import { queryAPI, conversationsAPI } from '../../services/api';
import { Send, Loader2, Sparkles, Copy, Check } from 'lucide-react';


const ChatArea = ({ selectedHistory, onNewMessage, onMessagesUpdate, currentMessages, currentConversationId, onConversationIdChange }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const messagesEndRef = useRef(null);

  // Load conversation messages when selectedHistory changes
  useEffect(() => {
    const loadConversation = async () => {
      if (selectedHistory) {
        console.log('Selected History:', selectedHistory);
        
        // If we have a conversation ID but no messages, fetch the full conversation
        if (selectedHistory._id && (!selectedHistory.messages || selectedHistory.messages.length === 0)) {
          try {
            const response = await conversationsAPI.getConversation(selectedHistory._id);
            console.log('Fetched conversation:', response.data);
            
            if (response.data.messages && Array.isArray(response.data.messages)) {
              const formattedMessages = [];
              response.data.messages.forEach(msg => {
                formattedMessages.push({
                  type: 'user',
                  content: msg.question,
                  timestamp: msg.timestamp,
                });
                formattedMessages.push({
                  type: 'assistant',
                  content: msg.answer,
                  sources: msg.sources || [],
                  responseTime: msg.response_time,
                  documentsQueried: msg.document_names || [],
                  timestamp: msg.timestamp,
                });
              });
              setMessages(formattedMessages);
            }
            
            if (onConversationIdChange) {
              onConversationIdChange(selectedHistory._id);
            }
            return;
          } catch (error) {
            console.error('Error loading conversation:', error);
          }
        }
        
        // Check if selectedHistory has messages array
        if (selectedHistory.messages && Array.isArray(selectedHistory.messages) && selectedHistory.messages.length > 0) {
          console.log('Messages found:', selectedHistory.messages);
          // Transform backend message format to ChatArea format
          const formattedMessages = [];
          selectedHistory.messages.forEach(msg => {
            // Add user message
            formattedMessages.push({
              type: 'user',
              content: msg.question,
              timestamp: msg.timestamp,
            });
            
            // Add assistant message
            formattedMessages.push({
              type: 'assistant',
              content: msg.answer,
              sources: msg.sources || [],
              responseTime: msg.response_time,
              documentsQueried: msg.document_names || [],
              timestamp: msg.timestamp,
            });
          });
          
          console.log('Formatted messages:', formattedMessages);
          setMessages(formattedMessages);
          
          // Update conversation ID
          if (onConversationIdChange && selectedHistory._id) {
            onConversationIdChange(selectedHistory._id);
          }
        } else if (selectedHistory.question && selectedHistory.answer) {
          // Fallback for old single Q&A format (backward compatibility)
          console.log('Using fallback format');
          setMessages([
            {
              type: 'user',
              content: selectedHistory.question,
              timestamp: selectedHistory.timestamp,
            },
            {
              type: 'assistant',
              content: selectedHistory.answer,
              sources: selectedHistory.sources || [],
              responseTime: selectedHistory.response_time,
              timestamp: selectedHistory.timestamp,
            },
          ]);
        } else {
          console.warn('No valid message format found in selectedHistory');
          setMessages([]);
        }
      } else {
        // New chat - start with empty messages or currentMessages
        setMessages(currentMessages || []);
      }
    };
    
    loadConversation();
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

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    
    // Update parent component with new messages
    if (onMessagesUpdate) {
      onMessagesUpdate(updatedMessages);
    }
    
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
      
      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);
      
      // Update parent component with final messages
      if (onMessagesUpdate) {
        onMessagesUpdate(finalMessages);
      }
      
      // Update conversation ID if returned
      if (response.data.conversation_id && onConversationIdChange) {
        onConversationIdChange(response.data.conversation_id);
      }
      
      onNewMessage?.(); // This will refresh the sidebar history
    } catch (error) {
      const errorMessage = {
        type: 'assistant',
        content:
          error.response?.data?.detail ||
          'Sorry, I encountered an error. Please make sure you have documents uploaded.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      // Update parent component with error messages
      if (onMessagesUpdate) {
        onMessagesUpdate(finalMessages);
      }
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
              placeholder="Ask Me..."
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