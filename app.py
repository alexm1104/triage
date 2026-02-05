import streamlit as st

# Configuration et Uniformisation de la police
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : ACCUEIL ET DIVULGATION ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True) # [cite: 2, 3, 8]
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?") # [cite: 5]
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS/Inf uniquement) ?") # [cite: 6]

with col_adm2:
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"]) # [cite: 10, 11, 12]

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Quels sont vos symptômes ?").lower() # [cite: 13]

    if recherche:
        t = {"prof": "IPS", "temps": "30 min", "prix": 0.0, "depot": 0.0, "annul": "48h", "note": ""}
        frais_ouv = 35.0 if dossier == "Non" else 0.0 # 
        
        # --- MODULE SANTÉ MENTALE ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"] # [cite: 14, 21, 26]
        
        if any(x in recherche for x in sm_keywords):
            st.error("🚨 **SÉCURITÉ :** Est-ce que vous avez des intentions de faire du mal à vous ou à autrui actuellement ?") # [cite: 15]
            danger = st.radio("Réponse du patient :", ["Non", "Oui"]) # [cite: 15, 17]
            
            if danger == "Oui":
                st.error("🚨 **ACTION IMMÉDIATE :** Veuillez composer le 911 ou vous présenter directement à l'urgence.") # [cite: 16]
            else:
                age = st.number_input("Quel est votre âge ?", min_value=0, value=18) # [cite: 18]
                if age < 18:
                    st.warning("❌ Désolé, nous ne traitons pas la clientèle de moins de 18 ans.") # [cite: 19]
                else:
                    est_tda = "tda" in recherche or "tdah" in recherche # [cite: 21]
                    
                    # Liste des 11 points (Sauf 1 et 8 pour TDA/TDAH) [cite: 27-37]
                    points = [
                        "1. Téléconsultation avec l’IPSSM d’une durée de 50 min.",
                        "2. Approche personnalisée selon votre condition.",
                        "3. Validation des antécédents personnels et familiaux.",
                        "4. Demande les investigations nécessaires (tests, etc.).",
                        "5. Pose les diagnostics.",
                        "6. Prescrit et ajuste la médication au besoin.",
                        "7. Donne des arrêts de travail si nécessaire.",
                        "8. Coût de 250$ pour la première consultation.",
                        "9. Si nécessaire, les suivis sont de 20 min à 195$.",
                        "10. Un dépôt de 100$ est demandé avant la prise de rendez-vous.",
                        "11. Vous recevrez un courriel de Telus Santé avec le lien de connexion."
                    ]

                    with st.expander("📝 Informations obligatoires (IPSSM)", expanded=True):
                        points_a_afficher = []
                        for i, p in enumerate(points):
                            if est_tda and (i == 0 or i == 7): # Enlever points 1 et 8 pour TDA
                                continue
                            points_a_afficher.append(p)
                        st.markdown("\n".join(points_a_afficher))

                    if est_tda:
                        t.update({
                            "prof": "Infirmière (1h) + IPSSM (50min)",
                            "temps": "1h (Inf) + 50min (IPSSM)", # 
                            "prix": 195.0, # Prix rencontre infirmière [cite: 23]
                            "depot": 100.0, # [cite: 25]
                            "annul": "72h", # [cite: 41]
                            "note": "Note : La consultation IPSSM de 50min (250$) suivra celle de l'infirmière."
                        })
                    else:
                        t.update({
                            "prof": "IPSSM (Télémédecine)",
                            "temps": "50 min", # [cite: 27]
                            "prix": 250.0, # [cite: 34]
                            "depot": 100.0, # [cite: 36]
                            "annul": "72h" # [cite: 41]
                        })

        # --- ÉTAPE 3 : RÉSULTATS ET SCRIPT FINAL ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total_facture = t["prix"] + frais_ouv
            msg_frais_ouv = " (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else "" # 
            
            # Modes de paiement par succursale
            paiement = "carte débit, carte de crédit ou argent comptant" if lieu == "Jonquière" else "carte débit ou carte de crédit seulement" # [cite: 45, 46]
            
            script = f"""
            **Script de fin à lire au patient :**
            
            "La durée de votre rendez-vous sera de **{t['temps']}**[cite: 39]. 
            Notez que nous ne traiterons que le problème mentionné; tout ajout supplémentaire peut entraîner des frais[cite: 40].
            
            **Frais et Annulation :**
            * Le coût de cette consultation est de **{total_facture:.2f} $**{msg_frais_ouv}.
            * Un dépôt de **{t['depot']:.2f} $** est requis lors de la prise de rendez-vous avec l'IPSSM[cite: 25, 36].
            * Les modes de paiement acceptés à **{lieu}** sont : {paiement}[cite: 45, 46].
            * Notre politique d'annulation est de **{t['annul']}**. En cas d'absence ou d'annulation tardive, **50% des frais** seront chargés à votre dossier[cite: 41].
            
            **Ponctualité :**
            * Veuillez vous connecter (ou vous présenter) **5 à 10 minutes à l'avance**[cite: 42]. 
            * Un retard de **10 minutes** est considéré comme une absence[cite: 43]."
            """
            st.info(script)
            if "IPSSM" in t["prof"]:
                st.write("📩 **Action secrétaire :** Faire parvenir le questionnaire à remplir avant le rendez-vous[cite: 44].")

else:
    st.info("Veuillez valider l'accueil et les divulgations pour débloquer le triage[cite: 5, 6, 10].")
