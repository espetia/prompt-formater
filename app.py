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
            
    c.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT,
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

def save_template(template_name, title, category, role, context, objective, steps, considerations, output_format):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    created_at = datetime.datetime.now()
    c.execute('''
        INSERT INTO templates (template_name, title, category, role, context, objective, steps, considerations, output_format, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (template_name, title, category, role, context, objective, steps, considerations, output_format, created_at))
    conn.commit()
    conn.close()

def update_template(template_id, template_name, title, category, role, context, objective, steps, considerations, output_format):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE templates 
        SET template_name=?, title=?, category=?, role=?, context=?, objective=?, steps=?, considerations=?, output_format=?
        WHERE id=?
    ''', (template_name, title, category, role, context, objective, steps, considerations, output_format, template_id))
    conn.commit()
    conn.close()

def delete_template(template_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM templates WHERE id=?', (template_id,))
    conn.commit()
    conn.close()

def get_all_templates():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, template_name FROM templates ORDER BY template_name ASC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_template(template_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT template_name, title, category, role, context, objective, steps, considerations, output_format FROM templates WHERE id = ?', (template_id,))
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

if st.sidebar.button("📄 Manage Templates", use_container_width=True):
    st.session_state.action = "manage_templates"
    st.session_state.current_template_id = None

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
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {"t": "", "c": "", "r": "", "ctx": "", "o": "", "s": "", "cons": "", "out": "Markdown Format"}

    # Determine default values on first load of the action
    if 'last_action' not in st.session_state or st.session_state.last_action != st.session_state.action or ('last_prompt_id' not in st.session_state or st.session_state.last_prompt_id != st.session_state.current_prompt_id):
        st.session_state.last_action = st.session_state.action
        st.session_state.last_prompt_id = st.session_state.current_prompt_id
        
        if st.session_state.action == "edit" and st.session_state.current_prompt_id:
            p_data = get_prompt(st.session_state.current_prompt_id)
            if p_data:
                st.session_state.form_data = {
                    "t": p_data[0] or "", "c": p_data[1] or "", "r": p_data[2] or "", 
                    "ctx": p_data[3] or "", "o": p_data[4] or "", "s": p_data[5] or "", 
                    "cons": p_data[6] or "", "out": p_data[7] or "Markdown Format"
                }
        else:
            st.session_state.form_data = {"t": "", "c": "", "r": "", "ctx": "", "o": "", "s": "", "cons": "", "out": "Markdown Format"}

    templates = get_all_templates()
    if templates:
        template_options = {"": "Select a template..."}
        for t in templates:
            template_options[t[0]] = t[1]
            
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            selected_template = st.selectbox("Apply Template", options=list(template_options.keys()), format_func=lambda x: template_options[x], help="Select a template and click 'Load Template' to autofill fields below.")
        with col_t2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Load Template", type="secondary"):
                if selected_template:
                    t_data = get_template(selected_template)
                    if t_data:
                        st.session_state.form_data = {
                            "t": t_data[1] or st.session_state.form_data["t"], "c": t_data[2] or st.session_state.form_data["c"], 
                            "r": t_data[3] or st.session_state.form_data["r"], "ctx": t_data[4] or st.session_state.form_data["ctx"], 
                            "o": t_data[5] or st.session_state.form_data["o"], "s": t_data[6] or st.session_state.form_data["s"], 
                            "cons": t_data[7] or st.session_state.form_data["cons"], "out": t_data[8] or st.session_state.form_data["out"]
                        }
                        st.success("Template loaded successfully!")

    with st.form("prompt_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Prompt Title *", value=st.session_state.form_data["t"], placeholder="Ex: Unit test generator")
            role = st.text_input("AI Role", value=st.session_state.form_data["r"], placeholder="Ex: You are a Senior Python Developer...")
        with col2:
            category = st.text_input("Category / Tag", value=st.session_state.form_data["c"], placeholder="Ex: Programming, Marketing, SEO")
            output_format = st.text_input("Output Format *", value=st.session_state.form_data["out"], help="Default is Markdown as requested.")
            
        context = st.text_area("Context", value=st.session_state.form_data["ctx"], height=100, placeholder="Background situation or information the AI needs to know.")
        objective = st.text_area("Objective *", value=st.session_state.form_data["o"], height=100, placeholder="What is the exact goal of this prompt?")
        steps = st.text_area("Steps (Optional)", value=st.session_state.form_data["s"], height=120, placeholder="First do this...\nThen analyze...")
        considerations = st.text_area("Considerations", value=st.session_state.form_data["cons"], height=100, placeholder="Rules, restrictions, or what NOT to do.")
        
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

# ACTION: MANAGE TEMPLATES
elif st.session_state.action == "manage_templates":
    st.header("📄 Manage Templates")
    st.markdown("Create and manage templates that can be used to quickly fill out prompts.")
    
    if 'template_action' not in st.session_state:
        st.session_state.template_action = "list"
        
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Prompts"):
            st.session_state.action = "create"
            st.rerun()
    with col2:
        if st.session_state.template_action in ["list", "edit"] and st.button("➕ Create New Template", type="primary"):
            st.session_state.template_action = "create"
            st.session_state.current_template_id = None
            st.rerun()
            
    st.divider()

    if st.session_state.template_action in ["create", "edit"]:
        t_action_text = "Create New Template" if st.session_state.template_action == "create" else "Edit Template"
        st.subheader(f"✨ {t_action_text}")
        
        t_name, t_title, t_cat, t_role, t_ctx, t_obj, t_steps, t_cons, t_out = ("", "", "", "", "", "", "", "", "Markdown Format")
        if st.session_state.template_action == "edit" and st.session_state.current_template_id:
            t_data = get_template(st.session_state.current_template_id)
            if t_data:
                t_name, t_title, t_cat, t_role, t_ctx, t_obj, t_steps, t_cons, t_out = t_data

        with st.form("template_form"):
            template_name = st.text_input("Template Name *", value=t_name, placeholder="Ex: Standard Developer Prompt")
            
            st.markdown("### Template Fields")
            st.caption("Leave fields blank if you don't want the template to overwrite them.")
            
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Prompt Title", value=t_title)
                role = st.text_input("AI Role", value=t_role)
            with c2:
                category = st.text_input("Category / Tag", value=t_cat)
                output_format = st.text_input("Output Format", value=t_out)
                
            context = st.text_area("Context", value=t_ctx, height=80)
            objective = st.text_area("Objective", value=t_obj, height=80)
            steps = st.text_area("Steps", value=t_steps, height=80)
            considerations = st.text_area("Considerations", value=t_cons, height=80)
            
            t_submit_text = "Save Template" if st.session_state.template_action == "create" else "Update Template"
            t_submit = st.form_submit_button(t_submit_text, type="primary")
            
            if t_submit:
                if template_name.strip() == "":
                    st.error("⚠️ Template Name is required.")
                else:
                    if st.session_state.template_action == "create":
                        save_template(template_name, title, category, role, context, objective, steps, considerations, output_format)
                        st.success("✅ Template saved successfully!")
                    else:
                        update_template(st.session_state.current_template_id, template_name, title, category, role, context, objective, steps, considerations, output_format)
                        st.success("✅ Template updated successfully!")
                    st.session_state.template_action = "list"
                    st.rerun()
                    
        if st.button("Cancel Template Editing", type="secondary"):
            st.session_state.template_action = "list"
            st.rerun()

    elif st.session_state.template_action == "list":
        templates = get_all_templates()
        if not templates:
            st.info("No templates found. Create one to get started!")
        else:
            for t in templates:
                with st.container():
                    tc1, tc2, tc3 = st.columns([6, 1, 1])
                    with tc1:
                        st.markdown(f"**{t[1]}**")
                    with tc2:
                        if st.button("✏️ Edit", key=f"edit_t_{t[0]}", use_container_width=True):
                            st.session_state.current_template_id = t[0]
                            st.session_state.template_action = "edit"
                            st.rerun()
                    with tc3:
                        if st.button("🗑️ Delete", key=f"del_t_{t[0]}", type="primary", use_container_width=True):
                            delete_template(t[0])
                            st.rerun()
                    st.divider()
