import requests
from bs4 import BeautifulSoup
import sqlite3
import time

con = sqlite3.connect("avesis.db")
cursor = con.cursor()

def today():
    timeNow = time.localtime()

    year = timeNow.tm_year
    month = timeNow.tm_mon
    day = timeNow.tm_mday
    return_time = f"{day}.{month}.{year}"
    return return_time


def create_table():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS academician (name TEXT, username TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS student (name TEXT, mail TEXT, academicians TEXT)")
    con.commit()
    con.close()

def nameOfTeacher(soup):
    name = soup.find_all("h1", {"class":"title"})
    name = name[0].text.strip()
    return name


def documentationList(soup):
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    docs = soup.find("div",attrs={"class": "ol-accordion"})
    docsList = docs.find_all("div",attrs={"class": "ac-item"})

    for doc in docsList:
        title = doc.find("div",attrs={"class","col-md-8 col-xs-3"}).find("span").text
        content = doc.find("div",attrs={"class": "item-body"})
        file = content.find("a",attrs={"class": "btn btn-warning btn-sm"})
        contentText = content.find("p").find("p")
        documentNameList = list()
        dateList = list()
        try:
            contentText = contentText.extract().text
        except:
            contentText = contentText
        label = doc.find("span",attrs={"class": "badge badge-primary"}).text
        date = doc.find("div",attrs={"class": "col-md-2 col-xs-5"}).find("span").text
        if file is None:
            file = "Yüklenen dosya yok"
        else:
            file = "Bir dosya yüklenmiş"
        documentNameList.append(f"{title}\t|\t{label}\t|\t{date}\t|\t{file}")
        dateList.append(date)
    con.close()
    return zip(documentNameList, dateList)

def username_finder(url):
    if url.startswith("https"):
        username = str(url.split("/")[3])
        return username
    try:
        username = str(url.split("/")[1])
    except:
        username = str(url)
    return username



def all_academicians():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("Select * From academician")
    all_data = cursor.fetchall()
    usernames = list()
    for thing in range(len(all_data)):
        username = all_data[thing][1]
        usernames.append(username)
    con.close()
    return usernames



def add_academician():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    informat = "***********************\n\n\tFor adding AVESIS pages, please paste the links one by one\n\t\
        if you want to exit from program, please press 'q' or leave a blank input\n\n \
             for information please write the word 'info'\n\n***********************"
    print(informat)
    
    usernames = list()
    url = input("enter the AVESIS page's URL: ")

    if url == "info":
        print(informat)

    controller = (url == "q") or (url == "")
    all_usernames = all_academicians()
    while not controller:
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        name = nameOfTeacher(soup)
        username = username_finder(url)
        if username not in all_usernames:
            cursor.execute("INSERT INTO academician VALUES(?,?)",(name, username))
            all_usernames.append(username)
        usernames.append(username)
        con.commit()
        url = input("enter the AVESIS page's URL: ")
        controller = (url == "q") or (url == "")
        if url == "info":
            print(informat)
    con.close()
    return usernames

def user_control():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("Select * From student")
    all_data = cursor.fetchall()
    mails = list()
    for thing in range(len(all_data)):
        mail = all_data[thing][1]
        mails.append(mail)
    con.close()
    return mails

def add_user():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    print("***********************\n\n\tThis is the page for your information")
    name = input("enter your name and surname: ")
    mail = input("enter your mail address: ")
    mails = user_control()
    while mail not in mails:
        print("Unfortunately someone is already uses this mail")
        mail = input("Please enter another e-mail address, if you want to quit press 'q'")
        if mail == "q":
            break
        elif mail not in mails:
            usernames = add_academician()
            usernames = ",".join(str(value) for value in usernames)
            cursor.execute("INSERT INTO student VALUES(?,?,?)",(name, mail, usernames))
            con.commit()
            break
    con.close()


def academic_control(day):
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("Select * From academician")
    all_data = cursor.fetchall()
    docs = dict()
    newDocs = list()
    for thing in range(len(all_data)):
        sorgu = "Select * From academician where username = ?"
        username = all_data[thing][1]
        cursor.execute(sorgu, (username,))
        docPage = cursor.fetchall()
        name = docPage[0]
        response = requests.get(f"https://avesis.yildiz.edu.tr/{username}/dokumanlar")
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        docList = documentationList(soup)
        count = 0
        for doc, date in docList:
            if date == day:
                newDocs.append(f"{doc}")
                count += 1
            else:
                break
        if count:
            docs[f"{username}"] = "┘".join(newDocs)
    con.close()
    return docs.copy()


def lengthOfStudents():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("Select * from student")
    all_data = cursor.fetchall()
    con.close()
    return len(all_data)


def requestfromstudent():
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    cursor.execute("Select * From student")
    all_data = cursor.fetchall()
    for thing in range(len(all_data)):
        student_name = all_data[thing][0]
        student_mail = all_data[thing][1]
        usernames = all_data[thing][2]
        infor = {"name":student_name, "mail":student_mail, "academic_usernames":usernames}
        yield infor.copy()
    con.close()
    return requestfromstudent()

def message_body(day,docs):
    con = sqlite3.connect("avesis.db")
    cursor = con.cursor()
    for inf in requestfromstudent():
        academic = inf["academic_usernames"].split(",")
        name = inf["name"]
        text = f"Merhaba {name},\n\n{day} tarihinde hocaların tarafından yüklenen dosyalar:\n\n\n"
        is_empty = True
        for username in academic:
            cursor.execute("Select * From academician where username = ?", (username,))
            academ_data = cursor.fetchall()
            academician_name = academ_data[0]
            try:
                documents = docs[username].split("┘")
                text += f"{academician_name[0]} tarafından yüklenenler\n"
                count = 1
                for thing in range(len(documents)):
                    text += f"{count}. {documents[thing]}\n"
                    count += 1
                is_empty = False
                text += "\n\n"
            except KeyError:
                pass

    all_stuff = {"mail": inf["mail"], "text": text, "emptiness": is_empty}
    con.close()
    return all_stuff



if __name__ == "__main__":
    create_table()
    add_user()

