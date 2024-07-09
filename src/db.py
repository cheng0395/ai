import sqlite3

conn = sqlite3.connect('D:\pycharm project\AIservice\sql\chat.db',timeout=10, check_same_thread=False)
cursor = conn.cursor()


def verify_login(user_id, user_password):
    # 查询数据库中是否有匹配的用户名和密码
    cursor.execute('''
    SELECT * FROM user
    WHERE user_id = ? AND user_password = ?
    ''', (user_id, user_password))

    # 获取查询结果（如果存在）
    user = cursor.fetchone()

    # 如果查询结果非空，说明用户名和密码匹配
    if user:
        return True
    else:
        return False

def get_user_name(user_id):
    cursor.execute('SELECT user_name FROM user WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def insert_chat_record(user_id, user_name, user_input, system_output):
    cursor.execute('''
        INSERT INTO memory (user_id, user_name, user_input, system_output)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_name, user_input, system_output))
    conn.commit()

def get_chat_history(user_id):
    cursor.execute('''
        SELECT user_input, system_output FROM memory WHERE user_id = ?
    ''', (user_id,))
    chat_history = cursor.fetchall()
    # print(chat_history)
    return chat_history