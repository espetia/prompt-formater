import streamlit as st
import sqlite3
import datetime
import re

# Database setup
DB_NAME = "prompts.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            role TEXT,
            context TEXT,
            objective TEXT,
            steps TEXT,
            considerations TEXT,
            output_format TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Simple migration to add new columns if the database already existed
    c.execute("PRAGMA table_info(prompts)")
    columns = [column[1] for column in c.fetchall()]
    
    new_columns = {
        "category": "TEXT",
        "role": "TEXT",
        "context": "TEXT",
        "output_format": "TEXT"
    }
    
    for col, data_type in new_columns.items():
        if col not in columns:
            c.execute(f"ALTER TABLE prompts ADD COLUMN {col} {data_type}")
            
    conn.commit()
    conn.close()

def save_prompt(title, category, role, context, objective, steps, considerations, output_format):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    created_at = datetime.datetime.now()
    c.execute('''
        INSERT INTO prompts (title, category, role, context, objective, steps, considerations, output_format, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, category, role, context, objective, steps, considerations, output_format, created_at))
    conn.commit()
    prompt_id = c.lastrowid
    conn.close()
    return prompt_id

def update_prompt(prompt_id, title, category, role, context, objective, steps, considerations, output_format):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE prompts 
        SET title=?, category=?, role=?, context=?, objective=?, steps=?, considerations=?, output_format=?
        WHERE id=?
    ''', (title, category, role, context, objective, steps, considerations, output_format, prompt_id))
    conn.commit()
    conn.close()

def delete_prompt(prompt_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM prompts WHERE id=?', (prompt_id,))
    conn.commit()
    conn.close()

def get_all_prompts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, title, category, created_at FROM prompts ORDER BY category ASC, created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_prompt(prompt_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT title, category, role, context, objective, steps, considerations, output_format FROM prompts WHERE id = ?', (prompt_id,))
    row = c.fetchone()
    conn.close()
    return row

def format_text_area(text):
    if not text:
        return ""
    lines = text.split('\n')
    
    # Clean up leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    formatted_lines = []
    levels = []

    for line in lines:
        if not line.strip():
            continue
            
        leading_ws = len(line) - len(line.lstrip())
        tabs = line[:leading_ws].count('\t')
        spaces = line[:leading_ws].count(' ')
        indent_level = tabs + (spaces // 4)

        stripped = line.strip()
        
        # If line already has list formatting, keep it as is
        if re.match(r'^(\d+(\.\d+)*\.|-|\*)\s+', stripped):
            formatted_lines.append(line)
            continue

        if indent_level >= len(levels):
            levels.extend([0] * (indent_level - len(levels) + 1))
        elif len(levels) > indent_level + 1:
            del levels[indent_level + 1:]

        levels[indent_level] += 1
        
        prefix = ".".join(str(lvl) for lvl in levels) + "."
        indent_str = "    " * indent_level
        formatted_lines.append(f"{indent_str}{prefix} {stripped}")

    return '\n'.join(formatted_lines)

def generate_markdown(title, role, context, objective, steps, considerations, output_format):
    md = f"# {title}\n\n"
    if role:
        md += f"## Role\n{role}\n\n"
    if context:
        md += f"## Context\n{format_text_area(context)}\n\n"
    if objective:
        md += f"## Objective\n{format_text_area(objective)}\n\n"
    if steps:
        md += f"## Steps to Follow\n{format_text_area(steps)}\n\n"
    if considerations:
        md += f"## Considerations\n{format_text_area(considerations)}\n\n"
    if output_format:
        md += f"## Output Format\n{output_format}\n\n"
    return md

st.set_page_config(page_title="Prompt Formater", page_icon="📝", layout="wide")

init_db()

# Initialize state variables
if 'current_prompt_id' not in st.session_state:
    st.session_state.current_prompt_id = None
if 'action' not in st.session_state:
    st.session_state.action = "create" # "create", "view", "edit"

# --- SIDEBAR ---
st.sidebar.title("📚 My Prompts")

if st.sidebar.button("➕ Create New Prompt", use_container_width=True, type="primary"):
    st.session_state.current_prompt_id = None
    st.session_state.action = "create"

st.sidebar.markdown("---")

# Group Prompts by Category
prompts = get_all_prompts()
categories = {}
for p in prompts:
    cat = p[2] if p[2] else "Uncategorized"
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(p)

for cat in sorted(categories.keys()):
    with st.sidebar.expander(f"📁 {cat}", expanded=True):
        for p in categories[cat]:
            if st.button(f"📝 {p[1]}", key=f"btn_{p[0]}", use_container_width=True):
                st.session_state.current_prompt_id = p[0]
                st.session_state.action = "view"


# --- MAIN SECTION ---
st.title("Prompt Formater & Creator 🤖")
st.markdown("Create, organize, edit, and copy your prompts with professional formatting.")

# ACTION: CREATE OR EDIT
if st.session_state.action in ["create", "edit"]:
    action_text = "Create New Prompt" if st.session_state.action == "create" else "Edit Prompt"
    st.header(f"✨ {action_text}")
    
    # Pre-fill data if editing
    p_title, p_cat, p_role, p_context, p_obj, p_steps, p_cons, p_out = ("", "", "", "", "", "", "", "Markdown Format")
    if st.session_state.action == "edit" and st.session_state.current_prompt_id:
        p_data = get_prompt(st.session_state.current_prompt_id)
        if p_data:
            p_title, p_cat, p_role, p_context, p_obj, p_steps, p_cons, p_out = p_data

    with st.form("prompt_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Prompt Title *", value=p_title, placeholder="Ex: Unit test generator")
            role = st.text_input("AI Role", value=p_role, placeholder="Ex: You are a Senior Python Developer...")
        with col2:
            category = st.text_input("Category / Tag", value=p_cat, placeholder="Ex: Programming, Marketing, SEO")
            output_format = st.text_input("Output Format *", value=p_out, help="Default is Markdown as requested.")
            
        context = st.text_area("Context", value=p_context, height=100, placeholder="Background situation or information the AI needs to know.")
        objective = st.text_area("Objective *", value=p_obj, height=100, placeholder="What is the exact goal of this prompt?")
        steps = st.text_area("Steps (Optional)", value=p_steps, height=120, placeholder="First do this...\nThen analyze...")
        considerations = st.text_area("Considerations", value=p_cons, height=100, placeholder="Rules, restrictions, or what NOT to do.")
        
        submit_text = "Save Prompt 🚀" if st.session_state.action == "create" else "Update Prompt 💾"
        submitted = st.form_submit_button(submit_text, type="primary")
        
        if submitted:
            if title.strip() == "" or objective.strip() == "":
                st.error("⚠️ Title and Objective fields are required.")
            else:
                if st.session_state.action == "create":
                    prompt_id = save_prompt(title, category, role, context, objective, steps, considerations, output_format)
                    st.session_state.current_prompt_id = prompt_id
                    st.success("✅ Prompt saved successfully!")
                else:
                    update_prompt(st.session_state.current_prompt_id, title, category, role, context, objective, steps, considerations, output_format)
                    st.success("✅ Prompt updated successfully!")
                
                st.session_state.action = "view"
                st.rerun()
                
    if st.session_state.action == "edit":
        if st.button("Cancel Editing", type="secondary"):
            st.session_state.action = "view"
            st.rerun()

# ACTION: VIEW
elif st.session_state.action == "view" and st.session_state.current_prompt_id:
    prompt_data = get_prompt(st.session_state.current_prompt_id)
    if prompt_data:
        title, category, role, context, objective, steps, considerations, output_format = prompt_data
        
        col_title, col_edit, col_del = st.columns([6, 1, 1])
        with col_title:
            st.header(f"📖 {title}")
            if category:
                st.caption(f"Category: **{category}**")
        with col_edit:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.action = "edit"
                st.rerun()
        with col_del:
            if st.button("🗑️ Delete", type="primary", use_container_width=True):
                delete_prompt(st.session_state.current_prompt_id)
                st.session_state.current_prompt_id = None
                st.session_state.action = "create"
                st.rerun()
                
        # Mostrar Markdown Listo para Copiar
        st.subheader("Generated Markdown")
        st.info("💡 Use the copy icon in the top right corner of the block below to copy your prompt.")
        
        md_text = generate_markdown(title, role, context, objective, steps, considerations, output_format)
        
        st.code(md_text, language="markdown")
        
        # Modo Vista Expandido
        with st.expander("View Breakdown Details"):
            if role: st.markdown(f"**Role:**\n{role}")
            if context: st.markdown(f"**Context:**\n{format_text_area(context)}")
            st.markdown(f"**Objective:**\n{format_text_area(objective)}")
            if steps: st.markdown(f"**Steps:**\n{format_text_area(steps)}")
            if considerations: st.markdown(f"**Considerations:**\n{format_text_area(considerations)}")
            if output_format: st.markdown(f"**Output Format:**\n{output_format}")
