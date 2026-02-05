import streamlit as st

# Configuration et Uniformisation de la police
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Assistant Triage - Clinique IPS Santé Plus")

# --- ÉTAPE 1 : ACCUEIL ET DIVULGATION ---
st.subheader("1️⃣ Accueil et Informations Légales")
col_adm1, col_adm2 = st.columns(2)

with col_adm1:
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS/Inf uniquement) ?")

with col_adm2:
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Quels sont vos symptômes ?").lower()

    if recherche:
        t = {"prof": "IPS", "temps": "30 min", "prix": 0.0, "depot": 0.0, "annul": "48h", "note": ""}
        frais_ouv = 35.0 if dossier == "Non" else 0.0
        
        # --- MODULE SANTÉ MENTALE ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            st.error("🚨 **SÉCURITÉ :** Est-ce que vous avez des intentions de faire du mal à vous ou à autrui actuellement ?")
            danger = st.radio("Réponse du patient :", ["Non", "Oui"])
            
            if danger == "Oui":
                st.error("🚨 **ACTION IMMÉDIATE :** Veuillez composer le 911 ou vous présenter directement à l'urgence.")
            else:
                age = st.number_input("Quel est votre âge ?", min_value=0, value=18)
                if age < 18:
                    st.warning("❌ Désolé, nous ne traitons pas la clientèle de moins de 18 ans en santé mentale.")
                else:
                    est_tda = "tda" in recherche or "tdah" in recherche
                    
                    # Reconstruction de la liste sans les points 1 et 8 si TDA
                    points_list = []
                    if not est_tda: points_list.append("1. Téléconsultation avec l’IPSSM d’une durée de 50 min.")
                    points_list.append("2. Approche personnalisée selon votre condition.")
                    points_list.append("3. Validation des antécédents personnels et familiaux.")
                    points_list.append("4. Demande les investigations nécessaires (tests, etc.).")
                    points_list.append("5. Pose les diagnostics.")
                    points_list.append("6. Prescrit et ajuste la médication au besoin.")
                    points_list.append("7. Donne des arrêts de travail si nécessaire.")
                    if not est_tda: points_list.append("8. Coût de 250$ pour la première consultation (Santé Mentale Générale).")
                    points_list.append("9. Si nécessaire, les suivis sont de 20 min à 195$.")
                    points_list.append("10. Un dépôt de 100$ est demandé avant la prise de rendez-vous.")
                    points_list.append("11. Vous recevrez un courriel de Telus Santé avec le lien de connexion.")

                    with st.expander("📝 Informations obligatoires (IPSSM)", expanded=True):
                        # On regroupe tout en une seule chaîne de caractères pour éviter les flèches
                        st.markdown("\n".join(points_list))

                    if est_tda:
                        st.success("✅ **Protocole TDA/TDAH (2 étapes)**")
                        t.update({
                            "prof": "Infirmière (1h) + IPSSM (50min)",
                            "temps": "1h (Inf) + 50min (IPSSM)",
                            "prix": 195.0, 
                            "depot": 100.0,
                            "annul": "72h",
                            "note": "Note : La consultation IPSSM suivra celle de l'infirmière (pas forcément le même jour)."
                        })
                    else:
                        st.success("✅ **Protocole Santé Mentale Générale**")
                        t.update({
                            "prof": "IPSSM (Télémédecine)",
                            "temps": "50 min",
                            "prix": 250.0,
                            "depot": 100.0,
                            "annul": "72h"
                        })

        # --- ÉTAPE 3 : RÉSULTATS ET SCRIPT FINAL ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total_facture = t["prix"] + frais_ouv
            msg_frais_ouv = " (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            
            script = f"""
            **Script de fin à lire au patient :**
            
            "La durée de votre rendez-vous sera de **{t['temps']}**. 
            Notez que nous ne traiterons que le problème mentionné; tout ajout supplémentaire peut entraîner des frais.
            
            **Frais et Annulation :**
            * Le coût de cette consultation est de **{total_facture:.2f} $**{msg_frais_ouv}.
            * Un dépôt de **{t['depot']:.2f} $** est requis lors de la prise de rendez-vous avec l'IPSSM.
            * Notre politique d'annulation est de **{t['annul']}**. En cas d'absence ou d'annulation tardive, **50% des frais** seront chargés à votre dossier.
            
            **Ponctualité :**
            * Veuillez vous connecter (ou vous présenter) **5 à 10 minutes à l'avance**. 
            * Un retard de **10 minutes** est considéré comme une absence."
            """
            st.info(script)

else:
    st.info("Veuillez valider l'accueil et les divulgations pour débloquer le triage.")
