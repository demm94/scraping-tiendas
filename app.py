from pydoc import describe
from flask import Flask, jsonify, render_template
import requests, json, re, time
from bs4 import BeautifulSoup

app = Flask(__name__)

CATEGORIAS_FALABELLA = {
    #"tv": "cat1012",
    #"notebooks": "cat70057",
    #"telefonos": "cat2018",
    #"computacion": "cat40052",
    #"computacion-gamer": "cat4850013",
    #"tecnologia": "cat7090034",
    #"decoracion-iluminacion": "cat2026",
    #"cocina": "cat3065",
    #"electrohogar": "cat16510006",
    #"hombre": "cat7450065",
    #"respaldos-veladores": "cat3212",
    #"sabanas": "cat3215"
    #"ropa-cama": "cat2073",
    #"banio": "cat2006",
    "sillas": "cat9130008",
}

CATEGORIAS_PARIS = {
    #"tecnologia": "/tecnologia/",
    #"electro": "/electro/",
    #"dormitorio": "/dormitorio/",
    #"muebles": "/muebles/",
    #"decoracion": "/decohogar/decoracion/",
    #"cocina": "/linea-blanca/cocina/",
    #"ropa-cama": "/dormitorio/ropa-cama/",
    #"tv": "/electro/television/",
    #"notebooks": "/tecnologia/computadores/notebooks/",
    "tecno": "/tecnologia/",
}

CATEGORIAS_RIPLEY = {
    #"decoracion": "/decoracion/decoracion-hogar/",
    #"notebooks": "/tecno/computacion/notebooks",
    #"celulares": "/tecno/celulares",
    #"tv": "/tecno/television/smart-tv",
    #"cocina": "/electro/cocina",
    "cortinas": "/decoracion/cortinas",
    "ropa-cama": "/dormitorio/ropa-de-cama",
}

CATEGORIAS_ABCDIN = {
    "computacion": "/computacion/notebooks",
    "ropa-cama": "/dormitorio/ropa-de-cama/toda-ropa-de-cama",
    "respaldo-velador": "/dormitorio/muebles-dormitorio/respaldo-y-velador",
    "ofertas": "/ofertas",
    "tv-video": "/electro/tv-y-video"
}

CATEGORIAS_LAPOLAR = {
    #"tecnologia": "/tecnologia/",
    #"linea-blanca": "/linea-blanca/",
    #"dormitorio": "/dormitorio/",
    #"muebles": "/muebles/",
    #"decohogar": "/decohogar/",
    #"deportes": "/deportes/",
    #"hombre": "/hombre/",
    "computacion": "/tecnologia/computadores/"
}

CATEGORIAS_LIDER = {
    "tecno": "Tecno",
    "celulares": "Celulares",
    "electro": "Electrohogar",
    "ferreteria": "Ferretería",
    "deportes": "Deportes",
}

CATEGORIAS_HITES = {
    "tecnologia": "/tecnologia/",
    "dormitorio": "/dormitorio/",
    "liquidacion": "/liquidacion/",
    "muebles": "/muebles/",
    "hogar": "/hogar/",
}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/falabella')
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
                        # Descuento
                        if 'discountBadge' in item and '%' in item['discountBadge']['label']:
                            descuento = int(item['discountBadge']['label'].replace("%", "").replace("-", ""))
                        else:
                            descuento = 0
                        product = {
                            "nombre": item['displayName'],
                            "marca": item['brand'] if "brand" in item else "Missing",
                            "precio": int(item['prices'][0]['price'][0].replace('.', '')),
                            "url": item['url'],
                            "descuento": descuento,
                        }
                        products.append(product)
                time.sleep(4)
                if page%150 == 0:
                    time.sleep(30)

    products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    with open("falabella_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()
    print(pagination)
    print(totalPages)
    return "<h1>Success!</h1>"

@app.route('/falabella/productos')
def productosFalabella():
    jf = open("falabella_productos.json")
    data = json.load(jf)['data']
    return render_template('falabella.html', products=data)

@app.route('/api/falabella')
def apiFalabella():
    jf = open("falabella_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/paris')
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
                    nombre = li.find("span", {"class": "ellipsis_text"})
                    marca = li.find("p", {"class": "brand-product-plp"})
                    precio = li.find("div", {"class": "price__text"})
                    descuento = li.find("div", {"class": "price__badge"})
                    url = li.find("a", {"class": "thumb-link js-product-layer"})

                    #Validaciones
                    if precio:
                        precio_procesado = precio.text.replace('$','').replace('.','').strip()
                        if precio_procesado.isdigit():
                            precio_procesado = int(precio_procesado)
                        else:
                            precio_procesado = 0

                    if url:
                        if "https" in url['href']:
                            url = url['href']
                        else:
                            url = f'https://www.paris.cl{url["href"]}'

                    product = {
                        "nombre": nombre.text.strip() if nombre else 'Missing',
                        "marca": marca.text.strip() if marca else 'Missing',
                        "precio": precio_procesado,
                        "descuento": int(descuento.text.strip().replace("%", "")) if descuento else 0,
                        "url": url
                    }
                    products.append(product)
            start+=size
            time.sleep(1)

    products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    with open("paris_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()
    return "<h1>Success!</h1>"

@app.route('/paris/productos')
def productosParis():
    jf = open("paris_productos.json")
    data = json.load(jf)['data']
    return render_template('paris.html', products=data)

@app.route('/api/paris')
def apiParis():
    jf = open("paris_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/ripley')
def ripley():
    size = 48
    products = []
    for key, categoria in CATEGORIAS_RIPLEY.items():
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
                    precio = div.find("li", {"class": "catalog-prices__offer-price"})
                    descuento = div.find("div", {"class": "catalog-product-details__discount-tag"})
                    url = div.find("a", {"class": "catalog-product-item"})
                    product = {
                        "nombre": nombre.text.strip() if nombre else 'Missing',
                        "marca": marca.text.strip() if marca else 'Missing',
                        "precio": int(precio.text.strip().replace('$','').replace('.','')) if precio else 0,
                        "descuento": int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento else 0,
                        "url": f'https://simple.ripley.cl{url["href"]}'
                    }
                    products.append(product)
            time.sleep(1)

    products = sorted(products, key=lambda p: int(p["descuento"]), reverse=True)

    with open("ripley_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()
    return "<h1>Success!</h1>"

@app.route('/ripley/productos')
def productosRipley():
    jf = open("ripley_productos.json")
    data = json.load(jf)['data']
    return render_template('ripley.html', products=data)

@app.route('/api/ripley')
def apiRipley():
    jf = open("ripley_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/abcdin')
def abcdin():
    BASE_ABCDIN = "https://www.abcdin.cl"
    per_page = 16
    products = []
    for key, categoria in CATEGORIAS_ABCDIN.items():
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
                        nombre = item.find("strong", {"class": "name"})
                        marca = item.find("span", {"class": "product-item-brand"})
                        descuento = item.find("div", {"class": "amasty-label-text"})
                        precio = item.find("span", {"class": "price"})
                        url = item.find("a", {"class": "product"})
                        
                        #Validaciones
                        if url:
                            if "https" in url['href']:
                                url = url['href']
                            else:
                                url = BASE_ABCDIN + url["href"]

                        product = {
                                "nombre": nombre.text.strip() if nombre else 'Missing',
                                "marca": marca.text.strip() if marca else 'Missing',
                                "precio": int(precio.text.strip().replace('$','').replace('.','')) if precio else 0,
                                "descuento": int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0,
                                "url": url
                            }
                        products.append(product)
                time.sleep(1)
    with open("abcdin_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()
    return "<h1>Success!</h1>"

@app.route('/abcdin/productos')
def productosAbcdin():
    jf = open("abcdin_productos.json")
    data = json.load(jf)['data']
    return render_template('abcdin.html', products=data)

@app.route('/api/abcdin')
def apiAbcdin():
    jf = open("abcdin_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/lapolar')
def lapolar():
    BASE_LAPOLAR = "https://www.lapolar.cl"
    per_page = 36
    products = []
    for key, categoria in CATEGORIAS_LAPOLAR.items():
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
                            nombre = item.find("div", {"class": "pdp-link"})
                            marca = item.find("div", {"class": "tile-brand"})
                            descuento = item.find("p", {"class": "promotion-badge"})
                            precio = item.find("span", {"class": "price-value"})
                            url = item.find("a", {"class": "link"})

                            #Validaciones
                            if url:
                                if "https" in url['href']:
                                    url = url['href']
                                else:
                                    url = BASE_LAPOLAR + url["href"]

                            product = {
                                    "nombre": nombre.text.strip() if nombre else 'Missing',
                                    "marca": marca.text.strip() if marca else 'Missing',
                                    "precio": int(precio.text.strip().replace('$','').replace('.','')) if precio else 0,
                                    "descuento": int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0,
                                    "url": url
                                }
                            products.append(product)
                time.sleep(1)
    with open("lapolar_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()

    return "<h1>Success!</h1>"


@app.route('/lapolar/productos')
def productosLapolar():
    jf = open("lapolar_productos.json")
    data = json.load(jf)['data']
    return render_template('lapolar.html', products=data)

@app.route('/api/lapolar')
def apiLapolar():
    jf = open("lapolar_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/lider')
def lider():
    BASE_LIDER = "https://buysmart-bff-production.lider.cl/buysmart-bff/category"
    per_page = 16
    products = []
    for key, categoria in CATEGORIAS_LIDER.items():
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
                        nombre = item['displayName']
                        marca = item['brand']
                        precio = item['price']['BasePriceSales']
                        descuento = item['discount']
                        url = "https://www.lider.cl/catalogo/product/sku/" + str(item['sku'])

                        product = {
                            "nombre": nombre,
                            "marca": marca,
                            "precio": precio,
                            "descuento": descuento,
                            "url": url
                        }
                        products.append(product)
                time.sleep(1)
    with open("lider_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()
        
    return "<h1>Success!</h1>"

@app.route('/lider/productos')
def productosLider():
    jf = open("lider_productos.json")
    data = json.load(jf)['data']
    return render_template('lider.html', products=data)

@app.route('/api/lider')
def apiLider():
    jf = open("lider_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )

@app.route('/hites')
def hites():
    BASE_HITES = "https://www.hites.com"
    per_page = 24
    products = []
    for key, categoria in CATEGORIAS_HITES.items():
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
                            nombre = item.find("a", {"class": "product-name--bundle"})
                            marca = item.find("span", {"class": "product-brand"})
                            descuento = item.find("span", {"class": "discount-badge"})
                            precio = item.find_all("span", {"class": "value"})
                            url = nombre['href']
                            
                            #Validaciones
                            if url:
                                if "https" in url:
                                    url = url
                                else:
                                    url = BASE_HITES + url

                            product = {
                                    "nombre": nombre.text.strip() if nombre else 'Missing',
                                    "marca": marca.text.strip() if marca else 'Missing',
                                    "precio": int(precio[0]['content']) if precio else 0,
                                    "descuento": int(descuento.text.strip().replace("%", "").replace("-", "")) if descuento and descuento.text != '' else 0,
                                    "url": url
                                }
                            products.append(product)
                time.sleep(1)

    with open("hites_productos.json", "w") as f:
            f.write('{"data": ' + json.dumps(products) + "}")
            f.close()

    return "<h1>Success!</h1>"

@app.route('/hites/productos')
def productosHites():
    jf = open("hites_productos.json")
    data = json.load(jf)['data']
    return render_template('hites.html', products=data)

@app.route('/api/hites')
def apiHites():
    jf = open("hites_productos.json")
    data = json.load(jf)['data']
    return jsonify(
        {
            "data": data,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "draw": 1,
        }
    )