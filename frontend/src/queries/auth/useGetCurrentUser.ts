import { useQuery } from "@tanstack/react-query";
import type { Session } from "@supabase/supabase-js";

import { getCurrentUser } from "./api";

export const authQueryKeys = {
  all: ["auth"] as const,
  currentUser: (accessToken: string | null) =>
    [...authQueryKeys.all, "currentUser", accessToken] as const,
};

export const useGetCurrentUser = (session: Session | null) =>
  useQuery({
    queryKey: authQueryKeys.currentUser(session?.access_token ?? null),
    queryFn: () => {
      if (!session) {
        throw new Error("Missing Supabase session");
      }

      return getCurrentUser(session);
    },
    enabled: Boolean(session),
  });
