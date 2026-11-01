import matplotlib
matplotlib.use('Agg')  # Використовувати backend без GUI
import matplotlib.pyplot as plt
import io
import base64

def create_person_statistics_chart(db):
    """
    Створення графіка топ-10 кінематографістів за кількістю фільмів
    """
    query = """
        SELECT p.first_name || ' ' || p.last_name as person_name, COUNT(mc.movie_id) as movies_count
        FROM persons p
        LEFT JOIN movie_crew mc ON p.person_id = mc.person_id
        GROUP BY p.person_id, p.first_name, p.last_name
        ORDER BY movies_count DESC
        LIMIT 10
    """
    cursor = db.execute_query(query)
    data = cursor.fetchall() if cursor else []

    if not data:
        return None

    names = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(names, counts, color='#3498db')

    # Додавання значень над стовпцями
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')

    plt.xlabel('Кінематографісти', fontsize=12)
    plt.ylabel('Кількість фільмів', fontsize=12)
    plt.title('Топ-10 кінематографістів за кількістю фільмів', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Конвертація в base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

def create_budget_distribution_chart(db):
    """
    Створення графіка розподілу бюджетів фільмів
    """
    query = "SELECT budget FROM movies WHERE budget IS NOT NULL ORDER BY budget"
    cursor = db.execute_query(query)
    data = cursor.fetchall() if cursor else []

    if not data:
        return None

    budgets = [row[0] for row in data]

    plt.figure(figsize=(10, 6))
    plt.hist(budgets, bins=15, color='#2ecc71', edgecolor='black', alpha=0.7)
    plt.xlabel('Бюджет ($)', fontsize=12)
    plt.ylabel('Кількість фільмів', fontsize=12)
    plt.title('Розподіл бюджетів фільмів', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url