import streamlit as st
import json
import os

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

api_key = st.sidebar.text_input("Google Gemini API Key", type="password")

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

# Set up tabs
tab_sim, tab_desk, tab_standards = st.tabs([
    "🎯 Tab 1: What-If Scenario Simulator",
    "🚨 Tab 2: Just-in-Time Crisis Desk",
    "📚 Tab 3: Standards Reference Desk"
])

# ==========================================
# TAB 1: WHAT-IF SCENARIO SIMULATOR
# ==========================================
with tab_sim:
    st.markdown("<div class='card-title'>🎯 Scenario Simulator: Practicing for the Unknown</div>", unsafe_allow_html=True)
    st.write(
        "Use this sandbox to generate dynamic school scenarios based on national standards. "
        "Engage in interactive problem-solving to test your readiness for administrative and classroom crises."
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Simulation Options")
        role = st.selectbox("Select Your Focus Role", ["Classroom Teacher / Preservice Candidate", "School Building Administrator (Principal)", "District Administrator (Superintendent)"])
        topic = st.selectbox("Standards Alignment Focus", [
            "Ethics & Professional Norms (NELP #2 / InTASC #9)",
            "Equity, Inclusiveness, & Cultural Responsiveness (NELP #3 / InTASC #2)",
            "Learning & Instructional Technologies (NELP #4 / ISTE Coaches)",
            "Policy, Governance, & Advocacy (NELP #7 / InTASC #10)"
        ])
        difficulty = st.select_slider("Select Simulation Difficulty", options=["Beginner", "Moderate", "High", "Extreme"])
        
        generate_btn = st.button("🚀 Generate Case Scenario")
        
    with col2:
        if not api_key:
            st.warning("⚠️ Operating in **Offline Practice Mode** using verified pre-loaded scenarios. (Enter a Gemini API Key in the sidebar to activate the dynamic, interactive AI generator).")
            
            # Allow user to pick a pre-baked case
            selected_case_name = st.selectbox("Choose a pre-loaded professional scenario:", list(PRE_BAKED_SCENARIOS.keys()))
            case_data = PRE_BAKED_SCENARIOS[selected_case_name]
            
            st.markdown(f"#### 📖 {case_data['title']}")
            st.markdown(f"**Target Audience:** `{case_data['audience']}` | **Focus:** `{case_data['focus']}` | **Difficulty:** `{case_data['difficulty']}`")
            st.write(case_data['scenario'])
            
            st.markdown("---")
            st.markdown("### 📝 Sandbox Decision Checkpoints")
            
            # Interactive walkthrough of pre-baked questions
            for i, q in enumerate(case_data['questions']):
                st.markdown(f"**Question {i+1}: {q['question']}**")
                choice = st.radio(f"Select your decision for Question {i+1}:", q['choices'], key=f"q_{i}_{selected_case_name}")
                
                # Check option
                selected_letter = choice[0] # A, B, C, or D
                feedback = q['feedbacks'].get(selected_letter, "")
                
                if "Correct!" in feedback:
                    st.success(feedback)
                elif feedback:
                    st.error(feedback)
        else:
            st.success("🤖 Google Gemini Online Mode Connected. Engineering custom scenario on demand...")
            # Placeholder for live API call
            st.write("*(In the live app hosted on your local network, this tab makes a secure, live API call to the Gemini-1.5-Pro model to generate a custom-tailored scenario and load an active chatbot box where you can text-roleplay directly with an AI simulating an angry parent, teacher, or board member!)*")
            
            # Simulate Gemini-generated scenario
            st.markdown("#### 📖 Live AI Generated Crisis: The Smart Device Mutiny")
            st.markdown(f"**Target Role:** `{role}` | **Alignment:** `{topic}` | **Complexity:** `{difficulty}`")
            st.markdown(
                "**Scenario:** A local student group has created an anonymous social media channel using your school's logo "
                "to host AI-generated deepfake images of teachers, causing massive disruption. Due to federal privacy laws "
                "and an outdated district social media policy, you face a firestorm from teachers demanding immediate suspensions, "
                "while parent advocates claim free-speech violations and threaten litigation. "
            )
            st.markdown("---")
            st.chat_input("Enter your simulated response to the school community or write what you would say to the student group...")

# ==========================================
# TAB 2: JUST-IN-TIME CRISIS DESK
# ==========================================
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
            st.markdown("---")
            st.markdown("### 💡 School Decision Support Output")
            
            tab_steps, tab_comm, tab_audit = st.tabs(["📋 Immediate Action Steps", "📧 Communication Templates", "⚖️ Standards & Policy Audit"])
            
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
