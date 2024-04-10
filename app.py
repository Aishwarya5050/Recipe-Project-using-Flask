from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
database = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True)
    password = database.Column(database.String(100))

# Recipe model
class Recipe(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(100), nullable=False)
    description = database.Column(database.Text)
    ingredients = database.Column(database.Text) 
    instructions = database.Column(database.Text)
    created_by = database.Column(database.Integer, database.ForeignKey('user.id'))
    user = database.relationship('User', backref=database.backref('recipes', lazy=True))

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    database.create_all()

# Homepage route
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    recipes = Recipe.query.paginate(page=page, per_page=per_page)
    return render_template('index.html', recipes=recipes)

# Recipe detail route
@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

# New recipe route
@app.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        new_recipe = Recipe(title=title, description=description, ingredients=ingredients, instructions=instructions, created_by=current_user.id)
        database.session.add(new_recipe)
        database.session.commit()
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('user_recipes'))
    return render_template('new_recipe.html')


@app.route('/recipe/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.created_by != current_user.id:
        flash('You are not authorized to edit this recipe.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.description = request.form['description']
        recipe.ingredients = request.form['ingredients']
        recipe.instructions = request.form['instructions']
        database.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('user_recipes'))
    return render_template('edit_recipe.html', recipe=recipe)



@app.route('/recipe/delete/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.created_by != current_user.id:
        flash('You are not authorized to delete this recipe.', 'danger')
        return redirect(url_for('index'))
    database.session.delete(recipe)
    database.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('user_recipes'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']  
        if password != confirm_password: 
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register')) 
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
        else:
            new_user = User(username=username, password=password)
            database.session.add(new_user)
            database.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('user_recipes'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/user/recipes')
@login_required
def user_recipes():
    user = current_user
    recipes = user.recipes
    return render_template('user_recipes.html', user=user, recipes=recipes)


# Logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
