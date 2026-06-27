import type { Session } from "@supabase/supabase-js";

import { httpService } from "../../utils";
import type { CurrentUser } from "./types";

export const getCurrentUser = (session: Session): Promise<CurrentUser> =>
  httpService.get<CurrentUser>("/auth/me", {
    accessToken: session.access_token,
  });
