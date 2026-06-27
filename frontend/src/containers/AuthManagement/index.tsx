import { Typography } from "@mui/material";

import { AuthPanel } from "./components";
import { useAuthManagement } from "./hooks";

export function AuthManagement() {
  const {
    email,
    error,
    loading,
    refreshSession,
    signInWithGoogle,
    signOut,
  } = useAuthManagement();

  return (
    <main className="min-h-screen bg-[var(--color-page-background)] px-6 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl items-center justify-center">
        <section className="grid w-full gap-10 lg:grid-cols-[minmax(0,1fr)_440px] lg:items-center">
          <div className="max-w-xl space-y-5">
            <Typography variant="overline" color="primary">
              Collaborative editor
            </Typography>
            <Typography variant="h3" component="h1">
              Write together without losing intent.
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Sign in to enter your document workspace. Create, organize, and
              share documents as the editor takes shape.
            </Typography>
          </div>

          <AuthPanel
            email={email}
            error={error}
            loading={loading}
            onRefresh={refreshSession}
            onSignInWithGoogle={signInWithGoogle}
            onSignOut={signOut}
          />
        </section>
      </div>
    </main>
  );
}

export default AuthManagement;
