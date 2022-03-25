import requests
import time
import db
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_LIDER = {
    "tecno": "Tecno",
    "celulares": "Celulares",
    "electro": "Electrohogar",
    "ferreteria": "Ferretería",
    "deportes": "Deportes",
    "liquidacion": "Destacados Mundo Lider/Liquidación",
    "cortinas": "Decohogar/Decoración/Cortinas",
}

def lider():
    BASE_LIDER = "https://buysmart-bff-production.lider.cl/buysmart-bff/category"
    per_page = 16
    for key, categoria in CATEGORIAS_LIDER.items():
        print(f'Procesando categoria {key}')
        r = requests.post(BASE_LIDER, json={
            "categories": categoria,
            "page": 1,
            "facets": [],
            "sortBy": "",
            "hitsPerPage": per_page
        })
        if r.status_code == 200:
            totalPages = int(r.json()['nbPages'])
            for page in range(1, totalPages + 1):
                print(f'Procesando página {page} de {totalPages}')
                r = requests.post(BASE_LIDER, json={
                    "categories": categoria,
                    "page": page,
                    "facets": [],
                    "sortBy": "",
                    "hitsPerPage": per_page
                })
                if r.status_code == 200:
                    items = r.json()['products']
                    for item in items:
                        id = item["ID"]
                        nombre = item['displayName']
                        marca = item['brand']
                        precio = item['price']['BasePriceSales']
                        descuento = item['discount']
                        url = "https://www.lider.cl/catalogo/product/sku/" + str(item['sku'])

                        #### DB ####
                        
                        if id:
                            try:
                                if not db.session.query(Articulo).get(id):
                                    a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Lider", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
                                    db.session.add(a)
                                    p = Precio(articulo_id=id, valor=precio)
                                    db.session.add(p)
                                else:
                                    a = db.session.query(Articulo).get(id)
                                    if a.best_precio > precio:
                                        a.best_precio = precio
                                    a.last_precio = precio
                                    a.tienda = "Lider"
                                    p = Precio(articulo_id=id, valor=precio)
                                    db.session.add(p)
                                db.session.commit()
                            except Exception as e:
                                print("Error al insertar Artículo", e)
                            finally:
                                db.session.close()

                        #### DB ####

                time.sleep(1)       

if __name__ == "__main__":
    lider()