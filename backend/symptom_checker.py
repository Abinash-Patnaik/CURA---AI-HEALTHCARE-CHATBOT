import re

# Severity Levels
SEVERITY_MILD = "Mild"
SEVERITY_MODERATE = "Moderate"
SEVERITY_EMERGENCY = "Emergency"

# Symptom Database
SYMPTOM_RULES = [
    {
        "keywords": ["chest pain", "pressure in chest", "angina", "heart attack symptoms"],
        "severity": SEVERITY_EMERGENCY,
        "conditions": ["Angina", "Myocardial Infarction (Heart Attack)", "Pericarditis"],
        "advice": [
            "This could be a life-threatening medical emergency.",
            "Call emergency services (e.g., 911 or your local emergency number) immediately.",
            "Do not drive yourself to the hospital. Wait for an ambulance.",
            "Sit down, rest, and try to remain calm while help arrives."
        ]
    },
    {
        "keywords": ["breathing difficulty", "shortness of breath", "dyspnea", "hard to breathe", "gasping"],
        "severity": SEVERITY_EMERGENCY,
        "conditions": ["Asthma Attack", "Severe Pneumonia", "Pulmonary Embolism", "Allergic Anaphylaxis"],
        "advice": [
            "This is a critical symptom requiring urgent medical care.",
            "Call emergency services immediately if breathing is severely labored or accompanied by blue lips/face.",
            "If you have an asthma inhaler, use it as prescribed.",
            "Sit upright and loosen any tight clothing."
        ]
    },
    {
        "keywords": ["severe bleeding", "hemorrhage", "bleeding heavily", "uncontrolled bleeding"],
        "severity": SEVERITY_EMERGENCY,
        "conditions": ["Arterial Laceration", "Severe Trauma", "Internal Bleeding"],
        "advice": [
            "Apply direct, firm pressure to the wound using a clean cloth or sterile bandage.",
            "Elevate the injured limb above heart level if possible.",
            "Call emergency services immediately.",
            "Do not remove pressure or peek at the wound; keep adding clean dressing if blood seeps through."
        ]
    },
    {
        "keywords": ["stroke symptoms", "slurred speech", "face drooping", "arm weakness", "numbness one side"],
        "severity": SEVERITY_EMERGENCY,
        "conditions": ["Transient Ischemic Attack (TIA)", "Stroke (Cerebrovascular Accident)"],
        "advice": [
            "Use the FAST test: Face drooping, Arm weakness, Speech difficulty, Time to call emergency.",
            "Call emergency services immediately. Time is critical for stroke recovery.",
            "Note the exact time symptoms first started, as this dictates available medical treatments.",
            "Do not give the person food, drink, or medication (like aspirin)."
        ]
    },
    {
        "keywords": ["fever", "high temperature", "chills", "sweating"],
        "severity": SEVERITY_MODERATE,
        "conditions": ["Influenza (Flu)", "Gastroenteritis", "Bacterial Infection", "Common Cold"],
        "advice": [
            "Stay well-hydrated by drinking water, herbal teas, or oral rehydration solutions.",
            "Get plenty of rest to support your immune system.",
            "You may use over-the-counter fever reducers like Paracetamol or Ibuprofen as directed.",
            "Consult a doctor if the fever exceeds 103°F (39.4°C) or lasts more than 3 consecutive days."
        ]
    },
    {
        "keywords": ["headache", "migraine", "throbbing head", "head pain"],
        "severity": SEVERITY_MODERATE,
        "conditions": ["Tension Headache", "Migraine", "Dehydration", "Sinusitis"],
        "advice": [
            "Rest in a quiet, dark, well-ventilated room.",
            "Apply a cold compress to your forehead or the back of your neck.",
            "Ensure you are fully hydrated, as dehydration is a common headache trigger.",
            "Consider mild pain relievers. If headache is sudden, severe ('thunderclap'), or follows a head injury, seek emergency care immediately."
        ]
    },
    {
        "keywords": ["cough", "sore throat", "coughing", "throat pain"],
        "severity": SEVERITY_MILD,
        "conditions": ["Common Cold", "Bronchitis", "Allergic Rhinitis", "Pharyngitis"],
        "advice": [
            "Soothe your throat with warm liquids like honey-lemon tea or warm salt water gargles.",
            "Use a humidifier or inhale steam from a hot shower to relieve airway irritation.",
            "Rest your voice and avoid environmental irritants like dust or cigarette smoke.",
            "Seek medical review if cough persists for more than 2-3 weeks or contains blood."
        ]
    },
    {
        "keywords": ["fatigue", "tiredness", "weakness", "lethargy", "exhaustion"],
        "severity": SEVERITY_MILD,
        "conditions": ["Lack of Sleep", "Iron Deficiency Anemia", "Vitamin D Deficiency", "Chronic Stress"],
        "advice": [
            "Prioritize getting 7-9 hours of quality sleep nightly in a dark, quiet environment.",
            "Maintain balanced meals with adequate iron, vitamins, and protein.",
            "Incorporate light, regular physical activity to boost baseline energy levels.",
            "Discuss persistent, unexplained fatigue with a physician to rule out thyroid or metabolic issues."
        ]
    },
    {
        "keywords": ["nausea", "vomiting", "stomach ache", "diarrhea", "indigestion"],
        "severity": SEVERITY_MODERATE,
        "conditions": ["Gastroenteritis (Stomach Flu)", "Food Poisoning", "Acid Reflux (GERD)"],
        "advice": [
            "Sip clear liquids (water, broth, diluted sports drinks) in small amounts to prevent dehydration.",
            "Avoid solid food for a few hours. When ready, follow a bland diet (bananas, rice, applesauce, toast).",
            "Avoid dairy, caffeine, alcohol, nicotine, and fatty or highly seasoned foods.",
            "Seek medical attention if vomiting is persistent, prevents fluid retention for 24 hours, or shows blood."
        ]
    }
]

def analyze_symptoms(symptom_text):
    if not symptom_text:
        return {
            "severity": SEVERITY_MILD,
            "conditions": ["Unknown System Condition"],
            "advice": ["Please enter one or more symptoms (e.g., 'fever and headache' or 'cough and chest pain') for analysis."],
            "is_emergency": False
        }

    normalized_text = symptom_text.lower()
    matched_rules = []
    
    # Check for keyword matches
    for rule in SYMPTOM_RULES:
        for keyword in rule["keywords"]:
            # Use regex pattern with word boundaries for better keyword matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, normalized_text):
                matched_rules.append(rule)
                break  # Matched one keyword in this rule, move to next rule

    # If no specific matches, default to mild general warning
    if not matched_rules:
        return {
            "severity": SEVERITY_MILD,
            "conditions": ["Undetermined Condition (symptoms did not trigger preset models)"],
            "advice": [
                "Your symptoms don't clearly match our common diagnostic categories.",
                "Ensure you rest and keep yourself hydrated.",
                "Monitor for any new, worsening, or severe symptoms.",
                "Always consult a qualified healthcare provider for proper diagnosis."
            ],
            "is_emergency": False
        }

    # Aggregate matched data
    # Priority order for severity: Emergency > Moderate > Mild
    final_severity = SEVERITY_MILD
    conditions = set()
    advice = []
    is_emergency = False

    # Check for emergency severity first
    if any(r["severity"] == SEVERITY_EMERGENCY for r in matched_rules):
        final_severity = SEVERITY_EMERGENCY
        is_emergency = True
    elif any(r["severity"] == SEVERITY_MODERATE for r in matched_rules):
        final_severity = SEVERITY_MODERATE

    for r in matched_rules:
        # If in emergency mode, prioritize displaying emergency advice
        if is_emergency and r["severity"] != SEVERITY_EMERGENCY:
            continue
        conditions.update(r["conditions"])
        for adv in r["advice"]:
            if adv not in advice:
                advice.append(adv)

    return {
        "severity": final_severity,
        "conditions": sorted(list(conditions)),
        "advice": advice,
        "is_emergency": is_emergency
    }
