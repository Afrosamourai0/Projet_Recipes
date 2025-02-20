import streamlit as st
import requests
import random
import asyncio
import asyncpg
import pandas as pd
from PIL import Image

# ----------------- Configuration PostgreSQL -----------------
DB_PARAMS = {
    "database": "projet3",
    "user": "hostautop",
    "password": "u3loBO7Xbr4Vdtq3SlskjBlYU6dZDxwY",
    "host": "dpg-cuj1701u0jms73d85d90-a.frankfurt-postgres.render.com",
    "port": "5432",
}

# ----------------- Définir la configuration de la page -----------------
st.set_page_config(page_title="🍽️ Application de Recettes", page_icon="🍲", layout="wide")

# ----------------- Initialisation de la Base de Données -----------------
async def init_db():
    """Initialise la base de données et crée la table newsletter si elle n'existe pas"""
    try:
        conn = await asyncpg.connect(**DB_PARAMS)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        await conn.close()
        st.success("Base de données connectée et table initialisée ✅")
    except Exception as e:
        st.error(f"Erreur de connexion à la base : {e}")

# Run the database initialization once when the app starts
if 'db_initialized' not in st.session_state:
    asyncio.run(init_db())
    st.session_state['db_initialized'] = True

# ----------------- Inscription à la Newsletter -----------------
async def register_user(nom, prenom, email):
    """Ajoute un utilisateur à la base PostgreSQL s'il n'existe pas encore"""
    try:
        conn = await asyncpg.connect(**DB_PARAMS)
        user = await conn.fetchrow("SELECT * FROM newsletter WHERE email = $1", email)
        if user:
            st.warning("⚠️ Cet email est déjà inscrit.")
        else:
            await conn.execute("INSERT INTO newsletter (nom, prenom, email) VALUES ($1, $2, $3)", nom, prenom, email)
            st.success("✅ Inscription réussie !")
        await conn.close()
    except Exception as e:
        st.error(f"Erreur d'inscription : {e}")

# ----------------- Récupération des Recettes -----------------
def get_random_recipe():
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    return response.json().get("meals", [])[0]

def get_recipe_details(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    return response.json().get("meals", [])[0]

def get_recipes_by_ingredient(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    return response.json().get("meals", [])

def get_recipes_by_category(category):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    response = requests.get(url)
    return response.json().get("meals", [])

# ----------------- Page d'Accueil Dynamique -----------------
def display_home_page():
    # En-tête d'introduction
    st.markdown("<h1 style='text-align: center; color: #F39C12;'>Bienvenue dans l'application Popotterecettes 🥗</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Mettez dans la couleur et de l'équilbre dans vos recettes ⭐ !</h2>", unsafe_allow_html=True)

    # Image de fond de la page d'accueil
    st.image("https://wallpapers.com/images/featured/1pf6px6ryqfjtnyr.jpg", use_container_width=True)

    # Explication de l'application
    st.markdown("""
        Notre objectif est de vous accompagner dans votre parcours culinaire en vous offrant des recettes variées et équilibrées, adaptées à vos goûts et préférences. Que vous soyez un passionné de cuisine, un novice ou un adepte de la cuisine saine, vous trouverez ici une multitude d'options pour ravir vos papilles tout en prenant soin de votre santé.
        
        🍽️ Découvrez des recettes de saison, équilibrées et pleines de saveurs.
        Nous vous proposons des recettes aléatoires, inspirées d'ingrédients frais et sains. Vous pouvez également explorer des recettes par ingrédient ou par catégorie pour trouver des plats adaptés à vos envies du moment.
        
        📝 Abonnez-vous à notre Newsletter !
        Ne manquez pas nos recettes exclusives et nos conseils en nutrition ! En vous inscrivant à notre newsletter, vous recevrez des astuces pour intégrer des produits sains dans votre alimentation et découvrir des recettes créatives pour cuisiner facilement chez vous.
        
        Pourquoi s'abonner ?
        - Des recettes saines et équilibrées directement dans votre boîte mail
        - Des conseils pratiques pour une alimentation plus saine et variée
        - Des astuces de cuisine pour simplifier vos repas tout en prenant soin de votre santé
        
        👉 Inscrivez-vous maintenant et rejoignez notre communauté de gourmets soucieux de leur bien-être !
    """)
    st.markdown("Ici un lien pour obtenir un [Exemple de Newsletter](https://drive.google.com/file/d/1yLS6duF5sf2fBp4Y5NrfZNoP0RCGQKWH/view?usp=sharing)")
    # Section d'inscription à la newsletter
    with st.form(key="newsletter_form"):
        st.subheader("📝 Inscrivez-vous à notre Newsletter !")
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        submit_button = st.form_submit_button("S'inscrire")
        if submit_button:
            if nom and prenom and email:
                asyncio.run(register_user(nom, prenom, email))
            else:
                st.warning("⚠️ Veuillez remplir tous les champs.")

    # Sections de navigation rapide
    st.markdown("---")
    st.subheader("🎲 Découvrez une recette aléatoire chaque jour !")
    if st.button("Obtenir une recette du jour"):
        meal = get_random_recipe()
        st.session_state['random_recipe'] = meal

    if 'random_recipe' in st.session_state:
        meal = st.session_state['random_recipe']
        st.image(meal["strMealThumb"], width=300)
        st.write(f"### {meal['strMeal']}")
        st.write(f"🍽 **Catégorie :** {meal['strCategory']} | 🌍 **Origine :** {meal['strArea']}")
        st.write("📜 **Instructions :**", meal["strInstructions"])
        st.write(f"🔗 [Voir la recette]({meal.get('strSource', 'https://www.themealdb.com/')})")

    # Statistiques ou rapport intéressant
    st.markdown("<h2 style='color: #F39C12;'>Ce que nos utilisateurs pensent</h2>", unsafe_allow_html=True)
    st.write("Découvrez ce que d'autres pensent de nos recettes et rejoignez la communauté grandissante de gourmets!")

# ----------------- Interface Utilisateur Streamlit -----------------
# 📌 Onglets pour les fonctionnalités
tab1, tab2, tab3, tab4 , tab5 = st.tabs(["🏠 Accueil", "🔎 Recherche par Ingrédient", "🎲 Recette Aléatoire", "📂 Recherche par Catégorie","📊 PowerBI"])

# 🔸 Page d'Accueil
with tab1:
    display_home_page()

# 🔎 Recherche par Ingrédient
with tab2:
    st.header("🔎 Trouver une Recette par Ingrédient")
    ingredient = st.text_input("Entrez un ingrédient (ex: Chicken)")
    if st.button("Rechercher"):
        recipes = get_recipes_by_ingredient(ingredient)
        if recipes:
            for recipe in recipes[:5]:
                meal = get_recipe_details(recipe["idMeal"])
                st.image(meal["strMealThumb"], width=300)
                st.write(f"### {meal['strMeal']}")
                st.write(f"🍽 **Catégorie :** {meal['strCategory']} | 🌍 **Origine :** {meal['strArea']}")
                st.write("📜 **Instructions :**", meal["strInstructions"])
                st.write(f"🔗 [Voir la recette]({meal.get('strSource', 'https://www.themealdb.com/')})")
                st.write("---")
        else:
            st.warning("Aucune recette trouvée.")

# 🎲 Recette Aléatoire
with tab3:
    st.header("🎲 Recette Aléatoire")
    if st.button("Obtenir une recette"):
        meal = get_random_recipe()
        st.session_state['random_recipe'] = meal

    if 'random_recipe' in st.session_state:
        meal = st.session_state['random_recipe']
        st.image(meal["strMealThumb"], width=300)
        st.write(f"### {meal['strMeal']}")
        st.write(f"🍽 **Catégorie :** {meal['strCategory']} | 🌍 **Origine :** {meal['strArea']}")
        st.write("📜 **Instructions :**", meal["strInstructions"])
        st.write(f"🔗 [Voir la recette]({meal.get('strSource', 'https://www.themealdb.com/')})")

# 📂 Recherche par Catégorie
with tab4:
    st.header("📂 Recherche par Catégorie")
    categories = ["Beef", "Chicken", "Dessert", "Seafood", "Vegetarian"]
    category = st.selectbox("Choisissez une catégorie", categories)
    if st.button("Rechercher par Catégorie"):
        recipes = get_recipes_by_category(category)
        if recipes:
            for recipe in recipes[:5]:
                meal = get_recipe_details(recipe["idMeal"])
                st.image(meal["strMealThumb"], width=300)
                st.write(f"### {meal['strMeal']}")
                st.write(f"🍽 **Catégorie :** {meal['strCategory']} | 🌍 **Origine :** {meal['strArea']}")
                st.write("📜 **Instructions :**", meal["strInstructions"])
                st.write(f"🔗 [Voir la recette]({meal.get('strSource', 'https://www.themealdb.com/')})")
        else:
            st.warning("Aucune recette trouvée.")
# 📊 Onglet Power BI
with tab5:
    st.header("📊 Dashboard Power BI")
    st.write("Visualisez les statistiques et analyses sur les recettes.")

    # URL de ton rapport Power BI (remplace par ton lien)
    power_bi_url = "https://app.powerbi.com/view?r=TON_LIEN_ICI"

    # Intégration via un iframe
    st.markdown(f"""
        <iframe title="Power BI Report" width="100%" height="600" src="{power_bi_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

