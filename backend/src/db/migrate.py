"""
Run database migrations on startup.
Uses IF NOT EXISTS so it's safe to run multiple times.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "")

def _get_connection_string() -> str:
    ref = _SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    from urllib.parse import quote_plus
    password = quote_plus(_SUPABASE_PASSWORD)
    return f"postgresql://postgres.{ref}:{password}@aws-1-us-east-1.pooler.supabase.com:5432/postgres"


def run_migrations():
    """Create required tables if they don't exist."""
    conn_str = _get_connection_string()

    try:
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        cur = conn.cursor()

        # --- Profiles table ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.profiles (
                id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                username text UNIQUE NOT NULL,
                email text NOT NULL UNIQUE,
                created_at timestamptz DEFAULT now()
            );
        """)

        cur.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;")

        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Public read'
                ) THEN
                    CREATE POLICY "Public read" ON public.profiles FOR SELECT USING (true);
                END IF;

                -- Drop old restrictive insert policy if it exists
                IF EXISTS (
                    SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Users insert own'
                ) THEN
                    DROP POLICY "Users insert own" ON public.profiles;
                END IF;

                IF NOT EXISTS (
                    SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Users update own'
                ) THEN
                    CREATE POLICY "Users update own" ON public.profiles FOR UPDATE USING (auth.uid() = id);
                END IF;
            END
            $$;
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS profiles_username_idx ON public.profiles (username);
        """)

        # --- Trigger: auto-create profile on user signup ---
        cur.execute("""
            CREATE OR REPLACE FUNCTION public.handle_new_user()
            RETURNS trigger
            LANGUAGE plpgsql
            SECURITY DEFINER
            SET search_path = public
            AS $$
            BEGIN
                INSERT INTO public.profiles (id, username, email)
                VALUES (
                    NEW.id,
                    COALESCE(NEW.raw_user_meta_data ->> 'username', SPLIT_PART(NEW.email, '@', 1)),
                    NEW.email
                )
                ON CONFLICT (id) DO NOTHING;
                RETURN NEW;
            END;
            $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger WHERE tgname = 'on_auth_user_created'
                ) THEN
                    CREATE TRIGGER on_auth_user_created
                        AFTER INSERT ON auth.users
                        FOR EACH ROW
                        EXECUTE FUNCTION public.handle_new_user();
                END IF;
            END
            $$;
        """)

        cur.close()
        conn.close()
        print("[migrate] Profiles table and trigger ready.")

    except Exception as e:
        print(f"[migrate] Warning: could not run migrations: {e}")
