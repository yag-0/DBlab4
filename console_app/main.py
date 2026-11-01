from database import DatabaseConnection

def add_movie(db, title, year, duration, rating, budget):
    query = """
        INSERT INTO movies (title, release_year, duration_minutes, rating, budget)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING movie_id
    """
    cursor = db.execute_query(query, (title, year, duration, rating, budget))
    if cursor:
        movie_id = cursor.fetchone()[0]
        print(f"Фільм успішно додано з ID: {movie_id}")
        return movie_id
    return None

def get_all_movies(db):
    query = """
        SELECT movie_id, title, release_year, duration_minutes, rating, budget
        FROM movies
        ORDER BY title
    """
    cursor = db.execute_query(query)
    if cursor:
        return cursor.fetchall()
    return []

def get_all_persons(db):
    query = "SELECT person_id, first_name, last_name, country FROM persons ORDER BY last_name"
    cursor = db.execute_query(query)
    if cursor:
        return cursor.fetchall()
    return []

def update_movie_budget(db, movie_id, new_budget):
    query = "UPDATE movies SET budget = %s WHERE movie_id = %s"
    cursor = db.execute_query(query, (new_budget, movie_id))
    if cursor:
        print(f"Бюджет фільму ID {movie_id} успішно оновлено")

def delete_movie(db, movie_id):
    query = "DELETE FROM movies WHERE movie_id = %s"
    cursor = db.execute_query(query, (movie_id,))
    if cursor:
        print(f"Фільм ID {movie_id} видалено з бази")

def search_movies(db, search_term):
    query = """
        SELECT m.movie_id, m.title, m.release_year, m.duration_minutes, m.rating, m.budget
        FROM movies m
        WHERE LOWER(m.title) LIKE LOWER(%s)
        ORDER BY m.title
    """
    search_pattern = f"%{search_term}%"
    cursor = db.execute_query(query, (search_pattern,))
    if cursor:
        return cursor.fetchall()
    return []

def main_menu():
    print("\n" + "="*50)
    print("СИСТЕМА УПРАВЛІННЯ КАТАЛОГОМ ФІЛЬМІВ")
    print("="*50)
    print("1. Переглянути всі фільми")
    print("2. Переглянути всіх кінематографістів")
    print("3. Додати новий фільм")
    print("4. Оновити бюджет фільму")
    print("5. Видалити фільм")
    print("6. Пошук фільмів за назвою")
    print("7. Статистика по кінематографістах (з View)")
    print("0. Вихід")
    print("="*50)
    return input("Оберіть опцію: ")

def display_movies(movies):
    if not movies:
        print("Фільми не знайдено")
        return

    print("\n" + "-"*110)
    print(f"{'ID':<5} {'Назва фільму':<35} {'Рік':<6} {'Хв.':<6} {'Рейтинг':<9} {'Бюджет ($)':<15}")
    print("-"*110)
    for m in movies:
        budget_str = f"{m[5]:,.2f}" if m[5] is not None else "N/A"
        print(f"{m[0]:<5} {m[1]:<35} {m[2]:<6} {m[3]:<6} {m[4]:<9} {budget_str:<15}")
    print("-"*110)

def display_persons(persons):
    if not persons:
        print("Кінематографістів не знайдено")
        return

    # Виносимо рядок заголовка у змінну, щоб уникнути проблеми зі слешами в f-стрічках
    name_header = "Ім'я"
    print("\n" + "-"*80)
    print(f"{'ID':<5} {name_header:<20} {'Прізвище':<20} {'Країна':<25}")
    print("-"*80)
    for p in persons:
        print(f"{p[0]:<5} {p[1]:<20} {p[2]:<20} {p[3]:<25}")
    print("-"*80)

def main():
    db = DatabaseConnection()
    db.connect()

    if not db.conn:
        print("Не вдалося підключитися до бази даних")
        return

    while True:
        choice = main_menu()

        if choice == '1':
            movies = get_all_movies(db)
            display_movies(movies)

        elif choice == '2':
            persons = get_all_persons(db)
            display_persons(persons)

        elif choice == '3':
            print("\n--- Додавання нового фільму ---")
            title = input("Назва фільму: ")
            year = int(input("Рік випуску: "))
            duration = int(input("Тривалість (хв): "))
            rating = float(input("Рейтинг (0-10): "))
            budget = float(input("Бюджет ($): "))

            add_movie(db, title, year, duration, rating, budget)

        elif choice == '4':
            movies = get_all_movies(db)
            display_movies(movies)
            movie_id = int(input("\nID фільму для оновлення бюджету: "))
            new_budget = float(input("Новий бюджет ($): "))
            update_movie_budget(db, movie_id, new_budget)

        elif choice == '5':
            movies = get_all_movies(db)
            display_movies(movies)
            movie_id = int(input("\nID фільму для видалення: "))
            confirm = input(f"Ви впевнені, що хочете видалити фільм ID {movie_id}? (так/ні): ")
            if confirm.lower() == 'так':
                delete_movie(db, movie_id)

        elif choice == '6':
            search_term = input("\nВведіть слова для пошуку в назві фільму: ")
            movies = search_movies(db, search_term)
            display_movies(movies)

        elif choice == '7':
            # Використання нашого створеного View (person_statistics)
            query = "SELECT * FROM person_statistics ORDER BY total_movies DESC"
            cursor = db.execute_query(query)
            if cursor:
                stats = cursor.fetchall()
                print("\n" + "-"*105)
                print(f"{'Кінематографіст':<30} {'Країна':<15} {'Фільмів':<10} {'Сер. бюджет ($)':<18} {'Сер. рейтинг':<12}")
                print("-"*105)
                for stat in stats:
                    avg_b = f"{stat[4]:,.2f}" if stat[4] is not None else "0.00"
                    print(f"{stat[1]:<30} {stat[2]:<15} {stat[3]:<10} {avg_b:<18} {stat[8]:<12}")
                print("-"*105)

        elif choice == '0':
            print("\nДякуємо за використання системи каталогів фільмів!")
            break

        else:
            print("\n❌ Невірна опція! Спробуйте ще раз.")

        input("\nНатисніть Enter для продовження...")

    db.disconnect()

if __name__ == "__main__":
    main()