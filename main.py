import mysql.connector
import sys
import hashlib
import io
import shutil
import os
from PyQt5 import QtCore
from PyQt5.QtGui import *
import platform
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import *
from datetime import date
from PyQt5.QtCore import *
import tempfile

    
def update_expired_contracts():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="car"
    )

    cursor = db.cursor()
    today = date.today().strftime("%Y-%m-%d")

    #update disponibility of cars

    cursor.execute("""
        UPDATE voiture
        SET Disponibilite = TRUE
        WHERE id IN (
            SELECT voiture_id FROM contract
            WHERE end_date < %s
        )
    """, (today,))

    # Delete expired contracts

    cursor.execute("""
        DELETE FROM contract
        WHERE end_date < %s
    """, (today,))


    db.commit()
    cursor.close()
    db.close()


        
class CarRentalApp(QMainWindow):
        
    def __init__(self):
        self.car_table = None

        super().__init__()
        self.db = self.connect_db()
        self.set_background_image("car.png")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.book_now_page = self.create_book_now_page()
        self.stacked_widget.addWidget(self.book_now_page)

        self.login_page = self.create_login_page()
        self.stacked_widget.addWidget(self.login_page)
        self.setFixedSize(1200, 1000)

        self.main_page = QWidget()
        self.init_ui()

    def set_background_image(self, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        brush = QBrush(pixmap)
        palette.setBrush(QPalette.Background, brush)
        self.setPalette(palette)

    def change_background_image(self, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        brush = QBrush(pixmap)
        palette.setBrush(QPalette.Background, brush)
        self.setPalette(palette)



    def connect_db(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="car"
        )
        return db
    
    
    def create_book_now_page(self):
        book_now_page = QWidget()
        layout = QVBoxLayout(book_now_page)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        book_now_button = QPushButton("Book Now")
        book_now_button.clicked.connect(self.on_book_now_clicked)

        # Customize button 
        book_now_button.setMinimumHeight(40)
        book_now_button.setMinimumWidth(150)
        book_now_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                font-size: 18px;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #003F7F;
            }
        """)

        layout.addWidget(book_now_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        return book_now_page

    def on_book_now_clicked(self):
        self.change_background_image("login.png")  
        self.stacked_widget.setCurrentWidget(self.login_page)

    def create_login_page(self):
        login_page = QWidget()
        layout = QVBoxLayout(login_page)
        layout.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white;")
        form_layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addWidget(self.username_input)

        username_label = QLabel("Password:")
        username_label.setStyleSheet("color: white;")
        form_layout.addWidget(username_label)        
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                font-size: 14px;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #003F7F;
            }
        """)
        layout.addWidget(login_button, alignment=Qt.AlignHCenter)

        create_account_button = QPushButton("Create Account")
        create_account_button.clicked.connect(self.show_create_account_form)
        create_account_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                font-size: 14px;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
            QPushButton:pressed {
                background-color: #3E4348;
            }
        """)
        layout.addWidget(create_account_button, alignment=Qt.AlignHCenter)

        self.registration_form = self.create_registration_form()
        self.registration_form.hide()
        layout.addWidget(self.registration_form)

        return login_page

    
    def create_account(self, username, password):
        # Hash the password using the SHA-256 algorithm
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cursor = self.db.cursor()
        cursor.execute("INSERT INTO authentication (username, mot_de_passe) VALUES (%s, %s)", (username, password_hash))
        self.db.commit()
        cursor.close()
        print("Creating account with username:", username)
        
        # Create a new tab to display the success message
        success_tab = QWidget()
        layout = QVBoxLayout(success_tab)
        layout.setAlignment(Qt.AlignCenter)
        message_label = QLabel("Account created successfully.")
        message_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #28A745;
                border: 2px solid #28A745;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout.addWidget(message_label, alignment=Qt.AlignCenter)


        self.stacked_widget.addWidget(success_tab)
        self.stacked_widget.setCurrentWidget(success_tab)

        # timer for the msg
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.stacked_widget.removeWidget(success_tab))
        timer.start(3000)

        self.new_username_input.setText("")
        self.new_password_input.setText("")


    def show_create_account_form(self):
        self.registration_form.show()

    def create_registration_form(self):
        registration_form = QWidget()
        layout = QVBoxLayout(registration_form)
        layout.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        new_username_label = QLabel("New Username:")
        new_username_label.setStyleSheet("color: white;")
        form_layout.addWidget(new_username_label)
        self.new_username_input = QLineEdit()
        self.new_username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addWidget(self.new_username_input)

        new_password_label = QLabel("New Password:")
        new_password_label.setStyleSheet("color: white;")
        form_layout.addWidget(new_password_label)
        self.new_password_input = QLineEdit()
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.new_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.new_password_input)

        layout.addLayout(form_layout)

        register_button = QPushButton("Register")
        register_button.clicked.connect(lambda: self.create_account(self.new_username_input.text(), self.new_password_input.text()))
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                font-size: 14px;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1E7E34;
            }
        """)
        layout.addWidget(register_button, alignment=Qt.AlignHCenter)

        return registration_form

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Hash the entered password using SHA-256
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM authentication WHERE username=%s AND mot_de_passe=%s", (username, password_hash))
        user = cursor.fetchone()
        cursor.close()

        if user:
            self.stacked_widget.addWidget(self.main_page)
            self.stacked_widget.setCurrentWidget(self.main_page)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def load_clients(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM client")
        clients = cursor.fetchall()
        self.clients_table.setRowCount(len(clients))
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(["ID", "Nom", "Prenom", "Email", "Telephone"])

        for row, client in enumerate(clients):
            for col, value in enumerate(client):
                cell = QTableWidgetItem(str(value))
                self.clients_table.setItem(row, col, cell)

        cursor.close()

        #Add client function
    def add_client(self, nom, prenom, email, telephone):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO client (nom, prenom, email, telephone) VALUES (%s, %s, %s, %s)", (nom, prenom, email, telephone))
        self.db.commit()
        cursor.close()

        print("Client added successfully.")
        self.load_clients()
        # clear input 
        self.nom_input.clear()
        self.prenom_input.clear()
        self.email_input.clear()
        self.telephone_input.clear()

    #Add car function
    def add_car(self, marque, modele, image_path, type_carburant, nombre_places, transmission, prix_par_jour):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO voiture (marque, modele, image, type_carburant, nombre_places, transmission, prix_par_jour) VALUES (%s, %s, %s, %s, %s, %s, %s)", (marque, modele, image_path, type_carburant, nombre_places, transmission, prix_par_jour))
        self.db.commit()
        cursor.close()

        print("Car added successfully.")
        self.load_cars()
        # clear input 
        self.marque_input.clear()
        self.modele_input.clear()
        self.image_input.clear()
        self.type_carburant_input.setCurrentIndex(0)
        self.nombre_places_input.clear()
        self.transmission_input.setCurrentIndex(0)
        self.prix_par_jour_input.setValue(0)

    #For load contract
    def get_client_details(self, client_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT nom, prenom, email, telephone FROM client WHERE id = %s", (client_id,))
        client_details = cursor.fetchone()
        cursor.close()

        return client_details

    #For load contract
    def get_car_details(self, voiture_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT marque, modele, id, type_carburant, transmission, prix_par_jour FROM voiture WHERE id = %s", (voiture_id,))
        car_details = cursor.fetchone()
        cursor.close()

        return car_details


    def generate_contract_pdf(self, client_id, voiture_id, start_date, end_date):
        car_details = self.get_car_details(voiture_id)
        marque, modele, id, transmission, type_carburant, prix_par_jour = car_details

        client_details = self.get_client_details(client_id)
        nom, prenom, email, telephone = client_details
        # PDF CUSTOMIZE
        content = f"""
            <h1>Car Rental Contract</h1>
            <img src="logo.jpg">

            <h4>Background:</h4>
            <p>1.	This Car Rental Agreement is made and entered into on the <b>{start_date}</b> between:</p>
            <h5>Owner:</h5><p><b>EMSI CAR RENTAL</b> Located at Route Safi with a mailing address <b>contact@emsi.ma (“Owner”)</b></p>
            <h5>Renter:</h5><p><b>{nom} {prenom}</b> with a mailing address <b>{email} (“Renter”)</b></p>
            <h4>Identification of Rental Vehicle:</h4>
            <p>2.	Identification of Rental Vehicle:</p>
            <b>{marque} {modele} {type_carburant} {transmission}</b> with the id: <b>{id}</b>
            <h4>Rental Term:</h4>
            <p>3.	The term of this Car Rental Agreement runs from <b>{start_date}</b> to<b> {end_date}</b>, upon completion of all terms of this agreement by both Parties. </P>
            <p>4.	........................................................................................</p>
            <h4>Scope of Use:</h4>
            <p> 5.	Renter will use the Rented Vehicle only for personal or routine business use and operate the Rented Vehicle only on properly maintained roads and parking lots. </p>
            <p> 6.	Renter will comply with all applicable laws relating to holding licensure to operate the vehicle and pertaining to operation of motor vehicles. </p>
            <p> 7.	Renter will not sublease the Rental Vehicle or use it as a vehicle for hire. </p>
            <p> 8.	Renter will not take the vehicle location limit.</p>

            <p>Signature for Renter : <b>{nom} {prenom}</p>

            <img src="footer.png">
            <p></p>
            <p>Signature for Owner :<b> EMSI RENTAL </p>
            <img src="footer.png">
        """
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName("contract.pdf")
        if platform.system() == "Windows":
                os.startfile("contract.pdf")
        doc = QTextDocument()
        doc.setHtml(content)
        doc.print_(printer)

    #Display car
    def load_cars(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM voiture")
        cars = cursor.fetchall()
        self.cars_table.setRowCount(len(cars))
        self.cars_table.setColumnCount(8)
        self.cars_table.setHorizontalHeaderLabels(["Image", "ID", "Marque", "Modele", "Type Carburant", "Nombre Places", "Transmission", "Prix par Jour"])

        for row, car in enumerate(cars):
            for col, value in enumerate(car):
                if col == 0:  
                    image_path = value.decode('utf-8')  # Convert  bytes l string
                    pixmap = QPixmap(image_path)
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio))  
                    self.cars_table.setCellWidget(row, col, label)
                else:
                    cell = QTableWidgetItem(str(value))
                    self.cars_table.setItem(row, col, cell)

        cursor.close()

    def init_ui(self):
        main_widget = self.main_page
        main_layout = QVBoxLayout(main_widget)

        button_style = "QPushButton { font-size: 16px; background-color: #1E90FF; color: white; padding: 8px 16px; border: none; }"
        button_style += "QPushButton:hover { background-color: #0066CC; }"

        # row 1 buttons
        row1_layout = QHBoxLayout()
        add_client_button = QPushButton("Add client")
        add_client_button.setStyleSheet(button_style)
        add_client_button.clicked.connect(self.show_add_client_form)
        row1_layout.addWidget(add_client_button)

        add_car_button = QPushButton("Add car")
        add_car_button.setStyleSheet(button_style)
        add_car_button.clicked.connect(self.show_add_car_form)
        row1_layout.addWidget(add_car_button)

        main_layout.addLayout(row1_layout)

        # row 2 butttons
        row2_layout = QHBoxLayout()
        search_car_button = QPushButton("Search car")
        search_car_button.setStyleSheet(button_style)
        search_car_button.clicked.connect(self.show_search_car_form)
        row2_layout.addWidget(search_car_button)

        reserved_cars_button = QPushButton("Show Reserved Cars")
        reserved_cars_button.setStyleSheet(button_style)
        reserved_cars_button.clicked.connect(self.show_reserved_cars)
        row2_layout.addWidget(reserved_cars_button)

        available_cars_button = QPushButton("Show Available Cars")
        available_cars_button.setStyleSheet(button_style)
        available_cars_button.clicked.connect(self.show_available_cars)
        row2_layout.addWidget(available_cars_button)

        main_layout.addLayout(row2_layout)

        # row 3 buttons
        row3_layout = QHBoxLayout()
        add_contract_button = QPushButton("Add contract")
        add_contract_button.setStyleSheet(button_style)
        add_contract_button.clicked.connect(self.show_add_contract_form)
        row3_layout.addWidget(add_contract_button)

        load_contracts_button = QPushButton("Load contracts")
        load_contracts_button.setStyleSheet(button_style)
        load_contracts_button.clicked.connect(self.load_contracts)
        row3_layout.addWidget(load_contracts_button)

        main_layout.addLayout(row3_layout)

        # form & Table
        self.form_container = QStackedWidget()
        main_layout.addWidget(self.form_container)

        self.clients_table = QTableWidget()
        self.load_clients()
        main_layout.addWidget(self.clients_table)

        self.cars_table = QTableWidget()
        self.load_cars()
        main_layout.addWidget(self.cars_table)

    def show_add_client_form(self):
        form = QWidget()
        form_layout = QFormLayout()
        add_client_label = QLabel("Add Client")
        add_client_label.setStyleSheet("color: white; font-size: 18px;")
        form_layout.addRow(add_client_label)
        nom_label = QLabel("Nom:")
        nom_label.setStyleSheet("color: white;")
        form_layout.addRow(nom_label)
        self.nom_input = QLineEdit()
        self.nom_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.nom_input)
        prenom_label = QLabel("Prenom:")
        prenom_label.setStyleSheet("color: white;")
        form_layout.addRow(prenom_label)
        self.prenom_input = QLineEdit()
        self.prenom_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.prenom_input)
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: white;")
        form_layout.addRow(email_label)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.email_input)
        telephone_label = QLabel("Telephone:")
        telephone_label.setStyleSheet("color: white;")
        form_layout.addRow(telephone_label)
        self.telephone_input = QLineEdit()
        self.telephone_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.telephone_input)
        add_client_button = QPushButton("Add")
        add_client_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
        """)
        add_client_button.clicked.connect(lambda: self.add_client(self.nom_input.text(), self.prenom_input.text(), self.email_input.text(), self.telephone_input.text()))
        form_layout.addRow(add_client_button)
        form.setLayout(form_layout)
        self.form_container.addWidget(form)
        self.form_container.setCurrentWidget(form)



    def choose_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose an Image", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)", options=options)
        if file_name:
            # Define a directory to store images
            images_directory = "car"
            
            # Create the directory if it doesn't exist
            if not os.path.exists(images_directory):
                os.makedirs(images_directory)
            
            # Copy the image to the new directory and store the new file path
            new_image_path = os.path.join(images_directory, os.path.basename(file_name))
            shutil.copy(file_name, new_image_path)
            self.image_input.setText(new_image_path)

    def show_add_car_form(self):
        form = QWidget()
        layout = QVBoxLayout(form)
        layout.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        marque_label = QLabel("<font color='white'>Marque:</font>")
        form_layout.addRow(marque_label)
        self.marque_input = QLineEdit()
        self.marque_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.marque_input)

        modele_label = QLabel("<font color='white'>Modele:</font>")
        form_layout.addRow(modele_label)
        self.modele_input = QLineEdit()
        self.modele_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.modele_input)

        choose_image_button = QPushButton("Choose Image")
        choose_image_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                font-size: 14px;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4682B4;
            }
            QPushButton:pressed {
                background-color: #1C86EE;
            }
        """)
        choose_image_button.clicked.connect(self.choose_image)
        form_layout.addRow(choose_image_button)
        self.image_input = QLineEdit()
        self.image_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.image_input)

        type_carburant_label = QLabel("<font color='white'>Type Carburant:</font>")
        form_layout.addRow(type_carburant_label)
        self.type_carburant_input = QComboBox()
        self.type_carburant_input.addItem("Diesel")
        self.type_carburant_input.addItem("Sans Plomb")
        self.type_carburant_input.addItem("Hybrid")
        self.type_carburant_input.addItem("Other")
        self.type_carburant_input.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
            }
        """)
        form_layout.addRow(self.type_carburant_input)

        nombre_places_label = QLabel("<font color='white'>Nombre Places:</font>")
        form_layout.addRow(nombre_places_label)
        self.nombre_places_input = QLineEdit()
        self.nombre_places_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.nombre_places_input)

        transmission_label = QLabel("<font color='white'>Transmission:</font>")
        form_layout.addRow(transmission_label)
        self.transmission_input = QComboBox()
        self.transmission_input.addItem("Manuel")
        self.transmission_input.addItem("Automatic")
        self.transmission_input.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
            }
        """)
        form_layout.addRow(self.transmission_input)


        prix_par_jour_label = QLabel("<font color='white'>Prix par Jour (Maximum):</font>")
        form_layout.addRow(prix_par_jour_label)
        QLabel("<font color='white'>Prix par Jour:</font>")
        form_layout.addRow(prix_par_jour_label)
        self.prix_par_jour_input = QDoubleSpinBox()
        self.prix_par_jour_input.setRange(0, 10000)
        self.prix_par_jour_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        form_layout.addRow(self.prix_par_jour_input)

        add_car_button = QPushButton("Add")
        add_car_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                font-size: 14px;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #32CD32;
            }
            QPushButton:pressed {
                background-color: #228B22;
            }
        """)
        add_car_button.clicked.connect(lambda: self.add_car(self.marque_input.text(), self.modele_input.text(), self.image_input.text(), self.type_carburant_input.currentText(), self.nombre_places_input.text(), self.transmission_input.currentText(), self.prix_par_jour_input.value()))
        form_layout.addRow(add_car_button)

        layout.addLayout(form_layout)
        self.form_container.addWidget(form)
        self.form_container.setCurrentWidget(form)

    def create_add_contract_form(self):
        form = QWidget()
        layout = QFormLayout(form)

        label_style = "QLabel { color: #1E90FF; font-size: 16px; }"
        input_style = "QLineEdit { border: 1px solid #ccc; padding: 6px; font-size: 16px; }"
        button_style = "QPushButton { background-color: #1E90FF; color: #fff; font-size: 16px; border: none; padding: 12px; }"
        button_style += "QPushButton:hover { background-color: #0066CC; }"

        client_id_input = QLineEdit()
        client_id_input.setPlaceholderText("Enter client ID")
        client_id_input.setStyleSheet(input_style)
        label_client_id = QLabel("Client ID:")
        label_client_id.setStyleSheet(label_style)
        layout.addRow(label_client_id, client_id_input)

        car_id_input = QLineEdit()
        car_id_input.setPlaceholderText("Enter car ID")
        car_id_input.setStyleSheet(input_style)
        label_car_id = QLabel("Car ID:")
        label_car_id.setStyleSheet(label_style)
        layout.addRow(label_car_id, car_id_input)

        start_date_input = QLineEdit()
        start_date_input.setPlaceholderText("YYYY-MM-DD")
        start_date_input.setStyleSheet(input_style)
        label_start_date = QLabel("Start Date:")
        label_start_date.setStyleSheet(label_style)
        layout.addRow(label_start_date, start_date_input)

        end_date_input = QLineEdit()
        end_date_input.setPlaceholderText("YYYY-MM-DD")
        end_date_input.setStyleSheet(input_style)
        label_end_date = QLabel("End Date:")
        label_end_date.setStyleSheet(label_style)
        layout.addRow(label_end_date, end_date_input)

        add_contract_button = QPushButton("Add Contract")
        add_contract_button.setStyleSheet(button_style)
        add_contract_button.clicked.connect(lambda: [self.add_contract(client_id_input.text(), car_id_input.text(), start_date_input.text(), end_date_input.text()), self.generate_contract_pdf(client_id_input.text(), car_id_input.text(), start_date_input.text(), end_date_input.text())])
        layout.addWidget(add_contract_button)

        for i in range(layout.rowCount()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget and isinstance(widget, QLabel):
                widget.setMinimumWidth(100)

        return form


    def create_contracts_table(self):
        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(5)
        self.contracts_table.setHorizontalHeaderLabels(["ID", "Client ID", "Car ID", "Start Date", "End Date"])
        return self.contracts_table

        #SEARCH
    def show_search_car_form(self):
        form = self.create_search_car_form()
        self.form_container.addWidget(form)
        self.form_container.setCurrentWidget(form)

    def search_car(self, model, transmission, places, marque, type_carburant, price):
        cursor = self.db.cursor()

        query = "SELECT * FROM voiture WHERE 1"
        query_params = []

        if model:
            query += " AND modele LIKE %s"
            query_params.append('%' + model + '%')

        if transmission:
            query += " AND transmission LIKE %s"
            query_params.append('%' + transmission + '%')

        if places:
            query += " AND nombre_places = %s"
            query_params.append(places)

        if marque:
            query += " AND marque LIKE %s"
            query_params.append('%' + marque + '%')

        if type_carburant:
            query += " AND type_carburant LIKE %s"
            query_params.append('%' + type_carburant + '%')

        if price:
            query += " AND prix_par_jour <= %s"
            query_params.append(price)

        cursor.execute(query, query_params)
        cars = cursor.fetchall()
        cursor.close()
        self.display_cars_in_table(cars)

        
    def create_search_car_form(self):
        form = QWidget()
        layout = QVBoxLayout(form)

        label_style = "QLabel { color: white; font-size: 16px; }"
        input_style = "QLineEdit, QSpinBox, QDoubleSpinBox { border: 1px solid #ccc; padding: 6px; font-size: 16px; }"
        input_style += "QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button, QPushButton { background-color: #1E90FF; color: #fff; font-size: 16px; border: none; padding: 12px; }"
        input_style += "QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover, QPushButton:hover { background-color: #0066CC; }"
        input_style += "QLineEdit::placeholder, QDoubleSpinBox::prefix { color: #ccc; }"

        model_label = QLabel("Model:")
        model_label.setStyleSheet(label_style)
        model_input = QLineEdit()
        model_input.setPlaceholderText("Enter model")
        model_input.setStyleSheet(input_style)
        layout.addWidget(model_label)
        layout.addWidget(model_input)

        transmission_label = QLabel("Transmission:")
        transmission_label.setStyleSheet(label_style)
        transmission_input = QLineEdit()
        transmission_input.setPlaceholderText("Enter transmission")
        transmission_input.setStyleSheet(input_style)
        layout.addWidget(transmission_label)
        layout.addWidget(transmission_input)

        places_label = QLabel("Places:")
        places_label.setStyleSheet(label_style)
        places_input = QSpinBox()
        places_input.setSpecialValueText("Enter places")
        places_input.setStyleSheet(input_style)
        places_input.setMaximum(10)
        layout.addWidget(places_label)
        layout.addWidget(places_input)

        marque_label = QLabel("Marque:")
        marque_label.setStyleSheet(label_style)
        marque_input = QLineEdit()
        marque_input.setPlaceholderText("Enter marque")
        marque_input.setStyleSheet(input_style)
        layout.addWidget(marque_label)
        layout.addWidget(marque_input)

        type_carburant_label = QLabel("Type carburant:")
        type_carburant_label.setStyleSheet(label_style)
        type_carburant_input = QLineEdit()
        type_carburant_input.setPlaceholderText("Enter type carburant")
        type_carburant_input.setStyleSheet(input_style)
        layout.addWidget(type_carburant_label)
        layout.addWidget(type_carburant_input)

        price_label = QLabel("Prix (MAX):")
        price_label.setStyleSheet(label_style)
        price_input = QDoubleSpinBox()
        price_input.setPrefix("$")
        price_input.setSpecialValueText("Enter max price")
        price_input.setStyleSheet(input_style)
        price_input.setDecimals(0)
        price_input.setMinimum(200)
        price_input.setMaximum(9999)
        layout.addWidget(price_label)
        layout.addWidget(price_input)

        search_button = QPushButton("Search")
        search_button.setStyleSheet(input_style)
        search_button.clicked.connect(lambda: self.search_car(model_input.text(), transmission_input.text(), places_input.value(), marque_input.text(), type_carburant_input.text(), price_input.value()))
        layout.addWidget(search_button)

        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget and isinstance(widget, QLabel):
                widget.setMinimumWidth(100)

        return form




    def show_add_contract_form(self):
        form = self.create_add_contract_form()
        self.form_container.addWidget(form)
        self.form_container.setCurrentWidget(form)

    def load_contracts(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM contract")
        contracts = cursor.fetchall()
        cursor.close()

        # Create a new dialog and layout for the contracts table
        contracts_dialog = QDialog()
        contracts_dialog.setWindowTitle("Contracts")
        contracts_layout = QVBoxLayout(contracts_dialog)

        # Create the contracts table and add it to the layout
        self.contracts_table = QTableWidget()
        self.contracts_table.setRowCount(len(contracts))
        self.contracts_table.setColumnCount(8)
        self.contracts_table.setHorizontalHeaderLabels(["ID", "Client ID", "Car ID", "Start Date", "End Date", "Price per Day", "Total Days", "Total Price"])

        for i, contract in enumerate(contracts):
            for j, value in enumerate(contract):
                self.contracts_table.setItem(i, j, QTableWidgetItem(str(value)))

        contracts_layout.addWidget(self.contracts_table)

        contracts_dialog.exec_()

    def show_reserved_cars(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM voiture WHERE Disponibilite = FALSE")
        reserved_cars = cursor.fetchall()
        cursor.close()
        self.display_cars_in_table(reserved_cars)

    def show_available_cars(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM voiture WHERE Disponibilite = TRUE")
        available_cars = cursor.fetchall()
        cursor.close()
        self.display_cars_in_table(available_cars)

    def display_cars_in_table(self, cars):
        self.car_table = QTableWidget()
        self.car_table.setColumnCount(8)
        self.car_table.setRowCount(len(cars))
        self.car_table.setHorizontalHeaderLabels(["Image", "ID", "Marque", "Modele", "Type Carburant", "Nombre Places", "Transmission", "Prix par Jour"])

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.car_table.setSizePolicy(size_policy)
        self.car_table.setMinimumSize(800, 600)  

        for row, car in enumerate(cars):
            for column, field in enumerate(car):
                if column == 0:  
                    image_path = field.decode('utf-8')  
                    pixmap = QPixmap(image_path)
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio)) 
                    self.car_table.setCellWidget(row, column, label)
                else:
                    self.car_table.setItem(row, column, QTableWidgetItem(str(field)))

        self.car_table.resizeColumnsToContents()
        self.car_table.show()

        self.setFixedSize(1200, 1000)  # window size 


        
    def add_contract(self, client_id, voiture_id, start_date, end_date):
        cursor = self.db.cursor()
        
        cursor.execute("SELECT prix_par_jour FROM voiture WHERE id = %s", (voiture_id,))
        prix_par_jour = cursor.fetchone()[0]

        # Calcul total_days and total_price 
        cursor.execute("SELECT DATEDIFF(%s, %s)", (end_date, start_date))
        total_days = cursor.fetchone()[0]
        total_price = prix_par_jour * total_days

        # Insert the values f contract
        cursor.execute("INSERT INTO contract (client_id, voiture_id, start_date, end_date, prix_par_jour, total_days, total_price) VALUES (%s, %s, %s, %s, %s, %s, %s)", (client_id, voiture_id, start_date, end_date, prix_par_jour, total_days, total_price))
        cursor.execute("UPDATE voiture SET Disponibilite = FALSE WHERE id = %s", (voiture_id,))
        
        self.db.commit()
        cursor.close()
        
        print("contract added successfully.")
        self.load_contracts()


if __name__ == '__main__':
    update_expired_contracts()
    app = QApplication(sys.argv)
            
    # css
    app.setStyleSheet("""
        QPushButton {
            background-color: #4681f4;
            color: black;
            border: 1px solid #80669d;
        }
        QPushButton:hover {
            background-color: #dd7973;
        }
        QPushButton:pressed {
            background-color: #ffbd03;
        }
    """)

    main = CarRentalApp()
    main.show()
    sys.exit(app.exec_())