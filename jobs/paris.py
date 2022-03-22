import requests, json, re
import time
import db
from bs4 import BeautifulSoup
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_PARIS = {
    #"tecnologia": "/tecnologia/",
    #"electro": "/electro/",
    #"dormitorio": "/dormitorio/",
    #"muebles": "/muebles/",
    #"cortinas": "/decohogar/decoracion/cortinas/",
    #"decoracion": "/decohogar/decoracion/",
    #"cocina": "/linea-blanca/cocina/",
    #"ropa-cama": "/dormitorio/ropa-cama/",
    #"sabanas": "/dormitorio/ropa-cama/sabanas/",
    #"tv": "/electro/television/",
    #"notebooks": "/tecnologia/computadores/notebooks/",
    "tecno": "/tecnologia/",
    #"moda-hombre": "/hombre/moda/",
    #"ropa-interior": "/hombre/ropa-interior/",
    #"zapatos": "/zapatos/hombre/",
    "mountain-bike": "/deportes/bicicletas/mountain-bike/",
    #"almohadas": "/dormitorio/ropa-cama/almohadas-fundas/",
}

def paris():
    for key, categoria in CATEGORIAS_PARIS.items():
            BASE_PARIS = "https://www.paris.cl" + categoria
            start = 0
            size = 40
            r = requests.get(BASE_PARIS)
            soup = BeautifulSoup(r.text, 'lxml')
            results = soup.find("div", {"class": "search-result-content"})
            totalProducts = re.sub(r'([^0-9])\w+', '', results.text.replace(',', '').strip()) # Total de productos
            totalPages = int(int(totalProducts)/size + 1)
            print(f'Total de productos: {totalProducts}')
            products = []
            for page in range(0, totalPages):
                print(f'Procesando página {page + 1} de {totalPages}')
                URL_PARIS = BASE_PARIS + '?start={}&sz={}'.format(start, size)
                r = requests.get(URL_PARIS)
                print(r.status_code)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    ul = soup.find("ul", {"id": "search-result-items"})
                    lis = ul.find_all("li", recursive=False) # Primer nivel
                    for li in lis:
                        id = li.find("div", {"class": "product-tile"})
                        nombre = li.find("span", {"class": "ellipsis_text"})
                        marca = li.find("p", {"class": "brand-product-plp"})
                        precio = li.find("div", {"class": "price__text"})
                        descuento = li.find("div", {"class": "price__badge"})
                        url = li.find("a", {"class": "thumb-link js-product-layer"})

                        id = id["data-itemid"]
                        nombre = nombre.text.strip() if nombre else 'Missing'
                        marca = marca.text.strip() if marca else 'Missing'
                        descuento = int(descuento.text.strip().replace("%", "")) if descuento else 0

                        #Validaciones
                        if precio:
                            precio_procesado = precio.text.replace('$','').replace('.','').strip()
                            if precio_procesado.isdigit():
                                precio = float(precio_procesado)
                            else:
                                precio = 0

                        if url:
                            if "https" in url['href']:
                                url = url['href']
                            else:
                                url = f'https://www.paris.cl{url["href"]}'

                        product = {
                            "nombre": nombre,
                            "marca": marca,
                            "precio": precio,
                            "descuento": descuento,
                            "url": url
                        }
                        products.append(product)

                        #### DB ####

                        try:
                            if not db.session.query(Articulo).get(id):
                                a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Paris", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
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

                start+=size
                time.sleep(1)

    #products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    #with open("paris_productos.json", "w") as f:
    #    f.write('{"data": ' + json.dumps(products) + "}")
    #    f.close()

if __name__ == "__main__":
    paris()