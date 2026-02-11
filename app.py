import streamlit as st

# 1. Configuration et style
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
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS/Inf uniquement) ?")

with col_adm2:
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Quels sont les symptômes ou le motif ?").lower()

    if recherche:
        # Initialisation sécurisée pour éviter les erreurs de variables non définies
        t = {
            "prof": "À déterminer", "temps": "30", "prix": 0.0, "depot": 0.0, 
            "annul": "48h", "est_sm": False, "est_tda": False, "prix_ipssm": 0.0
        }
        frais_ouv = 35.0 if dossier == "Non" else 0.0
        
        # --- MODULE SANTÉ MENTALE ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            t["est_sm"] = True
            t["annul"] = "72h"
            t["est_tda"] = "tda" in recherche or "tdah" in recherche
            
            st.error("🚨 **SÉCURITÉ :** Avez-vous des intentions de faire du mal à vous ou à autrui actuellement ?")
            if st.radio("Réponse :", ["Non", "Oui"]) == "Oui":
                st.error("🚨 **ACTION :** Composez le 911 ou allez à l'urgence.")
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne traitons pas la clientèle de moins de 18 ans.")
            else:
                points = [
                    "1. Téléconsultation avec l’IPSSM d’une durée de 50 min.",
                    "2. Approche personnalisée selon votre condition.",
                    "3. Validation des antécédents personnels et familiaux.",
                    "4. Demande les investigations nécessaires.",
                    "5. Pose les diagnostics.",
                    "6. Prescrit et ajuste la médication au besoin.",
                    "7. Donne des arrêts de travail si nécessaire.",
                    "8. Coût de 250$ pour la première consultation.",
                    "9. Si nécessaire, les suivis sont de 20 min à 195$.",
                    "10. Un dépôt de 100$ est demandé avant la prise de rendez-vous.",
                    "11. Vous recevrez un courriel de Telus Santé avec le lien de connexion.",
                    "12. Un questionnaire vous sera envoyé et doit être rempli avant le RDV."
                ]
                with st.expander("📝 Informations obligatoires IPSSM", expanded=True):
                    st.markdown("\n".join([p for i, p in enumerate(points) if not (t["est_tda"] and i in [0, 7])]))

                if t["est_tda"]:
                    t.update({"prof": "Infirmière + IPSSM", "temps": "1h (Inf) + 50min (IPSSM)", "prix": 195.0, "prix_ipssm": 250.0, "depot": 100.0})
                else:
                    t.update({"prof": "IPSSM (Télémédecine)", "temps": "50", "prix": 250.0, "depot": 100.0})

        # --- MODULE CONSULTATIONS ÉVOLUTIVES (Simple/Prolongée/Complexe) ---
        elif any(x in recherche for x in ["simple", "prolongée", "complexe", "suivi", "bilan", "saaq"]):
            if "simple" in recherche:
                t.update({"prof": "Infirmière", "prix": 140.0, "temps": "20", "annul": "24h"})
            elif "prolongée" in recherche:
                t.update({"prof": "IPS", "prix": 180.0, "temps": "30", "annul": "48h"})
            else:
                # Bilan, SAAQ, Complexe
                prix_bilan = 395.0 if dossier == "Non" else 345.0
                t.update({"prof": "IPS", "prix": prix_bilan, "temps": "45-60", "annul": "48h"})

        # --- MODULE URGENCE MINEURE ---
        else:
            est_ips = st.checkbox("Le problème nécessite-t-il l'expertise de l'IPS (selon l'aide-mémoire) ?")
            
            # Grille de prix spécifique
            if any(x in recherche for x in ["vagin", "vulc", "urètre", "écoulement"]):
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 195.0 if est_ips else 175.0, "annul": "48h" if est_ips else "24h"})
            else:
                # Otite, Gorge, Sinus, Zona, etc.
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 180.0 if est_ips else 140.0, "annul": "48h" if est_ips else "24h"})
                if not est_ips and st.checkbox("Besoin d'un avis IPS (+25$) ?"):
                    t["prix"] += 25.0
            
            if lieu == "Jonquière" and st.checkbox("Prélèvement supplémentaire requis ? (+35$)"):
                t["prix"] += 35.0

        # --- ÉTAPE 3 : CONCLUSION ET SCRIPT ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Conclusion de l'appel")
            
            total = t["prix"] + frais_ouv
            msg_ouv = f" (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            
            if t["est_sm"]:
                paiement = "**par téléphone par carte de crédit seulement**"
            else:
                paiement = "par carte débit, carte de crédit ou argent comptant" if lieu == "Jonquière" else "par carte débit ou carte de crédit seulement"

            if t["est_tda"]:
                texte_prix = f"Le coût est de **{total:.2f} $**{msg_ouv} pour l'infirmière et **250.00 $** pour l'IPSSM."
            else:
                texte_prix = f"Le coût de la consultation est de **{total:.2f} $**{msg_ouv}."

            script = f"""
            > **Script de fin :**
            > "La durée de votre rendez-vous sera de **{t['temps']} minutes**. Nous ne traiterons que votre problème mentionné.
            > 
            > * {texte_prix}
            > * {'Un dépôt de 100$ est requis pour l\'IPSSM.' if t['depot'] > 0 else ''}
            > * Le paiement se fera {paiement}.
            > * Politique d'annulation : **{t['annul']}** d'avance, sinon **50% des frais** seront chargés.
            > * Arrivez **5 à 10 min** d'avance. Un retard de **10 min** est une absence."
            """
            st.info(script)

else:
    st.info("Veuillez valider l'identification et les divulgations pour débuter.")
