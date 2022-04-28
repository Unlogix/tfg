import pandas as pd
import sys
import os
import numpy as np
from matplotlib import pyplot as plt

rutaGlobal =  "/home/kali/Desktop/TFG/proyectos/"

# CRAWLING DEL DOMINIO
def launch(domain):
    rutaProyecto = rutaGlobal + domain + "/"
    sfCrawlCommand = """screamingfrogseospider --crawl """ + domain + """ --headless --save-crawl --overwrite --output-folder """ + rutaGlobal + domain + """ --export-tabs "Internal:All,External:All,
    Response Codes:All, URL:All, URL:Parameters,
    Page Titles:All, Page Titles:Missing, Page Titles:Duplicate, Page Titles:Same as H1, Page Titles:Multiple,
    H1:All,H1:Missing,H1:Duplicate,H1:Multiple,
    Content:Exact Duplicates,Content:Near Duplicates,Content:Low Content Pages,
    Images:All, Images:Missing Alt Text, Images:Missing Alt Attribute, Images:Over X KB,
    Pagination:All, Sitemaps:All, 
    PageSpeed:All, Pagination:Contains Pagination, Link Metrics:All" --save-report "Crawl Overview" --bulk-export "Response Codes:Redirection (3xx) Inlinks" """
    print("Configuración del crawler finalizada")
    os.system(str(sfCrawlCommand))

def print_spaces():
    print("\n--------------------")

# ANÁLISIS DE ARQUITECTURA Y OPTIMIZACIÓN
def risk_analysis(domain):

    #Variables de proyecto y carpetas
    proyect = rutaGlobal + domain + "/"

    riskScore = 0

    # SCREAMING FROG READ DATA
    csv = ".csv"
    # Nombres comunes de archivos
    allData = "_all"
    duplicate = "_duplicate"
    missing = "_missing"
    multiple = "_multiple"

    #Variables de archivos - MEJOR LLAMAR A CADA UNO EN SU MOMENTO
    externalCsv = "external_all" + csv
    responseCodesCsv = "response_codes_all" + csv

    # Internal Data
    internalCsv = proyect + "internal_all" + csv
    imagesCsv = proyect + "images_all" + csv
    allImgsData = pd.DataFrame(pd.read_csv(imagesCsv, sep=","))
    #Importamos los docuementos necesarios
    internalData = pd.DataFrame(pd.read_csv(internalCsv, sep=","))
    allUrls = internalData['Address'].count()
    allImages = allImgsData['Address'].count()
    print("Total de URLs: " , allUrls)
    print("Total de Imágenes: " , allImages)
    
    # Análisis del ratio Html/Images
    # TOTAL RISK SCORE = 5
    ratioImgUrl = allImages / allUrls

    if(ratioImgUrl < 2):
        print("\n >>> Añadir más contenido multimedia a tus artículos.")
        riskScore += 5
    else:
        print("Ratio Images / HTML OK")
    print_spaces()

    # Tipos de archivos
    res = internalData['Content Type'].value_counts()
    totalHtml = res['text/html']
    #totalHtml = res['text/html; charset=UTF-8']
    #totalHtml = res['text/html; charset=utf-8'] + res['text/html; charset=iso-8859-1']
    totalImages = res['image/png'] + res['image/jpeg']
    importantContentTypeUrls = totalHtml + totalImages
    #internalData['Content Type'].value_counts().plot.pie()

    # URLs con parámetros
    parametersCsv = proyect + "url_parameters" + csv
    # Importamos el documento
    urlParamsData = pd.DataFrame(pd.read_csv(parametersCsv, sep=","))
    allUrlsWithParams = urlParamsData['Address'].count()
    print("URLs con parámetros:\n  >>> ", allUrlsWithParams)

    # Análisis de indexabilidad de parámetros
    print("Indexables vs Total con parámetros")
    paramsIndexability = urlParamsData['Indexability'].value_counts()
    flagNoIndexable = 0
    if paramsIndexability.empty:
        print("No hay URLs con parámetros indexables")
        flagNoIndexable = 1
    else:
        print("Indexability Distribution: \n >>> ", paramsIndexability.count())
    ## urlParamsData['Indexability'].value_counts().plot.pie()

    # Análisis del Ratio Indexables Vs Total con Parámetros
    # TOTAL RISK SCORE = 15
    res = urlParamsData['Indexability'].value_counts()
    if flagNoIndexable == 0:
        #if res['Non-Indexable'] != allUrlsWithParams:
        print("FLAG URLs con parámetros Indexables")
        print("Revisa el archivo parameters.csv en la carpeta de resultados")
        riskScore += 15
        print("Comprueba el archivo url_parameters.csv")
    else:
        print("No se han detectado URLs con parámetros indexables")
        print_spaces()

    # Response Codes
    res = internalData['Status Code'].value_counts()
    badResponseCodes = internalData['Status Code'].count() - res[200]
    print("URLs with bad response codes", badResponseCodes)
    ## internalData['Status Code'].value_counts().plot.pie()
    print("Comprueba el archivo internal_all.csv")
    print_spaces()

    # URLs Indexables
    res = internalData['Indexability'].value_counts()
    allIndexableUrls = res['Indexable']
    notIndexableUrls = allUrls-allIndexableUrls
    print("Non Indexable URLs:\n  >>> ", notIndexableUrls)
    ##res.plot.pie()
    print_spaces()
    # Ratio Non Indexable URLs
    # TOTAL RISK SCORE = 8
    ratioIndexablility = notIndexableUrls/allUrls
    if(ratioIndexablility > 0.025):
        print("FLAG Ratio indexability:\n  >>> ", round(ratioIndexablility, 4))
        print("Tienes demasiadas URLs no indexables. Valora apartar estas URLs en un subdominio")
        print("  >>> Eliminar enlaces internos. a estas URLs para mejorar Page Rank interno")
        print("Comprueba el archivo internal_all.csv")
        riskScore += 8
    else:
        print("Ratio Indexability OK")

    print_spaces()

    # H1 Tags
    h1Csv = proyect + "h1"
    hOneLabels = ['H1 OK', 'H1 Missing', 'H1 Duplicate', 'H1 Multiple']
    # importamos los documentos
    hOneAllCsv = h1Csv + allData + csv
    hOneMissingCsv = h1Csv + missing + csv
    hOneDuplicateCsv = h1Csv + duplicate + csv
    hOneMultipleCsv = h1Csv + multiple + csv

    hOneAllData = pd.DataFrame(pd.read_csv(hOneAllCsv, sep=","))
    hOneMissingData = pd.DataFrame(pd.read_csv(hOneMissingCsv, sep=","))
    hOneDuplicateData = pd.DataFrame(pd.read_csv(hOneDuplicateCsv, sep=","))
    hOneMultipleData = pd.DataFrame(pd.read_csv(hOneMultipleCsv, sep=","))

    # Analizamos los H1 que están mal
    totalH1Missing = hOneMissingData['Address'].count()
    totalH1Duplicate = hOneDuplicateData['Address'].count()
    totalH1Multiple = hOneMultipleData['Address'].count()
    badH1Tag = totalH1Missing + totalH1Duplicate + totalH1Multiple
    h1Fine = hOneAllData['Address'].count() - badH1Tag

    hOneData = [h1Fine, totalH1Missing, totalH1Duplicate, totalH1Multiple]
    h1Distribution = pd.DataFrame(hOneData, hOneLabels)

    # Creating plot
    ## plt.pie(hOneData, labels = hOneLabels)

    #  Comprobamos ratio de H1 Correctos
    # TOTAL RISK SCORE = 14
    ratioCorrectH = round((badH1Tag / (h1Fine + badH1Tag)), 2)
    if(ratioCorrectH < 0.01):
        print("Ratio Perfecto")
        riskScore += 0
    elif(ratioCorrectH >= 0.01 and ratioCorrectH < 0.5):
        print("Ratio Bueno")
        riskScore += 5
    elif(ratioCorrectH >= 0.05 and ratioCorrectH < 0.1):
        print("Ratio Aceptable")
        riskScore += 8
    elif(ratioCorrectH >= 0.1 and ratioCorrectH < 0.25):
        print("Ratio Peligroso")
        print("Comprueba el archivo h1_all.csv")  
        riskScore += 10
    elif(ratioCorrectH >= 0.25):
        print("Ratio Crítico")
        print("Comprueba el archivo h1_all.csv")  
        riskScore += 14
    print("  >>> ", ratioCorrectH)
    print_spaces()

    # Páginas indexables sin H1
    indexableBadHone = hOneMissingData['Indexability'].value_counts()
    indexableBadHone += hOneDuplicateData['Indexability'].value_counts()
    indexableBadHone += hOneMultipleData['Indexability'].value_counts()
    #print("URLs con H1 No Optimizado Indexables:\n  >>> ", indexableBadHone['Indexable'])

    # TOTAL RISK SCORE = 5
    #if(indexableBadHone['Indexable'].count() > 0):
        #print("  >>> Deberías revisar esas URLs")
        #print("Revisa el archivo url_parameters.csv en la carpeta de resultados")
        #riskScore += 5
    #else:
        #print("Títulos correctamente optimizados")

    # Page Titles
    titlesCsv = proyect + "page_titles"
    allTitles = titlesCsv + allData + csv
    missingTitles = titlesCsv + missing + csv
    duplicateTitles = titlesCsv + duplicate + csv
    multipleTitles = titlesCsv + multiple + csv
    sameAsH1Titles = titlesCsv + "_same_as_h1" + csv
    # Leemos los CSVs necesarios
    allTitlesData = pd.DataFrame(pd.read_csv(allTitles, sep=","))
    titlesDuplicateData = pd.DataFrame(pd.read_csv(duplicateTitles, sep=","))
    titlesMissingData = pd.DataFrame(pd.read_csv(missingTitles, sep=","))
    titlesMultipleData = pd.DataFrame(pd.read_csv(multipleTitles, sep=","))
    titlesSameAsData = pd.DataFrame(pd.read_csv(sameAsH1Titles, sep=","))

    # Analizamos los Títlos de página incorrectos
    totalTitleMissing = titlesMissingData['Address'].count()
    totalTitleDuplicate = titlesDuplicateData['Address'].count()
    totalTitleMultiple = titlesMultipleData['Address'].count()
    totalTitleSameAsH1 = titlesSameAsData['Address'].count()
    badTitlesTag = totalH1Missing + totalH1Duplicate + totalH1Multiple + totalTitleSameAsH1
    titlesOk = allTitlesData['Address'].count() - badTitlesTag

    titlesLabels = ['Correct', 'Missing', 'Duplicate', 'Multiple', 'Same As H1']
    titlesData = [titlesOk, totalTitleMissing, totalTitleDuplicate, totalTitleMultiple, totalTitleSameAsH1]

    titlesDistribution = pd.DataFrame(titlesData, titlesLabels)

    # Comprobamos ratio de correctos
    # TOTAL RISK SCORE = 12
    ratioBadTitles = badTitlesTag / allTitlesData['Address'].count()
    if(ratioBadTitles >= 0.3):
        riskScore += 12
        print("FLAG Titles: Revisa el archivo PAGE_TITLES.csv en la carpeta de resultados")
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba el archivo page_titles_all.csv")
        #os.sys('cp ' + titlesCsv + ' ' + proyect + '/results/page_titles.csv')  
    elif(ratioBadTitles < 0.3 and ratioBadTitles >= 0.20):
        riskScore += 8
        print("WARNING:\n")
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba el archivo page_titles_all.csv")
        #os.sys('cp ' + titlesCsv + ' ' + proyect + '/results/page_titles.csv')  
    elif ratioBadTitles < 0.20 and ratioBadTitles >= 0.08:
        print("Aceptable")
        riskScore += 4
    elif ratioBadTitles < 0.08:
        print("Bien")
    print("   >>> ", round(ratioBadTitles, 4))
    print_spaces()

    # Analisis de Contenido
    contentCsv = proyect + "content_"
    lowContent = contentCsv + "low_content_pages" + csv
    nearDuplicates = contentCsv + "near_duplicates" + csv
    exactDuplicates = contentCsv + "exact_duplicates" + csv
    # Importamos documentos
    exactDuplicatesData = pd.DataFrame(pd.read_csv(exactDuplicates, sep=","))
    nearDuplicatesData = pd.DataFrame(pd.read_csv(nearDuplicates, sep=","))
    lowContentData = pd.DataFrame(pd.read_csv(lowContent, sep=","))

    # URLs con problemas de contenido
    lowContentUrls = lowContentData['Address'].count()
    nearDuplicateContentUrls = nearDuplicatesData['Address'].count()
    exactDuplicateContentUrls = exactDuplicatesData['Address'].count()
    badContentUrls = lowContentUrls + nearDuplicateContentUrls + exactDuplicateContentUrls
    contentOk = allUrls - badContentUrls

    contentLabels = ['Correct', 'Near Duplicate', 'Exact Duplicate', 'Low Content']
    contentData = [contentOk, nearDuplicateContentUrls, exactDuplicateContentUrls, lowContentUrls]

    contentDistribution = pd.DataFrame(contentData, contentLabels)
    print(contentDistribution)
    ##plt.pie(contentData, labels = contentLabels)
    # EXPORTAR IMAGEN A CARPETA DE RESULTADOS

    # Ratio distribución contenido
    # TOTAL RISK SCORE = 14
    ratioContent = badContentUrls / (allUrls)
    if(ratioContent < 0.1):
        print("Content Distribution OK")
    elif(ratioContent >= 0.1 and ratioContent < 0.25):
        print("Content Distribution at Risk")
        riskScore += 10
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba los archivos:\n > content_low_content_pages.csv\n > content_near_duplicates.csv\n > content_exact_duplicates.csv")
    else:
        print("FLAG Content distribution")
        riskScore += 14
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba los archivos:\n > content_low_content_pages.csv\n > content_near_duplicates.csv\n > content_exact_duplicates.csv")
    print("   >>> ", round(ratioContent, 4))
    print_spaces()

    # Paginación
    # TOTAL RISK SCORE = 13
    paginationCsv = proyect + "pagination_contains_pagination.csv"
    # Mirar si es indexable
    paginationAllData = pd.DataFrame(pd.read_csv(paginationCsv, sep=","))
    totalPagination = paginationAllData['Address'].count()  
    # > 10% de paginación es crítico
    ratioPagination = totalPagination / allUrls
    if ratioPagination > 0.8:
        print("Existe demasiada paginación. Aumenta el número de entradas mostradas en el blog")
        riskScore += 13
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba el archivo pagination_contains_pagination.csv")
        #os.sys('cp ' + paginationCsv + ' ' + proyect + '/results/pagination.csv') 
    elif ratioPagination > 0.3:
        print("CUIDADO CON LA PAGINACIÓN.")
        riskScore += 9
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba el archivo pagination_contains_pagination.csv")
        #os.sys('cp ' + paginationCsv + ' ' + proyect + '/results/pagination.csv') 
    else:
        print("El índice de paginación es correcto")
    print('   >>> ', ratioPagination)

    # Del total de paginación - > 50% indexable es crítico
    # TOTAL RISK SCORE = 7
    pagIndexabilityCounts = paginationAllData['Indexability'].value_counts()
    paginationIndexableUlrs = pagIndexabilityCounts['Indexable']
    if(paginationIndexableUlrs/totalPagination > 0.5):
        print("FLAG Paginación")
        print("Revisa el archivo URLS_CON_PAGINACION.csv en la carpeta de resultados")
        riskScore += 7
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba el archivo pagination_contains_pagination.csv")
    else:
        print("Paginación Ok")
    print_spaces()

    # Imágenes
    imgsCsv = proyect + "images"
    allImgsCsv = imgsCsv + allData  + csv
    bigImgsCsv = imgsCsv + "_over_100_kb" + csv
    altTextImgsCsv = imgsCsv + missing + "_alt_text" + csv
    altAttributeImgsCsv = imgsCsv + missing + "_alt_attribute" + csv
    # allImgsData > Creada al comienzo
    imgAllData = pd.DataFrame(pd.read_csv(allImgsCsv, sep=","))
    imgBigSizeData = pd.DataFrame(pd.read_csv(bigImgsCsv, sep=","))
    imgAltTextData = pd.DataFrame(pd.read_csv(altTextImgsCsv, sep=","))
    imgAltAttributesData = pd.DataFrame(pd.read_csv(altAttributeImgsCsv, sep=","))

    # Img Type análisis
    resImgType = imgAllData['Content Type'].value_counts()
    ##resImgType.plot.pie()
    # EXPORTAR IMAGEN A CARPETA DE RESULTADOS

    # Img Indexability análisis
    resImgIndexability = imgAllData['Indexability'].value_counts()
    ##resImgIndexability.plot.pie()
    # EXPORTAR IMAGEN A CARPETA DE RESULTADOS

    # Datos de imágenes
    totalImgs = imgAllData['Address'].count()
    totalBigImgs = imgBigSizeData['Address'].count()
    totalAltTextImgs = imgAltTextData['Address'].count()
    totalAltAttributeImgs = imgAltAttributesData['Address'].count()
    correctImgs = totalImgs - (totalBigImgs + totalAltTextImgs + totalAltAttributeImgs)

    imgLabels = ['Correct', 'Big Imgs', 'Missing Alt Text', 'No Alt Attribute']
    imgData = [correctImgs, totalBigImgs, totalAltTextImgs, totalAltAttributeImgs]

    imgDistribution = pd.DataFrame(imgData, imgLabels)
    print(contentDistribution)
    ##plt.pie(imgData, labels = imgLabels)
    print_spaces()
    # EXPORTAR IMAGEN A CARPETA DE RESULTADOS

    # COMPROBACIÓN RATIO DE IMÁGENES
    # TOTAL RISK SCORE = 15 (8+7)
    # > 10% de paginación es crítico
    ratioBadImgs = 1 - (correctImgs / totalImgs)
    if ratioPagination > 0.3:
        print("FLAG: Revisa Contenido Multimedia")
        riskScore += 8
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba los archivos:\ > Imgs_missing_alt_text.csv\n > imgs_missing_alt_attribute.csv ")
        #os.sys('cp ' + allImgsCsv + ' ' + proyect + '/results/all_imgs.csv')
        #os.sys('cp ' + altTextImgsCsv + ' ' + proyect + '/results/alt_text.csv') 
        #os.sys('cp ' + altAttributeImgsCsv + ' ' + proyect + '/results/alt_attribute.csv') 
    elif ratioPagination > 0.2:
        print("Cuidado! Revisa las imágenes de la web")
        riskScore += 5
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        print("Comprueba los archivos:\ > Imgs_missing_alt_text.csv\n > imgs_missing_alt_attribute.csv ")
        #os.sys('cp ' + allImgsCsv + ' ' + proyect + '/results/all_imgs.csv')
        #os.sys('cp ' + altTextImgsCsv + ' ' + proyect + '/results/alt_text.csv') 
        #os.sys('cp ' + altAttributeImgsCsv + ' ' + proyect + '/results/alt_attribute.csv')
    else:
        print("Contenido multimedia optimizado")
    print('   >>> ', ratioPagination)
    print_spaces()

    if totalBigImgs >  0:
        print("ERROR CRÍTICO: IMÁGENES GRANDES")
        print("Revisa el archivo images_over_100_kb.csv en la carpeta de resultados")
        riskScore += 7
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        #os.sys('cp ' + bigImgsCsv + ' ' + proyect + '/results/big_imgs.csv') 
        print_spaces()

    # External Links
    externalCsv = proyect + "external_all" + csv
    externalData = pd.DataFrame(pd.read_csv(externalCsv, sep=","))
    totalExternalLinks = externalData['Address'].count()
    # Comprobar response codes
    # Exportar al CSV para CHECK MANUAL si se pueden registrar EXPIRED DOMAINS (APIS son de pago)
    # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
    print("Comprueba el archivo external_all.csv")
    #os.sys('cp ' + externalCsv + ' ' + proyect + '/results/external_links.csv') 

    # Códigos de respuesta del servidor de external links
    resExternalStatusCode = externalData['Status Code'].value_counts()
    externalOk = resExternalStatusCode[200]
    ##resExternalStatusCode.plot.pie()
    # EXPORTAR IMAGEN A CARPETA DE RESULTADOS

    # Ratio external links
    # TOTAL RISK SCORE = 5
    ratioExternalLinks = 1 -(externalOk / totalExternalLinks)
    if(ratioExternalLinks < 0.05):
        print('External Link Status OK')
    elif(ratioExternalLinks < 0.1 and externalOk/totalExternalLinks >= 0.05):
        print('External Link Status ACEPTABLE')
        riskScore += 3
    elif(ratioExternalLinks < 0.3 and externalOk/totalExternalLinks >= 0.1):
        #print('CUIDADO! Revisa EXTERNAL_ALL.csv para garantizar escalabilidad')
        print("Comprueba el archivo redirection_(3XX)_inlinks.csv")
        print("Comprueba el archivo client_error_(4XX)_inlinks.csv")
        #os.sys('cp ' + proyect + 'redirection_(3XX)_inlinks.csv ' + proyect + '/results/30X_inlinks.csv')
        #os.sys('cp ' + proyect + 'client_error_(4XX)_inlinks.csv ' + proyect + '/results/30X_inlinks.csv')
        riskScore += 5
    else:
        print('FLAG external links')
        #print("Revisa el archivo EXTERNAL_ALL en la carpeta de resultados")
        print("Comprueba el archivo redirection_(3XX)_inlinks.csv")
        print("Comprueba el archivo client_error_(4XX)_inlinks.csv")
        #os.sys('cp ' + proyect + 'redirection_(3XX)_inlinks.csv ' + proyect + '/results/30X_inlinks.csv')
        #os.sys('cp ' + proyect + 'client_error_(4XX)_inlinks.csv ' + proyect + '/results/40X_inlinks.csv')
        riskScore += 15
        # COMANDO DE SISTEMA PARA COPIAR ARCHIVO
        resQuery = """cp """ + proyect + """redirection_(3XX)_inlinks.csv """ + proyect + """results/30X_inlinks.csv"""
        #resQuery = """cp """ + proyect + """client_error_(4XX)_inlinks.csv """ + proyect + """/results/40X_inlinks.csv"""
        #os.sys('cp external_all.csv /results/external_links.csv')
    print('   >>> ', ratioExternalLinks)

    # Análisis final del índice de Riesgo de la página web
    print("\n>>>>> RESULTADO FINAL >>>>>")
    print(domain, " Risk Score:\n   >>> ",riskScore, " / 100")
    print("Total de URLs:\n   >>> ", allUrls)
    print_spaces()

# ANÁLISIS DE SEGURIDAD
def wafScan(domain):
    print('Análisis de WAF')
    # WAFW00F
    query = "wafw00f " + domain + " -o " + rutaGlobal + domain + "/results/wafResults.txt"
    os.system(str(query))

def techScan(domain):
    print('Análisis de Tecnología web')
    # WEBTECH
    query = "webtech -u https://" + domain
    os.system(str(query))

def emailScan(domain):
    # email & social media
    print('Análisis de cuentas existentes')
    # EMAIL HARVESTER
    query = "emailharvester -d " + domain + " -s " + rutaGlobal + domain + "/results/emails.txt"
    os.system(str(query))

def pentestingScan(domain):
    print("Auditoría de seguridad")
    query = "nuclei -target " + domain + """ -rate-limit 20 -header 'User-Agent: Googlebot Smartphone'"""
    output = " -o /" + rutaGlobal + domain + "/results/vulnerabilities.txt"
    # NUCLEI SCAN
    finalQuery = query + output
    # Ejecutar CMD
    os.system(str(finalQuery))

def socialScan():
    print("Búsqueda de perfiles y cuentas de usuario en redes sociales")
    # Solicitar al usuario el nombre del perfil
    # Capturar salida y guardar datos.
    print("Análisis de redes sociales")
    socialProfile = input("Introduce el perfil que quieres analizar\n")
    domain = input("A qué proyecto pertenece?\n")
    query = str("sherlock " + socialProfile + " -o " + rutaGlobal + domain +  "/results/social.txt")
    print(query)
    # Ejecutar cmd
    os.system(str(query))

def nmapScan(domain):
    print('Análisis con NMAP')
    # Sirve con el dominio o hace falta IP??
    output = " -o /" + rutaGlobal + domain + "/results/namp_scan.txt"
    query = "nmap -v --script=default,safe,vuln" + domain + output
    os.system(str(query))

def fuzzingScan(domain):
    print('Realizando Fuzzing de directorios y archivos')
    query = "dirsearch -u " + domain

def security_check(domain):
    print("Hacer check seguridad")
    #Check WAF
    wafScan(domain)
    #Scan tecnologia
    techScan(domain)
    #Email Scan
    emailScan(domain)
    #Check Vulns
    pentestingScan(domain)
    #print OutPut

## SECCIÓN DE MENÚS E INTERACCIÓN CON SISTEMA

def printMenu():
    print("Bienvenido...")
    print("Que quieres hacer?:")
    print("1) RASTREAR DOMINIO")
    print("2) ANÁLISIS SEGURIDAD")
    print("3) ANÁLISIS DE RESULTADOS")
    print("4) ANALISIS SOCIAL")
    print("5) CREAR PROYECTO")
    print("0) SALIR")

def createProyectFolder():
    domain = input("Introduce el nombre de dominio que quieres analizar - SIN HTTPS\n")
    query = rutaGlobal + domain + "/"
    os.mkdir(query)
    # Create results folder
    query += "/results/"
    os.mkdir(query)
    print("Quieres rastrear el dominio?")
    userInput = input("1 = SI \n Other = NO\n")
    if userInput == 1:
        launch(str(domain))
    else:
        print("\n   >>> Regresando al menú principal >>>\n\n")

def crawl():
    domain = input("\n >>> Introduce el dominio que quieres analizar - SIN HTTPS\n")
    print("Lanzando crawl para el dominio: " + domain)
    launch(str(domain))

def security_check():
    domain = input("Introduce el nombre de dominio que quieres analizar - SIN HTTPS\n")
    print(">>> Analizando existencia de WAF")
    wafScan(domain)
    print(">>> Analizando existencia de Tecnología Web >>> ")
    techScan(domain)
    print(">>> Recogiendo emails del dominio >>> ")
    emailScan(domain)
    print(">>> Iniciando Pentesting >>>")
    pentestingScan(domain)
    print("\n\n >>> Finalizado el scan de seguridad >>> ")

def main():
    os.system("pwd")
    userOption = 1
    while(userOption != 0):
        printMenu()
        userOption = int(input("\nEscoge opción\n >>> "))
        if userOption == 1:
            #Lanzamos crawl
            crawl()
        elif userOption == 2:
            #lanzamos security audit
            security_check()
        elif userOption == 3:
            #lanzamos analisis resultados
            domain = input("\n >>> Introduce el dominio que quieres analizar - SIN HTTPS\n")
            risk_analysis(domain)
        elif userOption == 4:
            #lanzamos analisis resultados
            socialScan()
        elif userOption == 5:
            createProyectFolder()
        elif userOption == 0:
            return 0

if __name__ == "__main__":
    main()