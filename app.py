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
    # Identification [cite: 2, 8]
    dossier = st.radio("Avez-vous un dossier à la clinique ?", ["Oui", "Non"], horizontal=True)
    # Divulgations obligatoires [cite: 5-6]
    privé = st.toggle("Le patient sait que c'est une CLINIQUE PRIVÉE (frais à sa charge) ?")
    pas_medecin = st.toggle("Le patient sait qu'il n'y a PAS DE MÉDECIN (IPS et infirmière uniquement) ?")

with col_adm2:
    # Localisation [cite: 10-12]
    lieu = st.selectbox("Point de service :", ["-- Choisir --", "Jonquière", "Saint-Félicien"])

# --- DÉBLOCAGE DU TRIAGE ---
if privé and pas_medecin and lieu != "-- Choisir --":
    st.divider()
    st.subheader("2️⃣ Analyse du besoin (Recherche par mot-clé)")
    recherche = st.text_input("Quels sont les symptômes ou le motif ?").lower() # [cite: 13]

    if recherche:
        # Initialisation des paramètres par défaut
        t = {"prof": "À déterminer", "temps": "30", "prix": 0.0, "depot": 0.0, "annul": "48h", "est_sm": False, "est_tda": False, "besoin_avis": False}
        frais_ouv = 35.0 if dossier == "Non" else 0.0 # [cite: 4]
        
        # --- MODULE SANTÉ MENTALE (SM) ---
        sm_keywords = ["mentale", "anxiété", "dépression", "sommeil", "alimentaire", "burnout", "deuil", "séparation", "épuisement", "tda", "tdah"]
        
        if any(x in recherche for x in sm_keywords):
            t["est_sm"] = True
            t["annul"] = "72h" # 
            t["est_tda"] = any(x in recherche for x in ["tda", "tdah"]) # [cite: 21]
            
            # Sécurité et Âge [cite: 15-20]
            st.error("🚨 **SÉCURITÉ :** Avez-vous des intentions de faire du mal à vous ou à autrui actuellement ?")
            if st.radio("Réponse :", ["Non", "Oui"]) == "Oui":
                st.error("🚨 ACTION : Composer le 911 ou présentez-vous à l'urgence.")
            elif st.number_input("Âge :", 0, 115, 18) < 18:
                st.warning("Désolé, nous ne traitons pas la clientèle de moins de 18 ans.")
            else:
                # Informations obligatoires [cite: 27-37, 66]
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
                    t.update({"prof": "Infirmière + IPSSM", "temps": "1h (Inf) + 50min (IPSSM)", "prix": 195.0, "depot": 100.0}) # [cite: 23-25]
                else:
                    t.update({"prof": "IPSSM (Télémédecine)", "temps": "50", "prix": 250.0, "depot": 100.0}) # [cite: 27, 34, 36]

        # --- MODULE URGENCE MINEURE ---
        else:
            # Questions Aide-mémoire (Simulées ici, à étendre selon votre doc)
            st.info("💡 Vérifiez les contre-indications dans l'Aide-mémoire secrétaire.")
            est_ips = st.checkbox("Le patient présente-t-il une contre-indication ou nécessite l'IPS d'emblée ?") # 
            t["besoin_avis"] = st.checkbox("L'infirmière aura-t-elle besoin d'un avis IPS (si applicable) ?")
            
            # Grille tarifaire Urgence Mineure 
            if "urine" in recherche or "urinaire" in recherche:
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 180.0 if est_ips else 140.0, "annul": "48h" if est_ips else "24h"})
                t["note"] = "Prélèvement obligatoire inclus."
            elif "gorge" in recherche or "pharyngite" in recherche:
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 180.0 if est_ips else 140.0, "annul": "48h" if est_ips else "24h"})
                if st.checkbox("Test de streptocoque requis ? (+35$)"): t["prix"] += 35.0 # [cite: 42]
            elif any(x in recherche for x in ["perte", "vagin", "écoulement", "urètre"]):
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 195.0 if est_ips else 175.0, "annul": "48h" if est_ips else "24h"})
            else:
                # Sinusite, Otite, Zona, etc. [cite: 43-48]
                t.update({"prof": "IPS" if est_ips else "Infirmière", "prix": 180.0 if est_ips else 140.0, "annul": "48h" if est_ips else "24h"})

            # Frais d'avis IPS 
            if t["besoin_avis"] and t["prof"] == "Infirmière":
                t["prix"] += 25.0
            
            # Prélèvements Jonquière 
            if lieu == "Jonquière" and st.checkbox("Autre prélèvement requis ? (+35$)"):
                t["prix"] += 35.0
            elif lieu == "Saint-Félicien":
                st.warning("⚠️ Aucun prélèvement possible ici (sauf Strep-test).")

        # --- ÉTAPE 3 : SCRIPT FINAL ---
        if t["prix"] > 0:
            st.divider()
            st.subheader("3️⃣ Script de fin d'appel")
            
            total = t["prix"] + frais_ouv
            msg_ouv = f" (incluant les frais d'ouverture de dossier de 35$)" if dossier == "Non" else ""
            
            # Paiement 
            if t["est_sm"]: paiement = "par téléphone par carte de crédit seulement"
            elif lieu == "Jonquière": paiement = "par carte débit, carte de crédit ou argent comptant"
            else: paiement = "par carte débit ou carte de crédit seulement"

            script = f"""
            > "La durée de votre rendez-vous sera de **{t['temps']} minutes**. [cite: 61]
            > Nous ne traiterons que votre problème mentionné, tout ajout peut entraîner des frais. [cite: 62]
            > 
            > **Frais et Annulation :**
            > * Le coût de la consultation est de **{total:.2f} $**{msg_ouv}.
            > * {'Un dépôt de 100$ est requis pour l’IPSSM.' if t['depot'] > 0 else ''} [cite: 36]
            > * Le paiement se fera **{paiement}**. 
            > * Nous chargerons **50% des frais** en cas d'absence ou d'annulation moins de **{t['annul']}** à l'avance. 
            > 
            > **Ponctualité :**
            > * Veuillez vous {'connecter' if t['est_sm'] else 'présenter'} **5 à 10 minutes à l'avance**. [cite: 64]
            > * Un retard de **10 minutes** est considéré comme une absence." [cite: 65]
            """
            st.info(script)
