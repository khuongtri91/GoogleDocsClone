# Supabase Workflow

Production stays on the Supabase `main` environment.

Development flow:

1. Keep source migrations in git feature branches, such as `feat/init_schema`.
2. Test migrations against a non-production Supabase target.
3. Merge feature branches into git `develop` after review.
4. Deploy the `develop` branch to a staging/development Supabase target.
5. After full testing, merge git `develop` into git `main`.
6. Deploy git `main` migrations to the production Supabase target.
7. Tag every production merge so the database state has a clear rollback marker.

Supabase dashboard branching is useful for previews, but those branches currently merge
back to `main`; branch-to-branch merges such as `feat/init_schema` to `develop` are not
supported there. For a strict `feat -> develop -> main` flow, use git branches plus a
separate Supabase staging project or GitHub-based deployment automation.

This project keeps document snapshot objects in the private `document-snapshots` bucket.
The browser should use Supabase only for Auth. Application document reads and writes go
through the FastAPI backend.
