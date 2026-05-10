# This SHOULD be detected as vulnerable
def vulnerable_query(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    cursor.execute(query)