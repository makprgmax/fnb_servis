from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('name-of-finetuned-model')
model = AutoModelForCausalLM.from_pretrained('name-of-finetuned-model')

def generate_sql_with_fingpt(user_input):
    prompt = f"Сформируй SQL-запрос для следующего вопроса: {user_input}\nSQL Query:"

    inputs = tokenizer.encode(prompt, return_tensors='pt')

    outputs = model.generate(inputs, max_length=100, num_return_sequences=1)

    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)

    sql_query = sql_query.split('SQL Query:')[-1].strip()
    return sql_query

user_input = "Какие транзакции были совершены в этом месяце?"
sql_query = generate_sql_with_fingpt(user_input)
print(f"Сгенерированный SQL-запрос: {sql_query}")

def generate_sql_with_examples_fingpt(user_input):
    prompt = """
    Вопрос: Какие транзакции были совершены сегодня?
    SQL Query: SELECT transaction_id, amount FROM transactions WHERE transaction_date = CURRENT_DATE;

    Вопрос: Сколько пользователей совершили транзакции в этом месяце?
    SQL Query: SELECT COUNT(DISTINCT user_id) FROM transactions WHERE transaction_date >= '2023-01-01';

    Вопрос: {user_input}
    SQL Query:
    """.format(user_input=user_input)

    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=150)
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)

    sql_query = sql_query.split('SQL Query:')[-1].strip()
    return sql_query

user_input = "Какие счета были оплачены в прошлом месяце?"
sql_query = generate_sql_with_examples_fingpt(user_input)
print(f"Сгенерированный SQL-запрос: {sql_query}")

import sqlparse

def validate_sql_query(query):
    try:
        parsed = sqlparse.parse(query)
        return True if parsed else False
    except Exception as e:
        return False


if validate_sql_query(sql_query):
    print(f"SQL-запрос корректен: {sql_query}")
else:
    print("SQL-запрос содержит ошибки.")


def generate_complex_sql_fingpt(user_input):
    prompt = """
    Вопрос: Какова сумма транзакций для каждого пользователя за последний месяц?
    SQL Query: SELECT user_id, SUM(amount) FROM transactions WHERE transaction_date >= '2023-01-01' GROUP BY user_id;

    Вопрос: Сколько счетов было оплачено в текущем месяце?
    SQL Query: SELECT COUNT(invoice_id) FROM invoices WHERE payment_date >= '2023-01-01';

    Вопрос: {user_input}
    SQL Query:
    """.format(user_input=user_input)

    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=150)
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)

    sql_query = sql_query.split('SQL Query:')[-1].strip()
    return sql_query

user_input = "Какова средняя сумма транзакций пользователей старше 40 лет?"
sql_query = generate_complex_sql_fingpt(user_input)
print(f"Сгенерированный сложный SQL-запрос: {sql_query}")
