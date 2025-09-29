import psycopg2


def check_tables():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            user='postgres',
            password='password',
            database='postgres'
        )
        cursor = conn.cursor()

        # Проверим существующие таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("Существующие таблицы:")
        for table in tables:
            print(f" - {table[0]}")

        # Проверим данные в pereval_added
        cursor.execute("SELECT COUNT(*) FROM pereval_added;")
        count = cursor.fetchone()[0]
        print(f"\nКоличество записей в pereval_added: {count}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_tables()