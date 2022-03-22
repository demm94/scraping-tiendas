import requests, json
import time
import db
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_FALABELLA = {
    #"tv": "cat1012",
    #"notebooks": "cat70057",
    #"telefonos": "cat2018",
    #"computacion": "cat40052",
    #"computacion-gamer": "cat4850013",
    "tecnologia": "cat7090034",
    #"decoracion-iluminacion": "cat2026",
    #"cocina": "cat3065",
    #"electrohogar": "cat16510006",
    #"hombre": "cat7450065",
    "respaldos-veladores": "cat3212",
    #"sabanas": "cat3215",
    #"ropa-cama": "cat2073",
    #"banio": "cat2006",
    #"sillas": "cat9130008",
    #"muebles": "cat1008",
    #"cortinas": "cat5540010",
    #"cortinas-roller": "CATG10086",
    #"almohadas": "cat13790009",
    "mountain-bike": "cat70008",
}

def falabella():
    products = []
    for key, categoria in CATEGORIAS_FALABELLA.items():
        print(f'Procesando categoria {key}')
        API_FALABELLA = 'https://www.falabella.com/s/browse/v1/listing/cl?page={}&categoryId={}&zones=ZL_CERRILLOS,LOSC,130617,RM,RM,13'.format("1", categoria)
        r = requests.get(API_FALABELLA)
        data = r.json()['data'] if r.status_code == 200 else None
        if data:
            pagination = data['pagination']
            print(pagination)
            totalPages = int((pagination['count']/pagination['perPage']) + 1)
            for page in range(1, totalPages + 1):
                print(f'Procesando página {page} de {totalPages + 1}')
                API_FALABELLA = 'https://www.falabella.com/s/browse/v1/listing/cl?page={}&categoryId={}&zones=ZL_CERRILLOS,LOSC,130617,RM,RM,13'.format(page, categoria)
                r = requests.get(API_FALABELLA)
                if r.status_code == 409:
                    break
                data = r.json()['data'] if r.status_code == 200 else None
                print(r.status_code)
                if data:
                    for item in data['results']:
                        id = item['productId']
                        nombre = item['displayName']
                        marca = item['brand'] if "brand" in item else "Missing"
                        precio = int(item['prices'][0]['price'][0].replace('.', ''))
                        url = item['url']

                        # Descuento
                        if 'discountBadge' in item and '%' in item['discountBadge']['label']:
                            descuento = int(item['discountBadge']['label'].replace("%", "").replace("-", ""))
                        else:
                            descuento = 0

                        product = {
                            "id": id,
                            "nombre": nombre,
                            "marca": marca,
                            "precio": precio,
                            "url": item['url'],
                            "descuento": descuento,
                        }
                        products.append(product)

                        #### DB ####

                        try:
                            if not db.session.query(Articulo).get(id):
                                a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Falabella", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
                                db.session.add(a)
                                p = Precio(articulo_id=id, valor=precio)
                                db.session.add(p)
                            else:
                                a = db.session.query(Articulo).get(id)
                                if a.best_precio > precio:
                                    a.best_precio = precio
                                a.last_precio = precio
                                p = Precio(articulo_id=id, valor=precio)
                                db.session.add(p)
                            db.session.commit()
                        except Exception as e:
                            print("Error al insertar Artículo", e)
                        finally:
                            db.session.close()

                        #### DB ####

                time.sleep(4)
                if page%150 == 0:
                    time.sleep(30)

    #products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    #with open("falabella_productos.json", "w") as f:
    #        f.write('{"data": ' + json.dumps(products) + "}")
    #        f.close()

if __name__ == "__main__":
    falabella()