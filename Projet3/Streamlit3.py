import streamlit as st
import psycopg2
import requests
import pandas as pd

# ----------------- Configuration PostgreSQL -----------------
DB_PARAMS = {
    "dbname": "projet3",
    "user": "hostautop",
    "password": "u3loBO7Xbr4Vdtq3SlskjBlYU6dZDxwY",
    "host": "dpg-cuj1701u0jms73d85d90-a.frankfurt-postgres.render.com",
    "port": "5432",
}

# ----------------- Initialisation de la Base de Données -----------------
def init_db():
    """Initialise la base de données et crée la table newsletter si elle n'existe pas"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        st.success("Base de données connectée et table initialisée ✅")
    except Exception as e:
        st.error(f"Erreur de connexion à la base : {e}")

init_db()  # Vérification que la table existe

# ----------------- Inscription à la Newsletter -----------------
def register_user(nom, prenom, email):
    """Ajoute un utilisateur à la base PostgreSQL s'il n'existe pas encore"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT * FROM newsletter WHERE email = %s", (email,))
        if cur.fetchone():
            st.warning("⚠️ Cet email est déjà inscrit.")
        else:
            cur.execute("INSERT INTO newsletter (nom, prenom, email) VALUES (%s, %s, %s)", (nom, prenom, email))
            conn.commit()
            st.success("✅ Inscription réussie !")
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erreur d'inscription : {e}")

# ----------------- Récupération des Utilisateurs -----------------
def get_users():
    """Récupère tous les utilisateurs inscrits"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        df = pd.read_sql("SELECT id, nom, prenom, email FROM newsletter ORDER BY id DESC", conn)
        conn.close()
        return df
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
st.set_page_config(page_title="🍽️ Application de Recettes", page_icon="🍲", layout="wide")

st.title("🍽️ Application de Recettes")

# 📌 Sidebar : Formulaire d'inscription
with st.sidebar:
    st.header("📝 Inscription à la Newsletter")
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("Email")
    if st.button("S'inscrire"):
        if nom and prenom and email:
            register_user(nom, prenom, email)
        else:
            st.warning("⚠️ Veuillez remplir tous les champs.")

# 📌 Onglets pour les fonctionnalités
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Recherche par Ingrédient", "🎲 Recette Aléatoire", "📂 Recherche par Catégorie", "📋 Liste des Inscrits"])

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

# 📋 Liste des Inscrits
with tab4:
    st.header("📋 Liste des Inscrits")
    users_df = get_users()
    if not users_df.empty:
        st.dataframe(users_df, hide_index=True, use_container_width=True)
    else:
        st.info("Aucun utilisateur inscrit.")

