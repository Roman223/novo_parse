from inits import mydb, mycursor

mycursor.execute(f"DELETE FROM novo_parse.main_data")
mycursor.execute(f"ALTER TABLE novo_parse.main_data AUTO_INCREMENT = 1")

mydb.commit()
print("DONE")