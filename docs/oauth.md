# OAuth Setup

The browser uses Supabase Auth for Google OAuth. The application backend remains the
authorization boundary for documents.

## Supabase Project

Project URL:

```txt
https://drxmrriapsxnpxukamvi.supabase.co
```

Google OAuth callback URL to register in Google Cloud:

```txt
https://drxmrriapsxnpxukamvi.supabase.co/auth/v1/callback
```

Supabase Auth URL configuration for local development:

```txt
Site URL: http://localhost:5173
Redirect URL allow list: http://localhost:5173/**
```

## Google Cloud

Create a Web OAuth client and add:

```txt
Authorized JavaScript origins:
http://localhost:5173

Authorized redirect URIs:
https://drxmrriapsxnpxukamvi.supabase.co/auth/v1/callback
```

Then add the Google Client ID and Client Secret to:

```txt
Supabase Dashboard -> Authentication -> Providers -> Google
```

## RLS

No permissive RLS policies are needed yet. React only uses Supabase Auth. Document
metadata and snapshot access will go through FastAPI, so the app tables should remain
default-deny from browser clients for now.
