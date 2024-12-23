from tkinter import *
import sqlite3
from PIL import Image, ImageTk
import os

def create_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_name TEXT NOT NULL,
        image_data BLOB NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def insert_image(image_path):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    with open(image_path, 'rb') as file:
        image_blob = file.read()

    image_name = os.path.basename(image_path).lower()  # Convertir el nombre de la imagen a minúsculas
    cursor.execute("INSERT INTO Images (image_name, image_data) VALUES (?, ?)", (image_name, sqlite3.Binary(image_blob)))
    conn.commit()

    conn.close()

def get_images_by_names(image_names):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(image_names))
    query = f"SELECT image_name, image_data FROM Images WHERE image_name IN ({placeholders})"
    cursor.execute(query, image_names)
    images = cursor.fetchall()

    conn.close()

    image_dict = {name: data for name, data in images}
    return image_dict

def text_to_image():
    root = Tk()
    root.title("Texto a Imagen")

    text = "Hola amigo".lower()  # Convertir el texto a minúsculas
    words = text.split()  # Separar el texto en palabras
    image_size = (100, 100)  # Tamaño deseado para las imágenes

    image_names = [f"{char}.png" for word in words for char in word]
    images_dict = get_images_by_names(image_names)

    row = 0

    for word in words:
        column = 0  # Reiniciar la columna a 0 al empezar una nueva palabra
        for char in word:
            image_name = f"{char}.png"
            if image_name in images_dict:
                image_data = images_dict[image_name]
                with open(f'image_from_db_{char}.png', 'wb') as file:
                    file.write(image_data)

                img = Image.open(f'image_from_db_{char}.png')
                img = img.resize(image_size, Image.LANCZOS)  # Redimensionar la imagen
                photo = ImageTk.PhotoImage(img)

                label = Label(root, image=photo)
                label.image = photo
                label.grid(row=row, column=column, padx=5, pady=5)  # Colocar en la fila y columna actuales

                column += 1
        
        row += 1  # Mover a la siguiente fila después de cada palabra

    root.mainloop()

# Crear la base de datos si no existe
create_db()

# Insertar imágenes en la base de datos si no están ya insertadas
images_to_insert = ['img/A.png', 'img/B.png', 'img/C.png', 'img/D.png', 'img/E.png', 'img/F.png', 'img/G.png', 
                    'img/H.png', 'img/I.png', 'img/J.png', 'img/K.png', 'img/L.png', 'img/LL.png', 'img/M.png', 
                    'img/N.png', 'img/Ñ.png', 'img/O.png', 'img/P.png', 'img/Q.png', 'img/R.png', 'img/S.png', 
                    'img/T.png', 'img/U.png', 'img/V.png', 'img/W.png', 'img/X.png', 'img/Y.png', 'img/Z.png']

for image in images_to_insert:
    insert_image(image)

# Mostrar texto como imágenes en la ventana
text_to_image()
