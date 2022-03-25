import requests
import time
import db
from bs4 import BeautifulSoup
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_ABCDIN = {
    #"computacion": "/computacion/notebooks",
    #"ropa-cama": "/dormitorio/ropa-de-cama/toda-ropa-de-cama",
    #"respaldo-velador": "/dormitorio/muebles-dormitorio/respaldo-y-velador",
    #"ofertas": "/ofertas",
    "celulares": "/telefonia",
    "electro": "/electro",
    "computacio-gamer": "/computacion/mundo-gamer",
    "monitores": "/computacion/monitores-y-proyectores",
    "bicicletas": "/outdoor-y-motos/bicicletas",
    "fitness": "/outdoor-y-motos/fitness/todo-fitness",
    "muebles-dormitorio": "/dormitorio/muebles-dormitorio",
    "ropa-cama": "/dormitorio/ropa-de-cama/toda-ropa-de-cama"
}

def abcdin():
    BASE_ABCDIN = "https://www.abcdin.cl"
    per_page = 16
    products = []
    for key, categoria in CATEGORIAS_ABCDIN.items():
        print(f'Procesando categoria {key}')
        URI = BASE_ABCDIN + categoria
        r = requests.get(URI)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            # Total de productos
            totalProducts = soup.find("span", {"class": "toolbar-number"}).text.strip()
            totalPages = int(int(totalProducts)/per_page + 1)
            for page in range(1, totalPages + 1):
                print(f'Procesando página {page} de {totalPages}')
                URI_PAGE = URI + "?p={}".format(page)
                r = requests.get(URI_PAGE)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    container_items = soup.find("ol", {"class": "items"})
                    items = container_items.find_all("li", {"class": "item"})
                    for item in items:
                        id = item.find("form")
                        nombre = item.find("strong", {"class": "name"})
                        marca = item.find("span", {"class": "product-item-brand"})
                        descuento = item.find("div", {"class": "amasty-label-text"})
                        precio = item.find("span", {"class": "price"})
                        url = item.find("a", {"class": "product"})

                        id = id['data-product-sku'] if id else None
                        nombre = nombre.text.strip() if nombre else 'Missing'
                        marca = marca.text.strip() if marca else 'Missing'
                        precio = int(precio.text.strip().replace('$','').replace('.','')) if precio else 0
                        descuento = int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0
                        
                        #Validaciones
                        if url:
                            if "https" in url['href']:
                                url = url['href']
                            else:
                                url = BASE_ABCDIN + url["href"]

                        product = {
                                "nombre": nombre,
                                "marca": marca,
                                "precio": precio,
                                "descuento": descuento,
                                "url": url
                            }
                        products.append(product)

                        #### DB ####
                        
                        if id:
                            try:
                                if not db.session.query(Articulo).get(id):
                                    a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Abcdin", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
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
                time.sleep(1)

if __name__ == "__main__":
    abcdin()