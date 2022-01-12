
from flask import Flask, render_template, request, abort, redirect, url_for, flash
import sqlite3
from sqlite3 import Error
from wtforms import Form, StringField, form, validators

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

# Form class


class CreateRecipeForm(Form):
    title = StringField("Recipe Title", [validators.Length(min=4, max=50)])
    image = StringField("Image Address", [validators.Length(min=10)])
    link = StringField("Recipe Link", [validators.Length(min=10)])


app = Flask(__name__)
app.secret_key = 'secret123'


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
            return recipes
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        return render_template('home.html', recipes=recipes)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/recipe/', methods=['POST', 'GET'])
def create_recipe():
    # instantiate the form to send when the request.method != POST
    form = CreateRecipeForm()
    if request.method == 'POST':
        try:
            form = CreateRecipeForm(request.form)
            if form.validate():
                title = form.title.data
                image = form.image.data
                link = form.link.data

                with create_connection("recipes.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT INTO recipes (title, image, link) VALUES (?, ?, ?)", (title, image, link))

                    connection.commit()
                    flash("You have added a new recipe.", "success")
                    print("Record inserted successfully")
        except:
            connection.rollback()
            print("Error in insert statement")
        finally:

            return redirect(url_for('home'))
    elif request.method == 'GET':
        # return the form to the template
        return render_template('create-recipe.html', form=form)

# Edit recipe


@app.route('/recipe/edit/<id>/', methods=['POST', 'GET'])
def edit_recipe(id):
    # Fetch data into the form
    connection = create_connection("recipes.db")
    cursor = connection.cursor()
    # Get recipe by id
    select_one_recipe = "SELECT * FROM recipes WHERE id=?"
    result = cursor.execute(select_one_recipe, (id,))
    recipe = result.fetchone()
    print(recipe)

    # Get form
    form = CreateRecipeForm(request.form)
    form.title.data = recipe[1]
    form.image.data = recipe[2]
    form.link.data = recipe[3]

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        image = request.form['image']
        link = request.form['link']

        connection = create_connection("recipes.db")
        cursor = connection.cursor()

        update_a_recipe = "UPDATE recipes SET title=?, image=?, link=? WHERE id=?"
        cursor.execute(update_a_recipe, (title, image, link, id))

        # Commit to db
        connection.commit()

        # Flash message
        flash('Recipe Updated', 'success')
        return redirect(url_for('home'))

    return render_template('edit-recipe.html', form=form)


# Delete recipe


@app.route('/recipe/delete/<id>/', methods=['POST'])
def delete_recipe(id):
    try:
        with create_connection("recipes.db") as connection:
            delete_a_recipe = "DELETE FROM recipes WHERE id=?"
            cursor = connection.cursor()
            cursor.execute(delete_a_recipe, (id,))
            connection.commit()
            flash("Recipe deleted successfully.", "success")
    except:
        connection.rollback()
        print("Error in delete statement")
    finally:

        return redirect(url_for('home'))


if __name__ == '__main__':
    # Assign connection
    # connection = create_connection("recipes.db")
    # execute_query(connection, create_recipes_table)
    app.run(debug=True)
