import streamlit as st

# Configuration et police uniforme
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
    # Identification du client [cite: 2-4, 8]
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    frais_ouverture = 35.0 if dossier == "Non" else 0.0
    
    # Divulgations obligatoires [cite: 5, 6]
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS et infirmière uniquement) ?")

with col_adm2:
    # Localisation [cite: 10-12]
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    # Banque de mots-clés incluant les urgences mineures et bilans [cite: 13, 38-59]
    recherche = st.text_input("Quels sont vos symptômes ou le motif de consultation ?").lower()

    if recherche:
        t = {"prof": "IPS", "temps": "30", "prix": 0.0, "depot": 0.0, "annul": "48h", "est_sm": False, "prix_ipssm": 0.0}
        
        # --- MODULE SANTÉ MENTALE (SM) --- [cite: 14]
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            t["est_sm"] = True
            t["annul"] = "72h" # 
            
            # Sécurité immédiate [cite: 15, 16]
            st.error("🚨 **SÉCURITÉ :** Est-ce que vous avez des intentions de faire du mal à vous ou à autrui actuellement ?")
            danger = st.radio("Réponse du patient :", ["Non", "Oui"])
            
            if danger == "Oui":
                st.error("🚨 **ACTION IMMÉDIATE :** Veuillez composer le 911 ou vous présenter directement à l’urgence.")
            else:
                # Vérification de l'âge [cite: 18-20]
                age = st.number_input("Quel est votre âge ?", min_value=0, value=18)
                if age < 18:
                    st.warning("❌ Désolé, nous ne traitons pas la clientèle de moins de 18 ans.")
                else:
                    est_tda = "tda" in recherche or "tdah" in recherche # [cite: 21]
                    
                    # Points d'information (1 à 12) [cite: 27-37, 66]
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
                        "11. Vous recevrez un courriel de Telus Santé avec le lien de connexion.",
                        "12. Un questionnaire vous sera envoyé par courriel et doit être rempli avant le rendez-vous."
                    ]

                    with st.expander("📝 Informations obligatoires (IPSSM)", expanded=True):
                        for i, p in enumerate(points):
                            # Retirer points 1 et 8 pour TDA (déjà précisés dans le script)
                            if est_tda and (i == 0 or i == 7): continue
                            st.write(p)

                    if est_tda:
                        st.success("✅ **Protocole TDA/TDAH (2 consultations)**") # [cite: 22]
                        t.update({
                            "prof": "Infirmière (1h) + IPSSM (50min)",
                            "temps": "1h (Inf) et 50min (IPSSM)",
                            "prix": 195.0, # Consultation infirmière [cite: 23]
                            "prix_ipssm": 250.0, # Consultation IPSSM [cite: 24]
                            "depot": 100.0 # [cite: 25]
                        })
                    else:
                        st.success("✅ **Protocole Santé Mentale Générale**")
                        t.update({
                            "prof": "IPSSM (Télémédecine)",
                            "temps": "50", # [cite: 27]
                            "prix": 250.0, # [cite: 34]
                            "depot": 100.0 # [cite: 36]
                        })

        # --- MODULE URGENCE MINEURE / AUTRES --- 
        else:
            # Note sur les prélèvements à Jonquière vs St-Félicien 
            if lieu == "Jonquière":
                st.caption("ℹ️ Si un prélèvement est requis, des frais de 35$ s'ajouteront.")
            
            # Exemple pour l'infirmière (à compléter avec l'aide-mémoire)
            if any(x in recherche for x in ["lavage", "oreille", "strep"]):
                t.update({"prof": "Infirmière", "prix": 140.0, "annul": "24h", "temps": "20"})

        # --- ÉTAPE 3 : CONCLUSION ET SCRIPT --- [cite: 60]
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total_facture = t["prix"] + frais_ouverture
            msg_frais_ouv = f" (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            
            # Modes de paiement [cite: 67-69]
            if t["est_sm"]:
                paiement = "par téléphone par carte de crédit seulement"
            elif lieu == "Jonquière":
                paiement = "par carte débit, carte de crédit ou argent comptant"
            else:
                paiement = "par carte débit ou carte de crédit seulement"
            
            # Détail du prix pour TDA
            detail_prix = f"Le coût de la consultation est de **{total_facture:.2f} $**{msg_frais_ouv}."
            if "Infirmière" in t["prof"] and est_tda:
                detail_prix = f"Le coût est de **{total_facture:.2f} $**{msg_frais_ouv} pour l'infirmière et **{t['prix_ipssm']:.2f} $** pour l'IPSSM."

            script = f"""
            **Script de fin à lire au patient :**
            
            "La durée de votre rendez-vous sera de **{t['temps']} minutes**. 
            Notez que nous ne traiterons que votre problème mentionné; tout ajout supplémentaire peut entraîner des frais. [cite: 61, 62]
            
            **Frais et Annulation :**
            * {detail_prix}
            * Un dépôt de **{t['depot']:.2f} $** est requis pour le rendez-vous IPSSM. [cite: 25, 36]
            * Le paiement se fera **{paiement}**. [cite: 67-69]
            * Nous chargerons **50% des frais** en cas d'absence ou d'annulation moins de **{t['annul']}** avant le rendez-vous. 
            
            **Ponctualité :**
            * Veuillez vous {'connecter' if t['est_sm'] else 'présenter'} **5 à 10 minutes à l'avance**. [cite: 64]
            * Un retard de **10 minutes** est considéré comme une absence." [cite: 65]
            """
            st.info(script)
