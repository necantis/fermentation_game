import streamlit as st
import pandas as pd
from game_logic import GameState, SCENARIO_DATA, ACTIONS, AI_ASSESSMENTS, STARTING_SCENARIO_ID
from ui_components import render_dashboard
from data_manager import log_data, log_feedback
import time

# Page Config
st.set_page_config(layout="wide", page_title="Fermentation Game")

# CSS for Layout
st.markdown("""
<style>
    .main-header { font-size: 2rem; color: #003366; }
    .stButton button { width: 100%; }
    .ai-box { background-color: #eef7ff; padding: 15px; border-radius: 5px; border: 1px solid #b3d7ff; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'game_state' not in st.session_state:
    st.session_state.game_state = None  # Will be GameState object
if 'prolific_id' not in st.session_state:
    st.session_state.prolific_id = ""
if 'page' not in st.session_state:
    st.session_state.page = 'LOGIN'  # LOGIN, TUTORIAL, GAME, END
if 'ai_visible' not in st.session_state:
    st.session_state.ai_visible = False
if 'user_assessment' not in st.session_state:
    st.session_state.user_assessment = ""
if 'last_assessment_before_ai' not in st.session_state:
    st.session_state.last_assessment_before_ai = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'end_time' not in st.session_state:
    st.session_state.end_time = None
if 'round_start_time' not in st.session_state:
    st.session_state.round_start_time = None

# --- NAV FUNCTIONS ---
def start_tutorial():
    if not st.session_state.prolific_id:
        st.error("Please enter your Prolific ID.")
        return
    st.session_state.game_state = GameState('TUTORIAL')
    st.session_state.game_state.current_scenario_id = 1 # Start good for tutorial
    st.session_state.game_state.seed_sensor_history(1)
    st.session_state.page = 'TUTORIAL'
    st.session_state.ai_visible = False
    st.session_state.user_assessment = ""
    st.session_state.tutorial_start_time = time.time() # Capture Tutorial Start Time

def start_game():
    st.session_state.game_state = GameState('GAME')
    st.session_state.game_state.current_scenario_id = STARTING_SCENARIO_ID
    st.session_state.game_state.seed_sensor_history(STARTING_SCENARIO_ID)
    st.session_state.page = 'GAME'
    st.session_state.ai_visible = False
    st.session_state.user_assessment = ""
    st.session_state.game_state.round_number = 1
    st.session_state.round_start_time = time.time() # Start Round 1 Timer

def next_round():
    gs = st.session_state.game_state
    
    # 1. Capture Inputs
    assessment = st.session_state.user_assessment
    action_key = st.session_state.get(f"action_{gs.round_number}", None)
    seq_score = st.session_state.get(f"seq_{gs.round_number}", None)
    
    # Calculate Round Duration
    round_duration = 0
    if st.session_state.round_start_time:
        round_duration = round(time.time() - st.session_state.round_start_time, 2)
    
    if not action_key or not seq_score or not assessment.strip():
        st.error("Please fill in Assessment, select an Action, and rate Difficulty.")
        return

    # 2. Logic: Text Changed?
    text_changed = False
    if st.session_state.ai_visible:
        # Check if text is different from what it was *right before* clicking AI?
        # Or just different from empty? 
        # Using simple heuristic: if AI was used, check if current text != text saved when AI button clicked
        # Note: We need to capture text *at moment* of AI click for robust diff.
        # Implementation: When AI button clicked, save `last_assessment_before_ai`
        if assessment != st.session_state.last_assessment_before_ai:
            text_changed = True

    # 3. Log Data
    log_entry = {
        'prolific_id': st.session_state.prolific_id,
        'round': gs.round_number,
        'batch_num': len(gs.sensor_history['sg']),
        'scenario_id': gs.current_scenario_id,
        'scenario_name': SCENARIO_DATA[gs.current_scenario_id]['name'],
        'assessment': assessment,
        'action': ACTIONS[action_key]['text'],
        'seq_score': seq_score,
        'ai_used': st.session_state.ai_visible,
        'text_changed': text_changed,
        'ai_assessment_text': AI_ASSESSMENTS.get(gs.current_scenario_id, ""),
        'user_assessment_final': assessment,
        'tutorial_duration_seconds': st.session_state.get('tutorial_duration_seconds', 0),
        'round_duration_seconds': round_duration
    }
    log_data(log_entry)

    # 4. Update Game State
    next_id = gs.determine_next_state(gs.current_scenario_id, action_key)
    
    if next_id == 1: # Win Condition
        st.session_state.end_time = time.time() # Stop Timer
        
        # Log the final state (Success State)
        log_entry_final = {
            'prolific_id': st.session_state.prolific_id,
            'round': gs.round_number + 1, # It would be the next round
            'batch_num': len(gs.sensor_history['sg']),
            'scenario_id': 1,
            'scenario_name': SCENARIO_DATA[1]['name'],
            'assessment': "Simulation Complete",
            'action': "None",
            'seq_score': 0,
            'ai_used': False,
            'text_changed': False,
            'ai_assessment_text': AI_ASSESSMENTS.get(1, ""),
            'user_assessment_final': "COMPLETED",
            'user_assessment_final': "COMPLETED",
            'tutorial_duration_seconds': st.session_state.get('tutorial_duration_seconds', 0),
            'round_duration_seconds': round_duration
        }
        log_data(log_entry_final)
        
        st.session_state.page = 'END'
    else:
        gs.current_scenario_id = next_id
        gs.round_number += 1
        gs.update_sensor_history()
        # Reset ephemeral inputs
        st.session_state.ai_visible = False
        st.session_state.user_assessment = ""
        # Rerun to refresh UI - NOT NEEDED IN CALLBACK
        # st.rerun() 
        
        # Reset Round Timer for next round
        st.session_state.round_start_time = time.time()

# --- PAGES ---

def render_login():
    st.title("Fermentation Troubleshooting Game")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Welcome!
        Your goal is to fix fermentation issues.
        1. Analyze **Graphs** (Left).
        2. Write **Assessment** (Middle).
        3. Choose **Action**.
        4. (Optional) Check **AI** (Right).
        """)
    
    with col2:
        st.markdown("### Get Started")
        st.session_state.prolific_id = st.text_input("Enter your Prolific ID:", value=st.session_state.prolific_id)
        if st.button("Start Tutorial"):
            if not st.session_state.prolific_id:
                st.error("Please enter your Prolific ID.")
                return
            start_tutorial()
            st.rerun()

def render_tutorial():
    gs = st.session_state.game_state
    st.header("Tutorial")
    
    # Step 1 is now merged into Login/Start, so we start essentially at old Step 2 logic
    # but we keep step numbering internal
    
    if gs.step == 1:
        # Just a redirect incase
        gs.step = 2
        st.rerun()
            
    elif gs.step == 2:
        # Scenario 1: All Good
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            render_dashboard(gs)
        with col2:
            st.info("Tutorial: Look at the graphs. Everything looks stable. Write 'All Good' below.")
            val = st.text_area("Your assessment:", key="tut_2_text")
            if st.button("Continue"):
                if "good" in val.lower():
                    gs.step = 3
                    gs.current_scenario_id = 5 
                    gs.seed_sensor_history(5)
                    st.rerun()
                else:
                    st.error("Please write 'All Good'.")
                    
    elif gs.step == 3:
        # Scenario 5: Sanitation Fail - USER TRY (No AI)
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            render_dashboard(gs)
        with col2:
            st.info("Tutorial: Something is wrong. Look at the graphs.")
            st.write("**What do you think is happening?**")
            st.session_state.user_assessment = st.text_area("Your assessment:", value=st.session_state.user_assessment, key="tut_3_text")
            
            st.write("**Select an action:**")
            act = st.radio("Select Action:", list(ACTIONS.keys()), format_func=lambda x: ACTIONS[x]['text'], key="tut_action")
            
            
            # st.markdown("**Rate Difficulty (1=Easy, 7=Hard)**")
            # st.caption("How hard was it to identify this issue?")
            # st.slider("Difficulty", 1, 7, 4, key="tut_diff")

            if st.button("I have a hypothesis! Double check with AI"):
                if len(st.session_state.user_assessment.strip()) < 3:
                    st.error("Please write something first.")
                else:
                    gs.step = 4
                    st.rerun()

    elif gs.step == 4:
        # Scenario 5: Sanitation Fail - AI INTRO
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            render_dashboard(gs)
            
        with col3:
            st.markdown("### AI Assistant")
            st.info("The AI button is now active. Check your analysis.")
            st.caption("AI use is optional in the game, but helpful for double-checking.")
            
            if st.button("Activate AI Analysis"):
                st.session_state.ai_visible = True
            
            # Persist AI visibility across reruns during this step
            if st.session_state.get('ai_visible', False):
                ai_analysis = "pH: Significant, continuous drop (souring). SG: Dropped too low. CO2: Low activity. Hints at bacterial contamination."
                ai_rec = "Sterilize Equipment"
                
                st.markdown(f"**Analysis:** {ai_analysis}")
                st.success(f"**Recommendation:** {ai_rec}")
                
                def copy_ai_rec():
                    # Update session state logic without rerun
                    current_text = st.session_state.tut_4_text if 'tut_4_text' in st.session_state else st.session_state.user_assessment
                    if "AI:" not in current_text:
                         new_text = f"{current_text}\n\nAI: {ai_analysis}\nRec: {ai_rec}"
                         st.session_state.user_assessment = new_text
                         st.session_state.tut_4_text = new_text # FORCE UPDATE WIDGET KEY
                
                st.button("Copy Analysis to Text", on_click=copy_ai_rec)

        with col2:
            st.markdown("**Complete the round**")
            # FIX: Initialize key if needed, remove value arg to avoid warning
            if 'tut_4_text' not in st.session_state:
                st.session_state.tut_4_text = st.session_state.user_assessment
            
            # Widget drives the state via key
            st.text_area("Your assessment:", key="tut_4_text")
            # Sync back to user_assessment for consistency
            st.session_state.user_assessment = st.session_state.tut_4_text
            
            # Show the correctly selected action from previous step
            act_key = st.session_state.get('tut_action', list(ACTIONS.keys())[0])
            act_idx = list(ACTIONS.keys()).index(act_key) if act_key in ACTIONS else 0

            act = st.radio("Select Action:", list(ACTIONS.keys()), 
                          format_func=lambda x: ACTIONS[x]['text'], 
                          key="tut_action_final",
                          index=act_idx)
            
            if st.button("Continue"):
                if act != 'sterilize':
                    st.error("Incorrect. The AI recommended 'Sterilize Equipment'.")
                else:
                    gs.step = 5
                    st.rerun()

    elif gs.step == 5:
        # Step 5: Difficulty Assessment
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
             render_dashboard(gs)
        with col2:
            st.subheader("Final Step: Rate Difficulty")
            st.info("In the real game, you will rate the difficulty of each round.")
            
            st.markdown("**Rate Difficulty (1=Easy, 7=Hard)**")
            st.caption("How hard was it to identify this issue?")
            st.slider("Difficulty", 1, 7, 4, key="tut_diff")
            
            if st.button("Finish Tutorial"):
                 # Calculate Tutorial Duration
                 if 'tutorial_start_time' in st.session_state:
                     st.session_state.tutorial_duration_seconds = round(time.time() - st.session_state.tutorial_start_time, 2)
                 
                 st.session_state.start_time = time.time() # Start Game Timer
                 start_game()
                 st.rerun()

def render_game():
    gs = st.session_state.game_state
    
    st.subheader(f"Round {gs.round_number}")
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    
    # Left: Dashboard
    with col1:
        render_dashboard(gs)
        
    # Middle: Interaction
    with col2:
        st.markdown("**1. Assessment**")
        
        # Callback to enable AI button check (simulated by just having text)
        def on_text_change():
            pass 

        st.session_state.user_assessment = st.text_area(
            "What is happening?", 
            value=st.session_state.user_assessment,
            height=100
        )
        
        st.markdown("**2. Action**")
        action_key = st.radio(
            "corrective_action", 
            list(ACTIONS.keys()), 
            format_func=lambda x: ACTIONS[x]['text'],
            key=f"action_{gs.round_number}",
            label_visibility="collapsed"
        )
        
        st.markdown("**3. Difficulty (1=Easy, 7=Hard)**")
        st.slider("Difficulty", 1, 7, 4, key=f"seq_{gs.round_number}")
        
        st.markdown("---")
        st.markdown("---")
        
        # Use callback to avoid double-click issue (state update vs rerun timing)
        st.button("Submit & Next Round", type="primary", on_click=next_round)

    # Right: AI
    with col3:
        # Only enable if text is entered (Streamlit refreshes on interaction so we can check state)
        disabled_ai = len(st.session_state.user_assessment.strip()) < 5
        
        if st.button("See AI Analysis", disabled=disabled_ai, use_container_width=True):
            st.session_state.ai_visible = not st.session_state.ai_visible
            if st.session_state.ai_visible:
                # Store text at moment of reveal
                st.session_state.last_assessment_before_ai = st.session_state.user_assessment
        
        if st.session_state.ai_visible:
            st.markdown("### AI Analysis")
            ai_text = AI_ASSESSMENTS.get(gs.current_scenario_id, "No analysis available.")
            current_causes = SCENARIO_DATA[gs.current_scenario_id]['causes']
            rec_actions = [ACTIONS[k]['text'] for k, v in ACTIONS.items() if v['fixes'] in current_causes]
            rec_text = "; ".join(rec_actions) if rec_actions else "No action needed."
            
            st.info(f"**Analysis:** {ai_text}")
            st.success(f"**Recommendation:** {rec_text}")
            
            # Copy buttons (Simulated copy by appending to text area? 
            # Streamlit can't easily clipboardwrite without components, 
            # but we can provide a button that updates session_state.user_assessment)
            if st.button("Copy Recommendation to Text"):
                st.session_state.user_assessment += f"\n\nAI: {ai_text}\nRec: {rec_text}"
                st.rerun()

def render_end():
    st.balloons()
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>Congratulations!</h1>
        <p>You have successfully stabilized the fermentation process.</p>
        <h2>Exit Code: <span style="color: green;">CAEU04L5</span></h2>
        <p>Please enter this code in Prolific to complete your submission.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.get("feedback_submitted", False):
         st.success("Thank you for your feedback! The game is now complete.")
         st.info("You may close this tab.")
    else:
        st.subheader("Optional Feedback")
        st.write("If you have any comments about the game, please share them below.")
        
        with st.form("feedback_form"):
            feedback_text = st.text_area("Your Feedback:", placeholder="Was it difficult? Did you understand the AI?")
            if st.form_submit_button("Submit Feedback"):
                total_time = 0
                if st.session_state.start_time and st.session_state.end_time:
                    total_time = st.session_state.end_time - st.session_state.start_time
                    
                success = log_feedback({
                    'prolific_id': st.session_state.prolific_id,
                    'total_time_seconds': round(total_time, 2),
                    'tutorial_duration_seconds': st.session_state.get('tutorial_duration_seconds', 0),
                    'feedback_text': feedback_text
                })
                
                # Always hide form after submission attempt
                st.session_state.feedback_submitted = True
                
                if success:
                    st.success("Thank you for your feedback!")
                else:
                    st.warning("Feedback saved locally (Cloud sync failed).")
                
                # Rerun to update UI (hide form)
                st.rerun()


# --- MAIN ---
if st.session_state.page == 'LOGIN':
    render_login()
elif st.session_state.page == 'TUTORIAL':
    render_tutorial()
elif st.session_state.page == 'GAME':
    render_game()
elif st.session_state.page == 'END':
    render_end()
