import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

headers = {
  'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

# Links contendo 20 placas de vídeo por página
links_kabum = [str("https://www.kabum.com.br/hardware/placa-de-video-vga?page_number={}&page_size=20&facet_filters=&sort=most_searched").format(i) for i in range(1, 64)]

driver = webdriver.Chrome()

# Features
price_list = []
gpu_list = []
brand_list = []
model_list = []
core_list = []
memory_size_list = []
memory_speed_list = []
memory_type_list = []
memory_interface_list = []
recommended_psu_list = []
garantia_list = []
peso_list = []

for link in links_kabum:
    req = requests.get(link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    products = soup.find_all(class_ = 'productCard')

    for product in products:
        product_path = (product.find('a'))['href']
        product_link = str(f"https://www.kabum.com.br{product_path}")

        # Teste de link de placa específico
        # product_link = "https://www.kabum.com.br/produto/383616/placa-de-video-pny-nvidia-geforce-rtx-3060-12-gb-gddr6-dlss-ray-tracing-vcg306012dfbpb1"

        product_req = requests.get(product_link, headers=headers)
        product_soup = BeautifulSoup(product_req.text, 'html.parser')

        print("Link do produto: ")
        print(product_link)

        try:
            driver.get(product_link)
            info = driver.find_element(By.ID, "secaoInformacoesTecnicas")
        except:
            continue
        
        info_string = info.text

        # Preço:

        price = product_soup.find(class_ = 'finalPrice')
        if price != None:
            # Tratando o preço:

            price = str(price.text)[3:].split('.')
            
            # Preços de mil reais pra cima
            if len(price) > 1:
                price[1] = price[1].split(',')
                formatted_price = float(f"{price[0]}{price[1][0]}.{price[1][1]}")

            # Preços abaixo de mil reais
            else:
                price[0] = price[0].split(',')
                formatted_price = float(f"{price[0][0]}.{price[0][1]}")

            print(f"Preço: R${formatted_price}")
            price_list.append(formatted_price)
        else:
            # O produto não tem preço
            price_list.append("")

        # Flags
        found_gpu = False
        found_brand = False
        found_model = False
        found_core = False
        found_memory_size = False
        found_memory_speed = False
        found_memory_type = False
        found_memory_interface = False
        found_recommended_psu = False
        found_garantia = False
        found_peso = False

        # GPU
        title = str(product_soup.find(class_ = 'col-purchase').find('h1').text)
        if "AMD" in title or "Radeon" in title:
            gpu_list.append("AMD")
            found_gpu = True
        elif "NVIDIA" in title or "Nvidia" in title or "GeForce" in title or "Geforce" in title:
            gpu_list.append("NVIDIA")
            found_gpu = True
        elif "Intel" in title:
            gpu_list.append("Intel")
            found_gpu = True

        # Garantia
        position = info_string.find("Meses")
        if position == -1:   
            position = info_string.find("meses")

        if position != -1:
            garantia = info_string[position-3:position-1]
            try:
                garantia_list.append(int(garantia))
                found_garantia = True
                print(f"Meses de garantia: {garantia}")
            except:
                pass

        # Peso
        position = info_string.find("Gramas")
        if position == -1:   
            position = info_string.find("gramas")

        if position != -1:
            peso = info_string[position-5:position-1]
            try:
                peso_list.append(int(peso))
                found_peso = True
                print(f"Peso: {peso}")
            except:
                pass
        
        lines = info_string.split('\n')
        for line in lines:

            # Interface de Memória
            if found_memory_interface == False and ("bits" in line or "bit" in line or "Bits" in line):
                if "64" in line:
                    memory_interface_list.append(64)
                    found_memory_interface = True
                    print("Interface: 64")
                elif "128" in line:
                    memory_interface_list.append(128)
                    found_memory_interface = True
                    print("Interface: 128")
                elif "192" in line:
                    memory_interface_list.append(192)
                    found_memory_interface = True
                    print("Interface: 192")
                elif "256" in line:
                    memory_interface_list.append(256)
                    found_memory_interface = True
                    print("Interface: 256")
                elif "384" in line:
                    memory_interface_list.append(384)
                    found_memory_interface = True
                    print("Interface: 384")
                elif "512" in line:
                    memory_interface_list.append(512)
                    found_memory_interface = True
                    print("Interface: 512")
            
            # Tipo de Memória
            if found_memory_type == False:
                pattern = r'([gG][dD][dD][rR]\d[xX]?\s*$)|([gG][dD][dD][rR]\d[xX]?\s*\b)|([dD][dD][rR]\d[xX]?\s*$)|([dD][dD][rR]\d[xX]?\s*\b)'
                result = re.search(pattern, line)
                if result != None:
                    found_memory_type = True
                    memory_type_list.append(result.group())
                    print("Tipo da Memória: " + result.group())

            # Velocidade da Memória
            if found_memory_speed == False:
                pattern = r'\d{1,2}\s*[Gg]bps'
                result = re.search(pattern, line)
                if  result != None:
                    # [^0-9] signifca tudo que não for um dígito de 0 a 9
                    only_numbers = re.sub('[^0-9]', '', result.group())
                    memory_speed = int(only_numbers)
                    if memory_speed < 30:
                        memory_speed_list.append(memory_speed)
                        found_memory_speed = True
                        print("Velocidade da Memória: " + result.group())

            # Tamanho da Memória
            if found_memory_size == False:
                pattern = r'(\d{1,2}\s*[Gg][Bb]\s*$)|(\d{1,2}\s*[Gg][Bb]\s*\b)'
                result = re.search(pattern, line)
                if result != None:
                    only_numbers = re.sub('[^0-9]', '', result.group())
                    memory_size = int(only_numbers)
                    if memory_size < 49:
                        memory_size_list.append(memory_size)
                        found_memory_size = True
                        print("Tamanho da Memória: " + result.group())
            
            # Fonte Recomendada
            if found_recommended_psu == False and ("PSU" in line or "psu" in line or "Fonte" in line or "fonte" in line or "Alimentação" in line or "alimentação" in line or "Potência" in line or "potência" in line):
                pattern = r'(\d{3,4}\s*[wW]?\s*$)|(\d{3,4}\s*[wW]?\s*\b)'
                result = re.search(pattern, line)
                if result != None:
                    only_numbers = re.sub('[^0-9]', '', result.group())
                    recommended_psu = int(only_numbers)
                    recommended_psu_list.append(recommended_psu)
                    found_recommended_psu = True
                    print("Fonte Recomendada: " + result.group())

                else:
                    next_line = lines[lines.index(line) + 1]

                    pattern = r'(\d{3,4}\s*[wW]?\s*$)|(\d{3,4}\s*[wW]?\s*\b)'
                    result = re.search(pattern, next_line)

                    if result != None:
                        only_numbers = re.sub('[^0-9]', '', result.group())
                        recommended_psu = int(only_numbers)
                        recommended_psu_list.append(recommended_psu)
                        found_recommended_psu = True
                        print("Fonte Recomendada: " + result.group())        

            # Core
            if found_core == False and "Speed" not in line and "Mhz" not in line and "mhz" not in line and "Velocidade" not in line and "velocidade" not in line and ("Processador" in line or "CUDA" in line or "Cuda" in line or "Núcleos" in line or "Unidades" in line or "unidades" in line):
                only_numbers = re.sub('[^0-9]', '', line)
                if len(only_numbers) > 2:
                    core = int(only_numbers)
                    core_list.append(core)
                    found_core = True
                    print(f"Core: {core}")

                # Verifico se o dado está na outra linha
                elif len(only_numbers) == 0:
                    next_line = lines[lines.index(line) + 1]
                    only_numbers = re.sub('[^0-9]', '', next_line)
                    if len(only_numbers) > 2:
                        core = int(only_numbers)
                        core_list.append(core)
                        found_core = True
                        print(f"Core: {core}")

            # Marca
            if found_brand == False and "Marca" in line:
                brand = line[line.find("Marca")+6:].strip()
                brand_list.append(brand)
                found_brand = True
                print(f"Marca: {brand}")

            # Modelo
            if found_model == False and "Modelo" in line:
                model = line[line.find("Modelo")+7:].strip()
                model_list.append(model)
                found_model = True
                print(f"Modelo: {model}")

        # Adicionando vazio a features não encontradas
        if found_memory_interface == False: 
            memory_interface_list.append("")
        
        if found_memory_type == False:
            memory_type_list.append("")

        if found_memory_size == False:
            memory_size_list.append("")

        if found_memory_speed == False:
            memory_speed_list.append("")

        if found_recommended_psu == False:
            recommended_psu_list.append("")

        if found_core == False:
            core_list.append("")

        if found_gpu == False:
            gpu_list.append("")
        
        if found_garantia == False:
            garantia_list.append("")

        if found_peso == False:
            peso_list.append("")
        
        if found_brand == False:
            brand_list.append("")

        if found_model == False:
            model_list.append("")
        
# Tamanho de cada lista
print(len(price_list))
print(len(memory_size_list))
print(len(memory_type_list))
print(len(memory_speed_list))
print(len(recommended_psu_list))
print(len(memory_interface_list))
print(len(core_list))
print(len(gpu_list))
print(len(garantia_list))
print(len(peso_list))
print(len(brand_list))
print(len(model_list))

# Criando DataFrame
df = pd.DataFrame({"Preço":price_list, "Marca":brand_list, "Modelo":model_list, "GPU": gpu_list, "Unidades de Processamento":core_list, "Tamanho da Memória (GB)":memory_size_list, "Velocidade da Memória (Gbps)":memory_speed_list, "Tipo da Memória":memory_type_list, "Interface da Memória (Bits)":memory_interface_list ,"Fonte Recomendada (W)":recommended_psu_list, "Garantia (Meses)":garantia_list, "Peso":peso_list})

# CSV
df.to_csv('placas_de_video_kabum_RAW.csv')
