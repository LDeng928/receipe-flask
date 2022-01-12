
from flask import Flask, render_template, request, abort, redirect, url_for
import sqlite3
from sqlite3 import Error

# Connect to database


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful.")
    except Error as e:
        print(f"The error `{e}` occured.")
    return connection

# Function to Execute queries


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error `{e}` occured.")


# Create recipes table - query
create_recipes_table = """
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  image TEXT NOT NULL,
  link TEXT NOT NULL
);
"""


# Initial placement data
recipes = [
    {
        "title": "BBQ Sweet and Sour Chicken Wings",
        "image": "https://image.freepik.com/free-photo/chicken-wings-barbecue-sweetly-sour-sauce-picnic-summer-menu-tasty-food-top-view-flat-lay_2829-6471.jpg",
        "link": "https://cookpad.com/us/recipes/347447-easy-sweet-sour-bbq-chicken"
    },
    {
        "title": "Striploin Steak",
        "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80",
        "link": "https://tasty.co/recipe/garlic-butter-steak"
    }
]

app = Flask(__name__)


@app.route('/')
@app.route("/index")
@app.route("/home")
def home():
    select_all_recipes = "SELECT * FROM recipes"
    recipes = None
    try:
        with create_connection("recipes.db") as connection:
            cursor = connection.cursor()
            cursor.execute(select_all_recipes)
            recipes = cursor.fetchall()
            print(recipes)
            return recipes
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        return render_template('home.html', recipes=recipes)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/recipe/', methods=['POST'])
def create_recipe():
    if request.method == 'POST':
        try:
            title = request.form['title']
            image = request.form['image']
            link = request.form['link']

            with create_connection("recipes.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO recipes (title, image, link) VALUES (?, ?, ?)", (title, image, link))

                connection.commit()
                print("Record inserted successfully")
        except:
            connection.rollback()
            print("Error in insert statement")
        finally:
            return redirect(url_for('home'))


if __name__ == '__main__':
    # Assign connection
    # connection = create_connection("recipes.db")
    # execute_query(connection, create_recipes_table)
    app.run(debug=True)
