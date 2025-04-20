import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background-color: white;
  border-bottom: 1px solid var(--border-color);
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
`;

const NavLinks = styled.nav`
  display: flex;
  gap: 1.5rem;
  
  a {
    color: var(--text-light);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
    
    &:hover {
      color: var(--primary-color);
    }
  }
`;

function Header() {
  return (
    <HeaderContainer>
      <Logo>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 3L5 7M5 7L9 11M5 7H15M15 13L19 17M19 17L15 21M19 17H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        LangChain Assistant
      </Logo>
      <NavLinks>
        <a href="/">Chat</a>
        <a href="https://github.com/langchain-ai/langchain" target="_blank" rel="noopener noreferrer">Docs</a>
      </NavLinks>
    </HeaderContainer>
  );
}

export default Header;
