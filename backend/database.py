import os
import sqlite3

# Define database path relative to workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'healthcare.db')

def init_db():
    # Ensure database folder exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create ChatHistory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ChatHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
    ''')

    # Create HealthTips table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS HealthTips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    # Create Medicines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        usage TEXT NOT NULL,
        side_effects TEXT NOT NULL,
        precautions TEXT NOT NULL
    )
    ''')

    # Seed initial data
    seed_data(cursor)

    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

def seed_data(cursor):
    # Seed default user if not exists
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Users (id, name, email) VALUES (1, 'Guest User', 'guest@curahealth.ai')")

    # Seed health tips if not exists
    cursor.execute("SELECT COUNT(*) FROM HealthTips")
    if cursor.fetchone()[0] == 0:
        tips = [
            ("Balanced Diet", "Eat balanced meals rich in fiber, lean proteins, and complex carbohydrates to sustain energy throughout the day.", "diet"),
            ("Sugar Reduction", "Reduce processed sugar intake to lower inflammation, support cardiovascular health, and prevent energy spikes.", "diet"),
            ("Eat Your Colors", "Include a variety of colorful vegetables and fruits in your meals to secure a broad spectrum of essential vitamins and minerals.", "diet"),
            ("Cardio Targets", "Aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity weekly to keep your heart healthy.", "exercise"),
            ("Strength Training", "Incorporate strength or resistance training exercises at least twice a week for muscle preservation and bone density.", "exercise"),
            ("Desk Breaks", "Take short walking/stretching breaks for 2-5 minutes every hour if you work a sedentary desk job.", "exercise"),
            ("Daily Hydration", "Drink at least 8-10 glasses (about 2-2.5 liters) of water daily to maintain cognitive function, digestion, and skin health.", "water"),
            ("Morning Flush", "Start your day with a full glass of water to kickstart hydration, digestion, and flush metabolic waste.", "water"),
            ("Active Hydration", "Increase fluid intake during and after strenuous exercise to replenish hydration levels lost to sweat.", "water"),
            ("Sleep Routine", "Maintain a consistent sleep schedule by going to bed and waking up at the same time, even on weekends.", "sleep"),
            ("Bedroom Environment", "Keep your bedroom cool, dark, and quiet (around 65°F / 18°C) to enhance deep sleep efficiency.", "sleep"),
            ("Blue Light Cutoff", "Avoid digital screens (phones, laptops, TVs) for at least 30-60 minutes before bedtime to support natural melatonin production.", "sleep")
        ]
        cursor.executemany("INSERT INTO HealthTips (title, content, category) VALUES (?, ?, ?)", tips)

    # Seed medicines
    medicines = [
        ("Paracetamol", 
         "Relief of mild to moderate pain (headaches, muscle aches, toothaches) and temporary fever reduction.", 
         "Mild nausea, abdominal discomfort, allergic skin rash. Severe liver damage is possible if overdosed.", 
         "Do not exceed 4000mg (4g) within a 24-hour window. Avoid alcohol consumption. Double check ingredients of other cold remedies to prevent duplicate acetaminophen intake."),
        
        ("Ibuprofen", 
         "Reduces inflammatory pain, joint swelling, fever, and symptoms of arthritis or menstrual cramps.", 
         "Stomach upset, heartburn, mild nausea, bloating, dizziness. Long-term use slightly increases cardiovascular risks.", 
         "Always take with food or milk to minimize gastric lining irritation. Avoid if you have active stomach ulcers, renal impairment, or severe heart failure."),
        
        ("Amoxicillin", 
         "Penicillin-type antibiotic used to treat bacterial infections of the lungs, ears, sinuses, and urinary tract.", 
         "Diarrhea, nausea, stomach pain, skin rash, or temporary oral thrush.", 
         "Complete the full prescribed course even if symptoms vanish early to prevent antibiotic resistance. This medication does NOT treat viral infections (like colds or flu)."),
        
        ("Metformin", 
         "Oral diabetes medicine that helps control blood sugar levels for people with type 2 diabetes.", 
         "Gastrointestinal distress (diarrhea, gas, bloating, nausea), metallic taste in the mouth, and very rarely, lactic acidosis.", 
         "Take with meals to minimize stomach side effects. Limit alcohol intake. Monitor kidney function regularly while using this drug."),
        
        ("Atorvastatin", 
         "Statin medication that lowers cholesterol, reduces low-density lipoprotein (LDL), and lowers risk of stroke or heart attack.", 
         "Mild muscle aches, headache, digestive discomfort, or minor increases in blood sugar levels.", 
         "Report any unexplained, severe muscle pain or weakness immediately, as it could indicate a rare, dangerous condition (rhabdomyolysis). Avoid consuming large amounts of grapefruit juice."),
        
        ("Cetirizine", 
         "Antihistamine that treats hay fever and allergy symptoms like sneezing, runny nose, watery eyes, or hives.", 
         "Mild drowsiness, dry mouth, sore throat, fatigue, or headache.", 
         "Exercise caution when driving or operating heavy machinery until you know how this medication affects you. Limit alcohol consumption."),
        
        ("Dolo 650", 
         "Widely prescribed Indian brand of Paracetamol (650mg). Used for fever relief and managing mild to moderate pain.", 
         "Nausea, allergic skin reactions, or stomach discomfort. High doses can cause liver damage.", 
         "Maintain a gap of at least 4 to 6 hours between doses. Do not exceed 4 tablets in 24 hours. Avoid alcohol."),
        
        ("Crocin", 
         "Popular Indian brand of Paracetamol (500mg). Rapid relief from headaches, toothaches, muscle aches, and fever.", 
         "Mild stomach discomfort, nausea, or allergic rash.", 
         "Be careful not to take other Paracetamol-containing medicines concurrently. Consult a physician if fever persists beyond 3 days."),
        
        ("Combiflam", 
         "Highly popular painkiller combining Ibuprofen (400mg) and Paracetamol (325mg). Used for muscular pain, headache, joint pain, and fever.", 
         "Acidity, heartburn, nausea, abdominal discomfort, flatulence.", 
         "Always take after meals to protect the stomach lining. Avoid if you have active stomach ulcers, severe kidney issues, or asthma."),
        
        ("Pantocid", 
         "Indian brand of Pantoprazole (40mg). Reduces stomach acid production. Used for acidity, gastroesophageal reflux (GERD), heartburn, and stomach ulcers.", 
         "Headache, diarrhea, flatulence, dizziness, or dry mouth.", 
         "Best taken in the morning on an empty stomach, 30-40 minutes before breakfast. Consult a doctor for long term usage."),
        
        ("Aciloc", 
         "Indian brand of Ranitidine (150mg/300mg). Reduces acid in the stomach to relieve indigestion, acidity, bloating, and heartburn.", 
         "Headache, dizziness, diarrhea, or fatigue.", 
         "Can be taken with or without food. Avoid heavy, spicy meals right before sleeping."),
        
        ("Pan-D", 
         "Combination drug containing Pantoprazole (40mg) and Domperidone (30mg). Relieves acidity, nausea, vomiting, gas, and stomach fullness.", 
         "Dry mouth, headache, diarrhea, weakness, or joint pain.", 
         "Take on an empty stomach, 30 minutes before breakfast. Domperidone content requires caution in patients with cardiac history."),
        
        ("Azithral", 
         "Indian brand of Azithromycin (250mg/500mg). Popular antibiotic used for throat infections, sinus congestion, bronchitis, and pneumonia.", 
         "Loose motions (diarrhea), stomach cramps, nausea, vomiting.", 
         "Complete the full prescribed course. Do not take if you have pre-existing liver issues or heart rhythm disorders."),
        
        ("Saridon", 
         "Popular headache relief pill combining Propyphenazone, Paracetamol, and Caffeine. Delivers rapid headache relief.", 
         "Acidity, palpitations, restlessness, or mild dizziness.", 
         "Contains caffeine; avoid taking close to bedtime or with excessive coffee. Avoid using with other paracetamol drugs."),
        
        ("Montair-LC", 
         "Combination tablet of Montelukast (10mg) and Levocetirizine (5mg). Widely used in India for allergic runny nose, sneezing, skin allergies, and asthma symptoms.", 
         "Mild drowsiness, tiredness, dry mouth, sleepiness, headache.", 
         "Best taken at night. Avoid driving or alcohol consumption after taking as it may impair focus."),
        
        ("Liv.52", 
         "Extremely popular herbal liver supplement manufactured by Himalaya. Promotes appetite, improves digestion, and protects the liver against toxins.", 
         "Generally free from side effects when taken in recommended dosages.", 
         "Mainly supportive. Consult a medical doctor for severe pathological liver disorders."),
        
        ("Metrogyl", 
         "Indian brand of Metronidazole (200mg/400mg). Used for stomach infections, amoebiasis, dental infections, and bacterial loose motions.", 
         "Metallic taste in mouth, dark colored urine, dry mouth, nausea.", 
         "Avoid alcohol consumption completely during treatment and for at least 48 hours after, to prevent a severe reaction (headache, flushing)."),
        
        ("Limcee", 
         "Chewable Vitamin C (500mg) orange tablet. Popular immune support supplement used for gum health, skin repair, and viral flu recovery.", 
         "Very safe. Excessive doses may cause mild stomach irritation or kidney stones in rare cases.", 
         "Chew thoroughly before swallowing. Safe for daily use within recommended guidelines."),
        
        ("Electral", 
         "WHO-formulation Oral Rehydration Salts (ORS). Widely used in India to restore water and electrolytes lost due to diarrhea, vomiting, heat stroke, or heavy sweating.", 
         "Generally no side effects if reconstituted in the correct volume of water.", 
         "Dissolve the entire pack contents in 1 liter of clean drinking water. Consume within 24 hours. Do not boil the prepared solution.")
    ]

    for name, usage, side_effects, precautions in medicines:
        cursor.execute("SELECT COUNT(*) FROM Medicines WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO Medicines (name, usage, side_effects, precautions) VALUES (?, ?, ?, ?)",
                (name, usage, side_effects, precautions)
            )

if __name__ == '__main__':
    init_db()
