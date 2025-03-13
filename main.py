import sys
import pandas as pd
import os
from PyQt6.QtWidgets import (
    QMainWindow, 
    QWidget, 
    QGridLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QHBoxLayout, 
    QVBoxLayout,
    QApplication,
    QMessageBox,
    QFileDialog,
    QTabWidget,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QFont, QPalette, QColor

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Fiyat Hesaplayıcı")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                color: #424242;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196F3;
                font-weight: bold;
            }
            QLabel {
                color: #424242;
                font-size: 14px;
            }
        """)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Sekme widget'ı oluştur
        self.tabs = QTabWidget()
        self.tab_manual = QWidget()
        self.tab_excel = QWidget()
        
        self.tabs.addTab(self.tab_manual, "Manuel Hesaplama")
        self.tabs.addTab(self.tab_excel, "Excel İşlemleri")
        
        layout.addWidget(self.tabs)
        
        # Manuel hesaplama sekmesini ayarla
        self.setup_manual_tab()
        
        # Excel işlemleri sekmesini ayarla
        self.setup_excel_tab()
        
    def setup_manual_tab(self):
        layout = QVBoxLayout(self.tab_manual)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Kart görünümü için frame
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        layout.addWidget(card)
        
        # Girdi alanları için grid layout
        grid = QGridLayout()
        grid.setSpacing(15)
        card_layout.addLayout(grid)
        
        # Input alanları
        input_fields = [
            ("Alış Fiyatı (₺):", "purchase"),
            ("Komisyon (%):", "commission"),
            ("Kargo (₺):", "shipping"),
            ("Kar (%):", "margin")
        ]
        
        for i, (label_text, field_name) in enumerate(input_fields):
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            entry = ModernLineEdit()
            setattr(self, f"{field_name}_label", label)
            setattr(self, f"{field_name}_entry", entry)
            
            grid.addWidget(label, i, 0)
            grid.addWidget(entry, i, 1)
            
            # Validator ve hizalama
            entry.setValidator(QDoubleValidator())
            entry.setAlignment(Qt.AlignmentFlag.AlignRight)
            entry.setText("0")
            
            # Enter tuşu bağlantısı
            entry.returnPressed.connect(self.calculate_sale_price)
        
        # Varsayılan değerler
        self.shipping_entry.setText("30")
        self.commission_entry.setText("10")
        self.margin_entry.setText("20")
        
        # Hesaplama Butonu
        button_layout = QHBoxLayout()
        self.calculate_btn = ModernButton("Satış Fiyatı Hesapla")
        self.calculate_btn.clicked.connect(self.calculate_sale_price)
        button_layout.addStretch()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addStretch()
        card_layout.addLayout(button_layout)
        
        # Sonuç kartı
        result_card = QFrame()
        result_card.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #1565C0;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        result_layout = QVBoxLayout(result_card)
        
        self.commission_result = QLabel("Pazaryeri Komisyonu: ₺ 0,00")
        self.shipping_result = QLabel("Kargo: ₺ 0,00")
        self.sale_price = QLabel("Satış Fiyatı: ₺ 0,00")
        
        for result in (self.commission_result, self.shipping_result, self.sale_price):
            result.setAlignment(Qt.AlignmentFlag.AlignRight)
            result_layout.addWidget(result)
        
        layout.addWidget(result_card)
        layout.addStretch()
        
    def setup_excel_tab(self):
        layout = QVBoxLayout(self.tab_excel)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Excel kartı
        excel_card = QFrame()
        excel_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        excel_layout = QVBoxLayout(excel_card)
        
        # Excel dosyası yükleme düğmesi
        self.load_excel_btn = ModernButton("Excel Dosyası Yükle")
        self.load_excel_btn.clicked.connect(self.load_excel_file)
        excel_layout.addWidget(self.load_excel_btn)
        
        # Yüklenen dosya bilgisi
        self.excel_info_label = QLabel("Dosya yüklenmedi")
        self.excel_info_label.setStyleSheet("color: #757575; font-size: 14px;")
        excel_layout.addWidget(self.excel_info_label)
        
        # Bilgi kartı
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #E65100;
                font-size: 14px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        
        info_text = """
        Excel dosyası aşağıdaki sütunları içermelidir:
        - Ürün Adı (isteğe bağlı)
        - Alış Fiyatı (gerekli)
        - Komisyon (isteğe bağlı, varsayılan: %10)
        - Kargo (isteğe bağlı, varsayılan: 30₺)
        - Kar (isteğe bağlı, varsayılan: %20)
        """
        self.column_info = QLabel(info_text)
        info_layout.addWidget(self.column_info)
        excel_layout.addWidget(info_card)
        
        # İşlem düğmesi
        self.process_excel_btn = ModernButton("Excel Dosyasını İşle ve Sonuçları Kaydet")
        self.process_excel_btn.clicked.connect(self.process_excel_file)
        self.process_excel_btn.setEnabled(False)
        excel_layout.addWidget(self.process_excel_btn)
        
        # Sonuç bilgisi
        self.excel_result_label = QLabel("")
        self.excel_result_label.setStyleSheet("color: #2E7D32; font-size: 14px;")
        excel_layout.addWidget(self.excel_result_label)
        
        layout.addWidget(excel_card)
        layout.addStretch()
        
        # Varsayılan değerleri oluştur
        self.excel_file_path = None
        self.excel_data = None

    def load_excel_file(self):
        """Excel dosyası yükleme fonksiyonu"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", 
            "Excel Dosyaları (*.xlsx *.xls);;Tüm Dosyalar (*)", 
            options=options
        )
        
        if file_path:
            try:
                self.excel_file_path = file_path
                self.excel_data = pd.read_excel(file_path)
                
                # Dosyadaki sütunları kontrol et
                required_columns = ["Alış Fiyatı"]
                missing_columns = [col for col in required_columns if col not in self.excel_data.columns]
                
                if missing_columns:
                    QMessageBox.warning(
                        self, "Eksik Sütunlar", 
                        f"Dosyada şu gerekli sütunlar eksik: {', '.join(missing_columns)}"
                    )
                    self.excel_info_label.setText("Dosya yüklenmedi - Eksik sütunlar")
                    self.process_excel_btn.setEnabled(False)
                    return
                
                row_count = len(self.excel_data)
                self.excel_info_label.setText(
                    f"Dosya yüklendi: {os.path.basename(file_path)}\n"
                    f"Toplam {row_count} ürün bulundu"
                )
                self.process_excel_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Dosya Okuma Hatası", 
                    f"Excel dosyası okunurken hata oluştu: {str(e)}"
                )
                self.excel_info_label.setText("Dosya yüklenemedi - Hata")
                self.process_excel_btn.setEnabled(False)
    
    def process_excel_file(self):
        """Excel dosyasını işle ve sonuçları yeni bir Excel dosyasına kaydet"""
        if self.excel_data is None or self.excel_file_path is None:
            QMessageBox.warning(self, "Hata", "Önce bir Excel dosyası yüklemelisiniz")
            return
        
        try:
            # Varsayılan değerleri hazırla
            default_commission = 10.0
            default_shipping = 30.0
            default_margin = 20.0
            
            # Yeni DataFrame oluştur
            result_df = self.excel_data.copy()
            
            # Her bir satır için hesaplamaları yap
            for index, row in result_df.iterrows():
                # Gerekli değerleri al, yoksa varsayılanları kullan
                purchase_price = row["Alış Fiyatı"]
                commission = row.get("Komisyon", default_commission)
                shipping = row.get("Kargo", default_shipping)
                margin = row.get("Kar", default_margin)
                
                # Hesaplamalar
                commission_amount = purchase_price * commission / 100
                total_with_commission = purchase_price + commission_amount
                # Önce kar hesaplanır
                total_with_margin = total_with_commission * (1 + margin / 100)
                # En son kargo eklenir
                sale_price = total_with_margin + shipping
                
                # Sonuçları DataFrame'e ekle
                result_df.at[index, "Komisyon Tutarı"] = commission_amount
                result_df.at[index, "Kargo Tutarı"] = shipping
                result_df.at[index, "Satış Fiyatı"] = sale_price
            
            # Çıktı dosyası için isim oluştur
            input_filename = os.path.basename(self.excel_file_path)
            output_path = os.path.join(
                os.path.dirname(self.excel_file_path),
                f"Sonuç_{input_filename}"
            )
            
            # Sonuçları yeni bir Excel dosyasına kaydet
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Sonuçları Kaydet", output_path, 
                "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)", 
                options=options
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                # Excel dosyasına dışa aktar
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    result_df.to_excel(writer, sheet_name='Satış Fiyatları', index=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Satış Fiyatları']
                    
                    # Para formatı
                    money_format = workbook.add_format({'num_format': '#,##0.00 ₺'})
                    percent_format = workbook.add_format({'num_format': '0.00%'})
                    
                    # Para kolonlarına para formatı uygula
                    for col_idx, col_name in enumerate(result_df.columns):
                        if col_name in ["Alış Fiyatı", "Komisyon Tutarı", "Kargo Tutarı", "Satış Fiyatı"]:
                            worksheet.set_column(col_idx, col_idx, 15, money_format)
                        elif col_name in ["Komisyon", "Kar"]:
                            worksheet.set_column(col_idx, col_idx, 10, percent_format)
                
                self.excel_result_label.setText(f"Sonuçlar başarıyla kaydedildi: {os.path.basename(file_path)}")
                QMessageBox.information(
                    self, "İşlem Tamamlandı", 
                    f"Hesaplanan satış fiyatları başarıyla şu dosyaya kaydedildi:\n{file_path}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self, "İşlem Hatası", 
                f"Excel dosyası işlenirken hata oluştu: {str(e)}"
            )
            self.excel_result_label.setText("İşlem sırasında hata oluştu")
    
    def calculate_sale_price(self):
        """Manuel sekmedeki satış fiyatı hesaplama fonksiyonu"""
        try:
            # Girdileri oku
            purchase = float(self.purchase_entry.text().replace(',', '.'))
            commission = float(self.commission_entry.text().replace(',', '.'))
            shipping = float(self.shipping_entry.text().replace(',', '.'))
            margin = float(self.margin_entry.text().replace(',', '.'))
            
            # Eğer alış fiyatı 0 ise uyarı göster
            if purchase <= 0:
                QMessageBox.warning(self, "Hata", "Alış fiyatı 0'dan büyük olmalıdır.")
                self.purchase_entry.setFocus()
                return
            
            # Hesaplamalar
            commission_amount = purchase * commission / 100
            total_with_commission = purchase + commission_amount
            # Önce kar hesaplanır
            total_with_margin = total_with_commission * (1 + margin / 100)
            # En son kargo eklenir
            sale_price = total_with_margin + shipping
            
            # Türkiye'deki para formatı için virgül kullan
            def tr_fmt(val):
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.commission_result.setText(f"Pazaryeri Komisyonu: ₺ {tr_fmt(commission_amount)}")
            self.shipping_result.setText(f"Kargo: ₺ {tr_fmt(shipping)}")
            self.sale_price.setText(f"Satış Fiyatı: ₺ {tr_fmt(sale_price)}")
            
        except ValueError as e:
            QMessageBox.critical(self, "Hata", f"Hesaplama sırasında bir hata oluştu: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Uygulama genelinde font ayarı
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
