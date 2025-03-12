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
    QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Fiyat Hesaplayıcı")
        self.setGeometry(100, 100, 600, 400)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
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
        
        # Girdi alanları için grid layout
        grid = QGridLayout()
        layout.addLayout(grid)
        
        # Alış Fiyatı
        self.purchase_label = QLabel("Alış Fiyatı (₺):")
        self.purchase_entry = QLineEdit()
        grid.addWidget(self.purchase_label, 0, 0)
        grid.addWidget(self.purchase_entry, 0, 1)
        
        # Pazaryeri Komisyonu
        self.commission_label = QLabel("Komisyon (%):")
        self.commission_entry = QLineEdit()
        grid.addWidget(self.commission_label, 1, 0)
        grid.addWidget(self.commission_entry, 1, 1)
        
        # KDV Oranı
        self.tax_label = QLabel("KDV (%):")
        self.tax_entry = QLineEdit()
        grid.addWidget(self.tax_label, 2, 0)
        grid.addWidget(self.tax_entry, 2, 1)
        
        # Kar Oranı
        self.margin_label = QLabel("Kar (%):")
        self.margin_entry = QLineEdit()
        grid.addWidget(self.margin_label, 3, 0)
        grid.addWidget(self.margin_entry, 3, 1)
        
        # Hesaplama Butonu
        button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("Satış Fiyatı Hesapla")
        self.calculate_btn.clicked.connect(self.calculate_sale_price)
        button_layout.addWidget(self.calculate_btn)
        layout.addLayout(button_layout)
        
        # Sonuçlar
        # Komisyon QLabel'ları
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        layout.addWidget(self.result_widget)
        
        self.commission_result = QLabel("Pazaryeri Komisyonu: ₺ 0,00")
        self.tax_result = QLabel("KDV: ₺ 0,00")
        self.sale_price = QLabel("Satış Fiyatı: ₺ 0,00")
        
        self.result_layout.addWidget(self.commission_result)
        self.result_layout.addWidget(self.tax_result)
        self.result_layout.addWidget(self.sale_price)
        
        # Doğrulayıcıları ekleyelim - sadece sayılara izin ver
        double_validator = QDoubleValidator()
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        for lineEdit in (self.purchase_entry, self.commission_entry, 
                         self.tax_entry, self.margin_entry):
            lineEdit.setValidator(double_validator)
            lineEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
            # Varsayılan değerler
            lineEdit.setText("0")
            
        # Birkaç varsayılan değer ekleyelim
        self.tax_entry.setText("18")  # Genel KDV oranı
        self.commission_entry.setText("10")  # Genel komisyon
        self.margin_entry.setText("20")  # Örnek kar marjı
        
        # Etiketleri sağa hizala
        for label in (self.purchase_label, self.commission_label, 
                      self.tax_label, self.margin_label):
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
        # Sonuç etiketlerini sağa hizala
        for result in (self.commission_result, self.tax_result, self.sale_price):
            result.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Enter tuşuyla hesaplama
        for entry in (self.purchase_entry, self.commission_entry, 
                      self.tax_entry, self.margin_entry):
            entry.returnPressed.connect(self.calculate_sale_price)
    
    def setup_excel_tab(self):
        layout = QVBoxLayout(self.tab_excel)
        
        # Excel dosyası yükleme düğmesi
        self.load_excel_btn = QPushButton("Excel Dosyası Yükle")
        self.load_excel_btn.clicked.connect(self.load_excel_file)
        layout.addWidget(self.load_excel_btn)
        
        # Yüklenen dosya bilgisi
        self.excel_info_label = QLabel("Dosya yüklenmedi")
        layout.addWidget(self.excel_info_label)
        
        # Varsayılan sütun isimleri için bilgi
        info_text = """
        Excel dosyası aşağıdaki sütunları içermelidir:
        - Ürün Adı (isteğe bağlı)
        - Alış Fiyatı (gerekli)
        - Komisyon (isteğe bağlı, varsayılan: %10)
        - KDV (isteğe bağlı, varsayılan: %18)
        - Kar (isteğe bağlı, varsayılan: %20)
        """
        self.column_info = QLabel(info_text)
        layout.addWidget(self.column_info)
        
        # İşlem düğmesi
        self.process_excel_btn = QPushButton("Excel Dosyasını İşle ve Sonuçları Kaydet")
        self.process_excel_btn.clicked.connect(self.process_excel_file)
        self.process_excel_btn.setEnabled(False)  # Başlangıçta devre dışı
        layout.addWidget(self.process_excel_btn)
        
        # Sonuç bilgisi
        self.excel_result_label = QLabel("")
        layout.addWidget(self.excel_result_label)
        
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
            default_tax = 18.0
            default_margin = 20.0
            
            # Yeni DataFrame oluştur
            result_df = self.excel_data.copy()
            
            # Her bir satır için hesaplamaları yap
            for index, row in result_df.iterrows():
                # Gerekli değerleri al, yoksa varsayılanları kullan
                purchase_price = row["Alış Fiyatı"]
                commission = row.get("Komisyon", default_commission)
                tax = row.get("KDV", default_tax)
                margin = row.get("Kar", default_margin)
                
                # Hesaplamalar
                commission_amount = purchase_price * commission / 100
                total_with_commission = purchase_price + commission_amount
                tax_amount = total_with_commission * tax / 100
                total_with_tax = total_with_commission + tax_amount
                sale_price = total_with_tax * (1 + margin / 100)
                
                # Sonuçları DataFrame'e ekle
                result_df.at[index, "Komisyon Tutarı"] = commission_amount
                result_df.at[index, "KDV Tutarı"] = tax_amount
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
                        if col_name in ["Alış Fiyatı", "Komisyon Tutarı", "KDV Tutarı", "Satış Fiyatı"]:
                            worksheet.set_column(col_idx, col_idx, 15, money_format)
                        elif col_name in ["Komisyon", "KDV", "Kar"]:
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
            tax = float(self.tax_entry.text().replace(',', '.'))
            margin = float(self.margin_entry.text().replace(',', '.'))
            
            # Eğer alış fiyatı 0 ise uyarı göster
            if purchase <= 0:
                QMessageBox.warning(self, "Hata", "Alış fiyatı 0'dan büyük olmalıdır.")
                self.purchase_entry.setFocus()
                return
            
            # Hesaplamalar
            commission_amount = purchase * commission / 100
            total_with_commission = purchase + commission_amount
            tax_amount = total_with_commission * tax / 100
            total_with_tax = total_with_commission + tax_amount
            sale_price = total_with_tax * (1 + margin / 100)
            
            # Türkiye'deki para formatı için virgül kullan
            def tr_fmt(val):
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.commission_result.setText(f"Pazaryeri Komisyonu: ₺ {tr_fmt(commission_amount)}")
            self.tax_result.setText(f"KDV: ₺ {tr_fmt(tax_amount)}")
            self.sale_price.setText(f"Satış Fiyatı: ₺ {tr_fmt(sale_price)}")
            
        except ValueError as e:
            QMessageBox.critical(self, "Hata", f"Hesaplama sırasında bir hata oluştu: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
