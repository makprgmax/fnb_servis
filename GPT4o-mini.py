import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import fitz  # PyMuPDF
import mysql.connector
from mysql.connector import Error
import pandas as pd
import openai

client = openai.OpenAI(api_key="")

model = 'gpt-4o-mini'

def extract_entity(user_input, account_uuid_loc):

    prompt = (
        "You are an AI assistant integrated into a financial services platform. "
        "You will create SQL queries to get answers to questions from users."
        "The query must necessarily contain a selection by accounts.uuid={account_uuid_loc}  in the accounts table."
        "For a given user by accounts.uuid={account_uuid_loc}, based on the database structure:"
        "answer the user's queries based on their input:'{user_input}'"
        """ 
..............        
            SQL-request: "
                SELECT first_name, last_name, currency, count(uuid) as count_successful_transaction, sum(amount) as Amount
                FROM (SELECT
                	*
                FROM
                	card_transactions
                WHERE
                	account_uuid = ''
                	AND (`status` = 1
                		or (`status` = 0
                			and `charged` = 1))) as c1
                			LEFT JOIN
                (SELECT
                	card_uuid,
                first_name,
                	last_name
                FROM
                	(
                	SELECT
                		user_uuid,
                		uuid as card_uuid
                	FROM
                		cards
                	WHERE
                		account_uuid = '') as c1
                LEFT JOIN
                (
                	SELECT
                		uuid as user_uuid,
                		first_name,
                		last_name
                	from
                		users) as c2
                		USING(user_uuid)) as c2
                USING(card_uuid)
                GROUP BY first_name, last_name, currency
            "
            3) user_input: 'Количество успешных транзакций по каждому тим мемберу (для тим аккаунта)'
            SQL-request: "
                SELECT first_name, last_name, count(uuid) as count_successful_transaction
                FROM (SELECT
                	*
                FROM
                	card_transactions
                WHERE
                	account_uuid = ''
                	AND (`status` = 1
                		or (`status` = 0
                			and `charged` = 1))) as c1
                			LEFT JOIN
                (SELECT
                	card_uuid,
                	first_name,
                	last_name
                FROM
                	(
                	SELECT
                		user_uuid,
                		uuid as card_uuid
                	FROM
                		cards
                	WHERE
                		account_uuid = '') as c1
                LEFT JOIN
                (
                	SELECT
                		uuid as user_uuid,
                		first_name,
                		last_name
                	from
                		users) as c2
                		USING(user_uuid)) as c2
                USING(card_uuid)
                GROUP BY first_name, last_name        
            "
......
       """
       "Here is the user question: '{user_input}'".format(user_input=user_input, account_uuid_loc=account_uuid_loc)
    )


    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": user_input},
            {"role": "system", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content

def fetch_cards_data(q1):
    try:

        connection = mysql.connector.connect(
            host='217.193',
            database='tion',
            user='assiss',
            password=''

        )

        if connection.is_connected():
            print("Успешно подключено к базе данных")

            cursor = connection.cursor()

            cursor.execute(q1)

            rows = cursor.fetchall()
            df = pd.DataFrame(rows)

            print("Результат работы запроса:")

            for row in rows:
                print(row)

            return df

    except Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Соединение с MySQL закрыто")

def on_submit():
    user_query = query_entry.get("1.0", tk.END).strip()
    if user_query:
        try:
            answer = extract_entity(user_query, account_uuid_loc.get())
            sql_display.delete("1.0", tk.END)
            sql_display.insert(tk.END, answer)  # Выводим чистый SQL-запрос
        except Exception as e:
            sql_display.delete("1.0", tk.END)
            sql_display.insert(tk.END, "Ошибка при генерации SQL-запроса:\n" + str(e))

def execute_sql():
    sql_query = sql_display.get("1.0", tk.END).strip()
    if sql_query:
        try:
            sql_query = sql_query.replace("```sql", "").replace("```","")
            result = fetch_cards_data(sql_query)
            sql_result_display.delete("1.0", tk.END)
            sql_result_display.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения SQL-запроса: {e}")
    else:
        messagebox.showwarning("Внимание", "SQL-запрос не может быть пустым!")

def start_work():
    if account_uuid_loc.get():
        account_uuid_entry.configure(state='disabled')
        submit_button.configure(state='normal')
        sql_display.configure(state='normal')
        execute_button.configure(state='normal')
        sql_result_display.configure(state='normal')
    else:
        messagebox.showwarning("Внимание", "Введите UUID пользователя!")

window = tk.Tk()
window.title("SQL Query Generator")

account_uuid_loc = tk.StringVar()
account_uuid_label = tk.Label(window, text="Введите account_uuid_loc:")
account_uuid_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
account_uuid_entry = tk.Entry(window, textvariable=account_uuid_loc)
account_uuid_entry.grid(row=0, column=1, padx=10, pady=5)

start_button = tk.Button(window, text="Начать", command=start_work)
start_button.grid(row=0, column=2, padx=10, pady=5)

query_label = tk.Label(window, text="Введите ваш вопрос:")
query_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

query_entry = scrolledtext.ScrolledText(window, height=5, width=60)
query_entry.grid(row=1, column=1, padx=10, pady=5)

submit_button = tk.Button(window, text="Сгенерировать SQL", command=on_submit, state='disabled')
submit_button.grid(row=2, column=1, padx=10, pady=10, sticky='w')

sql_display = scrolledtext.ScrolledText(window, height=5, width=60)
sql_display.grid(row=3, column=1, padx=10, pady=5)

execute_button = tk.Button(window, text="Выполнить SQL", command=execute_sql, state='disabled')
execute_button.grid(row=4, column=1, padx=10, pady=5)

sql_result_display = scrolledtext.ScrolledText(window, height=10, width=60, state='disabled')
sql_result_display.grid(row=5, column=1, padx=10, pady=5)

result_display = scrolledtext.ScrolledText(window, height=5, width=60)
result_display.grid(row=6, column=1, padx=10, pady=5)


window.mainloop()




            # If a user query includes date but does not specify a year, return the questions: "Можете ли вы указать дату поточнее?" or  
            # "What date are you referring to?". Make sure to ask for the date whenever\n 
            # there is uncertainty about the specific time period (such as month without year or incomplete date).\n


            # When the user mentions a time period in their input but does not specify the year, ask a clarifying 
            # question about which year they are referring to. Always ask: 'Could you please specify which year you are referring to?'



# "14. If there is uncertainty in the question, there is always an answer, return the question about this uncertainty, especially if there is no year, and it is needed.\n"


# "When processing the user's input, if a time period is mentioned but the year is not specified, always stop and ask for clarification by saying: 'Could you please specify which year you mean?' A year is required for generating the correct response."

# When processing user input, if a time period is mentioned but no year is given, and if a month is given but no year, always stop and ask for clarification by saying "Could you please clarify what year you mean?" The year is required to form a correct answer.\n"



        # "14. When processing the user's input, if a time period is mentioned but the year is not specified, always stop and ask for clarification by saying: 'Could you please specify which year you mean?' A year is required for generating the correct response.\n"
        # "15. When processing user input, if a time period is mentioned but no year is given, and if a month is given but no year, always stop and ask for clarification by saying `Could you please clarify what year you mean?` The year is required to form a correct answer.\n"
