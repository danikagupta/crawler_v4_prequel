import streamlit as st
import pandas as pd
import os
from datetime import datetime

import concurrent.futures as cf

from supabase_client import get_supabase_client, get_papers_from_db, update_processed, update_score_reason, update_score_reason2, update_processed2, get_papers2_from_db
from prompt_store import prompts, prompts2xxx, prompts3xxx, prompts4

from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel


SRC_DIR="pdf_pages"
DF_FILE="pdf_text.csv"
DIR_PATH="pdf_txt"
MAX_INPUT_LENGTH=100000

class PaperScore(BaseModel):
    score: int
    reason: str

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

# from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

def one_llm_classify_relevance(te, pr):
    #print(f"Starting Classification in {pr=}")
    llmModel = ChatOpenAI(model_name="gpt-4o-mini", api_key=st.secrets['OPENAI_API_KEY'],max_tokens=3000)

    messages=[
        SystemMessage(pr),
        HumanMessage(te[:MAX_INPUT_LENGTH])
    ]

    resp = llmModel.with_structured_output(PaperScore).invoke(messages)

    #print(f"\n\n* * * * *\nResponse: \n\n{resp}\n\n*********\n")
    #st.subheader("Analysis Result:")
    #st.write(f"Score: {resp.score}\n Reason: {resp.reason}")
    return resp.score, resp.reason


    
def process_one_paper_all_prompts(paper_id,filename):
    supabase=get_supabase_client()
    st.write(f"Processing file {filename}")
    print(f"Processing file {filename}")
    with open(os.path.join(DIR_PATH,filename),'r') as f:
        text_content=f.read()
    for p in prompts4:
        for i in range(1,4):
            prompt_name=p.get("prompt_name")
            prompt_text=p.get("prompt_text")        
            score,reason = one_llm_classify_relevance(text_content,prompt_text)
            update_score_reason2(supabase,paper_id,prompt_name,i,score,reason)
    update_processed2(supabase,paper_id)
    return
    
def process_one_paper():
    supabase=get_supabase_client()
    paper=get_papers2_from_db(supabase=supabase, old_status="new", new_status="processing")
    if not paper:
        return False
    paper_id=paper.get("id")
    paper_fn=paper.get("filename")
    process_one_paper_all_prompts(paper_id,paper_fn)
    return True
    
def process_multiple_papers(n):
    completed=0
    for i in range(n):
        completed += int(bool(process_one_paper()))
    return completed
    

def process_multiple_papers_parallel(parallel_runs: int, sequential_runs: int):
    """
    Launch `parallel_runs` workers in parallel.
    Each worker runs `sequential_runs` jobs sequentially.
    """
    total_tasks = parallel_runs * sequential_runs
    done = 0
    progress = st.progress(0.0)
    log = st.empty()

    with cf.ThreadPoolExecutor(max_workers=parallel_runs) as ex:
        futures = [ex.submit(process_multiple_papers, sequential_runs) for _ in range(parallel_runs)]
        for fut in cf.as_completed(futures):
            # Each worker returns how many it actually completed
            completed_by_worker = fut.result()
            done += completed_by_worker
            progress.progress(min(done / total_tasks, 1.0))
            log.text(f"Completed {done}/{total_tasks} planned jobs")

    st.success("All workers completed!")
    
def show_prompts():
    st.dataframe(prompts)   
    for p in prompts:
        prompt_name=p.get("prompt_name")
        col1=prompt_name+"_score"
        col2=prompt_name+"_reason"
        st.write(f"ALTER TABLE papers ADD COLUMN IF NOT EXISTS {col1} numeric; ")
        st.write(f"ALTER TABLE papers ADD COLUMN IF NOT EXISTS {col2} text; ")
        
def show_prompts4():
    st.dataframe(prompts4)   
    for p in prompts4:
        prompt_name=p.get("prompt_name")
        for i in range(1,4):
            col1=prompt_name+f"_{i}_score"
            col2=prompt_name+f"_{i}_reason"
            st.write(f"ALTER TABLE papers2 ADD COLUMN IF NOT EXISTS {col1} numeric; ")
            st.write(f"ALTER TABLE papers2 ADD COLUMN IF NOT EXISTS {col2} text; ")
    
def one_run():
    st.title("One run")
    with st.expander("Prompt Schema"):
        show_prompts4()
    parallel_runs=st.number_input("Parallelism", value=25)
    sequential_runs=st.number_input("Sequential",value=20)
    if st.button("Run"):
        process_multiple_papers_parallel(parallel_runs,sequential_runs)

    
if __name__ == "__main__":
    one_run()
    
