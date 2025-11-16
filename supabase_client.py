import streamlit as st
from supabase import create_client, Client

from datetime import datetime

def get_supabase_client():
    """Creates and returns a Supabase client."""
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        print(f"Error connecting to Supabase: {e}")
        return None
    
def update_score_reason(supabase,paper_id,prompt_name,score,reason):

    now_ts = datetime.utcnow().isoformat()
    score_column=prompt_name+"_score"
    reason_column=prompt_name+"_reason"

    update_resp = (
        supabase.table("papers")
        .update({score_column: score, 
                 reason_column: reason,
                 "last_modified": datetime.utcnow().isoformat()})
        .eq("id", paper_id)
        .execute()
    )
    return update_resp

def update_score_reason2(supabase,paper_id,prompt_name,i,score,reason):

    now_ts = datetime.utcnow().isoformat()
    score_column=prompt_name+f"_{i}_score"
    reason_column=prompt_name+f"_{i}_reason"

    update_resp = (
        supabase.table("papers2")
        .update({score_column: score, 
                 reason_column: reason,
                 "last_modified": datetime.utcnow().isoformat()})
        .eq("id", paper_id)
        .execute()
    )
    return update_resp

def update_processed2(supabase,paper_id):
    update_resp = (
        supabase.table("papers2")
        .update({"status":"processed",
                 "last_modified": datetime.utcnow().isoformat()})
        .eq("id", paper_id)
        .execute()
    )
    return update_resp

def update_processed(supabase,paper_id):
    update_resp = (
        supabase.table("papers")
        .update({"status":"processed",
                 "last_modified": datetime.utcnow().isoformat()})
        .eq("id", paper_id)
        .execute()
    )
    return update_resp
    
def get_papers_from_db(supabase, old_status, new_status):
    """Fetch one record with old_status, update its status to new_status and last_modified to current timestamp, and return the full row."""
    if not supabase:
        return None
    try:
        # Step 1: fetch one record with old_status
        fetch_resp = (
            supabase.table("papers")
            .select("*")
            .eq("status", old_status)
            .limit(1)
            .execute()
        )
        if not fetch_resp.data:
            return None
        row = fetch_resp.data[0]
        row_id = row["id"]

        # Step 2: update its status and last_modified
        from datetime import datetime
        now_ts = datetime.utcnow().isoformat()

        update_resp = (
            supabase.table("papers")
            .update({"status": new_status, "last_modified": now_ts})
            .eq("id", row_id)
            .execute()
        )
        if update_resp.data:
            return update_resp.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching/updating paper from database: {e}")
        print(f"Error fetching/updating paper from database: {e}")
        return None
    
    
def get_papers2_from_db(supabase, old_status, new_status):
    """Fetch one record with old_status, update its status to new_status and last_modified to current timestamp, and return the full row."""
    if not supabase:
        return None
    try:
        # Step 1: fetch one record with old_status
        fetch_resp = (
            supabase.table("papers2")
            .select("*")
            .eq("status", old_status)
            .limit(1)
            .execute()
        )
        if not fetch_resp.data:
            return None
        row = fetch_resp.data[0]
        row_id = row["id"]

        # Step 2: update its status and last_modified
        from datetime import datetime
        now_ts = datetime.utcnow().isoformat()

        update_resp = (
            supabase.table("papers2")
            .update({"status": new_status, "last_modified": now_ts})
            .eq("id", row_id)
            .execute()
        )
        if update_resp.data:
            return update_resp.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching/updating paper from database: {e}")
        print(f"Error fetching/updating paper from database: {e}")
        return None