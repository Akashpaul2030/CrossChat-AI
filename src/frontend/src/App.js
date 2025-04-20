import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import ChatInterface from './components/ChatInterface';
import SessionManager from './components/SessionManager';
import Header from './components/Header';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
  background-color: white;
  box-shadow: var(--box-shadow);
`;

const MainContent = styled.main`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

function App() {
  const [activeSession, setActiveSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  // Add a key state to force re-render of ChatInterface
  const [chatKey, setChatKey] = useState(0);

  useEffect(() => {
    // Initialize with a new session if none exists
    const initializeSession = async () => {
      try {
        setIsLoading(true);
        // Fetch available sessions
        const response = await fetch('http://localhost:8001/api/session/list');
        const data = await response.json();
        
        setSessions(data.sessions);
        
        if (data.sessions.length > 0) {
          // Use the most recent session
          setActiveSession(data.sessions[0]);
        } else {
          // Create a new session
          const newSessionResponse = await fetch('http://localhost:8001/api/session/new', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
          });
          const newSessionData = await newSessionResponse.json();
          setActiveSession(newSessionData.session_id);
          setSessions([newSessionData.session_id]);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []);

  const handleSessionChange = (sessionId) => {
    setActiveSession(sessionId);
    // Increment key to force ChatInterface to reload
    setChatKey(prevKey => prevKey + 1);
  };

  const handleNewSession = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8001/api/session/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state with new session
      setActiveSession(data.session_id);
      setSessions(prevSessions => [data.session_id, ...prevSessions]);
      
      // Increment key to force ChatInterface to reload
      setChatKey(prevKey => prevKey + 1);
      
      console.log('New session created:', data.session_id);
    } catch (error) {
      console.error('Error creating new session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Router>
      <AppContainer>
        <Header />
        <MainContent>
          <SessionManager 
            sessions={sessions}
            activeSession={activeSession}
            onSessionChange={handleSessionChange}
            onNewSession={handleNewSession}
            isLoading={isLoading}
          />
          <Routes>
            <Route 
              path="/" 
              element={
                <ChatInterface 
                  key={chatKey} // Add key to force re-render
                  sessionId={activeSession} 
                  isLoading={isLoading}
                />
              } 
            />
          </Routes>
        </MainContent>
      </AppContainer>
    </Router>
  );
}

export default App;