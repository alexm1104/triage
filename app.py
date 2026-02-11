import streamlit as st

# 1. Configuration et style
st.set_page_config(page_title="Triage Clinique IPS Santé Plus", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    .stAlert { border-radius: 10px; }
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
        # Initialisation sécurisée des variables pour éviter les erreurs "NameError"
        t = {
            "prof": "À déterminer", 
            "temps": "30", 
            "prix": 0.0, 
            "depot": 0.0, 
            "annul": "48h", 
            "est_sm": False, 
            "est_tda": False, 
            "prix_ipssm": 0.0
        }
        frais_ouv = 35.0 if dossier == "Non" else 0.0
        
        # --- LOGIQUE SANTÉ MENTALE ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            t["est_sm"] = True
            t["annul"] = "72h"
            t["est_tda"] = "tda" in recherche or "tdah" in recherche
            
            st.error("🚨 **SÉCURITÉ :** Avez-vous des intentions de faire du mal à vous ou à autrui actuellement ?")
            if st.radio("Réponse :", ["Non", "Oui"]) == "Oui":
                st.error("🚨 **ACTION :** Composez le 911 ou allez à l'urgence.")
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne voyons que les adultes (18+) en santé mentale.")
            else:
                # Affichage des 12 points IPSSM
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
                with st.expander("📝 Informations obligatoires IPSSM", expanded=True):
                    points_filtres = [p for i, p in enumerate(points) if not (t["est_tda"] and i in [0, 7])]
                    st.markdown("\n".join(points_filtres))

                if t["est_tda"]:
                    t.update({"prof": "Infirmière + IPSSM", "temps": "1h (Inf) + 50min (IPSSM)", "prix": 195.0, "prix_ipssm": 250.0, "depot": 100.0})
                else:
                    t.update({"prof": "IPSSM (Télémédecine)", "temps": "50", "prix": 250.0, "depot": 100.0})

        # --- LOGIQUE URGENCE MINEURE / GÉNÉRAL ---
        else:
            # Détermination Infirmière vs IPS (Selon votre liste)
            inf_keywords = ["lavage", "oreille", "strep", "injection", "pansement", "soins"]
            if any(x in recherche for x in inf_keywords):
                t.update({"prof": "Infirmière", "prix": 140.0, "annul": "24h", "temps": "20"})
            else:
                t.update({"prof": "IPS", "prix": 180.0, "annul": "48h", "temps": "30"})
            
            # Option Prélèvement (Jonquière seulement)
            if lieu == "Jonquière":
                if st.checkbox("Un prélèvement sera-t-il effectué ? (+35$)"):
                    t["prix"] += 35.0

        # --- ÉTAPE 3 : CONCLUSION ET SCRIPT ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Script de fin d'appel")
            
            total_facture = t["prix"] + frais_ouv
            msg_ouv = " (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            
            # Modes de paiement
            if t["est_sm"]:
                paiement = "**par téléphone par carte de crédit seulement**"
            elif lieu == "Jonquière":
                paiement = "par carte débit, carte de crédit ou argent comptant"
            else:
                paiement = "par carte débit ou carte de crédit seulement"

            # Détail prix spécifique TDA
            if t["est_tda"]:
                texte_prix = f"Le coût est de **{total_facture:.2f} $**{msg_ouv} pour l'infirmière et **{t['prix_ipssm']:.2f} $** pour l'IPSSM."
            else:
                texte_prix = f"Le coût de la consultation est de **{total_facture:.2f} $**{msg_ouv}."

            script = f"""
            > "La durée du rendez-vous sera de **{t['temps']} minutes**. 
            > Nous ne traiterons que votre problème mentionné; tout ajout peut entraîner des frais.
            > 
            > **Frais et Annulation :**
            > * {texte_prix}
            > * {'Un dépôt de 100$ est requis pour l\'IPSSM.' if t['depot'] > 0 else ''}
            > * Le paiement se fera {paiement}.
            > * Nous chargerons **50% des frais** en cas d'absence ou d'annulation moins de **{t['annul']}** à l'avance.
            > 
            > **Ponctualité :**
            > * Veuillez vous {'connecter' if t['est_sm'] else 'présenter'} **5 à 10 minutes à l'avance**. 
            > * Un retard de **10 minutes** est considéré comme une absence."
            """
            st.info(script)
