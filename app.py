# app.py (Complete Updated Version)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
from bson.objectid import ObjectId

app = Flask(__name__)
app.config.from_pyfile('config.py')

# MongoDB setup
mongo = PyMongo(app)

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin panel', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Frontend Routes
@app.route('/')
def index():
    # Get 3 most recent news
    recent_news = list(mongo.db.news.find().sort('date_created', -1).limit(3))
    
    # Get recently updated news - LIMIT TO 4
    updated_news = list(mongo.db.news.find().sort('date_updated', -1).limit(4))
    
    # Get news by category (4 per category)
    categories = ['Technology', 'Sports', 'Political', 'Programming']
    categorized_news = {}
    for category in categories:
        categorized_news[category] = list(mongo.db.news.find({'category': category}).sort('date_created', -1).limit(4))
    
    return render_template('frontend/index.html', 
                         recent_news=recent_news, 
                         updated_news=updated_news,
                         categorized_news=categorized_news)

@app.route('/all-news')
def all_news():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    category = request.args.get('category', '')
    
    # Build query based on category filter
    query = {}
    if category:
        query['category'] = category
    
    # Get total count for pagination
    total = mongo.db.news.count_documents(query)
    
    # Calculate skip value for pagination
    skip = (page - 1) * per_page
    
    # Get news with pagination
    news_list = list(mongo.db.news.find(query).sort('date_created', -1).skip(skip).limit(per_page))
    
    # Get categories for filter dropdown
    categories = mongo.db.news.distinct('category')
    
    return render_template('frontend/all_news.html', 
                         news_list=news_list, 
                         page=page, 
                         per_page=per_page,
                         total=total,
                         category=category,
                         categories=categories)

@app.route('/news/<news_id>')
def news_detail(news_id):
    news = mongo.db.news.find_one({'_id': ObjectId(news_id)})
    if not news:
        flash('News article not found', 'error')
        return redirect(url_for('index'))
    
    # Increment view count
    mongo.db.news.update_one({'_id': ObjectId(news_id)}, {'$inc': {'views': 1}})
    
    # Get related news (same category)
    related_news = list(mongo.db.news.find({
        '_id': {'$ne': ObjectId(news_id)},
        'category': news['category']
    }).sort('date_created', -1).limit(3))
    
    return render_template('frontend/news_detail.html', news=news, related_news=related_news)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Save contact message to database
        mongo.db.contacts.insert_one({
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'date_created': datetime.utcnow()
        })
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('frontend/contact.html')

# Admin Routes
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    # If there's already an admin, redirect to login
    if mongo.db.admin_users.count_documents({}) > 0:
        flash('Admin user already exists. Please log in instead.', 'info')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('admin/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('admin/signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('admin/signup.html')
        
        # Check if username already exists
        if mongo.db.admin_users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return render_template('admin/signup.html')
        
        # Create admin user
        admin_user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'date_created': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        
        mongo.db.admin_users.insert_one(admin_user)
        
        flash('Admin account created successfully! Please log in.', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/signup.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # If no admin exists, redirect to signup
    if mongo.db.admin_users.count_documents({}) == 0:
        flash('No admin account found. Please create an admin account first.', 'info')
        return redirect(url_for('admin_signup'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = mongo.db.admin_users.find_one({'username': username, 'is_active': True})
        
        if admin and check_password_hash(admin['password'], password):
            # Set session
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_id'] = str(admin['_id'])
            session['last_login'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update last login
            mongo.db.admin_users.update_one(
                {'_id': admin['_id']}, 
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# Updated Admin Dashboard Route with Fixed Analytics
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        # Get analytics data
        total_news = mongo.db.news.count_documents({})
        
        # Fix for total views aggregation
        total_views_result = list(mongo.db.news.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total_views': {'$sum': '$views'}
                }
            }
        ]))
        
        total_views_count = total_views_result[0]['total_views'] if total_views_result else 0
        
        # Get recent news (last 5)
        recent_news = list(mongo.db.news.find().sort('date_created', -1).limit(5))
        
        # Get most viewed news (top 5 by views)
        popular_news = list(mongo.db.news.find().sort('views', -1).limit(5))
        
        # Get category-wise counts
        category_stats = list(mongo.db.news.aggregate([
            {
                '$group': {
                    '_id': '$category',
                    'count': {'$sum': 1},
                    'total_views': {'$sum': '$views'}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]))
        
        # Get today's views (views from last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        today_views_result = list(mongo.db.news.aggregate([
            {
                '$match': {
                    'date_created': {'$gte': yesterday}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'today_views': {'$sum': '$views'}
                }
            }
        ]))
        today_views = today_views_result[0]['today_views'] if today_views_result else 0
        
        # Get news with images count
        news_with_images = mongo.db.news.count_documents({'image': {'$exists': True, '$ne': None}})
        
        # Calculate average views per article
        avg_views = total_views_count / total_news if total_news > 0 else 0
        
    except Exception as e:
        # Handle any database errors gracefully
        print(f"Error in dashboard analytics: {e}")
        total_news = 0
        total_views_count = 0
        recent_news = []
        popular_news = []
        category_stats = []
        today_views = 0
        news_with_images = 0
        avg_views = 0
    
    return render_template('admin/dashboard.html',
                         total_news=total_news,
                         total_views=total_views_count,
                         recent_news=recent_news,
                         popular_news=popular_news,
                         category_stats=category_stats,
                         today_views=today_views,
                         news_with_images=news_with_images,
                         avg_views=round(avg_views, 1))

@app.route('/admin/news')
@admin_required
def admin_news_list():
    news_list = list(mongo.db.news.find().sort('date_created', -1))
    return render_template('admin/news_list.html', news_list=news_list)

@app.route('/admin/news/add', methods=['GET', 'POST'])
@admin_required
def admin_add_news():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                # Generate unique filename
                filename = secure_filename(image.filename)
                image_filename = f"{uuid.uuid4().hex}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # Save news to database
        mongo.db.news.insert_one({
            'title': title,
            'content': content,
            'category': category,
            'image': image_filename,
            'date_created': datetime.utcnow(),
            'date_updated': datetime.utcnow(),
            'views': 0,
            'author': session.get('admin_username', 'Admin')
        })
        
        flash('News article added successfully!', 'success')
        return redirect(url_for('admin_news_list'))
    
    categories = ['Technology', 'Sports', 'Political', 'Programming']
    return render_template('admin/add_news.html', categories=categories)

@app.route('/admin/news/edit/<news_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_news(news_id):
    news = mongo.db.news.find_one({'_id': ObjectId(news_id)})
    
    if not news:
        flash('News article not found', 'error')
        return redirect(url_for('admin_news_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        
        update_data = {
            'title': title,
            'content': content,
            'category': category,
            'date_updated': datetime.utcnow()
        }
        
        # Handle image upload if a new image is provided
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                # Delete old image if exists
                if news.get('image'):
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], news['image'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = secure_filename(image.filename)
                image_filename = f"{uuid.uuid4().hex}_{filename}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                update_data['image'] = image_filename
        
        # Update news in database
        mongo.db.news.update_one({'_id': ObjectId(news_id)}, {'$set': update_data})
        
        flash('News article updated successfully!', 'success')
        return redirect(url_for('admin_news_list'))
    
    categories = ['Technology', 'Sports', 'Political', 'Programming']
    return render_template('admin/edit_news.html', news=news, categories=categories)

@app.route('/admin/news/delete/<news_id>')
@admin_required
def admin_delete_news(news_id):
    news = mongo.db.news.find_one({'_id': ObjectId(news_id)})
    
    if news:
        # Delete image if exists
        if news.get('image'):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], news['image'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete news from database
        mongo.db.news.delete_one({'_id': ObjectId(news_id)})
        flash('News article deleted successfully!', 'success')
    else:
        flash('News article not found', 'error')
    
    return redirect(url_for('admin_news_list'))

# API Routes for frontend functionality
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    
    if query:
        # Search in title and content
        news_list = list(mongo.db.news.find({
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}}
            ]
        }).sort('date_created', -1).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for news in news_list:
            news['_id'] = str(news['_id'])
            news['date_created'] = news['date_created'].isoformat()
            if news.get('date_updated'):
                news['date_updated'] = news['date_updated'].isoformat()
    else:
        news_list = []
    
    return jsonify(news_list)

# Database initialization
def init_database():
    with app.app_context():
        # Create admin user if it doesn't exist
        if mongo.db.admin_users.count_documents({}) == 0:
            admin_user = {
                'username': 'admin',
                'email': 'admin@newsportal.com',
                'password': generate_password_hash('admin123'),
                'date_created': datetime.utcnow(),
                'last_login': None,
                'is_active': True
            }
            mongo.db.admin_users.insert_one(admin_user)
            print("Admin user created: username='admin', password='admin123'")
        
        # Create sample news if the collection is empty
        if mongo.db.news.count_documents({}) == 0:
            sample_news = [
                {
                    'title': 'New Breakthrough in Artificial Intelligence',
                    'content': 'Researchers have developed a new AI model that can understand and generate human-like text with unprecedented accuracy. This breakthrough could revolutionize how we interact with technology.',
                    'category': 'Technology',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 150,
                    'author': 'Admin'
                },
                {
                    'title': 'Local Team Wins Championship',
                    'content': 'In an exciting final match, our local team secured the championship title with a stunning last-minute goal. Thousands of fans celebrated throughout the city.',
                    'category': 'Sports',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 89,
                    'author': 'Admin'
                },
                {
                    'title': 'New Programming Language Released',
                    'content': 'A team of developers has released a new programming language designed for web development. Early adopters report significant productivity improvements.',
                    'category': 'Programming',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 203,
                    'author': 'Admin'
                },
                {
                    'title': 'Political Summit Addresses Climate Change',
                    'content': 'World leaders gathered at the global political summit to discuss urgent climate change measures and international cooperation strategies.',
                    'category': 'Political',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 120,
                    'author': 'Admin'
                }
            ]
            mongo.db.news.insert_many(sample_news)
            print("Sample news articles created")

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Initialize database with sample data
    init_database()
    
    print("News Portal started successfully!")
    print("Frontend: http://localhost:5000")
    print("Admin Panel: http://localhost:5000/admin/login")
    print("Default Admin Credentials: username='admin', password='admin123'")
    
    app.run(debug=True)