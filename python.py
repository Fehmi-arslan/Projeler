# -*- coding: utf-8 -*-
import pandas as pd 
from matplotlib import pyplot as plt
import sys
import numpy as np
import mysql.connector

DATABASE = None
CURSOR = None

# Kullanıcıdan deger alır, EXIT girildiğinde uygulamayı sonlandırır
def get_input(description):
    user_input = input(description + ":")
    if user_input == 'EXIT':
        print("Uygulama sonlandırıldı.")
        sys.exit(0);
    else:        
        return user_input
    
# Menuyu yazdır
def print_menu():
    print("\n------------------------------------------------------------\n")
    print("[1]- Kullanıcı Oluştur")
    print("[2]- Telefon İşlemleri")
    print("    [2.1]- Telefon Ekle")
    print("    [2.2]- Telefon Listele")
    print("    [2.3]- Telefon Fiyat Güncelle")
    print("    [2.4]- Telefon Puanla")
    print("[3]- Analiz İşlemleri")
    print("    [3.1]- Fiyat Puan İlişki Analizi (Saçılma Grafiği)")
    print("    [3.2]- Markaya Göre Puan Dağılımı (Pasta Grafiği)")
    print("    [3.3]- Markaya Göre Puan Dağılımı (Histogram Grafiği)")
    print("[4]- Dosya İşlemleri")
    print("    [4.1]- Dosya okuma")
    print("    [4.2]- Dosyayı veri tabanına yazdırma")
    print("\n")
    print("* Uygulamadan çıkmak için EXIT giriniz ")
    print("* Yapmak istediğiniz işlem numarasını giriniz: (Örnek: 2.1)")
    print("\n------------------------------------------------------------\n")

# Seçilen işem numarasına göre islemi yap
def run_operation(islem_no):
    if islem_no == "1":
        create_user()
    elif islem_no == "2.1":
        create_cellphone()
    elif islem_no == "2.2":
        get_all_cellphone()
    elif islem_no == "2.3":
        update_cellphone()
    elif islem_no == "2.4":
        create_cellphone_rating()
    elif islem_no == "3.1":
        draw_scatter_graph()
    elif islem_no == "3.2":
        draw_pie_graph()
    elif islem_no == "3.3":
        draw_histogram_graph()
    elif islem_no == "4.1":
        read_excel_file()
    else:
        print("Geçersiz işlem no!")

# 1- Kullanıcı Oluşturma
def create_user():
    k_adi = get_input("Kullanıcı Adı")
    k_sifre = get_input("Şifre")
    query = "INSERT INTO kullanici(k_adi,k_sifre) VALUES (%s,%s)"
    CURSOR.execute(query,(k_adi, k_sifre))
    DATABASE.commit()
    print("Kullanıcı başarıyla kaydedildi.")

# 2.1- Telefon Ekle
def create_cellphone():
    t_marka = get_input("Marka")
    t_model = get_input("Model")
    t_fiyat = get_input("Fiyat")
    query = "INSERT INTO telefonlar(marka,model,fiyat) VALUES (%s,%s,%s)"
    CURSOR.execute(query, (t_marka, t_model, t_fiyat))
    DATABASE.commit()
    print("Telefon başarıyla kaydedildi.")

# 2.2- Telefon Listele
def get_all_cellphone():
    query = "SELECT * FROM telefonlar"
    CURSOR.execute(query)
    cellphones = CURSOR.fetchall()
    print("\n----------------------------------------------")
    print("ID\tMARKA\tMODEL\t\tFIYAT")
    print("----------------------------------------------")
    for cellphone in cellphones:
        print('{0}\t{1}\t{2}\t{3}'.format(cellphone[0],cellphone[1],cellphone[2],cellphone[3]))
    print("----------------------------------------------\n")

# 2.3- Telefon Fiyat Güncelle
def update_cellphone():
    get_all_cellphone()
    cellphone_id = get_input("Güncellecek telefon id")
    yeni_fiyat = get_input("Fiyat")
    query = "UPDATE telefonlar SET fiyat=%s WHERE id=%s"
    CURSOR.execute(query, (yeni_fiyat, cellphone_id))
    DATABASE.commit()
    print("Telefon fiyatı başarıyla güncellendi.")

# 2.4- Telefon Puanla
def create_cellphone_rating():
    get_all_cellphone()
    cellphone_id = get_input("Puanlanacak telefon id")
    print("1 ile 10 arasında bir puan girin")
    puan = get_input("Puan")
    query = "INSERT INTO puanlar(tel_id,tel_puan) VALUES (%s,%s)"
    CURSOR.execute(query,(cellphone_id, puan))
    DATABASE.commit()
    print("Telefon puanı başarıyla kaydedildi.")

# 3.1- Fiyat Puan İlişki Analizi (Saçilma Grafiği) 
def draw_scatter_graph():
    query = '''
    SELECT t.id as ID, (SELECT DISTINCT(t.fiyat)) AS FIYAT, SUM(tel_puan) as TOPLAM_PUAN FROM telefonlar t
    	LEFT JOIN puanlar p ON t.id = p.tel_id
    GROUP BY t.id
    '''
    CURSOR.execute(query)
    cellphone_stats = CURSOR.fetchall()
    print("\n------------------------------------")
    print("ID\tFIYAT\tPUAN")
    print("------------------------------------")
    for stat in cellphone_stats:
        print('{0}\t{1}\t{2}'.format(stat[0],stat[1],stat[2]))
    print("------------------------------------\n")
    
    df = pd.DataFrame(cellphone_stats, columns=['ID', 'FIYAT', 'PUAN'])
    df.plot.scatter(x='PUAN', y='FIYAT', c='Red')
    plt.show()
    
    return cellphone_stats

# 3.2- Markaya Göre Puan Dağılımı (Pasta Grafiği)
def draw_pie_graph():
   
    query = '''     
    SELECT t.marka as MARKA ,SUM(tel_puan) as TOPLAM_PUAN FROM telefonlar t
    	LEFT JOIN puanlar p ON t.id = p.tel_id
    WHERE p.tel_puan is not null
    GROUP BY t.marka  
    '''
    CURSOR.execute(query)
    cellphone_stats = CURSOR.fetchall()
    
    df = pd.DataFrame(cellphone_stats)
    df.fillna(0,inplace=True)
    x=df[1]
    label=df[0]
    plt.pie(x,labels=label)
    plt.show()

# 3.3- Markaya Göre Puan Dağılımı (Histogram Grafiği) 
def draw_histogram_graph():
    query = '''     
    SELECT t.marka as MARKA ,SUM(tel_puan) as TOPLAM_PUAN FROM telefonlar t
    	LEFT JOIN puanlar p ON t.id = p.tel_id
    WHERE p.tel_puan is not null
    GROUP BY t.marka  
    '''
    CURSOR.execute(query)
    cellphone_stats = CURSOR.fetchall()
    
    df = pd.DataFrame(cellphone_stats)
    df.fillna(0,inplace=True)

    fig, ax = plt.subplots()
    brands = df[0]
    raitings = df[1]
    y_pos = np.arange((brands.count()))

    ax.barh(y_pos, raitings, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(brands)
    # etiketleri yatay doğrultuda yazdır
    ax.invert_yaxis()  
    ax.set_xlabel('Puanlar')
    ax.set_title('Markaya Göre Puan Dağılımı (Histogram Grafiği)')
    plt.show()

# 4.1- Dosya Okuma
def read_excel_file():
    df = pd.read_excel("python-final/custom_cellphone_rating.xlsx")
    query = "INSERT INTO puanlar (tel_id,tel_puan) VALUES "
    for index, row in df.iterrows():
        query += "('{0}','{1}'),\n".format(row['cellphone_id'], row['rating'])
    query = query[:-2] + ';'
    
    CURSOR.execute(query)
    DATABASE.commit()
    print("Dosyadan okunan puanlar başarıyla kaydedildi.")

# Kullanıcının giriş yapmasını bekle
def wait_user_input():
    print("Devam etmek için bir tuşa basınız.")
    user_input = input()
    if user_input == 'EXIT':
        print("Uygulama sonlandırıldı.")
        sys.exit(0);
    

# Database bağlan
def connect_to_db():
    global DATABASE, CURSOR 
    DATABASE = mysql.connector.connect(host="localhost", user="root", password="", db="python_final")
    CURSOR = DATABASE.cursor()

# Uygulama Döngüsü
connect_to_db()

#Döngüye al 
while (True):
    print_menu()
    secilen_islem = get_input("İşlem No")
    run_operation(secilen_islem)
    wait_user_input()




"""
df = pd.read_csv("python-final/cellphone.csv")

query = 'INSERT INTO telefonlar (marka,model,fiyat) VALUES '
for index, row in df.iterrows():
    query += "('{0}','{1}',{2}),\n".format(row['brand'], row['model'],row['price'])
print(query)    
"""


# Dosyaya yazdırma
# path = r'C:\Users\AFA\.spyder-py3\python-final\export.txt'
# with open(path, 'a') as f: 
#     f.write(query)

#df = pd.DataFrame([[1,18000,9],[2,15000,0]]);
#print(df)

#result2 = df.replace(to_replace=[None], value=np.nan, inplace=True)
#result2 = df.fillna(0,inplace=True)
#print(result2)

#print(get_all_cellphone_rating())






'''
if (secilen_islem == 1):
    create_user()
elif (secilen_islem == 3.1):
    print("Fiyat Puan İlişki Analizi")
'''

"""
    0- Telefon verisini içe aktar
    1- Kullanıcı Girişi 
    2- Menu Yazdır
        - Kullanıcı Oluştur
        - Telefon İşlemleri
            - Telefon Ekle
            - Telefon Listele
            - Telefon Fiyat Güncelle
            - Telefon Silme
            - Telefon Puanla
        - Analiz İşlemleri
            - Fiyat Puan İlişki Analizi (Saçilma Grafiği)
            - Markaya Göre Puan Dağılımı (Pasta Grafiği)
            - Markaya Göre Puan Dağılımı (Histogram Grafiği) 
    3- Seçimi Al
    4- Verileri Al
    5- Verileri Kontrol et ve işlemi gerçekleştir
    6-> 2 (Menuyu Yazdır)
"""

    

"""
pasta grafiği denemesi

 query = '''     
 SELECT t.id as ID FROM telefonlar t
FT JOIN puanlar p ON t.id = p.tel_id
 where p.tel_puan is not null
 GROUP BY t.marka   
 '''
 CURSOR.execute(query)
 #CURSOR.fetchall()
 print("\n------------------------------------")
 print("ID\tMARKA\tPUAN")
 print("------------------------------------")
 #for stat in cellphone_stats:
 df=pd.DataFrame(columns=['ID'])
 y=np.array([df])
 label=["MARKA"]
 plt.pie(y,labels=label)
 plt.show()
 
    Pasta Grafiği
    -------------------
    2500 -> Toplam Puan
    750 -> Apple
    450 -> Samsung
    260 -> Oppo
    500 -> Xiaomi
    540 -> Casper
    
    Kullanıcılar
    ---------------------------------------
    id   username       password    
    1    fehmi          12345
    2    bilal          123    
    
    Telefonlar
    ---------------------------------------
    id   brand   model               price
    ---------------------------------------
    0    Apple   iPhone SE (2022)    10000
    1    Apple   iPhone 13 Mini      10000     
    ---------------------------------------

    Telefon Puanları
    ---------------------------------------
    id  cellphone_id  raiting
    0   0             5
    1   0             8
    2   0             7
    3   1             2
    4   1             7
    
"""


