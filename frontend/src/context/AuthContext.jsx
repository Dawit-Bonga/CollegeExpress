import React, { createContext, useState, useContext, useEffect } from 'react';
import { supabase } from '../supabase';

const AuthContext = createContext(null);
const DEV_MODE = import.meta.env.VITE_DEV_MODE === 'true';
const DEV_USER = {
  id: 'dev-user-123',
  email: 'dev@test.com',
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (DEV_MODE) {
      setUser(DEV_USER);
      setLoading(false);
      return undefined;
    }

    // Check active sessions
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const register = async (email, password, fullName, grade) => {
    if (DEV_MODE) {
      setUser(DEV_USER);
      return { user: DEV_USER };
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: fullName, grade: grade }
      }
    });
    if (error) throw error;
    return data;
  };

  const login = async (email, password) => {
    if (DEV_MODE) {
      setUser(DEV_USER);
      return { user: DEV_USER };
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    if (error) throw error;
    return data;
  };

  const loginWithGoogle = async () => {
    if (DEV_MODE) {
      setUser(DEV_USER);
      return { user: DEV_USER };
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin
      }
    });
    if (error) throw error;
    return data;
  };

  const logout = async () => {
    if (DEV_MODE) {
      setUser(DEV_USER);
      return;
    }

    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };

  const getToken = async () => {
    if (DEV_MODE) {
      return 'dev-token-bypass';
    }
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token;
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      register, 
      login, 
      loginWithGoogle, 
      logout,
      getToken,
      isDevMode: DEV_MODE,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
