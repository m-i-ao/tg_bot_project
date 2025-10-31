import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from utils.db import get_conn
import config

def generate_stats_graph(output_path: str = None):
    conn = get_conn()
    c = conn.cursor()
    
    # Последние 30 дней
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    c.execute('''
        SELECT DATE(timestamp), COUNT(*) FROM posts 
        WHERE timestamp >= ? 
        GROUP BY DATE(timestamp)
    ''', (thirty_days_ago,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return None

    dates = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker='o', color='blue')
    plt.title('Посты за последние 30 дней')
    plt.xlabel('Дата')
    plt.ylabel('Количество')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    output_path = output_path or os.path.join(config.PENDING_IMAGES_DIR, 'stats.png')
    plt.savefig(output_path)
    plt.close()
    return output_path

async def send_stats_report(bot, chat_id: int, period: str = 'day'):
    graph_path = generate_stats_graph()
    text = f"Статистика за {period}:\n"
    text += f"• Постов: {len(os.listdir(config.PENDING_IMAGES_DIR)) if os.path.exists(config.PENDING_IMAGES_DIR) else 0}\n"
    text += f"• Предложек: {len([f for f in os.listdir(config.PENDING_IMAGES_DIR) if 'prop_' in f])}\n"

    if graph_path and os.path.exists(graph_path):
        await bot.send_photo(chat_id, open(graph_path, 'rb'), caption=text)
        os.remove(graph_path)
    else:
        await bot.send_message(chat_id, text)

def get_user_ranking(limit: int = 10):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT user_id, COUNT(*) as cnt FROM proposals 
        GROUP BY user_id ORDER BY cnt DESC LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

async def send_top_users(bot, chat_id: int):
    ranking = get_user_ranking()
    if not ranking:
        await bot.send_message(chat_id, "Нет данных для рейтинга.")
        return
    text = "Топ пользователей по предложкам:\n"
    for i, (user_id, count) in enumerate(ranking, 1):
        text += f"{i}. Пользователь {user_id}: {count} предложек\n"
    await bot.send_message(chat_id, text)