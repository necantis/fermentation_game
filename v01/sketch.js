// =========================================================================
// === DATA: Scenarios, AI Text, Actions ===================================
// =========================================================================
const SCENARIO_DATA = { 1: { name: '1: All Good', causes: [], sg: 1.025, wortTemp: 20, co2Activity: 20, ph: 4.5 }, 2: { name: '2: Temp Control Fail', causes: ['C1'], sg: 1.018, wortTemp: 25.5, co2Activity: 40, ph: 4.6 }, 3: { name: '3: Yeast Health Issue', causes: ['C2'], sg: 1.045, wortTemp: 19.0, co2Activity: 3, ph: 5.0 }, 4: { name: '4: Oxygen Exposure', causes: ['C3'], sg: 1.018, wortTemp: 21.0, co2Activity: 35, ph: 4.4 }, 5: { name: '5: Sanitation Fail', causes: ['C4'], sg: 1.008, wortTemp: 19.5, co2Activity: 7, ph: 3.2 }, 6: { name: '6: Temp & Yeast', causes: ['C1', 'C2'], sg: 1.050, wortTemp: 25.5, co2Activity: 1, ph: 5.0 }, 7: { name: '7: Temp & Oxygen', causes: ['C1', 'C3'], sg: 1.022, wortTemp: 25.5, co2Activity: 45, ph: 4.7 }, 8: { name: '8: Temp & Sanitation', causes: ['C1', 'C4'], sg: 1.002, wortTemp: 26.0, co2Activity: 20, ph: 2.8 }, 9: { name: '9: Yeast & Oxygen', causes: ['C2', 'C3'], sg: 1.048, wortTemp: 19.0, co2Activity: 2, ph: 5.1 }, 10: { name: '10: Yeast & Sanitation', causes: ['C2', 'C4'], sg: 1.010, wortTemp: 19.5, co2Activity: 4, ph: 3.5 }, 12: { name: '12: Oxygen & Sanitation', causes: ['C3', 'C4'], sg: 1.005, wortTemp: 19.5, co2Activity: 10, ph: 3.0 }, 13: { name: '13: Temp, Yeast, Oxygen', causes: ['C1', 'C2', 'C3'], sg: 1.048, wortTemp: 25.5, co2Activity: 1, ph: 5.1 }, 14: { name: '14: Temp, Yeast, Sanitation', causes: ['C1', 'C2', 'C4'], sg: 1.008, wortTemp: 26.0, co2Activity: 5, ph: 3.0 }, 15: { name: '15: Temp, Oxygen, Sanitation', causes: ['C1', 'C3', 'C4'], sg: 1.001, wortTemp: 26.5, co2Activity: 15, ph: 2.7 }, 16: { name: '16: All Together', causes: ['C1', 'C2', 'C3', 'C4'], sg: 1.040, wortTemp: 26.0, co2Activity: 2, ph: 3.5 },};
const ACTIONS = { 'fix_temp': { text: 'Fix Temperature Controller', fixes: 'C1' }, 'pitch_yeast': { text: 'Pitch New/Healthy Yeast', fixes: 'C2' }, 'manage_oxygen': { text: 'Improve Oxygen Management', fixes: 'C3' }, 'sterilize': { text: 'Sterilize Equipment', fixes: 'C4' }};
const SENSOR_DEFS = { sg: { label: 'SG', unit: '', min: 0.990, max: 1.060 }, wortTemp: { label: 'Wort Temp', unit: '°C', min: 10, max: 30 }, co2Activity: { label: 'CO2 Activity', unit: 'b/min', min: 0, max: 50 }, ph: { label: 'pH', unit: '', min: 3.0, max: 6.0 }};
const AI_ASSESSMENTS = { 1: "All sensors report normal readings within their ideal fermentation ranges. The process appears stable and healthy.", 5: "pH: Significant, continuous drop, reaching unusually low levels (souring). SG: Dropped too low, indicating over-attenuation, likely by a non-yeast microbe. CO2: Low activity, suggesting the primary yeast culture is struggling or outcompeted. This pattern strongly indicates a sanitation failure and bacterial contamination.", 6: "Extremely slow or no SG drop, indicating fermentation is stuck. CO2 activity is almost zero. Wort temp is too high, which stresses the yeast. This combination points to a failure in both temperature control and a severely underperforming or unhealthy yeast pitch." };

// === NEW ===: Added safe operating ranges for graph backgrounds
const SENSOR_RANGES = {
    sg: { normal: [1.020, 1.035] },
    wortTemp: { normal: [19.5, 20.5] },
    co2Activity: { normal: [15, 25] },
    ph: { normal: [4.4, 4.6] }
};

// =========================================================================

const LINE_COLORS = { sg: '#E63946', wortTemp: '#457B9D', co2Activity: '#A8DADC', ph: '#1D3557' };

let gameState = { mode: 'TUTORIAL', step: 1 };
const STARTING_SCENARIO_ID = 6;
let currentScenarioID = null;
let roundNumber = 1; let gameLog = []; let userID = `User_${Date.now()}`; let selectedAction = null;
let sensorHistory = { sg: [], wortTemp: [], co2Activity: [], ph: [] };

// === MODIFIED ===: Layout variables changed for 3-column layout
let PADDING, PANEL_WIDTH, PANEL_Y;
let LEFT_PANEL_X, MID_PANEL_X, RIGHT_PANEL_X;
let mainTitle, roundTitle, rightPanel, userAssessmentEl, aiPanel, aiButton, aiStrategyBox;

// === MODIFIED: Replaced single elements with A/B testing elements ===
let aiAnalysisA_El, aiRecommendationA_El, aiCopyButtonA;
let aiAnalysisB_El, aiRecommendationB_El, aiCopyButtonB;
// === END MOD ===

let currentAIRecommendationText = ''; // To store plain text
let currentAIAnalysisText = ''; // To store plain text analysis
const currentAINoiseText = 'Noise'; // This is constant

let actionContainer, actionButtons = {}, seqContainer, seqRadio, logPanel, logPreviewEl, progressButton, tutorialTextContainer;

function setup() {
    // === MODIFIED ===: Adjusted canvas height for new layout
    createCanvas(windowWidth, 900).style('box-shadow', '0 4px 8px rgba(0,0,0,0.1)');
    angleMode(DEGREES);
    
    calculateLayout();

    // Create ALL UI elements once...
    // === MODIFIED ===: Titles positioned in left column
    mainTitle = createElement('h1', 'Fermentation Troubleshooting Game').position(PADDING, 10);
    tutorialTextContainer = createDiv('').position(PADDING, 80).size(windowWidth - PADDING * 2); // Full width for tutorial
    roundTitle = createElement('h2', '').position(PADDING, 80);
    
    // === SECTION 2: User Panel (Middle) ===
    // === MODIFIED ===: Positioned in Middle Column
    rightPanel = createDiv('').position(MID_PANEL_X, PANEL_Y);
    createElement('h2', 'Your Turn').parent(rightPanel);
    createSpan('1. Write your assessment of the situation:').parent(rightPanel).style('font-weight', 'bold').style('display', 'block').style('margin-top', '20px');
    userAssessmentEl = createElement('textarea').parent(rightPanel).size(PANEL_WIDTH, 100).attribute('placeholder', 'e.g., The temperature is too high...');
    userAssessmentEl.input(checkInputsForAIButton);
    
    createSpan('2. Select your action for the next batch:').parent(rightPanel).style('font-weight', 'bold').style('display', 'block').style('margin-top', '20px');
    actionContainer = createDiv('').parent(rightPanel);
    for (const [key, action] of Object.entries(ACTIONS)) {
        let btn = createButton(action.text).parent(actionContainer).size(PANEL_WIDTH, 35).style('display', 'block').style('margin-bottom', '5px');
        btn.mousePressed(() => {
            selectUserAction(key, btn);
            checkInputsForAIButton(); // Check if AI button can be enabled
        });
        actionButtons[key] = btn;
    }
    createSpan('3. How easy or difficult was this task? (1=Very easy, 7=Very difficult)').parent(rightPanel).style('font-weight', 'bold').style('display', 'block').style('margin-top', '20px');
    seqContainer = createDiv('').parent(rightPanel);
    seqRadio = createRadio().parent(seqContainer).style('display', 'flex').style('width', `${PANEL_WIDTH}px`).style('justify-content', 'space-between');
    for (let i = 1; i <= 7; i++) { seqRadio.option(i); }

    progressButton = createButton('Continue').parent(rightPanel).size(PANEL_WIDTH, 50).style('font-size', '18px').style('background-color', '#28a745').style('color', 'white').style('border', 'none').style('margin-top', '20px');
    
    // === SECTION 3: AI Panel (Right) ===
    // === MODIFIED ===: Positioned in Right Column
    aiPanel = createDiv('').position(RIGHT_PANEL_X, PANEL_Y);
    aiButton = createButton('See AI Analysis & Recommendation').parent(aiPanel).size(PANEL_WIDTH, 40).style('font-size', '16px').style('background-color', '#17a2b8').style('color', 'white').style('border', 'none').mousePressed(toggleAIStrategy);
    aiStrategyBox = createDiv('').parent(aiPanel).size(PANEL_WIDTH, 'auto').style('margin-top', '10px').style('background-color', '#eef7ff').style('border', '1px solid #b3d7ff').style('padding', '15px').style('border-radius', '5px');
    
    // === MODIFIED: Create A/B Testing Layout ===
    
    // --- Block A (Real) ---
    createElement('h3', 'AI Analysis A').parent(aiStrategyBox);
    aiAnalysisA_El = createP('').parent(aiStrategyBox)
        .style('padding', '10px')
        .style('background-color', '#f8f9fa')
        .style('border', '1px solid #ccc')
        .style('border-radius', '4px')
        .style('margin-bottom', '10px')
        .style('min-height', '20px');

    createElement('h3', 'Recommended Action A').parent(aiStrategyBox);
    aiRecommendationA_El = createP('').parent(aiStrategyBox)
        .style('padding', '10px')
        .style('background-color', '#f8f9fa')
        .style('border', '1px solid #ccc')
        .style('border-radius', '4px')
        .style('margin-bottom', '10px')
        .style('min-height', '20px');

    aiCopyButtonA = createButton('Copy AI Analysis A')
        .parent(aiStrategyBox)
        .style('width', `${PANEL_WIDTH - 32}px`) // -32 for padding/border
        .style('min-height', '40px')
        .style('padding', '10px')
        .style('background-color', '#007bff')
        .style('color', 'white')
        .style('border', 'none')
        .style('border-radius', '5px')
        .style('margin-top', '5px')
        .style('cursor', 'pointer');
        
    aiCopyButtonA.mousePressed(() => {
        const combinedText = `${currentAIAnalysisText}\n\nRecommended Action: ${currentAIRecommendationText}`;
        userAssessmentEl.value(combinedText.trim()); 
        checkInputsForAIButton(); // Re-check button states
    });

    // --- Divider ---
    createElement('hr').parent(aiStrategyBox).style('margin', '20px 0');

    // --- Block B (Noise) ---
    createElement('h3', 'AI Analysis B (Noise)').parent(aiStrategyBox);
    aiAnalysisB_El = createP(currentAINoiseText).parent(aiStrategyBox)
        .style('padding', '10px')
        .style('background-color', '#f8f9fa')
        .style('border', '1px solid #ccc')
        .style('border-radius', '4px')
        .style('margin-bottom', '10px')
        .style('min-height', '20px');

    createElement('h3', 'Recommended Action B (Noise)').parent(aiStrategyBox);
    aiRecommendationB_El = createP(currentAINoiseText).parent(aiStrategyBox)
        .style('padding', '10px')
        .style('background-color', '#f8f9fa')
        .style('border', '1px solid #ccc')
        .style('border-radius', '4px')
        .style('margin-bottom', '10px')
        .style('min-height', '20px');

    aiCopyButtonB = createButton('Copy AI Analysis B')
        .parent(aiStrategyBox)
        .style('width', `${PANEL_WIDTH - 32}px`) // -32 for padding/border
        .style('min-height', '40px')
        .style('padding', '10px')
        .style('background-color', '#6c757d') // Grey color
        .style('color', 'white')
        .style('border', 'none')
        .style('border-radius', '5px')
        .style('margin-top', '5px')
        .style('cursor', 'pointer');
        
    aiCopyButtonB.mousePressed(() => {
        const combinedText = `${currentAINoiseText}\n\nRecommended Action: ${currentAINoiseText}`;
        userAssessmentEl.value(combinedText.trim()); 
        checkInputsForAIButton(); // Re-check button states
    });
    // === END MODIFICATION ===
    
    // === Logging Section (at bottom) ===
    // === MODIFIED ===: Positioned at bottom, spans width
    logPanel = createDiv('').position(PADDING, LOG_Y);
    createElement('h2', 'Experiment Log').parent(logPanel);
    const downloadButton = createButton('Download Log (CSV)').parent(logPanel).mousePressed(downloadLog);
    logPreviewEl = createP('Log will appear here...').parent(logPanel).size(windowWidth - PADDING * 2, 100).style('background-color', '#e9ecef').style('padding', '10px').style('overflow-y', 'auto');
    
    updateUIForState();
}

// === NEW ===: Function to calculate all layout variables for 3 columns
function calculateLayout() {
    PADDING = windowWidth * 0.02;
    PANEL_WIDTH = constrain((windowWidth - PADDING * 4) / 3, 300, 500); // Width of one column
    PANEL_Y = 140; // Start Y for all 3 panels

    LEFT_PANEL_X = PADDING;
    MID_PANEL_X = PADDING * 2 + PANEL_WIDTH;
    RIGHT_PANEL_X = PADDING * 3 + PANEL_WIDTH * 2;

    // Graph dimensions (for 1x4 stack in left panel)
    GRAPH_W = PANEL_WIDTH;
    GRAPH_H = 120; // Height of one small graph (Reduced from 150)
    
    // Log Panel (Bottom)
    // Positioned below the tallest potential panel (graphs)
    const graphColumnHeight = (GRAPH_H + PADDING) * 4; // Approx 680px
    LOG_Y = PANEL_Y + graphColumnHeight + PADDING * 2; // Add padding
}


function windowResized() {
    // === MODIFIED ===: Adjusted canvas height
    resizeCanvas(windowWidth, 900);
    calculateLayout();

    // Reposition all elements
    mainTitle.position(PADDING, 10);
    tutorialTextContainer.position(PADDING, 80).size(windowWidth - PADDING * 2);
    roundTitle.position(PADDING, 80);
    
    // Middle Panel
    rightPanel.position(MID_PANEL_X, PANEL_Y).size(PANEL_WIDTH);
    userAssessmentEl.size(PANEL_WIDTH, 100);
    actionContainer.size(PANEL_WIDTH);
    for (const btn of Object.values(actionButtons)) {
        btn.size(PANEL_WIDTH, 35);
    }
    seqContainer.style('width', `${PANEL_WIDTH}px`);
    progressButton.size(PANEL_WIDTH, 50);

    // Right Panel
    aiPanel.position(RIGHT_PANEL_X, PANEL_Y).size(PANEL_WIDTH);
    aiButton.size(PANEL_WIDTH, 40);
    aiStrategyBox.size(PANEL_WIDTH, 'auto');
    // === MODIFIED: Resize new copy buttons ===
    aiCopyButtonA.style('width', `${PANEL_WIDTH - 32}px`);
    aiCopyButtonB.style('width', `${PANEL_WIDTH - 32}px`);
    // === END MODIFICATION ===
    
    // Log Panel
    logPanel.position(PADDING, LOG_Y);
    logPreviewEl.size(windowWidth - PADDING * 2, 100);
}

function draw() {
    background(248);
    // === MODIFIED ===: Call new function to draw 4 graphs
    if (currentScenarioID && gameState.mode !== 'TUTORIAL' || (gameState.mode === 'TUTORIAL' && gameState.step > 1)) {
        drawAllDashboardGraphs();
    }
}

// --- STATE MANAGEMENT & UI CONTROL ---
function updateUIForState() {
    [mainTitle, roundTitle, rightPanel, tutorialTextContainer, aiPanel, logPanel, progressButton].forEach(el => el.hide());
    resetActionButtonsStyle(); selectedAction = null; userAssessmentEl.value(''); seqRadio.value(null);

    aiButton.attribute('disabled', 'true').style('background-color', '#ccc');
    aiStrategyBox.hide();

    if (gameState.mode === 'TUTORIAL') {
        switch (gameState.step) {
            case 1:
                mainTitle.show(); tutorialTextContainer.show();
                
                drawTutorialStep1Text(); 
                
                // === MODIFIED ===: Button attached to tutorial container
                tutorialTextContainer.child(progressButton);
                progressButton.show();
                progressButton.html('Continue to Tutorial').mousePressed(goToTutorialStep2);
                break;
            case 2:
                // === MODIFIED ===: Show round title, hide tutorial text
                roundTitle.html('Tutorial: Write assessment and move forward').show();
                tutorialTextContainer.hide();
                
                rightPanel.show(); // Show Middle Panel
                rightPanel.child(progressButton);
                progressButton.show();
                [actionContainer, seqContainer, aiPanel].forEach(el => el.hide()); // Hide actions, seq, and AI
                progressButton.html('Continue').mousePressed(checkTutorialStep2);
                break;
            case 3:
                // === MODIFIED ===: Show round title, hide tutorial text
                roundTitle.html('Tutorial: Assess, Act, then Check AI').show();
                tutorialTextContainer.hide();
                
                rightPanel.show(); // Show Middle Panel
                aiPanel.show(); // Show Right Panel
                actionContainer.show();
                
                rightPanel.child(progressButton);
                progressButton.show();
                seqContainer.hide();
                progressButton.html('Check & Finish Tutorial').mousePressed(checkTutorialStep3);
                break;
        }
    } else if (gameState.mode === 'GAME') {
        // === MODIFIED ===: Show all 3 panels (graphs are in draw loop)
        mainTitle.show(); 
        roundTitle.html(`Round ${roundNumber}: Sensor Dashboard`).show();
        tutorialTextContainer.hide();
        
        rightPanel.show(); // Show Middle Panel
        aiPanel.show(); // Show Right Panel
        logPanel.show(); // Show Log Panel
        
        actionContainer.show();
        seqContainer.show();
        
        rightPanel.child(progressButton);
        progressButton.show();
        progressButton.html('Start Next Round').mousePressed(startNextBatch);
    }
    if (currentScenarioID) updateAIBoxContent();
}

// --- TUTORIAL PROGRESSION ---
function drawTutorialStep1Text() {
    tutorialTextContainer.html(`
        <h2 style="color: #003366;">Welcome to the Fermentation Game!</h2>
        <p style="font-size: 1.1em; line-height: 1.8;">
            You will be presented with sensor data from a fermentation batch. <br><br>
            <b>Your goal is to fix all issues in the minimum number of steps.</b><br><br>
            The workflow for each round is:
            <ol>
                <li>Analyze the 4 sensor graphs in the <b>left panel</b>. You will see data for Batch 3. Batches 1 & 2 are historical data.</li>
                <li>In the <b>middle panel</b>, write your assessment of the problem in the text box.</li>
                <li>Select the corrective action you want to take.</li>
                <li><b>(Optional)</b> Once you've done both, you can unlock the AI's analysis in the <b>right panel</b> to compare your strategy.</li>
                <li>Submit your action to start the next round.</li>
            </ol>
            <b>We will start with two examples. First, a perfect batch. Second, a problem batch.</b>
        </p>`);
}

function seedSensorHistory(startScenarioID) {
    sensorHistory = { sg: [], wortTemp: [], co2Activity: [], ph: [] };
    const goodData = SCENARIO_DATA[1];
    const startData = SCENARIO_DATA[startScenarioID];
    for (let i = 0; i < 2; i++) {
        sensorHistory.sg.push(goodData.sg);
        sensorHistory.wortTemp.push(goodData.wortTemp);
        sensorHistory.co2Activity.push(goodData.co2Activity);
        sensorHistory.ph.push(goodData.ph);
    }
    sensorHistory.sg.push(startData.sg);
    sensorHistory.wortTemp.push(startData.wortTemp);
    sensorHistory.co2Activity.push(startData.co2Activity);
    sensorHistory.ph.push(startData.ph);
}

function goToTutorialStep2() { 
    gameState.step = 2; 
    currentScenarioID = 1;
    seedSensorHistory(currentScenarioID); 
    updateUIForState(); 
}
function checkTutorialStep2() { 
    if (userAssessmentEl.value().trim().toLowerCase().includes('good')) { 
        gameState.step = 3; 
        currentScenarioID = 5;
        seedSensorHistory(currentScenarioID);
        updateUIForState(); 
    } else { 
        alert('Please look at the graphs (all lines stable and normal) and write "All good" in the text box to continue.'); 
    } 
}
function checkTutorialStep3() { 
    const assessmentFilled = userAssessmentEl.value().trim() !== '';
    if (!assessmentFilled) {
        alert('Please write your assessment first. Look at the graphs - what do you think is wrong?'); 
        return; 
    }
    if (selectedAction === null) {
        alert('Please select an action based on your assessment.'); 
        return; 
    }
    if (aiStrategyBox.style('display') === 'none') {
        alert('Great! You\'ve made your choice. Now click "See AI Analysis & Recommendation" to check your work.'); 
        return; 
    }
    if (selectedAction !== 'sterilize') {
        alert('Your selected action is incorrect. Look at the AI recommendation and select "Sterilize Equipment" to continue.'); 
        return; 
    }
    startGame(); 
}
function startGame() { 
    gameState.mode = 'GAME'; 
    currentScenarioID = STARTING_SCENARIO_ID; 
    roundNumber = 1;
    seedSensorHistory(currentScenarioID); 
    alert("Tutorial complete! The real challenge begins now."); 
    updateUIForState(); 
}

// --- MAIN GAME LOGIC ---
function startNextBatch() {
    const userAssessment = userAssessmentEl.value();
    const seqScore = seqRadio.value();
    if (!selectedAction || userAssessment.trim() === '' || !seqScore) { alert('Please write an assessment, select an action, and rate the difficulty.'); return; }
    
    const currentBatchNum = sensorHistory.sg.length;
    const logEntry = { userID, round: roundNumber, batch: currentBatchNum, currentScenarioID, currentScenarioName: SCENARIO_DATA[currentScenarioID].name, userAssessmentText: userAssessment.replace(/,/g, ';'), aiText: (AI_ASSESSMENTS[currentScenarioID] || '').replace(/,/g, ';'), aiChecked: aiStrategyBox.style('display') !== 'none', userAction: selectedAction, seqScore };
    
    const nextScenarioID = determineNextState(currentScenarioID, selectedAction);
    logEntry.nextScenarioID = nextScenarioID;
    gameLog.push(logEntry); logPreviewEl.html(`<pre>${JSON.stringify(gameLog, null, 2)}</pre>`);
    
    if (nextScenarioID === 1) { 
        currentScenarioID = nextScenarioID;
        updateSensorHistory();
        endGame(); 
        return; 
    }
    
    roundNumber++;
    currentScenarioID = nextScenarioID;
    updateSensorHistory();
    updateUIForState();
}

// --- HELPER & DRAWING FUNCTIONS ---

function updateSensorHistory() {
    if (!currentScenarioID) return;
    if (sensorHistory.sg.length >= 8) return; 
    const scenario = SCENARIO_DATA[currentScenarioID];
    sensorHistory.sg.push(scenario.sg);
    sensorHistory.wortTemp.push(scenario.wortTemp);
    sensorHistory.co2Activity.push(scenario.co2Activity);
    sensorHistory.ph.push(scenario.ph);
}

function checkInputsForAIButton() {
    const assessmentFilled = userAssessmentEl.value().trim() !== '';
    const actionSelected = selectedAction !== null;
    
    if ((gameState.mode === 'TUTORIAL' && gameState.step === 3) || gameState.mode === 'GAME') {
        if (assessmentFilled && actionSelected) {
            aiButton.removeAttribute('disabled');
            aiButton.style('background-color', '#17a2b8');
        } else {
            aiButton.attribute('disabled', 'true');
            aiButton.style('background-color', '#ccc');
            aiStrategyBox.hide();
        }
    }
}

// === MODIFIED ===: Main function to draw the 1x4 stack of graphs
function drawAllDashboardGraphs() {
    // 1x4 grid layout in the left panel
    const x = LEFT_PANEL_X;
    const y1 = PANEL_Y;
    const y2 = PANEL_Y + GRAPH_H + PADDING;
    const y3 = PANEL_Y + (GRAPH_H + PADDING) * 2;
    const y4 = PANEL_Y + (GRAPH_H + PADDING) * 3;
    
    drawSingleGraph('sg', x, y1, GRAPH_W, GRAPH_H);
    drawSingleGraph('wortTemp', x, y2, GRAPH_W, GRAPH_H);
    drawSingleGraph('co2Activity', x, y3, GRAPH_W, GRAPH_H);
    drawSingleGraph('ph', x, y4, GRAPH_W, GRAPH_H);
}


// === NEW ===: Reusable function to draw one graph
function drawSingleGraph(sensorID, x, y, w, h) {
    const def = SENSOR_DEFS[sensorID];
    const history = sensorHistory[sensorID];
    const color = LINE_COLORS[sensorID];
    const numPoints = history.length;
    
    push();
    
    // Draw graph boundary
    stroke(150);
    noFill();
    rect(x, y, w, h);
    
    // === NEW: Draw safety zone ===
    const ranges = SENSOR_RANGES[sensorID];
    if (ranges && ranges.normal) {
        // map(value, minIn, maxIn, minOut, maxOut)
        const yNormalMin = map(ranges.normal[1], def.min, def.max, y + h, y); // Map high value to low Y
        const yNormalMax = map(ranges.normal[0], def.min, def.max, y + h, y); // Map low value to high Y
        const normalRangeHeight = yNormalMax - yNormalMin;
        
        push();
        fill(220, 245, 220); // Light green background
        noStroke();
        rect(x, yNormalMin, w, normalRangeHeight);
        pop();
    }
    // === END NEW ===

    // Draw Graph Title
    fill(color);
    noStroke();
    textSize(14);
    textStyle(BOLD);
    textAlign(LEFT, TOP);
    text(`${def.label} (${def.unit})`, x + 10, y + 10);
    
    // Draw Y-axis min/max labels
    textSize(10);
    textStyle(NORMAL);
    fill(100);
    textAlign(RIGHT, TOP);
    text(def.max.toFixed(def.label === 'SG' ? 3 : (def.label === 'pH' ? 2 : 1)), x - 5, y + 5);
    textAlign(RIGHT, BOTTOM);
    text(def.min.toFixed(def.label === 'SG' ? 3 : (def.label === 'pH' ? 2 : 1)), x - 5, y + h - 5);


    // Draw X-axis labels for all 8 batches
    textAlign(CENTER, TOP);
    fill(100);
    noStroke();
    textSize(10);
    const xPad = w / 16; // Padding inside the graph
    for (let b = 1; b <= 8; b++) {
        const xPos = map(b, 1, 8, x + xPad, x + w - xPad);
        // === MODIFIED: Changed label from B to T ===
        text(`T${b}`, xPos, y + h + 5);
        // === END MODIFICATION ===
    }
    
    // Draw the line
    stroke(color);
    strokeWeight(2);
    noFill();
    beginShape();
    
    let lastX = 0, lastY = 0;

    for (let i = 0; i < numPoints; i++) {
        const val = history[i];
        const b = i + 1; // Batch number
        const xPos = map(b, 1, 8, x + xPad, x + w - xPad);
        const yPos = map(val, def.min, def.max, y + h, y); // Inverted Y-axis
        
        vertex(xPos, yPos);
        
        // Draw a small circle at each data point
        push();
        fill(color);
        noStroke();
        circle(xPos, yPos, 6);
        pop();
        
        if (i === numPoints - 1) {
            lastX = xPos;
            lastY = yPos;
        }
    }
    endShape();
    
    // Draw current value label at the end of the line
    if (numPoints > 0) {
        fill(color);
        noStroke();
        textSize(12);
        textAlign(LEFT, CENTER);
        textStyle(BOLD);
        const lastVal = history[numPoints - 1];
        text(lastVal.toFixed(def.label === 'SG' ? 3 : (def.label === 'pH' ? 2 : 1)), lastX + 8, lastY);
    }
    
    pop();
}


function updateAIBoxContent() {
    if (!currentScenarioID) return;
    const scenario = SCENARIO_DATA[currentScenarioID];
    
    // === MODIFIED: Store plain text for analysis ===
    currentAIAnalysisText = AI_ASSESSMENTS[currentScenarioID] || 'No detailed assessment available.';
    aiAnalysisA_El.html(currentAIAnalysisText); // Set HTML for Block A
    // === END MODIFICATION ===
    
    const recommendedActions = scenario.causes.map(cause => 
        Object.values(ACTIONS).find(a => a.fixes === cause).text
    );
    
    // === MODIFIED: Set P tag text and copy-text variable ===
    if (recommendedActions.length > 0) {
         currentAIRecommendationText = recommendedActions.join('; '); // Plain text for copy
         aiRecommendationA_El.html(recommendedActions.join('<br>')); // HTML for Block A
    } else {
         currentAIRecommendationText = 'No corrective action needed.';
         aiRecommendationA_El.html('No corrective action needed.');
    }
    
    // Set content for Block B (Noise)
    aiAnalysisB_El.html(currentAINoiseText);
    aiRecommendationB_El.html(currentAINoiseText);
    // === END MODIFICATION ===
}

function determineNextState(currentID, actionID) { const currentCauses = SCENARIO_DATA[currentID].causes; const causeToFix = ACTIONS[actionID].fixes; if (currentCauses.includes(causeToFix)) { const remainingCauses = currentCauses.filter(c => c !== causeToFix); for (const [id, scenario] of Object.entries(SCENARIO_DATA)) { if (scenario.causes.length === remainingCauses.length && remainingCauses.every(c => scenario.causes.includes(c))) { return parseInt(id); } } } return currentID; }
function endGame() { 
    const userRounds = roundNumber;
    gameLog.forEach(entry => entry.performanceScore = userRounds); 
    logPreviewEl.html(`<pre>${JSON.stringify(gameLog, null, 2)}</pre>`); 
    
    // Use a custom modal/div instead of alert
    const endMessage = createDiv(`
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;">
            <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); text-align: center;">
                <h2>Congratulations!</h2>
                <p style="font-size: 1.1em; margin: 15px 0;">You fixed all the issues in ${userRounds} rounds.</p>
                <p>Please download the log file to complete the game.</p>
            </div>
        </div>
    `);
    
    selectAll('button').forEach(b => b.attribute('disabled', '')); 
}
function selectUserAction(actionKey, button) { selectedAction = actionKey; resetActionButtonsStyle(); button.style('background-color', '#007bff').style('color', 'white'); }
function resetActionButtonsStyle() { for (const btn of Object.values(actionButtons)) { btn.style('background-color', '#f0f0f0').style('color', 'black'); } }
function toggleAIStrategy() { if (aiStrategyBox.style('display') === 'none') { aiStrategyBox.show(); } else { aiStrategyBox.hide(); } }
function downloadLog() { let csvContent = "data:text/csv;charset=utf-8,"; if (gameLog.length === 0) return; csvContent += Object.keys(gameLog[0]).join(",") + "\r\n"; gameLog.forEach(row => { csvContent += Object.values(row).join(",") + "\r\n"; }); const encodedUri = encodeURI(csvContent); const link = createA(encodedUri, ''); link.attribute("download", `fermentation_log_${userID}.csv`); link.elt.click(); link.remove(); }