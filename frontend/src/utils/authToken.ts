import { supabase } from "../lib/supabase";

export const getAccessToken = async (): Promise<string> => {
  const { data, error } = await supabase.auth.getSession();

  if (error) {
    throw new Error(error.message);
  }

  if (!data.session) {
    throw new Error("Missing Supabase session");
  }

  return data.session.access_token;
};
