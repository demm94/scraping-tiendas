import requests
import time
import db
from bs4 import BeautifulSoup
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_HITES = {
    "tecnologia": "/tecnologia/",
    "electro": "/electro-hogar/",
    "dormitorio": "/dormitorio/",
    "liquidacion": "/liquidacion/",
    "muebles": "/muebles/",
    "hogar": "/hogar/",
    "herramientas": "/herramientas/",
    "celulares": "/celulares/",
}

def hites():
    BASE_HITES = "https://www.hites.com"
    per_page = 24
    for key, categoria in CATEGORIAS_HITES.items():
        print(f'Procesando categoria {key}')
        URI = BASE_HITES + categoria
        r = requests.get(URI)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            # Total de productos
            totalProducts_label = soup.find("span", {"class": "product-results-count"}).text.strip()
            totalProducts = totalProducts_label.split(" ")[6].replace(",", "").replace(")", "")
            totalPages = int(int(totalProducts)/per_page + 1)
            for page in range(1, totalPages + 1):
                print(f'Procesando página {page} de {totalPages}')
                URI_PAGE = URI + "?sz={}&start={}&srule=best-matches".format(per_page, (page - 1)*per_page)
                r = requests.get(URI_PAGE)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    container_items = soup.find("div", {"class": "product-view"})
                    if container_items:
                        items = container_items.find_all("div", recursive=False) # First Level
                        for item in items:
                            id = item.find("div", {"class": "product-tile"})
                            nombre = item.find("a", {"class": "product-name--bundle"})
                            marca = item.find("span", {"class": "product-brand"})
                            descuento = item.find("span", {"class": "discount-badge"})
                            precio = item.find_all("span", {"class": "value"})
                            url = nombre['href']

                            id = id['data-pid'] if id else None
                            nombre = nombre.text.strip() if nombre else 'Missing'
                            marca = marca.text.strip() if marca else 'Missing'
                            precio = float(precio[0]['content']) if precio else 0
                            descuento = int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0
                            
                            #Validaciones
                            if url:
                                if "https" in url:
                                    url = url
                                else:
                                    url = BASE_HITES + url

                            #### DB ####
                        
                            if id:
                                try:
                                    if not db.session.query(Articulo).get(id):
                                        a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Hites", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
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
    hites()