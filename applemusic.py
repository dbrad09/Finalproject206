import os
import requests
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

url = "https://billboard-api5.p.rapidapi.com/api/charts/artist-100"

querystring = {"week": "2023-11-25"}

headers = {
    "X-RapidAPI-Key": "c3254f9db9msh45981f2889c9f06p162e08jsne86dc48cb693",
    "X-RapidAPI-Host": "billboard-api5.p.rapidapi.com"
}


def create_tables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS chart_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, rank INTEGER, artist TEXT, cover TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS second_table (id INTEGER PRIMARY KEY AUTOINCREMENT, rank INTEGER, positionlastweek INTEGER, peakposition INTEGER, weeksonchart INTEGER)")


def create_database():
    if not os.path.exists('chart_entries.db'):
        conn = sqlite3.connect('chart_entries.db')
        cursor = conn.cursor()
        create_tables(cursor)
        conn.commit()
        conn.close()
    if not os.path.exists('second_table.db'):
        conn = sqlite3.connect('second_table.db')
        cursor = conn.cursor()
        create_tables(cursor)
        conn.commit()
        conn.close()


def insert_entry_into_db(entry, cursor):
    rank = entry['rank']
    artist = entry['artist']
    cover = entry['cover']

    cursor.execute("INSERT INTO chart_entries (rank, artist, cover) VALUES (?, ?, ?)", (rank, artist, cover))

    position = entry.get('position', {})
    poslast = position.get('positionLastWeek', None)
    pospeak = position.get('peakPosition', None)
    weekson = position.get('weeksOnChart', None)

    cursor.execute("INSERT INTO second_table (rank, positionlastweek, peakposition, weeksonchart) VALUES (?, ?, ?, ?)",
                   (rank, poslast, pospeak, weekson))


def get_current_entry_count(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def process_entries(entries, cursor, table_name, start_index, batch_size=25):
    create_tables(cursor)

    current_count = get_current_entry_count(cursor, table_name)
    end_index = min(start_index + batch_size, len(entries), current_count + batch_size)

    for i in range(start_index, end_index):
        entry = entries[i]
        insert_entry_into_db(entry, cursor)

    return end_index


def delete_database():
    if os.path.exists('chart_entries.db'):
        os.remove('chart_entries.db')
        print("Database deleted.")
    elif os.path.exists('second_table.db'):
        os.remove('second_table.db')
        print("Database deleted.")
    else:
        print("Databases do not exist.")
        
        
def calculate_top_avg_weeks():
    conn_chart = sqlite3.connect('chart_entries.db')
    conn_second = sqlite3.connect('second_table.db')

    cursor_chart = conn_chart.cursor()
    cursor_second = conn_second.cursor()

    cursor_chart.execute("""
        SELECT ce.artist, SUM(st.weeksonchart) AS total_weeks
        FROM chart_entries ce
        JOIN second_table st ON ce.rank = st.rank
        GROUP BY ce.artist
        ORDER BY total_weeks DESC
        LIMIT 5;
    """)

    results = cursor_chart.fetchall()

    conn_chart.close()
    conn_second.close()

    return results

# Function to visualize top 5 artists with highest average weeks on chart
def visualize_top_avg_weeks(results):
    artists = [result[0] for result in results]
    total_weeks = [result[1] for result in results]
    colors = plt.cm.viridis(np.linspace(0, 1, len(artists)))
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(artists, total_weeks, color=colors)
    plt.xlabel('Artists')
    plt.ylabel('Total Weeks on Chart')
    plt.title('Total Weeks on Chart for Top 5 Artists')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
def write_to_file(results):
    with open('top_artists_weeks.txt', 'w') as file:
        file.write("Top 5 Artists and Their Total Weeks on Chart:\n")
        for result in results:
            file.write(f"{result[0]}: {result[1]} weeks\n")

def main():
    create_database()

    conn_chart = sqlite3.connect('chart_entries.db')
    cursor_chart = conn_chart.cursor()

    conn_second = sqlite3.connect('second_table.db')
    cursor_second = conn_second.cursor()

    last_processed_index_chart = get_current_entry_count(cursor_chart, 'chart_entries')

    response = requests.get(url, headers=headers, params=querystring)
    dict_charts = response.json()
    entries = dict_charts['chart']['entries']

    last_processed_index_chart = process_entries(entries, cursor_chart, 'chart_entries', last_processed_index_chart)
    last_processed_index_second = process_entries(entries, cursor_second, 'second_table', last_processed_index_chart)

    conn_chart.commit()
    conn_chart.close()

   
    conn_second.commit()
    conn_second.close()
    top_avg_weeks_results = calculate_top_avg_weeks()
    visualize_top_avg_weeks(top_avg_weeks_results)
    write_to_file(top_avg_weeks_results)

   # delete_database()
    


if __name__ == "__main__":
    main()
