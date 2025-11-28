# init_db.py
from app import app, mongo
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create admin user if it doesn't exist
        if mongo.db.admin_users.count_documents({}) == 0:
            admin_user = {
                'username': 'admin',
                'password': generate_password_hash('admin123'),
                'email': 'admin@newsportal.com',
                'date_created': datetime.utcnow()
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
                    'views': 150
                },
                {
                    'title': 'Local Team Wins Championship',
                    'content': 'In an exciting final match, our local team secured the championship title with a stunning last-minute goal. Thousands of fans celebrated throughout the city.',
                    'category': 'Sports',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 89
                },
                {
                    'title': 'New Programming Language Released',
                    'content': 'A team of developers has released a new programming language designed for web development. Early adopters report significant productivity improvements.',
                    'category': 'Programming',
                    'image': None,
                    'date_created': datetime.utcnow(),
                    'date_updated': datetime.utcnow(),
                    'views': 203
                }
            ]
            mongo.db.news.insert_many(sample_news)
            print("Sample news articles created")
        
        print("Database initialization completed successfully!")

if __name__ == '__main__':
    from datetime import datetime
    init_database()