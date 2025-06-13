from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)  # Crea un objeto de aplicación Flask

# URI de la base de datos de MongoDB
app.config["MONGO_URI"] = "mongodb://localhost/storedb"
mongo = PyMongo(app)  # Conexión a la base de datos
db = mongo.db.products  # Colección que se creará

@app.route('/', methods=["GET"])
def index():
    return "<h1>Hello World!</h1>"

# Inserción de un producto
@app.route('/products', methods=["POST"])
def createProduct():
    # Se hace la inserción
    product = db.insert_one({
        "title": request.json["title"],
        "price": request.json["price"],
        "category": request.json["category"],
        "description": request.json["description"],
        "image": request.json["image"]
    })
    # Se retorna la respuesta
    response = make_response(
        jsonify({
            "id": str(product.inserted_id)
        }),
        201
    )

    response.headers["Content-type"] = "application/json"
    return response

#Consulta de todos los productos
@app.route("/products", methods=["GET"])
def getProducts():
    products = [] #lista para almacenar los registros de la BD
    for product in db.find(): #por cada producto de la BD...
        #los agrega en la lista en forma de estructura JSON
        products.append({
            "_id": str(ObjectId(product["_id"])),
            "title": product["title"],
            "price": product["price"],
            "category": product["category"],
            "description": product["description"],
            "image": product["image"]
        })
    return jsonify(products) #parseamos la lista a tipo JSON

#Consulta de un producto específico
@app.route("/product/<id>", methods=["GET"])
def getProduct(id):
    product = db.find_one({"_id": ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(product["_id"])),
        "title": product["title"],
        "price": product["price"],
        "category": product["category"],
        "description": product["description"],
        "image": product["image"]
    })

#Eliminar un producto
@app.route("/product/<id>", methods=["DELETE"])
def deleteProduct(id):
    product = db.delete_one({"_id": ObjectId(id)})
    response = make_response(
        jsonify({
            "num_rows": str(product.deleted_count)
        }),
        200
    )
    response.headers["Content-type"] = "application/json"
    return response

# Actualización de un producto (excepto el _id)
@app.route("/product/<id>", methods=["PUT"])
def updateProduct(id):
    print(f"Update request received for ID: {id}")
    # Obtenemos los datos del cuerpo de la petición
    data = request.json

    # Creamos el diccionario de los campos que se pueden actualizar
    updated_data = {
        "title": data["title"],
        "price": data["price"],
        "category": data["category"],
        "description": data["description"],
        "image": data["image"]
    }

    # Realizamos la actualización
    result = db.update_one(
        {"_id": ObjectId(id)},  # Filtro por ID
        {"$set": updated_data}  # Campos a actualizar
    )

    # Verificamos si se modificó algo
    if result.modified_count == 1:
        return jsonify({"message": "Producto actualizado exitosamente"}), 200
    else:
        return jsonify({"message": "No se encontró el producto o no hubo cambios"}), 404


if __name__ == "__main__":
    app.run(debug=True)

