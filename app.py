from collections import _OrderedDictKeysView
from operator import contains
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://joaco:demodemo@cluster0.ou0gf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():

    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hola, Gracias por contactar *Amor Orgánico*.\nPuede elegir una de las siguientes opciones: "
                    "\n\n*Teclee*\n\n 1️⃣ Para *contactarnos* \n 2️⃣ Para *ordenar* snacks \n 3️⃣ Para conocer nuestro *horario* \n 4️⃣ "
                    "Para nuestra *dirección*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Por favor ingrese una respuesta válida")
            return str(res)
        
        if option == 1:
            res.message(
                "Puede ponerse en contacto con nosotros a través del teléfono o del correo electrónico.\n*Teléfono*: 3312792390 \n*E-mail* : contacto@amororganico.com \n*sitio web* : www.amororganico.com")
        elif option == 2:
            res.message("Usted ingresó *modo ordenar*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following cakes to order: \n\n1️⃣ Red Velvet  \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ Go Back")
        elif option == 3:
            res.message("Trabajamos de Lunes a Viernes *9 AM a 7 PM*.")
        elif option == 4:
            res.message("*Amor Orgánico*\n\n*Dirección*: Av de Las Rosas 559, Chapalita Oriente, 45040 Zapopan, Jal. \n\n*Tel*: 3319836946")
        else:
            res.message("Por favor ingrese una respuesta válida")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Por favor ingrese una respuesta válida")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("Puede elegir una de las siguientes opciones: "
                    "\n\n*Teclee*\n\n 1️⃣ Para *contactarnos* \n 2️⃣ Para *ordenar* snacks \n 3️⃣ Para conocer nuestro *horario* \n 4️⃣ "
                    "Para nuestra *dirección*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Excelente elección 😉")
            res.message("Por favor ingrese su dirección de entrega")
        else:
            res.message("Por favor ingrese una respuesta válida")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("¡Gracias por su orden! 😉")
        res.message(f"Su orden de *{selected}* ha sido recibida y será entregada en su dirección de entrega.")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_date": datetime.now()})
        users.update_one(
                {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hola, Gracias por contactarnos de nuevo.\nPuede elegir una de las siguientes opciones: "
                    "\n\n*Teclee*\n\n 1️⃣ Para *contactarnos* \n 2️⃣ Para *ordenar* snacks \n 3️⃣ Para conocer nuestro *horario* \n 4️⃣ "
                    "Para nuestra *dirección*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
        
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return str(res)

if __name__ == "__main__":
    app.run()
