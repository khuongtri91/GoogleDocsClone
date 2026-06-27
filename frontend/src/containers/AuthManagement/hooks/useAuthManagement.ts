import { useQueryClient } from "@tanstack/react-query";
import type { Session } from "@supabase/supabase-js";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { supabase } from "../../../lib/supabase";
import { authQueryKeys, useGetCurrentUser } from "../../../queries/auth";
import { PATHS } from "../../../utils/path";

type AuthSessionState = {
  session: Session | null;
  loading: boolean;
  error: string | null;
};

const getRedirectUrl = () =>
  new URL(PATHS.authCallback, window.location.origin).toString();

export const useAuthManagement = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [authSession, setAuthSession] = useState<AuthSessionState>({
    session: null,
    loading: true,
    error: null,
  });

  const currentUserQuery = useGetCurrentUser(authSession.session);
  const isCallbackRoute = location.pathname === PATHS.authCallback;

  useEffect(() => {
    let mounted = true;

    const loadSession = async () => {
      const { data, error } = await supabase.auth.getSession();

      if (!mounted) {
        return;
      }

      if (error) {
        setAuthSession({
          session: null,
          loading: false,
          error: error.message,
        });
        return;
      }

      setAuthSession({
        session: data.session,
        loading: false,
        error: null,
      });

      if (isCallbackRoute) {
        navigate(PATHS.home, { replace: true });
      }
    };

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthSession({
        session,
        loading: false,
        error: null,
      });

      if (!session) {
        queryClient.removeQueries({ queryKey: authQueryKeys.all });
      }
    });

    void loadSession();

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, [isCallbackRoute, navigate, queryClient]);

  const email = useMemo(
    () => currentUserQuery.data?.email ?? authSession.session?.user.email ?? null,
    [authSession.session?.user.email, currentUserQuery.data?.email],
  );

  const error =
    authSession.error ??
    (currentUserQuery.error instanceof Error
      ? currentUserQuery.error.message
      : null);

  const signInWithGoogle = useCallback(async () => {
    setAuthSession((current) => ({ ...current, error: null }));

    const { error: signInError } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: getRedirectUrl(),
      },
    });

    if (signInError) {
      setAuthSession((current) => ({
        ...current,
        loading: false,
        error: signInError.message,
      }));
    }
  }, []);

  const signOut = useCallback(async () => {
    setAuthSession((current) => ({ ...current, error: null }));

    const { error: signOutError } = await supabase.auth.signOut();

    if (signOutError) {
      setAuthSession((current) => ({
        ...current,
        loading: false,
        error: signOutError.message,
      }));
      return;
    }

    queryClient.removeQueries({ queryKey: authQueryKeys.all });
    setAuthSession({
      session: null,
      loading: false,
      error: null,
    });
  }, [queryClient]);

  const refreshSession = useCallback(async () => {
    setAuthSession((current) => ({ ...current, loading: true, error: null }));

    const { data, error: refreshError } = await supabase.auth.refreshSession();

    if (refreshError) {
      setAuthSession((current) => ({
        ...current,
        loading: false,
        error: refreshError.message,
      }));
      return;
    }

    setAuthSession({
      session: data.session,
      loading: false,
      error: null,
    });
  }, []);

  return {
    email,
    error,
    loading: authSession.loading || currentUserQuery.isFetching,
    refreshSession,
    signInWithGoogle,
    signOut,
  };
};
