'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import Keycloak from 'keycloak-js';

interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  roles: string[];
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  token: string | null;
  keycloak: Keycloak | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [keycloak, setKeycloak] = useState<Keycloak | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const initKeycloak = async () => {
      try {
        const keycloakConfig = {
          url: process.env.NEXT_PUBLIC_KEYCLOAK_URL || 'http://localhost:8080',
          realm: 'enterprise-reporting',
          clientId: 'reporting-app',
        };

        const kc = new Keycloak(keycloakConfig);
        
        const authenticated = await kc.init({
          onLoad: 'check-sso',
          silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
          checkLoginIframe: false,
        });

        setKeycloak(kc);
        setIsAuthenticated(authenticated);

        if (authenticated && kc.token) {
          setToken(kc.token);
          
          // Load user profile
          const profile = await kc.loadUserProfile();
          const tokenParsed = kc.tokenParsed;
          
          setUser({
            id: tokenParsed?.sub || '',
            username: tokenParsed?.preferred_username || '',
            email: profile.email || '',
            firstName: profile.firstName,
            lastName: profile.lastName,
            roles: tokenParsed?.realm_access?.roles || [],
          });

          // Setup token refresh
          kc.onTokenExpired = () => {
            kc.updateToken(30).then((refreshed) => {
              if (refreshed) {
                setToken(kc.token);
                console.log('Token refreshed');
              } else {
                console.log('Token still valid');
              }
            }).catch(() => {
              console.log('Failed to refresh token');
              logout();
            });
          };
        }
      } catch (error) {
        console.error('Failed to initialize Keycloak:', error);
      } finally {
        setLoading(false);
      }
    };

    initKeycloak();
  }, []);

  const login = () => {
    if (keycloak) {
      keycloak.login();
    }
  };

  const logout = () => {
    if (keycloak) {
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
      keycloak.logout();
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    token,
    keycloak,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}