import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

headers = {
  'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

links_kabum = [str("https://www.kabum.com.br/hardware/placa-de-video-vga?page_number={}&page_size=20&facet_filters=&sort=most_searched").format(i) for i in range(1, 42)]

driver = webdriver.Chrome()

# Arrays
ad_title = []
precos = []
marcas = []
modelos = []
gpu = []  # AMD ou NVIDIA
unidades_de_processamento = []
tamanhos_de_memoria = []
velocidades_de_memoria  = []
tipos_de_memoria = []
fontes_recomendadas = []
garantias = []
pesos = []

for link in links_kabum:
    # Getting products
    req = requests.get(link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    products = soup.find_all(class_ = 'productCard')

    for product in products:
        product_path = (product.find('a'))['href']
        product_link = str("https://www.kabum.com.br" + product_path)

        # Teste unitário
        # product_link = str("https://www.kabum.com.br/produto/355239/placa-de-video-colorful-nvidia-geforce-rtx-3060-bilibili-e-sports-edition-oc-igame-12gb-gddr6-lhr-v-192-bits")

        product_req = requests.get(product_link, headers=headers)
        product_soup = BeautifulSoup(product_req.text, 'html.parser')

        # Showing product link
        print("Link: " + product_link)

        try:
            driver.get(product_link)
            info = driver.find_element(By.ID, "secaoInformacoesTecnicas")
        except:
            continue

        info = driver.find_element(By.ID, "secaoInformacoesTecnicas")
        if info != None:
            # Preço: 
            price = product_soup.find(class_ = 'finalPrice')
            if price != None:
                price = str(product_soup.find(class_ = 'finalPrice').text)[3:].split('.')
                if (len(price) > 1):
                    price[1] = price[1].split(',')
                    price_formatted = float(price[0] + price[1][0] + '.' + price[1][1])
                else:
                    price[0] = price[0].split(',')
                    price_formatted = float(price[0][0] + '.' + price[0][1])

                # Showing price
                print(f"Preço: R${price_formatted}")
                precos.append(price_formatted)
            else:
                precos.append("")

            # Ad title
            title = str(product_soup.find(class_ = 'col-purchase').find('h1').text)
            ad_title.append(title)

            # Booleans
            gpu_bool = False
            marca_bool = False
            num_processadores_bool = False
            modelo_bool = False
            peso_bool = False
            garantia_bool = False
            fonte_recomendada_bool = False
            tamanho_memoria_bool = False
            velocidade_memoria_bool = False
            tipo_memoria_bool = False

            # GPU
            if "AMD" in title or "Radeon" in title:
                gpu.append("AMD")
                gpu_bool = True
            elif "NVIDIA" in title or "Nvidia" in title or "Geforce" in title or "GeForce" in title:
                gpu.append("NVIDIA")
                gpu_bool = True

            # Getting all raw data
            info_string = info.text
            primeiradiv = info.find_element(By.TAG_NAME, "div")
            elements = primeiradiv.find_elements(By.TAG_NAME, "p")

            # Array with p elements
            string = []
            for e in elements:
                string.append(e.text)

            # Garantia
            if "meses" in info_string:
                garantia = info_string[info_string.find("meses")-3:info_string.find("meses")]
                try:
                    print("Meses de garantia: " + garantia)
                    garantias.append(int(garantia))
                    garantia_bool = True
                except:
                    pass
            elif "Meses" in info_string:
                garantia = info_string[info_string.find("Meses")-3:info_string.find("Meses")]
                try:
                    print("Meses de garantia: " + garantia)
                    garantias.append(int(garantia))
                    garantia_bool = True
                except:
                    pass
            
            # Peso
            if "gramas" in info_string:
                peso = info_string[info_string.find("gramas")-6:info_string.find("gramas")].strip()
                try:
                    peso = int(peso)
                    pesos.append(peso)
                    peso_bool = True
                except:
                    only_numbers = re.sub('^[0-9]', '', peso)
                    only_numbers = only_numbers.replace(":", "")
                    only_numbers = only_numbers.rstrip()
                
                    try:
                        peso = int(only_numbers)
                        print("Peso: " + str(peso))
                        pesos.append(peso)
                        peso_bool = True
                    except:
                        pass

            # Testando por elementos p
            for e in string:
                # Quantidade de processadores
                if num_processadores_bool == False and ("Processadores de Fluxo" in e or "Processador de fluxo" in e or "Processadores de fluxo" in e or "Core" in e or "Núcleos" in e or "CUDA" in e or "Cuda" in e) and "speed" not in e and "MHz" not in e and "velocidade" not in e and "Clock" not in e:

                    # Caso a quantidade de processadores esteja no elemento atual
                    print(re.sub('[^0-9]', '', e))
                    if len(re.sub('[^0-9]', '', e)) > 2:
                        num_processadores = int(re.sub('[^0-9]', '', e))
                        print("Qtd de processadores: " + str(num_processadores))
                        unidades_de_processamento.append(num_processadores)
                        num_processadores_bool = True

                    # Caso a quantidade de processadores esteja no elemento seguinte da array
                    else:
                        proximo = string[string.index(e) + 1]
                        only_numbers = re.sub('[^0-9]', '', proximo)
                        if len(only_numbers) > 2:
                            num_processadores = int(only_numbers)
                            print("Qtd de processadores: " + str(num_processadores))
                            unidades_de_processamento.append(num_processadores)
                            num_processadores_bool = True
                
                # Tamanho da memória
                if tamanho_memoria_bool == False and ("GB" in e):
                    try:
                        tamanho = e[e.find("GB")-3:e.find("GB")].strip()
                        tamanho = tamanho.replace(":", "")
                        tamanho = int(tamanho)
                        print("Tamanho da memória: " + str(tamanho))
                        tamanhos_de_memoria.append(tamanho)
                        tamanho_memoria_bool = True
                    except:
                        pass

                # # Fonte recomendada
                if fonte_recomendada_bool == False and ("PSU" in e or "recomendada" in e or "Recomendada" in e or "Fonte" in e):
                    only_numbers = re.sub('[^0-9]', '', e)
                    if len(only_numbers) > 2:
                        fonte_recomendada = int(only_numbers)
                        print("Fonte recomendada: " + str(fonte_recomendada))
                        fontes_recomendadas.append(fonte_recomendada)
                        fonte_recomendada_bool = True
                    else:
                        proximo = string[string.index(e) + 1]
                        only_numbers = re.sub('[^0-9]', '', proximo)
                        if len(only_numbers) > 2:
                            fonte_recomendada = int(only_numbers)
                            print("Fonte recomendada: " + str(only_numbers))
                            fontes_recomendadas.append(fonte_recomendada)
                            fonte_recomendada_bool = True

            # Testando por string

            # Marca
            if marca_bool == False:
                if "Marca" in info_string:
                    marca = info_string[info_string.find("Marca")+6:]
                    marca = marca[0:marca.find('\n')]
                    print("Marca: " + marca)
                    marcas.append(marca.strip())
                    marca_bool = True

            # Modelo
            if modelo_bool == False:
                if "Modelo" in info_string:
                    modelo = info_string[info_string.find("Modelo")+7:]
                    modelo = modelo[0:modelo.find('\n')]
                    print("Modelo: " + modelo)
                    modelos.append(modelo.strip())
                    modelo_bool = True

            # Tamanho da memória
            if tamanho_memoria_bool == False:
                pattern = r'\d+[ GBgb]{2,3}'
                result = re.findall(pattern, info_string)
                if len(result) > 0:
                    only_numbers = re.sub('[^0-9]', '', result[0])
                    if len(only_numbers) > 0:
                        tamanho_memoria = int(only_numbers)
                        print("Tamanho da memória: " + str(tamanho_memoria))
                        tamanhos_de_memoria.append(tamanho_memoria)
                        tamanho_memoria_bool = True

            # Velocidade da memória
            if velocidade_memoria_bool == False:
                pattern = r'\d+[ Gbpsg]{4,5}'
                result = re.findall(pattern, info_string)
                if len(result) > 0:
                    only_numbers = re.sub('[^0-9]', '', result[0])
                    if len(only_numbers) > 0:
                        velocidade_memoria = int(only_numbers)
                        print("Velocidade da memória: " + str(velocidade_memoria))
                        velocidades_de_memoria.append(velocidade_memoria)
                        velocidade_memoria_bool = True
            
            # Tipo da memória
            if tipo_memoria_bool == False:
                if "GDDR" in info_string:
                    tipo = info_string[info_string.find("GDDR"):info_string.find("GDDR")+5]
                    
                elif "Gddr" in info_string:
                    tipo = info_string[info_string.find("Gddr"):info_string.find("Gddr")+5]

                try:
                    print("Tipo da Memória: " + tipo)
                    tipos_de_memoria.append(tipo.strip())
                    tipo_memoria_bool = True
                except:
                    pass

            # Unidades de Processamento
            if num_processadores_bool == False:
                cores = ""
                if "Cores" in info_string:
                    cores = info_string[info_string.find("Cores")+5:]
                    cores = cores[0:cores.find('\n')]

                elif "cores" in info_string:
                    cores = info_string[info_string.find("cores")+5:]
                    cores = cores[0:cores.find('\n')]

                elif "Core" in info_string:
                    cores = info_string[info_string.find("Core")+4:]
                    cores = cores[0:cores.find('\n')]

                elif "core" in info_string:
                    cores = info_string[info_string.find("core")+4:]
                    cores = cores[0:cores.find('\n')]

                elif "Cuda" in info_string:
                    cores = info_string[info_string.find("Cuda")+4:]
                    cores = cores[0:cores.find('\n')]

                elif "CUDA" in info_string:
                    cores = info_string[info_string.find("Cuda")+4:]
                    cores = cores[0:cores.find('\n')]
                    
                elif "Núcleos" in info_string:
                    cores = info_string[info_string.find("Núcleos")+7:]
                    cores = cores[0:cores.find('\n')]

                elif "Processador" in info_string:
                    cores = info_string[info_string.find("Processador")+11:]
                    cores = cores[0:cores.find('\n')]

                elif "processador" in info_string:
                    cores = info_string[info_string.find("processador")+11:]
                    cores = cores[0:cores.find('\n')]

                if "Mhz" not in cores and "mhz" not in cores and "Clock" not in cores and "velocidade" not in cores and "Velocidade" not in cores and "speed" not in cores and "Speed" not in cores:
                    try:
                        only_numbers = re.sub('[^0-9]', '', cores)
                        if len(only_numbers) > 2:
                            cores = int(only_numbers)
                            print("Cores: " + str(cores))
                            unidades_de_processamento.append(cores)
                            num_processadores_bool = True
                    except:
                        pass

            # Fonte Recomendada
            if fonte_recomendada_bool == False:
                after = ""
                if "Recomendada" in info_string:
                    after = str(info_string[info_string.find("Recomendada"):])
                    
                elif "Recomendado" in info_string:
                    after = str(info_string[info_string.find("Recomendado"):])
                    
                elif "recomendada" in info_string:
                    after = str(info_string[info_string.find("recomendada"):])
                    
                elif "recomendado" in info_string:
                    after = str(info_string[info_string.find("recomendado"):])
                    
                elif "Fonte de Alimentação" in info_string:
                    after = str(info_string[info_string.find("Fonte de Alimentação"):])
                
                elif "sugerido" in info_string:
                    after = str(info_string[info_string.find("sugerido"):])
                    
                pattern = r'\d+[ wW]{1,2}'
                resultado = re.findall(pattern, after)
                if len(resultado) > 0:
                    only_numbers = re.sub('[^0-9]', '', resultado[0])
                    if len(only_numbers) > 0:
                        fonte_recomendada = int(only_numbers)
                        print("Fonte recomendada: " + str(fonte_recomendada))
                        fontes_recomendadas.append(fonte_recomendada)
                        fonte_recomendada_bool = True   

            # Adicionando features vazios        
            if marca_bool == False:
                marcas.append("")

            if modelo_bool == False:
                modelos.append("")

            if gpu_bool == False:
                gpu.append("")

            if num_processadores_bool == False:
                unidades_de_processamento.append("")

            if tamanho_memoria_bool == False:
                tamanhos_de_memoria.append("")

            if velocidade_memoria_bool == False:
                velocidades_de_memoria.append("")

            if tipo_memoria_bool == False:
                tipos_de_memoria.append("")
            
            if fonte_recomendada_bool == False:
                fontes_recomendadas.append("")

            if peso_bool == False:
                pesos.append("")

            if garantia_bool == False:
                garantias.append("")

        
        
# Tamanho de cada lista
print(len(precos))
print(len(marcas))
print(len(modelos))
print(len(gpu))
print(len(unidades_de_processamento))
print(len(tamanhos_de_memoria))
print(len(velocidades_de_memoria))
print(len(tipos_de_memoria))
print(len(fontes_recomendadas))
print(len(garantias))
print(len(pesos))

# Criando DataFrame
df = pd.DataFrame({"Preço":precos, "Marca":marcas, "Modelo":modelos, "GPU": gpu, "Unidades de Processamento": unidades_de_processamento, "Tamanho da Memória (GB)":tamanhos_de_memoria, "Velocidade da Memória (Gbps)":velocidades_de_memoria, "Tipo da Memória":tipos_de_memoria, "Fonte Recomendada (W)":fontes_recomendadas, "Garantia (Meses)":garantias, "Peso": pesos})

# CSV
df.to_csv('placas_de_video_kabum.csv')

