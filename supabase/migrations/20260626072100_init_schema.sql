create extension if not exists pgcrypto;

do $$
begin
  if exists (
    select 1
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = 'rls_auto_enable'
      and pg_get_function_arguments(p.oid) = ''
  ) then
    revoke execute on function public.rls_auto_enable() from anon, authenticated;
  end if;
end $$;

do $$
begin
  if not exists (select 1 from pg_type where typname = 'document_role') then
    create type public.document_role as enum ('owner', 'editor', 'viewer');
  end if;
end $$;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete restrict,
  title text not null check (length(trim(title)) > 0 and length(title) <= 200),
  storage_bucket text not null default 'document-snapshots',
  storage_path text not null,
  snapshot_version bigint not null default 0 check (snapshot_version >= 0),
  head_revision bigint not null default 0 check (head_revision >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz,
  constraint documents_storage_path_unique unique (storage_bucket, storage_path)
);

create table public.document_members (
  document_id uuid not null references public.documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role public.document_role not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (document_id, user_id)
);

create table public.document_ops (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  actor_id uuid not null references auth.users(id) on delete restrict,
  op_id text not null,
  client_id text not null,
  client_clock bigint not null check (client_clock >= 0),
  revision bigint not null check (revision >= 0),
  op_type text not null check (op_type in ('insert', 'delete', 'replace', 'snapshot')),
  payload jsonb not null,
  created_at timestamptz not null default now(),
  compacted_at timestamptz,
  constraint document_ops_document_op_unique unique (document_id, op_id),
  constraint document_ops_payload_object check (jsonb_typeof(payload) = 'object')
);

create index documents_owner_id_idx on public.documents(owner_id);
create index documents_deleted_at_idx on public.documents(deleted_at);
create index document_members_user_id_idx on public.document_members(user_id);
create index document_members_role_idx on public.document_members(role);
create index document_ops_document_revision_idx on public.document_ops(document_id, revision);
create index document_ops_document_created_at_idx on public.document_ops(document_id, created_at);
create index document_ops_uncompacted_idx on public.document_ops(document_id, created_at)
  where compacted_at is null;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

create trigger documents_set_updated_at
before update on public.documents
for each row execute function public.set_updated_at();

create trigger document_members_set_updated_at
before update on public.document_members
for each row execute function public.set_updated_at();

create or replace function public.handle_new_user_profile()
returns trigger
language plpgsql
security definer
set search_path = public, auth
as $$
begin
  insert into public.profiles (id, email, display_name, avatar_url)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name'),
    new.raw_user_meta_data ->> 'avatar_url'
  )
  on conflict (id) do update
    set email = excluded.email,
        display_name = excluded.display_name,
        avatar_url = excluded.avatar_url,
        updated_at = now();

  return new;
end;
$$;

drop trigger if exists on_auth_user_created_create_profile on auth.users;

create trigger on_auth_user_created_create_profile
after insert on auth.users
for each row execute function public.handle_new_user_profile();

revoke execute on function public.set_updated_at() from public, anon, authenticated;
revoke execute on function public.handle_new_user_profile() from public, anon, authenticated;

alter table public.profiles enable row level security;
alter table public.documents enable row level security;
alter table public.document_members enable row level security;
alter table public.document_ops enable row level security;

insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'document-snapshots',
  'document-snapshots',
  false,
  10485760,
  array['text/plain', 'application/json']
)
on conflict (id) do update
set public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;
