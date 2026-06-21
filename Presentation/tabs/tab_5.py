import streamlit as st
from Presentation.config import COLOR_PALETTE

def render_tab_5(df, df_feedback):
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 24px; margin-bottom: 25px; border-left: 4px solid {COLOR_PALETTE['secondary']};">
            <span style="font-size: 0.85rem; letter-spacing: 0.15em; color: {COLOR_PALETTE['secondary']}; font-weight: 600; text-transform: uppercase;">
                Theoretical Contribution & Conclusions
            </span>
            <h2 style="margin-top: 5px; font-weight: 700; font-size: 2.2rem;">
                Discussion & Concluding Framework
            </h2>
            <p style="color: {COLOR_PALETTE['text_muted']}; font-size: 1.05rem; margin-top: 5px; max-width: 950px; line-height: 1.6;">
                We extend standard organizational frameworks by proving that the capability frontier is dynamic and dependent on behavioral architecture, 
                demonstrating a trace-measurable metabolic control loop.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Pushing the Boundaries of Organization Science
    st.markdown("### 1. Pushing the Boundaries of Organization Science")
    
    col_os1, col_os2 = st.columns(2)
    with col_os1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['primary']};">
                <h4 style="color: {COLOR_PALETTE['primary']}; font-weight: 600;">From Task Placement to Process Intervention</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    The <i>Organization Science</i> article treats the jagged capability frontier as fixed based on the task type 
                    (e.g., brand strategy is outside, shoe ideation is inside). Our CFF "write-before-checking" test proves 
                    that the frontier is highly dynamic and dependent on <b>behavioral architecture</b>. 
                    By modifying the interaction interface, organizations can turn a negative performance drop into an active learning process.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_os2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-top: 3px solid {COLOR_PALETTE['secondary']};">
                <h4 style="color: {COLOR_PALETTE['secondary']}; font-weight: 600;">Granular Trace-Mapping of Delegation States</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    While traditional macro studies rely on total timing outcomes, we utilize Baird & Maruping's (2021) 
                    framework to track real-time trace transitions. By analyzing text similarity metrics and duration variations dynamically, 
                    we trace exactly when a user shifts from <b>Appraisal</b> (building trust) to <b>Distribution</b> (lazy hand-off) 
                    and <b>Coordination</b> (active auditing).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Improving the Metabolic Framework (Xylem vs Phloem corporate strategy translation)
    st.markdown("### 2. The Trace-Measurable Metabolic Architecture Framework")
    st.markdown(
        "Integrating these elements refines our core model—the trace-measurable metabolic architecture that balances "
        "structural viscosity with localized environmental inputs. To translate the botanical metaphors into corporate strategy terms:"
    )

    # ASCII metabolic loop
    st.markdown(
        f"""
        <pre style="font-family: monospace; font-size: 0.9rem; line-height: 1.4; color: {COLOR_PALETTE['primary']}; background: rgba(0,0,0,0.25); padding: 15px; border-radius: 8px; border: 1px solid {COLOR_PALETTE['grid']}; overflow-x: auto;">
                            METABOLIC ACCELERATION LOOP
                            
      [Xylem Friction] ───► [Write-First Filter] ───► [Phloem Governance]
       (Raw Local Influx)    (Engineered Viscosity)    (AI Strategic Push)
                ▲                                               │
                └─────────────────── [Improver State] ──────────┘
                             (Optimal Metabolic Exchange)
        </pre>
        """,
        unsafe_allow_html=True
    )

    col_met_1, col_met_2 = st.columns(2)
    
    with col_met_1:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: {COLOR_PALETTE['success']}; font-weight: 600;">Xylem (Solid Wood) ──► Formal Structure</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    The localized environmental input (Xylem) represents raw, unstructured frontline data. 
                    If a user checks the AI immediately and follows its routines, the Phloem instantly overwrites local human variance. 
                    The "write-first" protocol acts as a xylem filter, <b>protecting local human data inputs</b> in the formal structure 
                    before they are homogenized by the machine.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_met_2:
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: {COLOR_PALETTE['warning']}; font-weight: 600;">Phloem (Viscous Bark) ──► Relational Structure</h4>
                <p style="font-size: 0.95rem; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                    The AI's strategic push (Phloem) operates within the relational structure of the firm, pushing information dynamically. 
                    <b>Engineered Structural Viscosity:</b> The "write-first" step is the literal design implementation of beneficial structural viscosity. 
                    It purposefully slows down the information routing system, driving up perceived difficulty (H3) and coordination costs, 
                    which keeps the firm operating safely on the calculated Efficient Frontier (y = 1 + x²₁).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="glass-card" style="margin-top: 15px;">
            <p style="margin: 0; line-height: 1.6; color: {COLOR_PALETTE['text']};">
                <b>Trace-Measurable Metabolic Control:</b> By tracking real-time dashboard metrics—such as answer length, complexity, and semantic similarity—our 
                architecture can programmatically flag when a node is slipping into passive copying (inducing structural liquefaction) versus active improving. 
                This allows the organization to tune its internal constraints dynamically based on live trace data.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Conclusion (Toulmin Framework)
    st.markdown("---")
    st.markdown("### 3. Conclusion (Toulmin Validation Framework)")
    st.markdown("To provide rigorous validation, we formalize our thesis using the Toulmin framework of argumentation:")

    toulmin_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['primary']};">
            <h5 style="color: {COLOR_PALETTE['primary']}; font-weight: 600; margin: 0 0 5px 0;">Claim</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                Maximizing productivity in human-AI systems requires organizations to discard linear speed assumptions and design interactive workflows that enforce structural viscosity through cognitive forcing functions.
            </p>
        </div>
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['success']};">
            <h5 style="color: {COLOR_PALETTE['success']}; font-weight: 600; margin: 0 0 5px 0;">Data</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                Empirical data shows unchecked AI access causes severe automation bias outside the frontier. Meanwhile, our CFF test proves "write-before-AI" expands output length (from 11.29 to 122.38 chars) and shatters the "Efficiency Illusion" by realigning effort with perceived difficulty (4.65 vs 3.78).
            </p>
        </div>
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['warning']};">
            <h5 style="color: {COLOR_PALETTE['warning']}; font-weight: 600; margin: 0 0 5px 0;">Warrant</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                Forcing human formulation prior to machine exposure blocks passive cognitive offloading, compelling users to execute independent analytical synthesis before initiating the "read-verify-decide" coordination loop.
            </p>
        </div>
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['secondary']};">
            <h5 style="color: {COLOR_PALETTE['secondary']}; font-weight: 600; margin: 0 0 5px 0;">Backing</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                Information Processing Theory and delegation frameworks (Baird & Maruping, 2021) demonstrate that agentic artifacts introduce hidden communication and monitoring taxes that bottleneck human cognitive processing if left unmanaged.
            </p>
        </div>
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['no_ai']};">
            <h5 style="color: {COLOR_PALETTE['no_ai']}; font-weight: 600; margin: 0 0 5px 0;">Rebuttal</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                While traditional frameworks suggest that any latency or subjective task difficulty is inefficient, our trace-based analytics prove that this calculated viscosity prevents decoupling and protects local human nodes from total structural liquefaction.
            </p>
        </div>
        <div class="glass-card" style="border-left: 4px solid {COLOR_PALETTE['text_muted']};">
            <h5 style="color: {COLOR_PALETTE['text_muted']}; font-weight: 600; margin: 0 0 5px 0;">Qualifier</h5>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                Consequently, this behavioral orchestration applies specifically to knowledge-intensive, high-stakes professional workflows where preserving human judgment and raw sensory data integrity takes priority over pure execution speed.
            </p>
        </div>
    </div>
    """
    st.markdown(toulmin_html, unsafe_allow_html=True)
