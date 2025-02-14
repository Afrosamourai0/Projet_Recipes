import streamlit as st
import asyncpg
import requests
import pandas as pd
import asyncio

# ----------------- Configuration PostgreSQL -----------------
DB_PARAMS = {
    "database": "projet3",
    "user": "hostautop",
    "password": "u3loBO7Xbr4Vdtq3SlskjBlYU6dZDxwY",
    "host": "dpg-cuj1701u0jms73d85d90-a.frankfurt-postgres.render.com",
    "port": "5432",
}

# ----------------- Définir la configuration de la page -----------------
st.set_page_config(page_title="🍽️ Popotrecettes Application de Recettes pour les nullos", page_icon="🍲", layout="wide")

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

asyncio.run(init_db())  # Vérification que la table existe

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

# ----------------- Récupération des Utilisateurs -----------------
async def get_users():
    """Récupère tous les utilisateurs inscrits"""
    try:
        conn = await asyncpg.connect(**DB_PARAMS)
        users = await conn.fetch("SELECT id, nom, prenom, email FROM newsletter ORDER BY id DESC")
        await conn.close()
        return pd.DataFrame(users)
    except Exception as e:
        st.error(f"Erreur de récupération des utilisateurs : {e}")
        return pd.DataFrame()

# ----------------- Fonction pour Récupérer les Recettes -----------------
def get_recipes_by_ingredient(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    return response.json().get("meals", [])

def get_recipes_by_category(category):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    response = requests.get(url)
    return response.json().get("meals", [])

def get_random_recipe():
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response = requests.get(url)
    return response.json().get("meals", [])[0]

def get_recipe_details(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    return response.json().get("meals", [])[0]

# ----------------- Interface Utilisateur Streamlit -----------------

st.title("🍽️ Application de Recettes")

# 📌 Sidebar : Formulaire d'inscription
with st.sidebar:
    st.header("📝 Inscription à la Newsletter")
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("Email")
    if st.button("S'inscrire"):
        if nom and prenom and email:
            asyncio.run(register_user(nom, prenom, email))
        else:
            st.warning("⚠️ Veuillez remplir tous les champs.")

# 📌 Onglets pour les fonctionnalités
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Recherche par Ingrédient", "🎲 Recette Aléatoire", "📂 Recherche par Catégorie", "📊 Informations"])

# 🔎 Recherche par Ingrédient
with tab1:
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
with tab2:
    st.header("🎲 Recette Aléatoire")
    if st.button("Obtenir une recette"):
        meal = get_random_recipe()
        st.image(meal["strMealThumb"], width=300)
        st.write(f"### {meal['strMeal']}")
        st.write(f"🍽 **Catégorie :** {meal['strCategory']} | 🌍 **Origine :** {meal['strArea']}")
        st.write("📜 **Instructions :**", meal["strInstructions"])
        st.write(f"🔗 [Voir la recette]({meal.get('strSource', 'https://www.themealdb.com/')})")

# 📂 Recherche par Catégorie
with tab3:
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

# 📊 Power BI - Avec iframe
with tab4:
    st.header("📊 Rapport d'informations sur notre contenu")
    st.markdown("""
        <iframe width="800" height="600" src="https://app.powerbi.com/view?r=eyJrIjoiOTFkYmJmZDUtMDA3OC00MWVjLWIyNzktYWQ1ZDRiMDA4MzZjIiwidCI6IjM3NmIxOTc2LTQxZmEtNDc4OC05NWIzLWFmZGY3MDFlNzkyNyJ9" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)


