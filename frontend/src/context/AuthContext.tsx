import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface User {
  username: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  role: string | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, username: string, role: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    // Check localStorage on mount
    const storedToken = localStorage.getItem("ccms_token");
    const storedUsername = localStorage.getItem("ccms_username");
    const storedRole = localStorage.getItem("ccms_role");

    if (storedToken && storedUsername && storedRole) {
      setToken(storedToken);
      setUser({ username: storedUsername, role: storedRole });
    }
    setIsInitializing(false);
  }, []);

  const login = (newToken: string, username: string, role: string) => {
    localStorage.setItem("ccms_token", newToken);
    localStorage.setItem("ccms_username", username);
    localStorage.setItem("ccms_role", role);
    setToken(newToken);
    setUser({ username, role });
  };

  const logout = () => {
    localStorage.removeItem("ccms_token");
    localStorage.removeItem("ccms_username");
    localStorage.removeItem("ccms_role");
    setToken(null);
    setUser(null);
    
    // Redirect to login after logout
    window.location.href = "/login";
  };

  if (isInitializing) {
    return null; // or a loading spinner
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user?.role || null,
        token,
        isAuthenticated: !!token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
