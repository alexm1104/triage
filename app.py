import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Triage IPS Santé Plus", page_icon="🏥", layout="centered")

# Style personnalisé pour correspondre à une image professionnelle
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant de Triage - Clinique IPS Santé Plus")
st.info("Outil d'aide à la décision pour la réception (Jonquière & Saint-Félicien)")

# --- COLLECTE DES DONNÉES ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nom_patient = st.text_input("Nom du patient (Optionnel)")
        point_service = st.selectbox("Point de service", ["Jonquière", "Saint-Félicien"])
    with col2:
        age = st.number_input("Âge du patient", min_value=0, max_value=115, value=18)
        nouveau_patient = st.toggle("Nouveau dossier (Frais d'ouverture 35$)")

st.subheader("Sélection du motif")
motif = st.selectbox("Quel est le problème de santé ?", [
    "-- Choisir un motif --",
    "Urgence Mineure (Otite, gorge, urinaire, ITSS, infection peau)",
    "Consultation Prolongée (Hypertension, douleur chronique, PAP test, 2 motifs)",
    "Bilan de Santé Complet (Examen physique + Prise de sang)",
    "TDA/H / Santé Mentale (Évaluation ou suivi)",
    "Soins Infirmiers (Lavage d'oreilles, injection, cryothérapie)",
    "Examen SAAQ (Conducteur)",
    "Cardiologie (CardioSTAT ou MAPA)"
])

# --- ALGORITHME DE TRIAGE ---
if motif != "-- Choisir un motif --":
    trajectoire = ""
    prof = ""
    temps = ""
    prix_base = 0.0
    alerte = ""

    if "Urgence Mineure" in motif:
        trajectoire, prof, temps, prix_base = "Aiguë", "IPS ou Infirmière", "20-30 min", 138.0
    
    elif "Consultation Prolongée" in motif:
        trajectoire, prof, temps, prix_base = "Complexe", "IPS", "45 min", 180.0
    
    elif "Bilan de Santé" in motif:
        trajectoire, prof, temps, prix_base = "Préventive", "IPS", "45-60 min", 350.0
    
    elif "TDA/H" in motif:
        if age < 18:
            alerte = "❌ ERREUR : L'IPSSM ne voit que la clientèle ADULTE. Rediriger vers le public ou pédiatrie."
        else:
            trajectoire, prof, temps, prix_base = "Santé Mentale", "IPSSM (Télémédecine)", "60 min", 250.0
            
    elif "Soins Infirmiers" in motif:
        trajectoire, prof, temps, prix_base = "Technique", "Infirmière", "30 min", 40.0
        
    elif "SAAQ" in motif:
        trajectoire, prof, temps, prix_base = "Administrative", "IPS", "30 min", 160.0
        
    elif "Cardiologie" in motif:
        type_cardio = st.radio("Type de test", ["CardioSTAT (ECG)", "MAPA (Pression)"])
        if "CardioSTAT" in type_cardio:
            trajectoire, prof, temps, prix_base = "Spécialisée", "IPS + Cardiologue", "Varie", 507.0
        else:
            trajectoire, prof, temps, prix_base = "Spécialisée", "Infirmière", "20 min", 60.0

    # --- AFFICHAGE DES RÉSULTATS ---
    if alerte:
        st.error(alerte)
    else:
        st.divider()
        st.subheader("📋 Résultat pour la secrétaire")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Professionnel", prof)
        c2.metric("Durée à bloquer", temps)
        c3.metric("Trajectoire", trajectoire)

        # Calcul financier
        frais_ouverture = 35.0 if nouveau_patient else 0.0
        sous_total = prix_base + frais_ouverture
        tps = sous_total * 0.05
        tvq = sous_total * 0.09975
        total = sous_total + tps + tvq

        st.markdown(f"""
        **Détails de la facturation :**
        * Consultation : {prix_base:.2f}$
        * Frais d'ouverture : {frais_ouverture:.2f}$
        * Taxes (TPS/TVQ) : {(tps+tvq):.2f}$
        
        ### **TOTAL À PAYER : {total:.2f} $**
        """)
        
        if point_service == "Saint-Félicien":
            st.warning("📍 Note : Nouveau point de service. Rappeler l'adresse au patient.")

st.sidebar.markdown("---")
st.sidebar.write("Propriété de Clinique IPS Santé Plus © 2026")
