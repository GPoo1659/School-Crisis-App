import streamlit as st
import json
import os
import requests

# Set page configuration
st.set_page_config(
    page_title="Just-in-Time School Decision Support App",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern look
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4b5563;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border-left: 5px solid #1e3a8a;
    }
    .card-title {
        font-size: 1.3rem;
        color: #1e3a8a;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
    .highlight {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Pre-baked Case Study Database (Offline Fallback)
PRE_BAKED_SCENARIOS = {
    "Case 1: The Plagiarism Plight (Teacher Prep Focus)": {
        "title": "Case 1: The Plagiarism Plight",
        "audience": "Preservice Teacher",
        "focus": "InTASC #9 (Professional Learning & Ethical Practice), ISTE #4.7 (Digital Citizen Advocate)",
        "scenario": (
            "A student in your high school chemistry class submits a highly sophisticated lab report. "
            "The vocabulary, structure, and depth are vastly superior to their previous work. When queried, "
            "the student insists they wrote it themselves but admits to using an AI writing assistant "
            "for 'rephrasing and polish.' The school district currently has no explicit policy "
            "governing Generative AI in coursework, and the grading rubric only mentions 'originality.' "
            "How do you handle the grading, and how do you turn this into a learning moment without "
            "creating an adversarial parent-student dynamic?"
        ),
        "difficulty": "Moderate",
        "questions": [
            {
                "question": "What is your immediate pedagogical next step?",
                "choices": [
                    "A) Assign a zero for plagiarism based on standard school academic honesty definitions.",
                    "B) Sit down with the student, run through the report, and ask them to explain the complex concepts in their own words to verify their actual understanding.",
                    "C) Accept the paper as-is, since the district's handbook does not explicitly ban AI writing tools.",
                    "D) Call the parents immediately and schedule a disciplinary meeting."
                ],
                "feedbacks": {
                    "A": "Incorrect. Awarding a zero in the absence of clear guidelines and proof of bad intent can alienate the student and invite severe pushback from parents.",
                    "B": "Correct! This aligns with InTASC #6 (Assessment) and #9. It prioritizes student learning and agency over punitive measures, verifying their comprehension while establishing trust.",
                    "C": "Incorrect. Ignoring the clear disparity in their work fails to address the underlying issue of academic integrity and misses a crucial teachable moment regarding digital citizenship.",
                    "D": "Incorrect. Escallating to an official disciplinary meeting prematurely without a discussion with the student first can create defensive and adversarial dynamics."
                }
            },
            {
                "question": "What is your proactive, systems-level step for future assignments?",
                "choices": [
                    "A) Ban all computers and digital devices during writing phases, forcing paper-and-pencil drafting.",
                    "B) Create a co-designed 'AI Usage Scale' for all rubrics, clarifying to students exactly what level of AI assistance (none, editing, brainstorming, co-creation) is allowed for each assignment.",
                    "C) Demand the district technology department purchase a school-wide AI detector subscription.",
                    "D) Tell students that AI is strictly banned but do not modify your rubrics."
                ],
                "feedbacks": {
                    "A": "Incorrect. Banning technology fails to align with ISTE Standards which mandate the purposeful infusion of digital tools to enrich professional and classroom practice.",
                    "B": "Correct! This aligns with ISTE #4.4 (Learning Designer) and ISTE #4.7 (Digital Citizen Advocate). Creating an AI usage framework establishes clear, transparent expectations and teaches students responsible, ethical technology use.",
                    "C": "Incorrect. AI detectors are notoriously unreliable and frequently produce false positives, particularly for English Language Learners, creating equity issues.",
                    "D": "Incorrect. Vague bans with no rubric updates fail to provide transparent assessment criteria, violating InTASC #6."
                }
            }
        ]
    },
    "Case 2: The Silent Board Policy (Leadership Focus)": {
        "title": "Case 2: The Silent Board Policy",
        "audience": "Future School Leader",
        "focus": "NELP #2 (Ethics & Professional Norms), NELP #7 (Policy, Governance, & Advocacy)",
        "scenario": (
            "As a newly appointed middle school principal, you discover teachers are highly frustrated "
            "with severe student distractions from smartphones. Your teachers collaboratively propose "
            "a strict classroom smartphone-lockbox policy. However, several school board members express "
            "grave concerns: they claim parents will feel disconnected and panic during an emergency. "
            "The superintendent advises you to tread carefully. How do you construct a policy that protects "
            "the academic learning environment while ensuring transparency, family partnerships, and board alignment?"
        ),
        "difficulty": "High",
        "questions": [
            {
                "question": "How do you build consensus with stakeholders before presenting the policy?",
                "choices": [
                    "A) Implement the lockbox policy immediately under your administrative authority and deal with complaints later.",
                    "B) Host a collaborative feedback loop—surveying parents, presenting research on cognitive load and cell phones, and establishing a clear parent emergency-contact channel to the main office.",
                    "C) Side with the school board and tell teachers to just handle cell phone distractions individually.",
                    "D) Postpone any action indefinitely to avoid political conflict."
                ],
                "feedbacks": {
                    "A": "Incorrect. Unilateral policy changes without parent and board engagement frequently backfire, violating NELP #5 (Community Leadership) and NELP #1 (Mission & Vision).",
                    "B": "Correct! This directly aligns with NELP #5 (engaging families) and NELP #1.2 (using data to lead continuous improvement). It structures a collaborative vision that balances academic focus with safety.",
                    "C": "Incorrect. Leaving teachers without systemic support damages morale and classroom environments, failing to support staff professional capacity (NELP #7).",
                    "D": "Incorrect. Indecision violates NELP #2 (Ethics & Professional Norms) which demands that leaders actively advocate for student wellbeing and optimal learning cultures."
                }
            }
        ]
    },
    "Case 3: The Equity Gap (Collaborative Focus)": {
        "title": "Case 3: The Equity Gap",
        "audience": "Collaborative (Leader & Teacher)",
        "focus": "NELP #3 (Equity & Cultural Responsiveness), InTASC #2 (Learning Differences)",
        "scenario": (
            "Your district launches a major 1:1 laptop initiative. However, three weeks in, "
            "a teacher notes that English Language Learners (ELL) and students with special needs "
            "cannot utilize their laptops effectively at home. Their families lack high-speed "
            "internet, and the district-issued devices have software blocks that prevent parents "
            "from downloading translation tools or accessibility extensions. The administration's "
            "response is that all software must be standardized for security. How do you resolve this "
            "disturbing inequity?"
        ),
        "difficulty": "Extreme",
        "questions": [
            {
                "question": "What is the joint leadership-pedagogy solution?",
                "choices": [
                    "A) Tell the affected students to do alternative, paper-based assignments at home.",
                    "B) The teacher and principal collaboratively advocate to the IT director to whitelist and pre-install standardized accessibility extensions (e.g., text-to-speech, translation tools) and negotiate district-funded Wi-Fi hotspots for families in need.",
                    "C) Tell parents they must buy their own internet and devices if they want accessibility tools.",
                    "D) Do nothing and let students grade suffer if they cannot complete online work."
                ],
                "feedbacks": {
                    "A": "Incorrect. Separating students into technology-haves and have-nots creates an exclusionary educational program, violating InTASC #2 and school-wide equity guidelines.",
                    "B": "Correct! This beautifully bridges classroom teaching needs (InTASC #2 and #10) with systemic technology leadership (NELP #3 and #4). It ensures equitable access to educational resources, technologies, and services.",
                    "C": "Incorrect. Shifting the burden to historically marginalized families is highly inequitable and directly violates NELP #3 (Equity & Cultural Responsiveness).",
                    "D": "Incorrect. Allowing student failure due to systemic access gaps violates the fundamental ethical obligation to promote the well-being and success of each student (NELP #2)."
                }
            }
        ]
    }
}

# Core Application Layout
st.sidebar.markdown("## ⚙️ System Setup")
st.sidebar.markdown(
    "Configure your AI model. For dynamic, personalized generation, please "
    "enter your Gemini API Key below. If left blank, the app will operate in "
    "**Offline Practice Mode** using pre-loaded professional cases."
)

# Try to load API key from Streamlit Secrets first
api_key_default = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key_default = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

api_key = st.sidebar.text_input("Google Gemini API Key", value=api_key_default, type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎓 Credential Badge Profile")
st.sidebar.info(
    "**Facilitator Credentials:**\n"
    "*   Google Certified Champion Trainer\n"
    "*   ISTE Certified Ed Tech Leader\n"
    "*   JTATE Editorial Board Member"
)

# App Title and Description
st.markdown("<div class='main-header'>🏫 Just-in-Time Decision Support App</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-header'>A Two-Engine AI framework aligning <b>NELP Standards</b> (School Leaders) and "
    "<b>ISTE/InTASC Standards</b> (Preservice Teachers) to navigate the unpredictable realities of schools.</div>",
    unsafe_allow_html=True
)

# Helper Functions for Live Gemini API Integration
def query_gemini(api_key_val, prompt_val, system_instruction_val=None, json_mode_val=False):
    # API key validation helper
    key = api_key_val.strip()
    # Support both old AIza keys and new secure AQ. keys
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    
    contents = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_val}
                ]
            }
        ]
    }
    
    if system_instruction_val:
        contents["systemInstruction"] = {
            "parts": [
                {"text": system_instruction_val}
            ]
        }
        
    if json_mode_val:
        contents["generationConfig"] = {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    else:
        contents["generationConfig"] = {
            "temperature": 0.7
        }
        
    try:
        response = requests.post(url, headers=headers, json=contents, timeout=90)
        if response.status_code == 200:
            res_json = response.json()
            text = res_json['candidates'][0]['content']['parts'][0]['text']
            return text
        else:
            st.error(f"Gemini API returned error code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to Gemini API: {str(e)}")
        return None

def parse_json_safely(text):
    if not text:
        return None
    try:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except Exception as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        return None

# Set up tabs
tab_sim, tab_desk, tab_standards, tab_crowd = st.tabs([
    "🎯 Tab 1: What-If Scenario Simulator",
    "🚨 Tab 2: Just-in-Time Crisis Desk",
    "📚 Tab 3: Standards Reference Desk",
    "📥 Tab 4: Crowd-Sourced Scenario Bank"
])

# ==========================================
# TAB 1: WHAT-IF SCENARIO SIMULATOR
# ==========================================
# Initialize session state keys
if "crowdsourced_scenarios" not in st.session_state:
    st.session_state.crowdsourced_scenarios = {}
if "desk_chat_history" not in st.session_state:
    st.session_state.desk_chat_history = []
if "offline_case_selection" not in st.session_state:
    st.session_state.offline_case_selection = list(PRE_BAKED_SCENARIOS.keys())[0]
if "live_case" not in st.session_state:
    st.session_state.live_case = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "antagonist_name" not in st.session_state:
    st.session_state.antagonist_name = ""

with tab_sim:
    st.markdown("<div class='card-title'>🎯 Scenario Simulator: Practicing for the Unknown</div>", unsafe_allow_html=True)
    st.write(
        "Use this sandbox to generate dynamic school scenarios based on national standards. "
        "Engage in interactive problem-solving to test your readiness for administrative and classroom crises."
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Simulation Options")
        if api_key:
            sim_mode = st.radio("Choose Sandbox Mode:", ["🚀 Dynamic Roleplay Engine", "🎮 Practice Case Playroom"])
        else:
            sim_mode = "🎮 Practice Case Playroom"
            
        role = st.selectbox("Select Your Focus Role", ["Classroom Teacher / Preservice Candidate", "School Building Administrator (Principal)", "District Administrator (Superintendent)"])
        topic = st.selectbox("Standards Alignment Focus", [
            "Ethics & Professional Norms (NELP #2 / InTASC #9)",
            "Equity, Inclusiveness, & Cultural Responsiveness (NELP #3 / InTASC #2)",
            "Learning & Instructional Technologies (NELP #4 / ISTE Coaches)",
            "Policy, Governance, & Advocacy (NELP #7 / InTASC #10)"
        ])
        difficulty = st.select_slider("Select Simulation Difficulty", options=["Beginner", "Moderate", "High", "Extreme"])
        
        generate_btn = st.button("🚀 Generate Case Scenario")
        
        if generate_btn:
            if not api_key:
                # Offline Practice Mode Fallback
                best_match = None
                if "Preservice" in role:
                    if "Equity" in topic:
                        best_match = "Case 3: The Equity Gap (Collaborative Focus)"
                    else:
                        best_match = "Case 1: The Plagiarism Plight (Teacher Prep Focus)"
                else:
                    if "Equity" in topic:
                        best_match = "Case 3: The Equity Gap (Collaborative Focus)"
                    else:
                        best_match = "Case 2: The Silent Board Policy (Leadership Focus)"
                
                if best_match:
                    st.session_state.offline_case_selection = best_match
                    st.toast(f"🎯 Matched with: {best_match} based on your selections!")
            else:
                # Live AI Mode Case Generation
                with st.spinner("🔮 Engineering custom scenario on demand..."):
                    system_instruction_sim = (
                        "You are an expert professor of educational leadership and teacher preparation.\n"
                        "Generate a highly realistic, challenging school crisis scenario matching the user's choices.\n"
                        "You must respond ONLY with a valid JSON object with these exact keys:\n"
                        "{\n"
                        "  \"title\": \"A short, punchy title for the crisis\",\n"
                        "  \"audience\": \"The target role matching the user's choice\",\n"
                        "  \"focus\": \"Specific standards component aligned\",\n"
                        "  \"scenario\": \"The full scenario text describing the active crisis (2-4 paragraphs). It must be emotionally charged, highly realistic, and open-ended.\",\n"
                        "  \"antagonist_name\": \"The name and role of the key person challenging the educator (e.g., 'Mrs. Gable (Angry Parent)', 'Mr. Vance (Union Rep)')\"\n"
                        "}"
                    )
                    prompt_sim = f"Role: {role}\nFocus: {topic}\nDifficulty: {difficulty}\n"
                    
                    text_sim_out = query_gemini(api_key, prompt_sim, system_instruction_sim, json_mode_val=True)
                    data_sim_parsed = parse_json_safely(text_sim_out)
                    
                    if data_sim_parsed:
                        st.session_state.live_case = data_sim_parsed
                        st.session_state.chat_messages = []
                        st.session_state.antagonist_name = data_sim_parsed.get("antagonist_name", "Angry Stakeholder")
                        st.toast("🎯 Live AI Case Engineered Successfully!")
                    else:
                        st.error("Failed to generate a custom scenario. Please try again.")

    with col2:
        if sim_mode == "🎮 Practice Case Playroom":
            if not api_key:
                st.warning("⚠️ Operating in **Offline Practice Mode** using verified pre-loaded scenarios. (Enter a Gemini API Key in the sidebar to activate the dynamic, interactive AI generator).")
            else:
                st.success("🤖 Google Gemini Online Mode Connected. Practice Playroom Active.")
                
            # Combine preloaded and crowdsourced scenarios
            available_scenarios = PRE_BAKED_SCENARIOS.copy()
            if st.session_state.crowdsourced_scenarios:
                available_scenarios.update(st.session_state.crowdsourced_scenarios)
                
            selected_case_name = st.selectbox(
                "Choose an active scenario (Pre-Loaded or Crowdsourced):", 
                list(available_scenarios.keys()),
                key="offline_case_selection"
            )
            case_data = available_scenarios[selected_case_name]
            
            st.markdown(f"#### 📖 {case_data.get('title', selected_case_name)}")
            st.markdown(f"**Target Audience:** `{case_data.get('audience', 'N/A')}` | **Focus:** `{case_data.get('focus', 'N/A')}` | **Difficulty:** `{case_data.get('difficulty', 'Moderate')}`")
            st.write(case_data.get('scenario', ''))
            
            st.markdown("---")
            st.markdown("### 📝 Sandbox Decision Checkpoints")
            
            # Interactive walkthrough of pre-baked questions
            for i, q in enumerate(case_data.get('questions', [])):
                st.markdown(f"**Question {i+1}: {q['question']}**")
                choice = st.radio(
                    f"Select your decision for Question {i+1}:", 
                    q['choices'], 
                    index=None, # Fix immediate feedback: start with nothing selected!
                    key=f"q_{i}_{selected_case_name}"
                )
                
                # Check option only if selected
                if choice is not None:
                    selected_letter = choice[0] # A, B, C, or D
                    feedback = q['feedbacks'].get(selected_letter, "")
                    
                    if "Correct!" in feedback:
                        st.success(feedback)
                    elif feedback:
                        st.error(feedback)
        else:
            # Dynamic Roleplay Engine Output
            if st.session_state.live_case:
                case_data = st.session_state.live_case
                st.success("🤖 Google Gemini Online Mode Connected. Live Simulation Active.")
                st.markdown(f"#### 📖 {case_data.get('title', 'Live Scenario')}")
                st.markdown(f"**Target Audience:** `{case_data.get('audience', role)}` | **Focus:** `{case_data.get('focus', topic)}` | **Difficulty:** `{difficulty}`")
                st.write(case_data.get("scenario", ""))
                
                st.markdown("---")
                st.markdown(f"### 💬 Roleplay Chat with {st.session_state.antagonist_name}")
                st.write("Type your response to the stakeholder below to practice your active de-escalation and leadership skills.")
                
                # Render Chat messages
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                        
                chat_input_val = st.chat_input(f"Speak to {st.session_state.antagonist_name}...")
                if chat_input_val:
                    # Append user message
                    st.session_state.chat_messages.append({"role": "user", "content": chat_input_val})
                    st.rerun()
                    
                # If last message is from user, generate AI response
                if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
                    user_history = ""
                    for m in st.session_state.chat_messages:
                        user_history += f"{m['role']}: {m['content']}\n"
                        
                    prompt_reply = (
                        f"Scenario: {case_data.get('scenario', '')}\n\n"
                        f"Chat History:\n{user_history}\n"
                        "Generate your next response. Keep it realistic, emotional, and targeted to the educator's actions."
                    )
                    system_instruction_reply = (
                        f"You are roleplaying as {st.session_state.antagonist_name}. Do not break character. "
                        "Respond to the user's statements in character, challenging them in a school-based scenario."
                    )
                    
                    with st.spinner(f"💬 {st.session_state.antagonist_name} is typing..."):
                        reply = query_gemini(api_key, prompt_reply, system_instruction_reply)
                        if reply:
                            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                            st.rerun()
            else:
                st.info("👈 Choose your Options on the left, then click **🚀 Generate Case Scenario** to engineer a dynamic, live-roleplay AI crisis scenario!")

# ==========================================
# TAB 2: JUST-IN-TIME CRISIS DESK
# ==========================================
# Initialize session state keys for crisis desk
if "last_crisis_text" not in st.session_state:
    st.session_state.last_crisis_text = ""
if "last_crisis_output" not in st.session_state:
    st.session_state.last_crisis_output = None

with tab_desk:
    st.markdown("<div class='card-title'>🚨 Just-in-Time Crisis Desk: Real-World Action Plans</div>", unsafe_allow_html=True)
    st.write(
        "Are you currently facing a challenging situation in your classroom or building? "
        "Describe your active crisis below, select your target guidelines, and instantly extract a "
        "policy-compliant action plan, communication drafts, and professional alignment audits."
    )
    
    crisis_text = st.text_area(
        "Describe the active problem you are facing (e.g. parent complaints about AI policy, school security issues, grading equity disputes, special education resource alignment):",
        placeholder="A parent is threatening to sue because we flagged their student's paper as AI-generated, but our district handbook doesn't explicitly mention GenAI. What do I do?",
        height=150
    )
    
    col_desk_1, col_desk_2 = st.columns([1, 1])
    with col_desk_1:
        standards_selected = st.multiselect("Select standards to audit against:", [
            "NELP Standard 2: Ethics and Professional Norms",
            "NELP Standard 3: Equity, Inclusiveness, and Cultural Responsiveness",
            "NELP Standard 4: Learning and Instruction",
            "NELP Standard 7: Policy, Governance, and Advocacy",
            "ISTE Standards for Coaches / Educators",
            "InTASC Model Core Teaching Standards"
        ], default=["NELP Standard 2: Ethics and Professional Norms", "NELP Standard 7: Policy, Governance, and Advocacy"])
        
    with col_desk_2:
        output_format = st.selectbox("Preferred Decision Output Style", [
            "Superintendent Briefing & Rapid Action Plan",
            "Teacher-Parent Mediation Script & Communication Templates",
            "School Board Policy Exception Memo"
        ])
        
    solve_btn = st.button("🛠️ Resolve Crisis & Generate Solutions")
    
    if solve_btn:
        if not crisis_text:
            st.warning("Please enter some details about your active crisis before running the resolution engine.")
        else:
            st.session_state.last_crisis_text = crisis_text
            if not api_key:
                # Offline Practice Mode Fallback
                st.session_state.last_crisis_output = "offline"
            else:
                # Dynamic Online Analysis
                with st.spinner("🔮 Dual-Engine AI is analyzing active crisis and auditing professional standards..."):
                    system_instruction_desk = (
                        "You are a highly qualified school superintendent and expert educational policy consultant.\n"
                        "Your job is to analyze the user's school-based crisis and produce a structured, professional resolution plan.\n"
                        "You must respond ONLY with a valid JSON object with these exact keys:\n"
                        "{\n"
                        "  \"immediate_steps_1_24_h\": \"Markdown text detailing immediate, professional, tactical steps to de-escalate and find facts in the first 24 hours.\",\n"
                        "  \"immediate_steps_2_5_d\": \"Markdown text detailing logical, supportive local resolution steps for the next 2-5 days.\",\n"
                        "  \"communication_templates\": \"Markdown text containing drafted professional emails, meeting agendas, scripts, or board memos matching the user's selected output style, customized specifically to the details of their crisis.\",\n"
                        "  \"standards_audit\": \"Markdown text providing a detailed legal, regulatory, and professional standard audit linking the crisis actions directly to the selected standards (e.g. NELP, InTASC, ISTE) and incorporating Oklahoma board authorities or policies (such as Parent's Bill of Rights, dress policies, or district discretion).\"\n"
                        "}"
                    )
                    prompt_desk = f"""
                    Analyze this real-world school crisis:
                    "{crisis_text}"
                    
                    Selected Standards for Alignment: {", ".join(standards_selected)}
                    Requested Style of Outputs: {output_format}
                    
                    Provide specific, robust, and highly practical solutions tailored to this exact scenario.
                    """
                    text_desk_out = query_gemini(api_key, prompt_desk, system_instruction_desk, json_mode_val=True)
                    data_desk_parsed = parse_json_safely(text_desk_out)
                    
                    if data_desk_parsed:
                        st.session_state.last_crisis_output = data_desk_parsed
                        st.session_state.desk_chat_history = [
                            {"role": "assistant", "content": "Hello! I am your AI Policy Co-Pilot. I have generated your rapid action plan, parent/staff communication templates, and standards audit above. How can I help you customize, adapt, or expand on this response? You can ask me to write alternative emails, roleplay as the parent, or analyze a 'what if' progression of this crisis."}
                        ]
                    else:
                        st.error("Failed to analyze the crisis. Please try again.")

    # Render Output Sections
    if st.session_state.last_crisis_output is not None:
        st.markdown("---")
        st.markdown("### 💡 School Decision Support Output")
        
        tab_steps, tab_comm, tab_audit = st.tabs(["📋 Immediate Action Steps", "📧 Communication Templates", "⚖️ Standards & Policy Audit"])
        
        if st.session_state.last_crisis_output == "offline":
            # STATIC PRE-BAKED CHESTNUT PLAGIARISM OUTPUT
            with tab_steps:
                st.markdown("#### 🛑 Next 1 to 24 Hours: De-escalation & Fact Finding")
                st.write("1. **Pause punitive actions:** Delay inputting any official grade penalties until you conduct an objective, diagnostic review.")
                st.write("2. **Conduct a cognitive conference:** Schedule a brief meeting with the student. Rather than accusing them, ask them to talk through the logical structure and vocabulary of the submitted essay to assess actual learning mastery.")
                st.write("3. **Notify Leadership:** Brief the assistant principal or principal on the parental objection to ensure administrative alignment and prevent administrative blindsiding.")
                
                st.markdown("#### 📅 Next 2 to 5 Days: Local Resolution")
                st.write("1. **Schedule a supportive parent-teacher conference:** Reframe the conversation away from 'cheating' and toward 'academic progress and demonstration of learning standards.'")
                st.write("2. **Offer a low-stakes reassessment option:** Let the student demonstrate subject-matter knowledge through an alternative, supervised format (e.g., in-class essay prompt or oral presentation).")
                
            with tab_comm:
                st.markdown("#### Draft Email to Parent (Reframing Conflict to Collaboration)")
                st.code(
                    "Subject: Collaborative Academic Support for [Student Name] - Chemistry Class\n\n"
                    "Dear [Parent Name],\n\n"
                    "Thank you for reaching out regarding the feedback on [Student Name]'s chemistry report. "
                    "Our goal is always to ensure that every student fully understands the scientific concepts "
                    "we cover, preparing them to succeed in college and future careers. \n\n"
                    "Because our digital landscape is evolving rapidly, we see this as an exciting opportunity to partner "
                    "with you. I would love to invite you and [Student Name] to a brief, supportive chat. "
                    "Instead of focusing on digital detection tools, I want to invite [Student Name] to share "
                    "their chemistry insights and walk through the lab report's experiments with me in person. "
                    "This will let us celebrate what they have mastered and confirm exactly where we can "
                    "support their ongoing learning.\n\n"
                    "Please let me know if Monday after school or Tuesday morning works for a quick, 15-minute meeting.\n\n"
                    "Warm regards,\n"
                    "[Educator Name]\n"
                    "[School Name]",
                    language="markdown"
                )
                
            with tab_audit:
                st.markdown("#### ⚖️ Grounded Standards Analysis")
                st.info(
                    "**NELP Standard Component 2.1 (Ethics and Professional Norms):**\n"
                    "Requires school leaders and staff to reflect on and cultivate professional dispositions (transparency, trust, fairness, collaboration). "
                    "Conducting a collaborative dialogue instead of issuing immediate disciplinary sanctions directly upholds district integrity and fosters trust.\n\n"
                    "**NELP Standard Component 7.3 (Policy, Governance & Advocacy):**\n"
                    "Highlights the need to evaluate and represent district needs. A silent board policy on GenAI must not be filled by random punitive reactions. "
                    "A systemic exception or local guideline must be drafted collaboratively, advocating for board-level updates."
                )
        else:
            # LIVE AI DYNAMIC OUTPUT
            out = st.session_state.last_crisis_output
            with tab_steps:
                st.markdown("#### 🛑 Next 1 to 24 Hours: De-escalation & Fact Finding")
                st.write(out.get("immediate_steps_1_24_h", "No immediate steps found."))
                
                st.markdown("#### 📅 Next 2 to 5 Days: Local Resolution")
                st.write(out.get("immediate_steps_2_5_d", "No long-term steps found."))
                
            with tab_comm:
                st.write(out.get("communication_templates", "No templates found."))
                
            with tab_audit:
                st.markdown("#### ⚖️ Grounded Standards & Policy Analysis")
                st.info(out.get("standards_audit", "No standards audit found."))
                
        # Co-Pilot Chat integration (Active only when live online mode is connected)
        if st.session_state.last_crisis_output != "offline" and api_key:
            st.markdown("---")
            st.markdown("### 💬 Tab 2 Co-Pilot Chat")
            st.write("Need to adjust the action plan, rewrite an email, or prepare for follow-up hurdles? Ask your AI Co-Pilot below:")
            
            # Render Co-Pilot Chat history
            for msg in st.session_state.desk_chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            desk_chat_input = st.chat_input("Ask a follow-up or request modifications (e.g. 'Translate the email into Spanish' or 'What if the parent refuses to meet?')...", key="desk_chat_input_key")
            
            if desk_chat_input:
                st.session_state.desk_chat_history.append({"role": "user", "content": desk_chat_input})
                st.rerun()
                
            # Generate AI follow-up response if the last message is from the user
            if st.session_state.desk_chat_history and st.session_state.desk_chat_history[-1]["role"] == "user":
                # Prepare history context
                chat_context = f"Original Crisis Context:\n\"{st.session_state.last_crisis_text}\"\n\nGenerated Solution Context:\n{json.dumps(st.session_state.last_crisis_output, indent=2)}\n\n"
                chat_history_str = ""
                for m in st.session_state.desk_chat_history:
                    chat_history_str += f"{m['role']}: {m['content']}\n"
                    
                prompt_followup = (
                    f"{chat_context}"
                    f"Conversational History:\n{chat_history_str}\n"
                    "Provide a helpful, professional follow-up response as an expert educational consultant. "
                    "If the user asks to modify communication templates, write new templates in full. Maintain standard-alignment and policy awareness."
                )
                system_instruction_followup = (
                    "You are a helpful, professional, and expert school superintendent and policy consultant. "
                    "Answer the user's follow-up questions regarding their active school crisis, and help them refine, modify, "
                    "or expand on their action plans or communication materials. Ground all suggestions in school leadership and teacher standards."
                )
                
                with st.spinner("💬 Co-Pilot is generating response..."):
                    reply_followup = query_gemini(api_key, prompt_followup, system_instruction_followup)
                    if reply_followup:
                        st.session_state.desk_chat_history.append({"role": "assistant", "content": reply_followup})
                        st.rerun()

# ==========================================
# TAB 3: STANDARDS REFERENCE DESK
# ==========================================
with tab_standards:
    st.markdown("<div class='card-title'>📚 Standards Reference Library</div>", unsafe_allow_html=True)
    st.write(
        "Access the complete, searchable text of professional frameworks from your preparation program "
        "to ensure your classroom and administrative practices are grounded in national benchmarks."
    )
    
    st_cat = st.radio("Select Framework to Browse:", [
        "NELP Building-Level Standards (2018)", 
        "ISTE Standards for Coaches", 
        "InTASC Model Core Teaching Standards"
    ], horizontal=True)
    
    if st_cat == "NELP Building-Level Standards (2018)":
        st.markdown("### 🏆 National Educational Leadership Preparation (NELP) Standards")
        st.write("*Approved by the National Policy Board for Educational Administration (NPBEA)*")
        
        nelp_std_data = {
            "Standard 1: Mission, Vision, and Improvement": "Understand and demonstrate the capacity to collaboratively lead, design, and implement a school mission, vision, and process for continuous improvement that reflects a core set of values including data use, technology, equity, diversity, and community.",
            "Standard 2: Ethics and Professional Norms": "Understand and demonstrate the capacity to advocate for ethical decisions and to cultivate professional norms and culture (equity, integrity, transparency, trust, and lifelong learning).",
            "Standard 3: Equity, Inclusiveness, and Cultural Responsiveness": "Understand and demonstrate the capacity to develop and maintain a supportive, equitable, culturally responsive, and inclusive school culture.",
            "Standard 4: Learning and Instruction": "Evaluate, develop, and implement coherent systems of curriculum, instruction, data systems, supports, and assessment.",
            "Standard 5: Community and External Leadership": "Understand and demonstrate the capacity to represent and support school communities in engaging families, community members, business and civic partners to strengthen learning.",
            "Standard 6: Operations and Management": "Develop, monitor, evaluate, and manage school systems for operations, resources, technology, and human capital.",
            "Standard 7: Building Professional Capacity": "Understand and demonstrate the capacity to collaboratively build the professional capacity of educators through systems of support, coaching, and professional development."
        }
        for name, text in nelp_std_data.items():
            with st.expander(name):
                st.write(text)
                
    elif st_cat == "ISTE Standards for Coaches":
        st.markdown("### 🚀 International Society for Technology in Education (ISTE) Standards")
        iste_coaches_data = {
            "4.1 Change Agent": "Coaches inspire educators and leaders to use technology to create equitable and ongoing access to high-quality learning, including building a shared vision and maximizing tech potential.",
            "4.2 Connected Learner": "Coaches model standards and pursue professional learning to continually improve coaching and teaching practice.",
            "4.3 Collaborator": "Coaches establish trusting and respectful coaching relationships to explore new instructional strategies and culturally relevant digital content.",
            "4.4 Learning Designer": "Coaches model instructional design principles to create effective digital learning environments.",
            "4.5 Professional Learning Facilitator": "Coaches design professional learning based on adult-learning frameworks to build the capacity of educational staff.",
            "4.6 Data-Driven Decision-Maker": "Coaches model and support the use of qualitative and quantitative data to inform instruction and improve program outcome.",
            "4.7 Digital Citizen Advocate": "Coaches model and promote safe, legal, and ethical use of digital tools and protect personal data and student privacy."
        }
        for name, text in iste_coaches_data.items():
            with st.expander(name):
                st.write(text)
                
    else:
        st.markdown("### 📘 InTASC Model Core Teaching Standards")
        st.write("*Developed by the Interstate Teacher Assessment and Support Consortium (InTASC)*")
        intasc_data = {
            "Standard #1: Learner Development": "The teacher understands how learners grow and develop, designing and implementing developmentally appropriate and challenging learning experiences.",
            "Standard #2: Learning Differences": "The teacher uses understanding of individual differences and diverse cultures to ensure inclusive learning environments.",
            "Standard #3: Learning Environments": "The teacher works with others to create environments that support individual and collaborative learning.",
            "Standard #4: Content Knowledge": "The teacher understands central concepts and structures of the discipline, making the content accessible and meaningful.",
            "Standard #5: Application of Content": "The teacher connects concepts to engage learners in critical thinking, creativity, and collaborative problem-solving.",
            "Standard #6: Assessment": "The teacher understands and uses multiple methods of assessment to monitor learner progress and guide decision-making.",
            "Standard #7: Planning for Instruction": "The teacher plans instruction that supports every student in meeting rigorous learning goals based on curriculum, pedagogy, and context.",
            "Standard #8: Instructional Strategies": "The teacher understands and uses a variety of instructional strategies to develop deep understanding.",
            "Standard #9: Professional Learning and Ethical Practice": "The teacher engages in ongoing professional learning, evaluating practice and choices on others (students, families, and community).",
            "Standard #10: Collaboration and Leadership": "The teacher collaborates with learners, families, colleagues, and community members to ensure growth."
        }
        for name, text in intasc_data.items():
            with st.expander(name):
                st.write(text)

# ==========================================
# TAB 4: CROWD-SOURCED SCENARIO BANK
# ==========================================
with tab_crowd:
    st.markdown("<div class='card-title'>📥 Crowdsourced Scenario Builder: Learning from Experience</div>", unsafe_allow_html=True)
    st.write(
        "Enrich our workshop training by sharing real-world dilemmas you have personally navigated. "
        "Our AI engine will securely anonymize all personal data (removing teacher/school names) and "
        "transform your lived experience into an interactive, standards-aligned practice case study "
        "for your peers to solve!"
    )
    
    crowd_role = st.selectbox("Role Involved in the Incident", ["Classroom Teacher", "School Principal", "District Superintendent", "Instructional Coach"], key="crowd_role_key")
    crowd_standards = st.multiselect("Primary Standards Violated or Involved", [
        "InTASC Standards (Teaching Practice)",
        "NELP Building Standards (Leadership)",
        "ISTE Standards (Tech & Coaching)"
    ], default=["InTASC Standards (Teaching Practice)"], key="crowd_std_key")
    
    raw_event = st.text_area(
        "Describe the actual real-world event in your own words (e.g. 'Last year a 5th grade teacher took a photo of a student's project and posted it to her personal Facebook with the kid's face visible. The dad got super mad because of custody issues.'):",
        placeholder="Type or paste the raw details of the real event. Keep it candid—the AI will clean and sanitize all names and identifiers.",
        height=150,
        key="raw_event_key"
    )
    
    crowd_btn = st.button("🔒 Anonymize & Engineer Practice Case", key="crowd_btn_key")
    
    if crowd_btn:
        if not raw_event:
            st.warning("Please describe the real-world event before submitting.")
        elif not api_key:
            st.warning("⚠️ Enter a Gemini API Key in the sidebar to activate the live Crowdsourced Generator.")
        else:
            with st.spinner("🔒 Sanitizing and engineering interactive case study..."):
                system_instruction_crowd = (
                    "You are an expert professor of education and professional case study writer.\n"
                    "Your job is to take a raw, unstructured real-world incident and:\n"
                    "1. SCRUB all personal identifiable information (PII) including real names, cities, schools, and districts. Replace them with realistic but generalized descriptors.\n"
                    "2. Polish the narrative into an engaging, 2-3 paragraph professional case study.\n"
                    "3. Align the case study with national educational standards (InTASC, NELP, or ISTE).\n"
                    "4. Generate exactly TWO challenging multiple-choice questions (Checkpoints) with 4 options each (A, B, C, D) and detailed, high-pedagogy feedback explaining why every single option is correct or incorrect based on professional ethics and standards.\n"
                    "You must respond ONLY with a valid JSON object with this exact structure:\n"
                    "{\n"
                    "  \"title\": \"A short, catchy case title (e.g., 'The Social Media Boundary Slip')\",\n"
                    "  \"audience\": \"Target audience\",\n"
                    "  \"focus\": \"Standards alignment summary\",\n"
                    "  \"scenario\": \"The polished, fully anonymized 2-3 paragraph narrative study.\",\n"
                    "  \"difficulty\": \"High\",\n"
                    "  \"questions\": [\n"
                    "    {\n"
                    "      \"question\": \"Question text for checkpoint 1\",\n"
                    "      \"choices\": [\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"],\n"
                    "      \"feedbacks\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}\n"
                    "    },\n"
                    "    {\n"
                    "      \"question\": \"Question text for checkpoint 2\",\n"
                    "      \"choices\": [\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"],\n"
                    "      \"feedbacks\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}\n"
                    "    }\n"
                    "  ]\n"
                    "}"
                )
                prompt_crowd = f"Raw Event Story: {raw_event}\nTarget Role: {crowd_role}\nStandards Base: {', '.join(crowd_standards)}\n"
                
                text_crowd_out = query_gemini(api_key, prompt_crowd, system_instruction_crowd, json_mode_val=True)
                data_crowd_parsed = parse_json_safely(text_crowd_out)
                
                if data_crowd_parsed:
                    case_title = data_crowd_parsed.get("title", "Submitted Case")
                    st.session_state.crowdsourced_scenarios[case_title] = data_crowd_parsed
                    st.success(f"🎉 Success! Real-world event securely anonymized and added to the **Crowdsourced Session Bank** as **'{case_title}'**!")
                    st.balloons()
                    
                    st.markdown("### 👁️ Preview of Your Engineered Case Study")
                    st.markdown(f"**Title:** `{case_title}`")
                    st.markdown(f"**Audience:** `{data_crowd_parsed.get('audience')}` | **Focus:** `{data_crowd_parsed.get('focus')}`")
                    st.write(data_crowd_parsed.get("scenario"))
                    
                    # Show JSON representation so they can copy/save it
                    st.markdown("---")
                    st.markdown("#### 📥 Shareable Case JSON")
                    st.write("You can copy this JSON to share with your workshop facilitator or import into other classes:")
                    st.json(data_crowd_parsed)
                else:
                    st.error("Failed to parse the crowdsourced case. Please check your API key or description and try again.")
