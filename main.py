import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# am considerat ca elementul product_id cel mai probabil este codul EAN / GTIN, deoarece nu am gasit un alt element
# cu un nume sau o forma similara cu un cod EAN / GTIN, iar valoarea numerica din campul product_id seamana cu un
# cod de acel format.

# Setam URL-ul paginii de scrape-uit
url = 'https://citygross.se'

# Adaugam headere pentru a imita un utilizator real, deoarece primeam eroarea 403 cand incercam sa accesez site-ul
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

try:
    # Utilizam Selenium pentru a gestiona continutul cu incarcare dinamica
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Rulam Chrome in modul headless
    driver = webdriver.Chrome(options=options)

    # Incarcam pagina
    driver.get(url)

    # Asteptam sa fim siguri ca tot continutul paginii este incarcat cand incercam sa facem scraping
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "productcard-container")))

    # Incepem scraping-ul dupa ce pagina s-a incarcat complet
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Gasim toate containerele de produse de pe pagina
    products = soup.find_all('div', class_='l-column-30_xs-30_sm-20_md-15_lg-12_xlg-10-mobileGutter p-carousel_card')
    print(f'Number of products found: {len(products)}')  # Afisam numarul de produse gasite

    # Cream o lista in care sa stocam datele extrase
    products_data = []

    # Iteram prin toate containerele, extragand datele relevante din acestea
    for product in products:
        try:
            # Extragem numele produsului
            name = product.find('h2', class_='details__name').text.strip()
            print(f'Name: {name}')  # Il si afisam

            # Extragem marca
            brand = product.find('h3').text.strip()
            # Cantitatea de produs este inclusa si in string-ul ce reprezinta marca, separata prin o virgula,
            # asa ca o scoatem ca sa pastram doar numele marcii
            brand = brand.split(',')[0].strip()
            print(f'Brand: {brand}')  # Afisam marca
            # Extragem pretul
            price_effect_type = product.find('p', class_='c-pricetag__effect-type') # Mai intai extragem numarul de unitati incluse
            price_integer = product.find('span', class_='integer') # Apoi extragem numarul aferenta pretului
            price = price_integer.text.replace('\n', '').replace(
                price_integer.find('div', class_='integer__column').text, '').strip() # Scoatem simbolul :- care indica pretul pe site
            if price_effect_type:
                price = f"{price_effect_type.text.strip()} {price}"
            print(f'Price: {price}')  # Afisam pretul

            # Extragem codul EAN / GTIN al produsului
            product_id = product['data-productid']
            print(f'EAN: {product_id}')
            # Adaugam toate datele extrase in lista
            products_data.append({
                'name': name,
                'brand': brand,
                'price': price,
                'ean': product_id
            })
        except Exception as e:
            print(f'Error processing product: {e}')  # Eroare in caz ca nu se extrag corect datele

    # Afisam din nou toate datele sub forma de liste
    for product in products_data:
        print(product)
except Exception as e:
    print(f'Error scraping website: {e}')  # Eroare in caz ca esueaza scraping-ul
 # Inchidem browserul
driver.quit()
