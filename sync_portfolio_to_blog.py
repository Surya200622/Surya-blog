import sqlite3
import json
import urllib.request
import re
from datetime import datetime

SUPABASE_URL = "https://tqalcrxzycebpnksaghx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxYWxjcnh6eWNlYnBua3NhZ2h4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3MDc2NTYsImV4cCI6MjA5NTI4MzY1Nn0.GQBsbpuZk2CNc5P8hKIHLgioDCbrYyC9sXToonC8-XY"

PROJECT_DATA = {
    'business': {'price': 3500, 'timeline': 14},
    'ecommerce': {'price': 8000, 'timeline': 28},
    'portfolio': {'price': 2500, 'timeline': 10},
    'saas': {'price': 12000, 'timeline': 35},
    'admin': {'price': 7500, 'timeline': 21},
    'landing': {'price': 1500, 'timeline': 7},
}

def get_base_metrics(category):
    cat_lower = category.lower()
    for key, data in PROJECT_DATA.items():
        if key in cat_lower:
            return data['price'], data['timeline']
    return 3500, 14 

def fetch_portfolio_projects():
    print("Fetching projects from Supabase...")
    url = f"{SUPABASE_URL}/rest/v1/portfolio_projects?select=*"
    req = urllib.request.Request(url)
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
        return []

def get_or_create_category(cursor, category_name):
    slug = category_name.lower().replace(' ', '-')
    cursor.execute("SELECT id FROM blog_category WHERE slug = ?", (slug,))
    res = cursor.fetchone()
    if res:
        return res[0]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    cursor.execute("INSERT INTO blog_category (name, slug, description, icon, color, \"order\", created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (category_name, slug, '', 'fa-folder', '#4a90e2', 0, now))
    return cursor.lastrowid

def sync_tags(cursor, post_id, tech_array):
    # Clear existing tags for this post
    cursor.execute("DELETE FROM blog_post_tags WHERE post_id = ?", (post_id,))
    
    for tech in tech_array:
        slug = tech.lower().replace(' ', '-').replace('.', '')
        # Check if tag exists
        cursor.execute("SELECT id FROM blog_tag WHERE name = ? OR slug = ?", (tech, slug))
        res = cursor.fetchone()
        if res:
            tag_id = res[0]
        else:
            try:
                cursor.execute("INSERT INTO blog_tag (name, slug) VALUES (?, ?)", (tech, slug))
                tag_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                cursor.execute("SELECT id FROM blog_tag WHERE name = ? OR slug = ?", (tech, slug))
                tag_id = cursor.fetchone()[0]
        # Link tag
        cursor.execute("INSERT INTO blog_post_tags (post_id, tag_id) VALUES (?, ?)", (post_id, tag_id))

def generate_rich_html(project):
    desc = project.get('description', '')
    
    # Extract embedded price
    price_match = re.search(r"Price:\s*(.*)", desc, re.IGNORECASE)
    if price_match:
        price_str = price_match.group(1).strip()
        desc = re.sub(r"Price:\s*(.*)", "", desc, flags=re.IGNORECASE).strip()
    else:
        base_price, _ = get_base_metrics(project.get('category', ''))
        price_str = f"Starting at ₹{base_price}"
        
    _, timeline = get_base_metrics(project.get('category', ''))
    
    # Remove link back to blog
    desc = re.sub(r"Read more details:\s*https?:\/\/[^\s]+", "", desc, flags=re.IGNORECASE).strip()

    tech_stack = project.get('tech_array', [])
    
    html = f"""
    <div class="project-detailed-view">
        <h2 style="color: var(--accent); margin-bottom: 1rem;">Project Overview</h2>
        <p style="font-size: 1.1rem; line-height: 1.8; color: var(--text-secondary);">{desc}</p>
        
        <div style="background: var(--bg-tertiary); padding: 2rem; border-radius: 1rem; margin: 2rem 0; border: 1px solid var(--border-color);">
            <h3 style="margin-top: 0;">Scope & Delivery</h3>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div>
                    <span style="display: block; color: var(--text-tertiary); font-size: 0.9rem;">Estimated Price</span>
                    <strong style="color: #25D366; font-size: 1.5rem;">{price_str}</strong>
                </div>
                <div>
                    <span style="display: block; color: var(--text-tertiary); font-size: 0.9rem;">Estimated Timeline</span>
                    <strong style="color: var(--text-primary); font-size: 1.5rem;">~{timeline} Days</strong>
                </div>
                <div>
                    <span style="display: block; color: var(--text-tertiary); font-size: 0.9rem;">Category</span>
                    <strong style="color: var(--text-primary); font-size: 1.2rem;">{project.get('category', 'Custom')}</strong>
                </div>
            </div>
        </div>
        
        <h3>Technologies Leveraged</h3>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 2rem;">
            {"".join([f'<span class="badge" style="background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 0.4rem 1rem;">{t}</span>' for t in tech_stack])}
        </div>
    </div>
    """
    return html, desc, price_str

def sync_projects():
    projects = fetch_portfolio_projects()
    if not projects:
        return

    print(f"Found {len(projects)} projects. Integrating into Django SQLite DB...")
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    for proj in projects:
        slug = proj.get('slug')
        if not slug: continue
        title = proj.get('title', 'Untitled')
        
        # Determine category ID dynamically
        cat_id = get_or_create_category(cursor, proj.get('category', 'Portfolio Project'))
        
        html_content, plain_excerpt, price_str = generate_rich_html(proj)
        excerpt = plain_excerpt[:150] + '...' if len(plain_excerpt) > 150 else plain_excerpt
        
        cursor.execute("SELECT id FROM blog_post WHERE slug = ?", (slug,))
        existing = cursor.fetchone()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        live_url = proj.get('link', '')
        
        if existing:
            post_id = existing[0]
            print(f"Updating advanced blog post: {title}")
            cursor.execute("""
                UPDATE blog_post 
                SET title=?, content=?, excerpt=?, project_live_url=?, project_price=?, updated_at=?, category_id=?
                WHERE id=?
            """, (title, html_content, excerpt, live_url, price_str, now, cat_id, post_id))
        else:
            print(f"Inserting advanced blog post: {title}")
            cursor.execute("""
                INSERT INTO blog_post 
                (title, slug, content, excerpt, status, is_premium, is_featured, views_count, reading_time, meta_title, meta_description, published_at, created_at, updated_at, author_id, category_id, project_live_url, project_price, featured_image) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, slug, html_content, excerpt, 'published', 0, 0, 0, 4, title, excerpt, now, now, now, 1, cat_id, live_url, price_str, ''))
            post_id = cursor.lastrowid
            
        # Sync the tags relationally
        sync_tags(cursor, post_id, proj.get('tech_array', []))
        
    conn.commit()
    conn.close()
    print("Super-Sync complete! Categories, Tags, HTML Scope, and Timelines have all been dynamically linked.")

if __name__ == "__main__":
    sync_projects()
