import requests
import time
import db
from bs4 import BeautifulSoup
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_LAPOLAR = {
    "tecnologia": "/tecnologia/",
    "linea-blanca": "/linea-blanca/",
    "dormitorio": "/dormitorio/",
    "muebles": "/muebles/",
    #"decohogar": "/decohogar/",
    #"deportes": "/deportes/",
    #"hombre": "/hombre/",
    #"computacion": "/tecnologia/computadores/",
    #"cortinas": "/decohogar/decoracion/cortinas/",
}

def lapolar():
    BASE_LAPOLAR = "https://www.lapolar.cl"
    per_page = 36
    for key, categoria in CATEGORIAS_LAPOLAR.items():
        print(f'Procesando categoria {key}')
        URI = BASE_LAPOLAR + categoria
        r = requests.get(URI)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            # Total de productos
            totalProducts = soup.find_all("span", {"class": "filtering__results-count"})[1].text.strip()
            totalPages = int(int(totalProducts)/per_page + 1)
            for page in range(1, totalPages + 1):
                print(f'Procesando página {page} de {totalPages}')
                URI_PAGE = URI + "?start={}&sz={}".format((page - 1)*per_page, per_page)
                r = requests.get(URI_PAGE)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    container_items = soup.find("div", {"class": "product-grid"})
                    if container_items:
                        items = container_items.find_all("div", {"class": "product-tile__item"})
                        for item in items:
                            id = item.find("div", {"class": "product-tile__wrapper"})
                            nombre = item.find("div", {"class": "pdp-link"})
                            marca = item.find("div", {"class": "tile-brand"})
                            descuento = item.find("p", {"class": "promotion-badge"})
                            precio = item.find("span", {"class": "price-value"})
                            url = item.find("a", {"class": "link"})

                            id = id["data-pid"] if id else None
                            nombre = nombre.text.strip() if nombre else 'Missing'
                            marca = marca.text.strip() if marca else 'Missing'
                            precio = int(precio.text.strip().replace('$','').replace('.','')) if precio else 0
                            descuento = int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0
                            
                            #Validaciones
                            if url:
                                if "https" in url['href']:
                                    url = url['href']
                                else:
                                    url = BASE_LAPOLAR + url["href"]

                            #### DB ####
                        
                            if id:
                                try:
                                    if not db.session.query(Articulo).get(id):
                                        a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Lapolar", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
                                        db.session.add(a)
                                        p = Precio(articulo_id=id, valor=precio)
                                        db.session.add(p)
                                    else:
                                        a = db.session.query(Articulo).get(id)
                                        if a.best_precio > precio:
                                            a.best_precio = precio
                                        a.last_precio = precio
                                        a.tienda = "Lapolar"
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
    lapolar()