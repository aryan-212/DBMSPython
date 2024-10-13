import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="aryan",
    password="aryan@012",
    charset="utf8mb4",
    collation="utf8mb4_general_ci",
)
cursor = mydb.cursor()

# Execute the query to show databases
cursor.execute("SHOW DATABASES")

# Fetch all the results
databases = cursor.fetchall()

# Print each database name
print(databases[0], databases[1])

# Close the cursor and connection
cursor.close()
mydb.close()
