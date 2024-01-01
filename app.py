from accounts import create_app
app = create_app()

if __name__ == "__main__":
    app.run()
import mysql.connector
import pandas as pd
if True:
     cnx = mysql.connector.connect(

        host = 'buzzpulse.ccvv7zf7lno9.eu-west-1.rds.amazonaws.com',

        user = 'admin',

        password = '99q&cUzpOG2%',

        database='buzzpulse')

 

     df = pd.read_sql_query('SELECT * from user', con=cnx)
     pd.set_option('display.max_columns', None)
     print(df)

