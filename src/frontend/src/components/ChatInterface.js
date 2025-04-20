import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--border-color);
  background-color: white;
`;

const Title = styled.h2`
  font-size: 1rem;
  margin: 0;
  color: var(--text-color);
`;

const ClearButton = styled.button`
  background-color: var(--error-color);
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: var(--transition);
  
  &:hover {
    opacity: 0.9;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  
  ${props => props.isUser ? `
    align-self: flex-end;
    background-color: var(--primary-color);
    color: white;
  ` : `
    align-self: flex-start;
    background-color: white;
    border: 1px solid var(--border-color);
  `}
  
  p {
    margin: 0;
  }
  
  a {
    color: ${props => props.isUser ? 'white' : 'var(--primary-color)'};
    text-decoration: underline;
  }
  
  pre {
    background-color: ${props => props.isUser ? 'rgba(0, 0, 0, 0.2)' : 'var(--background-dark)'};
    padding: 0.5rem;
    border-radius: 0.25rem;
    overflow-x: auto;
  }
  
  code {
    font-family: monospace;
  }
  
  ul, ol {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    padding-left: 1.5rem;
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: white;
`;

const MessageInput = styled.textarea`
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  height: 60px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
  }
`;

const SendButton = styled.button`
  margin-left: 0.75rem;
  padding: 0 1.25rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  
  &:hover {
    background-color: var(--primary-hover);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-light);
`;

const ThinkingIndicator = styled.div`
  align-self: flex-start;
  color: var(--text-light);
  font-style: italic;
  padding: 0.5rem 1rem;
`;

function ChatInterface({ sessionId, isLoading }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const messagesEndRef = useRef(null);
  
  useEffect(() => {
    if (sessionId) {
      fetchMessages();
    }
  }, [sessionId]);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const fetchMessages = async () => {
    if (!sessionId) return;
    
    try {
      const response = await axios.get(`http://localhost:8001/api/conversation/${sessionId}`);
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
      setMessages([]);
    }
  };
  
  const handleSendMessage = async () => {
    if (!input.trim() || !sessionId) return;
    
    const userMessage = input;
    setInput('');
    
    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsThinking(true);
    
    try {
      const response = await axios.post('http://localhost:8001/api/message', {
        message: userMessage,
        session_id: sessionId
      });
      
      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your request. Please try again.' 
      }]);
    } finally {
      setIsThinking(false);
    }
  };
  
  const handleClearConversation = async () => {
    if (!sessionId) return;
    
    setIsClearing(true);
    
    try {
      // Call the API to clear the conversation
      const response = await axios.delete(`http://localhost:8001/api/conversation/${sessionId}`);
      
      if (response.data && response.data.success) {
        // Clear messages in the UI
        setMessages([]);
        console.log('Conversation cleared successfully');
      } else {
        console.error('Failed to clear conversation');
      }
    } catch (error) {
      console.error('Error clearing conversation:', error);
    } finally {
      setIsClearing(false);
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  if (isLoading || !sessionId) {
    return (
      <ChatContainer>
        <LoadingIndicator>Loading conversation...</LoadingIndicator>
      </ChatContainer>
    );
  }
  
  return (
    <ChatContainer>
      <Header>
        <Title>Conversation</Title>
        <ClearButton 
          onClick={handleClearConversation} 
          disabled={isClearing || messages.length === 0}
        >
          {isClearing ? 'Clearing...' : 'Clear Conversation'}
        </ClearButton>
      </Header>
      
      <MessagesContainer>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-light)', margin: 'auto' }}>
            <p>Start a new conversation with the assistant.</p>
            <p>You can ask questions, request information, or have a chat!</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <MessageBubble 
            key={index} 
            isUser={message.role === 'user'}
          >
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          </MessageBubble>
        ))}
        
        {isThinking && (
          <ThinkingIndicator>Assistant is thinking...</ThinkingIndicator>
        )}
        
        <div ref={messagesEndRef} />
      </MessagesContainer>
      
      <InputContainer>
        <MessageInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here..."
          disabled={isThinking || isClearing}
        />
        <SendButton 
          onClick={handleSendMessage}
          disabled={!input.trim() || isThinking || isClearing}
        >
          Send
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
}

export default ChatInterface;