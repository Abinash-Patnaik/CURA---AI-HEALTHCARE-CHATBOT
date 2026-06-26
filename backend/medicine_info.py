import os
import json
import urllib.request
import urllib.error
import difflib

# Load Custom Env Loader to load .env variables manually
def load_env():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            print("Error loading .env file in medicine_info:", e)

# Run environment loader
load_env()

# Embedded database of Indian medicines
paracetamol_info = {
    "generic_name": "Paracetamol (Acetaminophen)",
    "category": "Analgesic (Pain Reliever) & Antipyretic (Fever Reducer)",
    "uses": "Temporary relief of mild to moderate pain (headache, toothache, muscle soreness, menstrual cramps) and reduction of fever.",
    "how_it_works": "Inhibits cyclooxygenase (COX) enzymes in the central nervous system, reducing the synthesis of prostaglandins which cause pain and fever.",
    "dosage": "Adults: 500 mg to 1000 mg every 4-6 hours as needed. Do not exceed 4000 mg (4g) in a 24-hour period.",
    "how_to_take": "Take orally with a glass of water. Can be taken with or without food. Do not crush sustained-release tablets.",
    "common_side_effects": "Mild stomach upset, nausea, headache, or sleep issues.",
    "serious_side_effects": "Skin rash, hives, swelling of face/lips/throat, difficulty breathing, dark urine, or yellowing of skin/eyes (signs of liver damage).",
    "precautions": "Avoid alcohol. Do not take with other paracetamol-containing products. Caution in liver or kidney disease.",
    "interactions": "Warfarin (increased bleeding risk), Cholestyramine (reduced absorption), Metoclopramide (accelerated absorption).",
    "warnings": "Severe liver damage may occur if you take more than the maximum daily amount or consume alcohol concurrently.",
    "pregnancy_safety": "Generally considered safe during pregnancy when used at the lowest effective dose for the shortest duration.",
    "breastfeeding_safety": "Considered safe as it is excreted in breast milk in very small, clinically insignificant amounts.",
    "storage": "Store in a cool, dry place below 30°C, away from direct sunlight."
}

# Base templates for classes of medicines
antibiotic_info = {
    "generic_name": "Azithromycin",
    "category": "Macrolide Antibiotic",
    "uses": "Treats bacterial infections such as throat infections (pharyngitis/tonsillitis), bronchitis, pneumonia, ear infections, and skin infections.",
    "how_it_works": "Inhibits bacterial protein synthesis by binding to the 50S ribosomal subunit, preventing bacterial growth.",
    "dosage": "Adults: Typically 500 mg once daily for 3 to 5 days, depending on the infection severity.",
    "how_to_take": "Can be taken with or without food. Taking with food may reduce stomach upset. Swallow the tablet whole.",
    "common_side_effects": "Diarrhea, nausea, abdominal pain, vomiting, or headache.",
    "serious_side_effects": "QT prolongation (irregular heart rhythm), severe allergic reactions (anaphylaxis), liver problems, or severe watery diarrhea.",
    "precautions": "Finish the entire prescribed course even if symptoms improve. Caution in heart rhythm disorders or liver disease.",
    "interactions": "Antacids containing aluminum/magnesium (take azithromycin 1 hour before or 2 hours after), Digoxin, Colchicine.",
    "warnings": "May cause severe allergic skin reactions. Overuse of antibiotics leads to bacterial resistance.",
    "pregnancy_safety": "Generally considered safe during pregnancy, but should be used only if clearly needed and prescribed.",
    "breastfeeding_safety": "Excreted in small amounts. Monitor infant for diarrhea or rash. Consult doctor.",
    "storage": "Store at room temperature below 30°C in a dry place."
}

amoxicillin_info = {
    "generic_name": "Amoxicillin",
    "category": "Penicillin Antibiotic",
    "uses": "Treatment of bacterial infections of the ear, nose, throat, urinary tract, skin, and lower respiratory tract.",
    "how_it_works": "Binds to penicillin-binding proteins inside the bacterial cell wall, inhibiting cell wall synthesis and causing cell lysis.",
    "dosage": "Adults: 250 mg to 500 mg every 8 hours, or 500 mg to 875 mg every 12 hours, as directed by a doctor.",
    "how_to_take": "Swallow whole with water. Can be taken with or without food. Maintain consistent dosing intervals.",
    "common_side_effects": "Diarrhea, nausea, vomiting, or skin rash.",
    "serious_side_effects": "Anaphylaxis (severe allergic reaction), colitis (severe persistent diarrhea), dark urine, or yellowing eyes/skin.",
    "precautions": "Contraindicated in patients with a history of penicillin allergy. Inform doctor of kidney impairment.",
    "interactions": "Oral contraceptives (may reduce effectiveness), Allopurinol (increases risk of rash), Methotrexate, Anticoagulants.",
    "warnings": "Allergic reactions can occur suddenly and be life-threatening. Seek immediate help if swelling or hives occur.",
    "pregnancy_safety": "Considered safe and commonly prescribed during pregnancy under medical supervision.",
    "breastfeeding_safety": "Considered safe, but trace amounts excreted may cause diarrhea or yeast infection in the infant.",
    "storage": "Store below 25°C. Reconstituted oral suspensions must be stored in a refrigerator and used within 7-14 days."
}

augmentin_info = {
    "generic_name": "Amoxicillin & Potassium Clavulanate",
    "category": "Penicillin Antibiotic & Beta-lactamase Inhibitor Combo",
    "uses": "Treats severe or resistant bacterial infections like sinusitis, otitis media, respiratory tract infections, and animal bites.",
    "how_it_works": "Amoxicillin kills bacteria; Clavulanic acid blocks beta-lactamase enzymes that bacteria use to destroy amoxicillin.",
    "dosage": "Adults: 1 tablet (typically 625 mg containing 500mg amoxicillin and 125mg clavulanic acid) 2 to 3 times daily.",
    "how_to_take": "Take immediately before or at the start of a meal to optimize absorption and minimize gastrointestinal discomfort.",
    "common_side_effects": "Diarrhea, nausea, thrush (yeast infection), or vomiting.",
    "serious_side_effects": "Severe liver dysfunction (hepatitis), severe skin rash (Stevens-Johnson syndrome), or pseudomembranous colitis.",
    "precautions": "Strictly avoid if allergic to penicillin or cephalosporin class of antibiotics. Monitor liver function during long courses.",
    "interactions": "Probenecid, Allopurinol, Oral anticoagulants (increases bleeding times), Methotrexate.",
    "warnings": "If severe diarrhea occurs, do not take anti-diarrheal medicines without consulting a doctor.",
    "pregnancy_safety": "Considered safe, but should only be used under direct prescription and monitoring by your obstetrician.",
    "breastfeeding_safety": "Considered compatible. Watch the baby for potential side effects like thrush, diarrhea, or diaper rash.",
    "storage": "Store in dry airtight container below 25°C. Keep protected from moisture."
}

ppi_info = {
    "generic_name": "Pantoprazole",
    "category": "Proton Pump Inhibitor (PPI)",
    "uses": "Treatment of gastroesophageal reflux disease (GERD), acid acidity, stomach ulcers, and Zollinger-Ellison syndrome.",
    "how_it_works": "Irreversibly inhibits the hydrogen-potassium ATPase pump (proton pump) in gastric parietal cells, shutting down acid production.",
    "dosage": "Adults: 40 mg once daily, taken 30-60 minutes before breakfast.",
    "how_to_take": "Swallow the tablet whole. Do not crush, chew, or split the tablet, as it has an enteric coating to protect it from stomach acid.",
    "common_side_effects": "Headache, diarrhea, nausea, flatulence, stomach pain, or dizziness.",
    "serious_side_effects": "Severe allergic reactions, severe diarrhea caused by C. difficile, bone fractures (long term use), or vitamin B12 deficiency.",
    "precautions": "Long term therapy may decrease magnesium levels. Inform doctor if you have osteoporosis or liver disease.",
    "interactions": "Ketoconazole, Itraconazole, Atazanavir, iron salts (pantoprazole reduces absorption of these drugs).",
    "warnings": "Do not self-medicate for more than 14 days without consulting a medical professional.",
    "pregnancy_safety": "Category B. Should be used in pregnancy only if clearly needed and recommended by a doctor.",
    "breastfeeding_safety": "Excreted in small amounts. Consult doctor to weigh benefits against risks.",
    "storage": "Store at room temperature below 30°C in a dry place."
}

rantac_info = {
    "generic_name": "Ranitidine",
    "category": "H2-Receptor Antagonist",
    "uses": "Treatment and prevention of heartburn, acid indigestion, stomach ulcers, and acid reflux disease.",
    "how_it_works": "Blocks histamine H2-receptors on stomach cells, reducing gastric acid volume and concentration.",
    "dosage": "Adults: 150 mg twice daily (morning and night) or 300 mg at bedtime.",
    "how_to_take": "Can be taken with or without food. Take 30-60 minutes before meals if trying to prevent symptoms.",
    "common_side_effects": "Headache, constipation, diarrhea, or mild dizziness.",
    "serious_side_effects": "Slow/fast heartbeat, confusion, easy bruising, yellowing of skin/eyes, or severe skin rashes.",
    "precautions": "Caution in kidney or liver impairment. Use lowest effective dose.",
    "interactions": "Ketoconazole, Itraconazole, Procainamide, blood thinners.",
    "warnings": "Inform doctor of unintended weight loss, difficulty swallowing, or black stools before using H2 blockers.",
    "pregnancy_safety": "Generally considered safe, but check with a physician before starting.",
    "breastfeeding_safety": "Excreted in breast milk. Use only if advised by a doctor.",
    "storage": "Store below 25°C in a dry place. Keep container tightly closed."
}

antacid_gel_info = {
    "generic_name": "Magaldrate & Simethicone",
    "category": "Antacid & Antiflatulent Combo",
    "uses": "Provides rapid relief from acidity, heartburn, gas, indigestion, and bloating.",
    "how_it_works": "Magaldrate neutralizes excess stomach acid; Simethicone reduces surface tension of gas bubbles, allowing them to coalesce and pass easily.",
    "dosage": "Adults: 10-20 ml (2-4 teaspoons) or 1-2 tablets chewed after meals and at bedtime.",
    "how_to_take": "Shake liquid suspension well before use. Chew tablets thoroughly before swallowing. Do not take within 2 hours of other medicines.",
    "common_side_effects": "Mild diarrhea or constipation.",
    "serious_side_effects": "Muscle weakness, slow reflexes, or severe kidney symptoms (due to aluminum/magnesium buildup).",
    "precautions": "Do not take continuously for more than 2 weeks. Avoid in patients with severe kidney disease.",
    "interactions": "Tetracyclines, Ciprofloxacin, Iron supplements (antacids severely reduce their absorption).",
    "warnings": "If stomach symptoms persist after 2 weeks, consult a physician for a proper diagnosis.",
    "pregnancy_safety": "Considered safe for occasional use, but consult doctor first.",
    "breastfeeding_safety": "Safe as it does not enter breast milk in significant amounts.",
    "storage": "Store at room temperature below 30°C. Protect from freezing."
}

antihistamine_info = {
    "generic_name": "Cetirizine",
    "category": "Second-Generation Antihistamine",
    "uses": "Relief of allergy symptoms such as running nose, sneezing, watery eyes, itching, and hives.",
    "how_it_works": "Selectively blocks peripheral histamine H1 receptors, stopping the allergic response.",
    "dosage": "Adults: 5 mg to 10 mg once daily, preferably in the evening.",
    "how_to_take": "Swallow the tablet with a glass of water. Can be taken with or without food.",
    "common_side_effects": "Drowsiness, dry mouth, tiredness, headache, or sore throat.",
    "serious_side_effects": "Fast or irregular heartbeat, severe dizziness, restlessness, or difficulty urinating.",
    "precautions": "Avoid driving or operating machinery if you experience drowsiness. Limit alcohol consumption.",
    "interactions": "Sedatives, tranquilizers, alcohol, or muscle relaxants (increases drowsiness).",
    "warnings": "Use with caution in elderly patients, as they may be more sensitive to drowsiness and urinary retention.",
    "pregnancy_safety": "Generally considered safe. Category B. Consult doctor before taking.",
    "breastfeeding_safety": "Not recommended as cetirizine passes into breast milk and can cause drowsiness in the infant.",
    "storage": "Store in dry place below 25°C."
}

allegra_info = {
    "generic_name": "Fexofenadine",
    "category": "Non-Sedating Antihistamine",
    "uses": "Relief of seasonal allergic rhinitis (sneezing, runny nose, itchy throat) and chronic skin itching/hives.",
    "how_it_works": "Blocks histamine H1 receptors. Does not cross the blood-brain barrier, making it truly non-drowsy.",
    "dosage": "Adults: 120 mg to 180 mg once daily with water.",
    "how_to_take": "Take with water. Do not take with fruit juice (apple, orange, or grapefruit) as it reduces drug absorption.",
    "common_side_effects": "Headache, drowsiness (rare), nausea, or dizziness.",
    "serious_side_effects": "Severe allergic reaction, chest tightness, or swelling.",
    "precautions": "Do not take within 2 hours of taking aluminum/magnesium antacids.",
    "interactions": "Erythromycin, Ketoconazole (increases fexofenadine blood levels), Antacids.",
    "warnings": "Check with doctor if you have kidney disease, as dosage adjustment may be needed.",
    "pregnancy_safety": "Use only if benefits outweigh risks. Consult doctor.",
    "breastfeeding_safety": "Use with caution. Excreted in breast milk. Consult doctor.",
    "storage": "Store at room temperature between 20°C and 25°C."
}

montek_lc_info = {
    "generic_name": "Montelukast & Levocetirizine",
    "category": "Leukotriene Receptor Antagonist & Antihistamine Combo",
    "uses": "Treatment of allergic rhinitis, asthma symptoms, allergic bronchitis, sneezing, and runny nose.",
    "how_it_works": "Levocetirizine blocks histamine; Montelukast blocks leukotrienes, reducing inflammation and mucus in the airways.",
    "dosage": "Adults: 1 tablet (10 mg montelukast + 5 mg levocetirizine) once daily, preferably at bedtime.",
    "how_to_take": "Take in the evening with or without food. Swallow the tablet whole with a glass of water.",
    "common_side_effects": "Dry mouth, headache, sleepiness, fatigue, mild abdominal pain, or upper respiratory infection.",
    "serious_side_effects": "Neuropsychiatric changes (mood swings, aggression, suicidal thoughts - due to montelukast), severe skin rash.",
    "precautions": "Monitor for any unusual changes in mood or behavior. Avoid alcohol and driving.",
    "interactions": "Phenobarbital, Phenytoin, Rifampicin (reduces montelukast levels).",
    "warnings": "Do not use to treat acute asthma attacks. Have your quick-relief inhaler ready for emergencies.",
    "pregnancy_safety": "Not recommended unless clearly needed and prescribed by a doctor.",
    "breastfeeding_safety": "Avoid. Both active ingredients pass into breast milk and may affect the baby.",
    "storage": "Store in original package below 30°C to protect from light and moisture."
}

benadryl_info = {
    "generic_name": "Diphenhydramine",
    "category": "Sedating Antihistamine & Cough Suppressant",
    "uses": "Relief of cough, runny nose, sneezing, itchy watery eyes, and symptoms of the common cold.",
    "how_it_works": "Blocks histamine action and has central antitussive effects in the brain to suppress cough.",
    "dosage": "Adults: 10 ml (2 teaspoons) every 4 to 6 hours as needed.",
    "how_to_take": "Measure dose carefully with a measuring cup. Take with or without food.",
    "common_side_effects": "Marked drowsiness, dry mouth, blurred vision, constipation, or dizziness.",
    "serious_side_effects": "Confusion, rapid heart rate, difficulty urinating, or seizures.",
    "precautions": "Do not drive, operate heavy machinery, or consume alcohol. Avoid in glaucoma or enlarged prostate.",
    "interactions": "Alcohol, sleeping pills, sedatives, muscle relaxants.",
    "warnings": "May cause excitability in children. Do not use to make a child sleepy.",
    "pregnancy_safety": "Use only under medical advice. Avoid during late pregnancy.",
    "breastfeeding_safety": "Not recommended. Excreted in breast milk and may cause sedation/excitability in infants.",
    "storage": "Store below 25°C. Do not freeze."
}

cough_syrup_info = {
    "generic_name": "Ambroxol, Levosalbutamol & Guaiphenesin",
    "category": "Mucolytic, Bronchodilator & Expectorant Combo",
    "uses": "Relief of wet cough, chest congestion, asthma symptoms, and bronchitis.",
    "how_it_works": "Ambroxol thins mucus; Guaiphenesin increases mucus excretion; Levosalbutamol relaxes airway muscles to make breathing easier.",
    "dosage": "Adults: 5-10 ml, 3 times a day or as directed by a doctor.",
    "how_to_take": "Take with or without food. Measure with a spoon/cup. Stay well hydrated to help thin mucus.",
    "common_side_effects": "Nausea, vomiting, diarrhea, tremors, headache, or fast heart rate.",
    "serious_side_effects": "Chest pain, irregular heartbeats, severe allergic rash, or muscle cramps.",
    "precautions": "Caution in patients with high blood pressure, heart disease, thyroid issues, or diabetes.",
    "interactions": "Beta-blockers (like Propranolol), diuretics, other bronchodilators.",
    "warnings": "Consult a doctor if cough lasts more than 7 days, recurs, or is accompanied by fever or rash.",
    "pregnancy_safety": "Not recommended during the first trimester. Consult doctor.",
    "breastfeeding_safety": "Consult doctor before use, as salbutamol may pass into breast milk.",
    "storage": "Store below 30°C in a dark place. Keep bottle tightly closed."
}

sinarest_info = {
    "generic_name": "Chlorpheniramine, Paracetamol & Phenylephrine",
    "category": "Antihistamine, Analgesic & Decongestant Combo",
    "uses": "Treatment of symptoms of common cold, flu, sinus congestion, headache, fever, runny nose, and watery eyes.",
    "how_it_works": "Paracetamol reduces pain/fever; Chlorpheniramine stops allergies; Phenylephrine constricts blood vessels in nasal passages to relieve congestion.",
    "dosage": "Adults: 1 tablet 3-4 times a day as prescribed.",
    "how_to_take": "Take with water. Can be taken with or without food. Space doses at least 4-6 hours apart.",
    "common_side_effects": "Drowsiness, dry mouth, headache, mild nausea, or blurred vision.",
    "serious_side_effects": "Severe raise in blood pressure, heart palpitations, severe insomnia, or difficulty urinating.",
    "precautions": "Do not take other paracetamol-containing products. Avoid alcohol. Caution in high blood pressure or diabetes.",
    "interactions": "MAO inhibitors, antidepressants, antihypertensive drugs, sedatives.",
    "warnings": "May cause severe drowsiness. Do not drive or operate machinery while taking this medication.",
    "pregnancy_safety": "Not recommended during pregnancy unless explicitly prescribed by a doctor.",
    "breastfeeding_safety": "Avoid. Active decongestants and antihistamines can pass into breast milk and affect the baby.",
    "storage": "Store below 30°C in a dry place. Protect from direct heat."
}

ors_info = {
    "generic_name": "Oral Rehydration Salts (ORS)",
    "category": "Electrolyte Rehydrant",
    "uses": "Restores lost fluids and electrolytes due to diarrhea, vomiting, dehydration, or heavy sweating during hot weather/exercise.",
    "how_it_works": "Provides glucose, sodium, potassium, and chloride in an isotonic ratio that accelerates water absorption in the intestines.",
    "dosage": "Dissolve the entire contents of a packet in 1 liter (or as specified) of clean drinking water. Drink throughout the day.",
    "how_to_take": "Always dissolve ONLY in water. Do not mix with milk, juice, or soup. Do not boil the prepared solution.",
    "common_side_effects": "None when mixed in the correct volume of water.",
    "serious_side_effects": "Nausea or vomiting if consumed too quickly; salt overload if mixed with too little water.",
    "precautions": "Use clean, boiled and cooled drinking water. Discard any unused solution after 24 hours.",
    "interactions": "No major interactions. Safe with other medications.",
    "warnings": "In patients with severe kidney disease, caution is needed when taking potassium-rich solutions.",
    "pregnancy_safety": "Completely safe. Highly recommended for dehydration during pregnancy.",
    "breastfeeding_safety": "Completely safe and recommended for nursing mothers experiencing dehydration.",
    "storage": "Store packets in a dry place below 30°C. Protect from moisture."
}

shelcal_info = {
    "generic_name": "Calcium Carbonate & Vitamin D3",
    "category": "Mineral & Vitamin Supplement",
    "uses": "Prevention and treatment of calcium deficiency, osteoporosis, bone weakness, and supporting joint health.",
    "how_it_works": "Calcium builds and maintains bones; Vitamin D3 enhances intestinal calcium absorption.",
    "dosage": "Adults: 1 tablet daily or as directed by a doctor.",
    "how_to_take": "Take after meals, as calcium carbonate requires stomach acid for optimal absorption. Swallow with water.",
    "common_side_effects": "Constipation, gas, bloating, or mild stomach upset.",
    "serious_side_effects": "Hypercalcemia (high blood calcium levels causing nausea, weakness, confusion), kidney stones.",
    "precautions": "Drink plenty of water to prevent constipation. Caution in history of kidney stones.",
    "interactions": "Iron supplements, Tetracycline antibiotics, Thyroid medicines (take calcium at least 2-4 hours apart).",
    "warnings": "Do not take high doses of calcium supplements without getting your blood levels checked.",
    "pregnancy_safety": "Safe and commonly prescribed during pregnancy to support fetal bone development.",
    "breastfeeding_safety": "Safe. Both calcium and Vitamin D are excreted in breast milk and support infant development.",
    "storage": "Store in a cool, dry place. Protect from heat and moisture."
}

vitamin_supplement_info = {
    "generic_name": "Multivitamins & Minerals",
    "category": "Nutritional Supplement",
    "uses": "Treatment of vitamin deficiencies, support immunity, build stamina, reduce weakness, and maintain general wellness.",
    "how_it_works": "Supplies essential micronutrients needed for cell repair, immune response, and energy metabolism.",
    "dosage": "Adults: 1 capsule/tablet daily after meals.",
    "how_to_take": "Swallow whole with water. Avoid taking on an empty stomach to prevent mild nausea.",
    "common_side_effects": "Mild stomach upset, yellow discoloration of urine (due to Vitamin B2), or metallic taste.",
    "serious_side_effects": "Rare. Allergic reaction, breathing trouble, or severe dizziness (if allergic).",
    "precautions": "Do not exceed the recommended daily dose. Inform doctor of any pre-existing health conditions.",
    "interactions": "Antacids, certain antibiotics, and thyroid medications.",
    "warnings": "Supplements are not a substitute for a balanced diet. Do not double-dose.",
    "pregnancy_safety": "Safe, but consult obstetrician to ensure no overlap with prenatal vitamins.",
    "breastfeeding_safety": "Safe. Recommended to consult doctor to ensure optimal dosage.",
    "storage": "Store in a cool, dry place below 25°C, protected from light."
}

limcee_info = {
    "generic_name": "Vitamin C (Ascorbic Acid)",
    "category": "Antioxidant / Vitamin Supplement",
    "uses": "Prevention and treatment of scurvy, boosting immune health, aiding wound healing, and improving iron absorption.",
    "how_it_works": "Acts as a powerful antioxidant, cofactor in collagen synthesis, and supports white blood cell functions.",
    "dosage": "Adults: 1 chewable tablet (500 mg) daily or as recommended by a physician.",
    "how_to_take": "Chew the tablet thoroughly before swallowing. Can be taken with or without food.",
    "common_side_effects": "Mild diarrhea, stomach cramps, or nausea if taken in high doses.",
    "serious_side_effects": "Kidney stones (with long-term massive doses exceeding 2000mg/day).",
    "precautions": "Caution in patients with history of kidney stones or G6PD deficiency.",
    "interactions": "Iron supplements (increases absorption), oral contraceptives, antacids containing aluminum.",
    "warnings": "Do not exceed recommended doses as high Vitamin C intake can lead to digestive discomfort.",
    "pregnancy_safety": "Safe and recommended, but stay within the recommended daily allowance (RDA) values.",
    "breastfeeding_safety": "Safe and compatible. It naturally passes into breast milk to benefit the infant.",
    "storage": "Store below 25°C in a dry place. Protect from heat and moisture."
}

topical_gel_info = {
    "generic_name": "Diclofenac, Methyl Salicylate & Menthol Gel",
    "category": "Topical Analgesic & Anti-inflammatory Gel",
    "uses": "Local relief from muscle pain, backache, neck pain, sprains, strains, joint pain, and sports injuries.",
    "how_it_works": "Diclofenac penetrates skin to block pain/inflammation enzymes; Methyl Salicylate and Menthol produce a warming and cooling effect to distract from pain.",
    "dosage": "Apply a thin layer to the affected area 3-4 times daily, massaging gently.",
    "how_to_take": "Wash hands before and after application. Apply only to clean, dry, unbroken skin.",
    "common_side_effects": "Mild skin irritation, redness, itching, or dryness at application site.",
    "serious_side_effects": "Severe skin burns, peeling, breathing difficulty, or systemic NSAID allergic reactions (rare).",
    "precautions": "Do not apply to open wounds, cuts, eyes, or mucous membranes. Do not wrap with tight bandages.",
    "interactions": "Minimal systemic absorption, but caution if taking other oral NSAIDs (like Ibuprofen).",
    "warnings": "For external use only. Discontinue immediately if severe burning or skin rash occurs.",
    "pregnancy_safety": "Avoid applying in the third trimester of pregnancy due to risks of systemic absorption.",
    "breastfeeding_safety": "Generally safe. Do not apply on or near the breasts to prevent infant contact.",
    "storage": "Store below 30°C. Do not freeze. Keep tube tightly closed after use."
}

betadine_info = {
    "generic_name": "Povidone-Iodine",
    "category": "Antiseptic & Disinfectant",
    "uses": "Prevention and treatment of infections in minor cuts, scrapes, burns, and surgical wounds.",
    "how_it_works": "Releases free iodine which oxidizes microbial proteins and essential nucleic acids, killing bacteria, viruses, and fungi.",
    "dosage": "Apply a small amount to the cleaned affected area 1 to 3 times daily. May be covered with a sterile bandage.",
    "how_to_take": "Clean the wound and dry it before application. For external topical use only.",
    "common_side_effects": "Mild skin irritation, redness, or staining of the skin (temporary brown stain).",
    "serious_side_effects": "Allergic contact dermatitis, thyroid dysfunction (if applied on large deep wounds for long periods).",
    "precautions": "Avoid getting in the eyes. Caution in patients with thyroid disorders.",
    "interactions": "Do not use with hydrogen peroxide, silver, or taurolidine antiseptics.",
    "warnings": "Do not apply over large areas of the body or for longer than 7-10 days without consulting a doctor.",
    "pregnancy_safety": "Use with caution. Prolonged use can lead to absorption of iodine, potentially affecting fetal thyroid.",
    "breastfeeding_safety": "Use with caution. Avoid applying to large areas or on the chest area.",
    "storage": "Store below 25°C in a dry place. Keep out of reach of children."
}

diabetes_info = {
    "generic_name": "Metformin",
    "category": "Oral Antidiabetic (Biguanide)",
    "uses": "Management of Type 2 Diabetes Mellitus, helping lower blood glucose levels. Also used off-label for PCOS.",
    "how_it_works": "Decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity.",
    "dosage": "Adults: Usually starts at 500 mg once or twice daily, adjusted gradually. Maximum daily dose is 2000-2500 mg.",
    "how_to_take": "Take with meals to reduce the risk of gastrointestinal side effects (nausea, metallic taste, cramps).",
    "common_side_effects": "Nausea, vomiting, diarrhea, abdominal pain, loss of appetite, or metallic taste.",
    "serious_side_effects": "Lactic acidosis (rare but life-threatening build-up of lactic acid in the blood), vitamin B12 deficiency.",
    "precautions": "Contraindicated in severe kidney failure, acute heart failure, or severe dehydration. Check kidney function regularly.",
    "interactions": "Contrast dyes (injectable iodine), alcohol (increases risk of lactic acidosis), cimetidine, diuretics.",
    "warnings": "Avoid excessive alcohol while taking Metformin. Discontinue drug temporarily before undergoing surgeries or imaging with contrast.",
    "pregnancy_safety": "Often used, but insulin is preferred. Seek specialist advice.",
    "breastfeeding_safety": "Passes into breast milk in small quantities. Generally considered acceptable, consult doctor.",
    "storage": "Store below 30°C in dry blister packs."
}

DRUGS_DB = {}

# Seed Paracetamol varieties
for brand in ["Paracetamol", "Dolo 650", "Crocin", "Calpol"]:
    DRUGS_DB[brand.lower()] = dict(paracetamol_info, medicine_name=brand)
    if brand == "Dolo 650":
        DRUGS_DB[brand.lower()]["dosage"] = "Adults: 1 tablet (650 mg) every 4-6 hours as needed. Maximum 4 tablets in 24 hours."

# Combiflam
DRUGS_DB["combiflam"] = {
    "medicine_name": "Combiflam",
    "generic_name": "Ibuprofen & Paracetamol",
    "category": "Non-Steroidal Anti-Inflammatory Drug (NSAID) & Analgesic Combo",
    "uses": "Relief of inflammatory pain, joint stiffness, arthritis, dental pain, backache, and headache.",
    "how_it_works": "Ibuprofen inhibits prostaglandin synthesis peripherally to reduce inflammation and pain; Paracetamol works centrally to reduce pain and fever.",
    "dosage": "Adults: 1 tablet 2-3 times daily, preferably after meals. Do not exceed 3 tablets in 24 hours.",
    "how_to_take": "Always take after food or with milk to reduce the risk of gastrointestinal irritation and stomach upset.",
    "common_side_effects": "Heartburn, indigestion, nausea, vomiting, dizziness, or mild diarrhea.",
    "serious_side_effects": "Gastrointestinal bleeding (black tarry stools), stomach ulcers, chest pain, shortness of breath, or swelling of limbs.",
    "precautions": "Contraindicated in active stomach ulcers, severe heart failure, or asthma triggered by NSAIDs.",
    "interactions": "Aspirin, oral anticoagulants (Warfarin), antihypertensives, corticosteroids, and lithium.",
    "warnings": "Long term use increases risk of heart attack, stroke, and severe stomach bleeding. Use the shortest effective duration.",
    "pregnancy_safety": "Avoid, especially in the third trimester (may cause premature closure of ductus arteriosus).",
    "breastfeeding_safety": "Use with caution. Consult doctor as ibuprofen and paracetamol pass into breast milk.",
    "storage": "Store below 25°C in a dry place. Protect from light."
}

# Azithromycin
for brand in ["Azithromycin", "Azithral"]:
    DRUGS_DB[brand.lower()] = dict(antibiotic_info, medicine_name=brand)

# Amoxicillin / Augmentin
DRUGS_DB["amoxicillin"] = dict(amoxicillin_info, medicine_name="Amoxicillin")
DRUGS_DB["augmentin"] = dict(augmentin_info, medicine_name="Augmentin")

# PPIs
for brand in ["Pantop", "Pantocid"]:
    DRUGS_DB[brand.lower()] = dict(ppi_info, medicine_name=brand)

# Pan D
DRUGS_DB["pan d"] = {
    "medicine_name": "Pan D",
    "generic_name": "Pantoprazole & Domperidone",
    "category": "Antiacid Proton Pump Inhibitor & Prokinetic Combo",
    "uses": "Relief from acid reflux, heartburn, indigestion accompanied by nausea, vomiting, and upper abdominal pain.",
    "how_it_works": "Pantoprazole reduces stomach acid; Domperidone acts on the upper digestive tract to speed up stomach emptying and prevent nausea.",
    "dosage": "Adults: 1 capsule daily in the morning, 30 to 60 minutes before the first meal (breakfast).",
    "how_to_take": "Swallow the capsule whole with water on an empty stomach. Do not open or chew the capsule.",
    "common_side_effects": "Dry mouth, diarrhea, headache, flatulence, or weakness.",
    "serious_side_effects": "Palpitations, irregular heartbeats, muscle spasms, breast swelling/discharge (due to domperidone).",
    "precautions": "Caution in patients with cardiac rhythm disorders, kidney/liver disease, or low magnesium levels.",
    "interactions": "Ketoconazole, Erythromycin, Amiodarone, other medications that affect heart rhythm.",
    "warnings": "Domperidone may increase the risk of heart rhythm disorders, especially in elderly patients or at high doses.",
    "pregnancy_safety": "Not recommended during pregnancy unless explicitly deemed essential by your physician.",
    "breastfeeding_safety": "Excreted in small amounts in breast milk. Generally not recommended; consult a doctor.",
    "storage": "Store below 30°C in a cool and dry place."
}

DRUGS_DB["rantac"] = dict(rantac_info, medicine_name="Rantac")

# Antacid gels
for brand in ["Gelusil", "Digene"]:
    DRUGS_DB[brand.lower()] = dict(antacid_gel_info, medicine_name=brand)

# Antihistamines
DRUGS_DB["cetirizine"] = dict(antihistamine_info, medicine_name="Cetirizine")
DRUGS_DB["allegra"] = dict(allegra_info, medicine_name="Allegra")
DRUGS_DB["montek lc"] = dict(montek_lc_info, medicine_name="Montek LC")

# Cough and cold
DRUGS_DB["benadryl"] = dict(benadryl_info, medicine_name="Benadryl")
for brand in ["ascoril", "corex"]:
    DRUGS_DB[brand.lower()] = dict(cough_syrup_info, medicine_name=brand.capitalize())
DRUGS_DB["sinarest"] = dict(sinarest_info, medicine_name="Sinarest")

# ORS
for brand in ["ors", "electral"]:
    DRUGS_DB[brand.lower()] = dict(ors_info, medicine_name=brand.upper())

# Vitamins
DRUGS_DB["shelcal"] = dict(shelcal_info, medicine_name="Shelcal")
for brand in ["zincovit", "revital h", "becosules"]:
    DRUGS_DB[brand.lower()] = dict(vitamin_supplement_info, medicine_name=brand.capitalize() if brand != "revital h" else "Revital H")
DRUGS_DB["limcee"] = dict(limcee_info, medicine_name="Limcee")

# Gels
for brand in ["volini", "moov", "iodex"]:
    DRUGS_DB[brand.lower()] = dict(topical_gel_info, medicine_name=brand.capitalize())

DRUGS_DB["betadine"] = dict(betadine_info, medicine_name="Betadine")

# Chronics
DRUGS_DB["omez"] = {
    "medicine_name": "Omez",
    "generic_name": "Omeprazole",
    "category": "Proton Pump Inhibitor (PPI)",
    "uses": "Short-term treatment of active duodenal ulcers, gastric ulcers, GERD, acid acidity, and erosive esophagitis.",
    "how_it_works": "Suppresses gastric acid secretion by specific inhibition of the H+/K+-ATPase enzyme system in the gastric parietal cells.",
    "dosage": "Adults: 20 mg once daily, taken 30-60 minutes before breakfast.",
    "how_to_take": "Swallow capsule whole. Do not open, crush, or chew. Take with a glass of water.",
    "common_side_effects": "Headache, abdominal pain, diarrhea, nausea, vomiting, or flatulence.",
    "serious_side_effects": "Bone fractures (long-term), kidney inflammation, low magnesium levels, severe diarrhea (C. diff).",
    "precautions": "Inform doctor of bone osteoporosis, low vitamin B12, or liver problems. Do not self-treat for more than 2 weeks.",
    "interactions": "Clopidogrel, Ketoconazole, Atazanavir, Mycophenolate Mofetil.",
    "warnings": "Long-term PPI use may hide gastric cancer symptoms. Consult doctor if symptoms worsen.",
    "pregnancy_safety": "Considered safe when clearly indicated, under professional recommendation.",
    "breastfeeding_safety": "Excreted in small amounts. Consult doctor before use.",
    "storage": "Store below 25°C, protect from moisture and light."
}

DRUGS_DB["ecosprin"] = {
    "medicine_name": "Ecosprin",
    "generic_name": "Aspirin (Acetylsalicylic Acid)",
    "category": "Antiplatelet / Blood Thinner",
    "uses": "Prevention of heart attack, stroke, and angina in high-risk patients. Also used at higher doses for pain and fever.",
    "how_it_works": "Irreversibly inhibits COX-1 enzyme, stopping platelet aggregation (clotting) for the lifespan of the platelet.",
    "dosage": "Cardioprotection: 75 mg to 150 mg once daily, as prescribed by a cardiologist.",
    "how_to_take": "Swallow the enteric-coated tablet whole. Always take with or immediately after food to protect stomach lining.",
    "common_side_effects": "Heartburn, nausea, indigestion, or increased bleeding tendency (bruising, nosebleeds).",
    "serious_side_effects": "Gastrointestinal bleeding (black stools, vomiting blood), tinnitus (ringing in ears), severe allergic asthma.",
    "precautions": "Contraindicated in active bleeding disorders (hemophilia), bleeding stomach ulcers, or severe kidney/liver failure.",
    "interactions": "Other blood thinners (Warfarin, Clopidogrel), NSAIDs (Ibuprofen), steroids (increases ulcer risk).",
    "warnings": "Never give to children or teenagers with fever due to the risk of Reye's syndrome (a fatal brain and liver condition).",
    "pregnancy_safety": "Avoid in high doses. Low-dose (75-150mg) is sometimes prescribed under strict obstetric guidance.",
    "breastfeeding_safety": "Not recommended in regular doses. Consult doctor.",
    "storage": "Store below 25°C in a dry place. Keep protected from humidity."
}

# Diabetes
for brand in ["metformin", "glycomet"]:
    DRUGS_DB[brand.lower()] = dict(diabetes_info, medicine_name=brand.capitalize())

DRUGS_DB["telma"] = {
    "medicine_name": "Telma",
    "generic_name": "Telmisartan",
    "category": "Antihypertensive (Angiotensin II Receptor Blocker - ARB)",
    "uses": "Treatment of high blood pressure (hypertension) and reducing the risk of heart attack, stroke, or death in high-risk patients.",
    "how_it_works": "Blocks angiotensin II receptors, preventing blood vessels from constricting, which lowers blood pressure.",
    "dosage": "Adults: 40 mg to 80 mg once daily, taken at the same time each day.",
    "how_to_take": "Swallow the tablet whole with a glass of water. Can be taken with or without food.",
    "common_side_effects": "Dizziness, sinus pain, back pain, diarrhea, or pharyngitis.",
    "serious_side_effects": "Hyperkalemia (high blood potassium levels), kidney function deterioration, low blood pressure, swelling.",
    "precautions": "Do not take potassium supplements without checking with your doctor. Monitor kidney function and potassium levels.",
    "interactions": "ACE inhibitors, Aliskiren, Potassium-sparing diuretics, Lithium, NSAIDs.",
    "warnings": "Strictly contraindicated during pregnancy. May cause serious injury or death to the developing fetus.",
    "pregnancy_safety": "Contraindicated. Discontinue immediately if pregnancy is detected.",
    "breastfeeding_safety": "Not recommended. Excreted in animal milk. Consult doctor for alternative antihypertensive agents.",
    "storage": "Store in the original package below 30°C to protect from moisture."
}

DRUGS_DB["amlodipine"] = {
    "medicine_name": "Amlodipine",
    "generic_name": "Amlodipine Besylate",
    "category": "Antihypertensive (Calcium Channel Blocker)",
    "uses": "Treatment of high blood pressure (hypertension) and chest pain (angina).",
    "how_it_works": "Relaxes the smooth muscle cells of coronary and peripheral arteries, widening the vessels and reducing workload on the heart.",
    "dosage": "Adults: 5 mg to 10 mg once daily.",
    "how_to_take": "Take at the same time daily, with or without food.",
    "common_side_effects": "Swelling of ankles/feet (peripheral edema), fatigue, flushing, palpitations, or headache.",
    "serious_side_effects": "Worsening chest pain, heart attack symptoms (rare), severe dizziness, or fainting.",
    "precautions": "Caution in severe liver disease. Monitor blood pressure closely during initial treatment.",
    "interactions": "Simvastatin (requires lowering simvastatin dose), Ketoconazole, Cyclosporine, blood pressure lowering agents.",
    "warnings": "Do not stop taking amlodipine suddenly, as it can cause rebound high blood pressure or angina attacks.",
    "pregnancy_safety": "Use only if benefit outweighs risk. Consult doctor.",
    "breastfeeding_safety": "Amlodipine passes into breast milk. Generally considered safe, but consult physician.",
    "storage": "Store between 20°C and 25°C in a dry place."
}

DRUGS_DB["thyronorm"] = {
    "medicine_name": "Thyronorm",
    "generic_name": "Levothyroxine Sodium",
    "category": "Thyroid Hormone Replacement",
    "uses": "Treatment of hypothyroidism (underactive thyroid gland) and thyroid goiter.",
    "how_it_works": "Replaces the natural thyroid hormone thyroxine (T4) which is deficient in the body, restoring normal metabolism.",
    "dosage": "Individualized: Usually starts at 12.5 mcg to 100 mcg once daily, adjusted based on TSH blood test results.",
    "how_to_take": "Take on an empty stomach in the morning, at least 30-60 minutes before breakfast, with a full glass of water.",
    "common_side_effects": "Generally none if dose is correct. If dose is too high: palpitations, anxiety, weight loss, diarrhea.",
    "serious_side_effects": "Chest pain, rapid heart rate, breathing trouble (signs of hyperthyroidism/overdose).",
    "precautions": "Do not take calcium, iron, or antacids within 4 hours of taking thyronorm, as they block absorption.",
    "interactions": "Calcium carbonate, Ferrous sulfate, Antacids, Warfarin, Insulin.",
    "warnings": "Therapy is usually lifelong. Periodic blood tests (TSH) are required to monitor dosage accuracy.",
    "pregnancy_safety": "Completely safe. Dosage requirements often increase during pregnancy; consult endocrinologist immediately.",
    "breastfeeding_safety": "Safe and compatible. It naturally supports healthy metabolism in both mother and baby.",
    "storage": "Store below 25°C. Protect from light and moisture."
}


def get_autocomplete_suggestions(query, limit=10):
    """
    Search the in-memory database for partial matches on name or generic name.
    """
    if not query:
        return []
    q = query.strip().lower()
    suggestions = []
    
    # Priority 1: Exact prefix matches of medicine name or generic name
    for key, drug in DRUGS_DB.items():
        name = drug.get("medicine_name", "").strip()
        generic = drug.get("generic_name", "").strip()
        
        name_lower = name.lower()
        generic_lower = generic.lower()
        
        if name_lower.startswith(q) or generic_lower.startswith(q):
            suggestions.append({
                "name": name,
                "generic_name": generic
            })
            
    # Priority 2: Substring matches inside medicine name or generic name
    if len(suggestions) < limit:
        for key, drug in DRUGS_DB.items():
            name = drug.get("medicine_name", "").strip()
            generic = drug.get("generic_name", "").strip()
            
            name_lower = name.lower()
            generic_lower = generic.lower()
            
            # Skip if already added
            if name_lower.startswith(q) or generic_lower.startswith(q):
                continue
                
            if q in name_lower or q in generic_lower:
                suggestions.append({
                    "name": name,
                    "generic_name": generic
                })
                
    # Deduplicate list
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        s_tuple = (s["name"], s["generic_name"])
        if s_tuple not in seen:
            seen.add(s_tuple)
            unique_suggestions.append(s)
            if len(unique_suggestions) >= limit:
                break
                
    return unique_suggestions


def find_spelling_suggestion(query):
    """
    Tries to match query against medicine names or generic names using difflib.
    """
    q = query.strip().lower()
    targets = {}
    
    for key, drug in DRUGS_DB.items():
        name = drug.get("medicine_name", "")
        generic = drug.get("generic_name", "")
        targets[name.lower()] = name
        
        # Strip generic name brackets for cleaner matching
        generic_clean = generic.split('(')[0].strip()
        targets[generic_clean.lower()] = generic_clean

    matches = difflib.get_close_matches(q, targets.keys(), n=1, cutoff=0.7)
    if matches:
        return targets[matches[0]]
    return None


def query_llama_for_medicine(name):
    """
    Fallback to GROQ Llama 3.3 to fetch structured drug index information.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "found": False,
            "error": "Medicine not found in local database, and AI lookup is disabled (GROQ_API_KEY is not configured)."
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    system_prompt = (
        "You are an expert AI clinical pharmacist assistant. Provide reliable, detailed, "
        "and medically accurate information for the requested drug or medicine. "
        "Return the response ONLY as a valid JSON object matching the exact schema below. "
        "Do not include any intro, markdown, backticks, or explanation. Just return raw JSON.\n\n"
        "Schema:\n"
        "{\n"
        "  \"found\": true,\n"
        "  \"medicine_name\": \"[Common Brand Name or requested name]\",\n"
        "  \"generic_name\": \"[Generic active chemical composition]\",\n"
        "  \"category\": \"[Drug Class/Category]\",\n"
        "  \"uses\": \"[Primary indications]\",\n"
        "  \"how_it_works\": \"[Pharmacological action mechanism]\",\n"
        "  \"dosage\": \"[Standard adult dosage information]\",\n"
        "  \"how_to_take\": \"[Directions for safe ingestion/administration]\",\n"
        "  \"common_side_effects\": \"[Common mild side effects]\",\n"
        "  \"serious_side_effects\": \"[Serious side effects requiring medical intervention]\",\n"
        "  \"precautions\": \"[Warnings, contraindications, and things to avoid]\",\n"
        "  \"interactions\": \"[Major clinical drug/food interactions]\",\n"
        "  \"warnings\": \"[Severe boxed warnings or critical safety instructions]\",\n"
        "  \"pregnancy_safety\": \"[FDA pregnancy safety category/advice]\",\n"
        "  \"breastfeeding_safety\": \"[Excretion details & nursing compatibility]\",\n"
        "  \"storage\": \"[Storage temperature and humidity guidelines]\"\n"
        "}\n\n"
        "If the query is not a recognized drug, medicine, chemical compound, or health supplement, "
        "return: { \"found\": false }"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Lookup the medicine: {name}"}
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"}
    }

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            content = res_json['choices'][0]['message']['content'].strip()
            
            # Parse the inner JSON from LLM
            drug_data = json.loads(content)
            if not drug_data.get("found", True):
                return {
                    "found": False,
                    "error": f"Medicine '{name}' is not recognized as a valid drug or compound."
                }
                
            # Set required fields
            drug_data["found"] = True
            return drug_data
            
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return {
            "found": False,
            "error": f"AI Lookup failed with status code {e.code}. Details: {err_body}"
        }
    except Exception as e:
        return {
            "found": False,
            "error": f"AI Lookup connection error: {str(e)}"
        }


def lookup_medicine(name):
    """
    Lookup a medicine by name or generic composition in the database, with fuzzy spelling fallback and Llama fallback.
    """
    if not name:
        return {
            "found": False,
            "error": "Medicine name parameter is required."
        }

    query = name.strip()
    q_lower = query.lower()

    # 1. Try exact match on key (brand name) or value matches
    # Search brand name keys first
    if q_lower in DRUGS_DB:
        data = DRUGS_DB[q_lower]
        return dict(data, found=True)

    # Search generic name matches or brand names within objects
    for key, drug in DRUGS_DB.items():
        if drug.get("medicine_name", "").lower() == q_lower or drug.get("generic_name", "").lower() == q_lower:
            return dict(drug, found=True)

    # 2. Try partial/substring match in database (if unique or close)
    partial_matches = []
    for key, drug in DRUGS_DB.items():
        name_val = drug.get("medicine_name", "").lower()
        generic_val = drug.get("generic_name", "").lower()
        if q_lower in name_val or q_lower in generic_val:
            partial_matches.append(drug)
            
    if len(partial_matches) == 1:
        return dict(partial_matches[0], found=True)

    # 3. Try fuzzy spelling matching to offer "Did you mean?" suggestions
    spelling_suggestion = find_spelling_suggestion(query)
    if spelling_suggestion:
        return {
            "found": False,
            "has_suggestion": True,
            "suggestion": spelling_suggestion,
            "error": f"Did you mean {spelling_suggestion}?"
        }

    # 4. Fallback to Llama 3.3 dynamically
    return query_llama_for_medicine(query)
