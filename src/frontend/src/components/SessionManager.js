import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const SessionContainer = styled.div`
  width: 250px;
  background-color: var(--background-dark);
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const SessionTitle = styled.h2`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-color);
`;

const SessionList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
`;

const SessionItem = styled.li`
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  background-color: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-color)'};
  box-shadow: var(--box-shadow);
  transition: var(--transition);
  
  &:hover {
    background-color: ${props => props.active ? 'var(--primary-hover)' : 'var(--secondary-color)'};
  }
`;

const NewSessionButton = styled.button`
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
  
  &:hover {
    background-color: var(--primary-color);
    color: white;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingIndicator = styled.div`
  text-align: center;
  padding: 1rem;
  color: var(--text-light);
`;

function SessionManager({ sessions, activeSession, onSessionChange, onNewSession, isLoading }) {
  const [sessionNames, setSessionNames] = useState({});

  useEffect(() => {
    // Generate readable names for sessions
    const fetchSessionNames = async () => {
      const names = {};
      
      // Process each session to get its name
      for (let i = 0; i < sessions.length; i++) {
        const sessionId = sessions[i];
        
        try {
          // Try to get the conversation name from the API
          const response = await fetch(`http://localhost:8001/api/session/${sessionId}`);
          const data = await response.json();
          
          if (data.conversation_name) {
            names[sessionId] = data.conversation_name;
          } else {
            // Fallback if no name is available
            names[sessionId] = `Conversation ${i + 1}`;
          }
        } catch (error) {
          console.error(`Error fetching session info for ${sessionId}:`, error);
          names[sessionId] = `Conversation ${i + 1}`;
        }
      }
      
      setSessionNames(names);
    };
    
    fetchSessionNames();
  }, [sessions]);

  if (isLoading) {
    return (
      <SessionContainer>
        <LoadingIndicator>Loading sessions...</LoadingIndicator>
      </SessionContainer>
    );
  }

  return (
    <SessionContainer>
      <SessionTitle>Conversations</SessionTitle>
      <SessionList>
        {sessions.map((sessionId) => (
          <SessionItem
            key={sessionId}
            active={sessionId === activeSession}
            onClick={() => onSessionChange(sessionId)}
          >
            {sessionNames[sessionId] || sessionId.substring(0, 8)}
          </SessionItem>
        ))}
      </SessionList>
      <NewSessionButton onClick={onNewSession} disabled={isLoading}>
        New Conversation
      </NewSessionButton>
    </SessionContainer>
  );
}

export default SessionManager;