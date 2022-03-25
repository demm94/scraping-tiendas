import requests, re
import time
import db
from bs4 import BeautifulSoup
from models.Articulo import Articulo
from models.Precio import Precio

CATEGORIAS_RIPLEY = {
    "decoracion": "/decoracion/decoracion-hogar/",
    "notebooks": "/tecno/computacion/notebooks",
    "celulares": "/tecno/celulares",
    "tv": "/tecno/television/smart-tv",
    "audio": "/tecno/audio-y-musica",
    "audifonos": "/tecno/especial-audifonos",
    "tecno-gamer": "/tecno/computacion-gamer",
    "cocina": "/electro/cocina",
    "cortinas": "/decoracion/cortinas",
    "ropa-cama": "/dormitorio/ropa-de-cama",
    "jeans": "/moda-hombre/jeans-y-pantalones",
    "chaquetas": "/moda-hombre/tops-y-chaquetas",
    "ropa-interior": "/moda-hombre/ropa-interior-y-pijamas",
    "pesas-entrenamiento": "/deporte-y-aventura/fitness/pesas-y-entrenamiento",
    "sabanas": "/dormitorio/ropa-de-cama/sabanas",
    "polerones": "/moda-hombre/tops-y-chaquetas/polerones",
    "jeans": "/moda-hombre/jeans-y-pantalones/jeans",
    "almohadas": "/dormitorio/ropa-de-cama/almohadas",
    "zapatillas": "/zapatos-y-zapatillas/zapatillas/zapatillas-deportivas",
    "muebles-dormitorio-bano": "/muebles/dormitorio-y-bano",
    "muebles-living": "/muebles/living-y-sala-de-estar",
    "muebles-home-office": "/muebles/home-office-y-oficina",
    "electro-electrodomesticos": "/electro/electrodomesticos",
    "electro-cuidado-personal": "/electro/cuidado-personal",
    "bicicletas": "/deporte-y-aventura/bicicletas",
    "deporte-zapatillas": "/deporte-y-aventura/zapatillas",
    "ropa-deportiva": "/deporte-y-aventura/ropa-deportiva",
    "vitaminas": "/salud-y-bienestar/vitaminas-y-suplementos/ver-todo-vitaminas-y-suplementos",
    "cuidado-personal": "/salud-y-bienestar/salud-y-cuidado-personal",


}

def ripley():
    size = 48
    for key, categoria in CATEGORIAS_RIPLEY.items():
        print(f'Procesando categoria {key}')
        BASE_RIPLEY = "https://simple.ripley.cl"
        URI = BASE_RIPLEY + categoria + "?s=mdco"
        r = requests.get(URI)
        soup = BeautifulSoup(r.text, 'lxml')
        results = soup.find("div", {"class": "catalog-page__results-text"})
        totalProducts = re.sub(r'([^0-9])\w+', '', results.text.strip()) # Total de productos
        print(f'Total de productos: {totalProducts}')
        totalPages = int(int(totalProducts)/size + 1)
        for page in range(1, totalPages + 1):
            print(f'Procesando página {page} de {totalPages}')
            API_RIPLEY = URI + "&page={}".format(page)
            r = requests.get(API_RIPLEY)
            print(r.status_code)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                catalog = soup.find("div", {"class": "catalog-container"})
                divs = catalog.find_all("div", {"class": "catalog-product-item"})
                for div in divs:
                    nombre = div.find("div", {"class": "catalog-product-details__name"})
                    marca = div.find("div", {"class": "brand-logo"})
                    precios = div.find("ul", {"class": "catalog-prices__list"})
                    descuento = div.find("div", {"class": "catalog-product-details__discount-tag"})
                    url = div.find("a", {"class": "catalog-product-item"})

                    id = url["id"].replace("P", "")
                    nombre = nombre.text.strip() if nombre else 'Missing'
                    marca = marca.text.strip() if marca else 'Missing'
                    descuento = int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento else 0
                    url = f'https://simple.ripley.cl{url["href"]}'

                    #Validaciones
                    if precios:
                        precios = precios.find_all("li")
                        precio = precios[-1]
                        precio = int(precio.text.strip().replace('$','').replace('.',''))
                    else:
                        precio = 0
                        
                    #### DB ####

                    try:
                        if not db.session.query(Articulo).get(id):
                            a = Articulo(id=id, nombre=nombre, marca=marca, tienda="Ripley", url=url, best_precio=precio, last_precio=precio, descuento=descuento)
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

    #products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    #with open("ripley_productos.json", "w") as f:
    #        f.write('{"data": ' + json.dumps(products) + "}")
    #        f.close()

if __name__ == "__main__":
    ripley()