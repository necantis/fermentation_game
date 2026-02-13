import random

# =========================================================================
# === DATA: Scenarios, AI Text, Actions ===================================
# =========================================================================

SCENARIO_DATA = {
    1: {'name': '1: All Good', 'causes': [], 'sg': 1.025, 'wortTemp': 20, 'co2Activity': 20, 'ph': 4.5},
    2: {'name': '2: Temp Control Fail', 'causes': ['C1'], 'sg': 1.018, 'wortTemp': 25.5, 'co2Activity': 40, 'ph': 4.6},
    3: {'name': '3: Yeast Health Issue', 'causes': ['C2'], 'sg': 1.045, 'wortTemp': 19.0, 'co2Activity': 3, 'ph': 5.0},
    4: {'name': '4: Oxygen Exposure', 'causes': ['C3'], 'sg': 1.018, 'wortTemp': 21.0, 'co2Activity': 35, 'ph': 4.4},
    5: {'name': '5: Sanitation Fail', 'causes': ['C4'], 'sg': 1.008, 'wortTemp': 19.5, 'co2Activity': 7, 'ph': 3.2},
    6: {'name': '6: Temp & Yeast', 'causes': ['C1', 'C2'], 'sg': 1.050, 'wortTemp:': 25.5, 'co2Activity': 1, 'ph': 5.0},
    7: {'name': '7: Temp & Oxygen', 'causes': ['C1', 'C3'], 'sg': 1.022, 'wortTemp': 25.5, 'co2Activity': 45, 'ph': 4.7},
    8: {'name': '8: Temp & Sanitation', 'causes': ['C1', 'C4'], 'sg': 1.002, 'wortTemp': 26.0, 'co2Activity': 20, 'ph': 2.8},
    9: {'name': '9: Yeast & Oxygen', 'causes': ['C2', 'C3'], 'sg': 1.048, 'wortTemp': 19.0, 'co2Activity': 2, 'ph': 5.1},
    10: {'name': '10: Yeast & Sanitation', 'causes': ['C2', 'C4'], 'sg': 1.010, 'wortTemp': 19.5, 'co2Activity': 4, 'ph': 3.5},
    12: {'name': '12: Oxygen & Sanitation', 'causes': ['C3', 'C4'], 'sg': 1.005, 'wortTemp': 19.5, 'co2Activity': 10, 'ph': 3.0},
    13: {'name': '13: Temp, Yeast, Oxygen', 'causes': ['C1', 'C2', 'C3'], 'sg': 1.048, 'wortTemp': 25.5, 'co2Activity': 1, 'ph': 5.1},
    14: {'name': '14: Temp, Yeast, Sanitation', 'causes': ['C1', 'C2', 'C4'], 'sg': 1.008, 'wortTemp': 26.0, 'co2Activity': 5, 'ph': 3.0},
    15: {'name': '15: Temp, Oxygen, Sanitation', 'causes': ['C1', 'C3', 'C4'], 'sg': 1.001, 'wortTemp': 26.5, 'co2Activity': 15, 'ph': 2.7},
    16: {'name': '16: All Together', 'causes': ['C1', 'C2', 'C3', 'C4'], 'sg': 1.040, 'wortTemp': 26.0, 'co2Activity': 2, 'ph': 3.5},
}

# Fix typo in original data for scenario 6 key 'wortTemp:' -> 'wortTemp'
SCENARIO_DATA[6]['wortTemp'] = 25.5
if 'wortTemp:' in SCENARIO_DATA[6]:
    del SCENARIO_DATA[6]['wortTemp:']


ACTIONS = {
    'fix_temp': {'text': 'Fix Temperature Controller', 'fixes': 'C1'},
    'pitch_yeast': {'text': 'Pitch New/Healthy Yeast', 'fixes': 'C2'},
    'manage_oxygen': {'text': 'Improve Oxygen Management', 'fixes': 'C3'},
    'sterilize': {'text': 'Sterilize Equipment', 'fixes': 'C4'}
}

SENSOR_DEFS = {
    'sg': {'label': 'SG', 'unit': '', 'min': 0.990, 'max': 1.060},
    'wortTemp': {'label': 'Wort Temp', 'unit': '°C', 'min': 10, 'max': 30},
    'co2Activity': {'label': 'CO2 Activity', 'unit': 'b/min', 'min': 0, 'max': 50},
    'ph': {'label': 'pH', 'unit': '', 'min': 3.0, 'max': 6.0}
}

SENSOR_RANGES = {
    'sg': {'normal': [1.020, 1.035]},
    'wortTemp': {'normal': [19.5, 20.5]},
    'co2Activity': {'normal': [15, 25]},
    'ph': {'normal': [4.4, 4.6]}
}

AI_ASSESSMENTS = {
    1: "All sensors report normal readings within their ideal fermentation ranges. The process appears stable and healthy.",
    2: "Wort Temp: High (25.5°C). CO2: Very High. SG: Dropping normally. High temp accelerates fermentation but produces off-flavors.",
    3: "SG: High (1.045). CO2: Very Low. Wort Temp: Low side. Hints at unhealthy yeast that's failing to start fermentation.",
    4: "CO2: Active. SG: Dropping. But Wort Temp is slightly high and pH is dropping faster than expected? Check for Oxygen ingress.",
    5: "pH: Significant, continuous drop (souring). SG: Dropped too low. CO2: Low activity. Hints at bacterial contamination.",
    6: "Extremely slow or no SG drop, low CO2, high temp. The yeast is stressed by heat and poor health.",
    7: "Wort Temp: High. CO2: Very High. Fast fermentation, but likely oxidizing due to agitation or leaks.",
    8: "Wort Temp: High. pH: Very Low (Acidic). SG: Very Low. High temp encouraged bacterial growth (Lactobacillus?).",
    9: "SG: High (stuck). pH: High (no acid production). Yeast isn't working, and oxygen might be stalling it.",
    10: "SG: Slow drop. pH: Low. Sanitation failed, and the weak yeast couldn't outcompete the bacteria.",
    12: "pH: Very Low. CO2: Moderate. Oxygen leak might be fueling acetobacter or other aerobic bacteria.",
    13: "SG: High. Temp: High. Yeast won't start despite the heat. Oxygen might be confusing the yeast phase.",
    14: "Total collapse. High Temp + Bad Yeast + bacteria taking over. pH is crashing.",
    15: "High Temp + Oxygen + Bacteria. This is making vinegar, not beer.",
    16: "All systems failing. High Temp, Bad Yeast, Oxygen leak, and Infection. Dump it."
}

STARTING_SCENARIO_ID = 6

class GameState:
    def __init__(self, mode='TUTORIAL'):
        self.mode = mode
        self.step = 1 if mode == 'TUTORIAL' else 0
        self.current_scenario_id = None
        self.round_number = 1
        self.sensor_history = {
            'sg': [],
            'wortTemp': [],
            'co2Activity': [],
            'ph': []
        }
    
    def seed_sensor_history(self, scenario_id):
        """Seed history with 2 good rounds + 1 current scenario round."""
        self.sensor_history = {k: [] for k in self.sensor_history}
        good_data = SCENARIO_DATA[1]
        start_data = SCENARIO_DATA[scenario_id]
        
        for _ in range(2):
            for k in self.sensor_history:
                self.sensor_history[k].append(good_data[k])
                
        for k in self.sensor_history:
            self.sensor_history[k].append(start_data[k])
            
    def update_sensor_history(self):
        """Add current scenario data to history."""
        if not self.current_scenario_id:
            return
        # Limit history length if needed, but original code capped visual at 8
        if len(self.sensor_history['sg']) >= 8:
            return

        scenario = SCENARIO_DATA[self.current_scenario_id]
        for k in self.sensor_history:
            self.sensor_history[k].append(scenario[k])

    def determine_next_state(self, current_id, action_key):
        """Determine next scenario based on current state and action."""
        if current_id not in SCENARIO_DATA:
            return current_id
            
        current_causes = SCENARIO_DATA[current_id]['causes']
        action_fix = ACTIONS[action_key]['fixes']
        
        if action_fix in current_causes:
            remaining_causes = [c for c in current_causes if c != action_fix]
            
            # Find scenario that matches remaining causes exactly
            for sid, data in SCENARIO_DATA.items():
                s_causes = data['causes']
                if len(s_causes) == len(remaining_causes) and \
                   all(c in s_causes for c in remaining_causes):
                    return sid
                    
        return current_id

LINE_COLORS = {
    'sg': '#E63946',
    'wortTemp': '#457B9D',
    'co2Activity': '#A8DADC',
    'ph': '#1D3557'
}

