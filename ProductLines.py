import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QHeaderView
from mydbutils import do_query

class ProductLinesDialog(QDialog):
    """
    The product lines dialog.
    """
    
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('productLines_dialog.ui')

        ### PER PRODUCT LINE
        # Product lines menu and query button event handlers.
        self.ui.product_lines_cb.currentIndexChanged.connect(self._initialize_table)
        self.ui.query_button.clicked.connect(self._enter_product_lines_data)
        
        # Initialize the product lines menu and the sales table.
        self._initialize_product_lines_menu()
        self._initialize_table()
        self.ui.monthly_radio.toggled.connect(self._initialize_table)
        self.ui.quarterly_radio.toggled.connect(self._initialize_table)

        ### PER LOCATION
        # Location menu and query button event handlers.
        # When the country is changed, initialize the city menu again
        self.ui.country_cb.currentIndexChanged.connect(self._initialize_city_menu)
        self.ui.query_button_location.clicked.connect(self._enter_product_lines_data_location)

        # Initialize the location menu and sales table.
        self._initialize_country_menu()
        self._initialize_table_location()
        self.ui.monthly_radio_location.toggled.connect(self._initialize_table_location)
        self.ui.quarterly_radio_location.toggled.connect(self._initialize_table_location)
        self.ui.country_cb.currentIndexChanged.connect(self._initialize_table_location)
        self.ui.city_cb.currentIndexChanged.connect(self._initialize_table_location)
        
    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()
    
    def _initialize_product_lines_menu(self):
        """
        Initialize the product lines menu with product lines from the database.
        """
        sql = """
            SELECT productLineName FROM productline
            """
        rows, _ = do_query(sql)

        # Set the menu items to the teacher names.
        for row in rows:
            name = row[0]
            self.ui.product_lines_cb.addItem(name, row)
    
    def _initialize_country_menu(self):
        """
        Initialize the country menu of clients' location from the database.
        """
        sql = """
            SELECT distinct country FROM customers
            ORDER BY country
            """
        rows_country, _ = do_query(sql)

        # Set the menu items to the country
        for row in rows_country:
            c = row[0]
            self.ui.country_cb.addItem(c, row)

    def _initialize_city_menu(self):
        """
        Initialize the city menu of clients' location from the database.
        """
        self.ui.city_cb.clear()
        country = self.ui.country_cb.currentData()
        _country = country[0]
        sql = """
            SELECT distinct city FROM customers
            WHERE country = '""" + _country + """' ORDER BY city
            """ 
        
        rows_city, _ = do_query(sql)

        # Set the menu items to the city by selected country
        for row in rows_city:
            c = row[0]
            self.ui.city_cb.addItem(c, row)
            
    def _adjust_column_widths(self):
        """
        Adjust the column widths of the student table to fit the contents.
        """
        header = self.ui.sales_table.horizontalHeader();
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

    def _adjust_column_widths_location(self):
        """
        Adjust the column widths of the sales table per location
        to fit the contents.
        """
        header = self.ui.sales_table_location.horizontalHeader();
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        
    def _initialize_table(self):
        """
        Clear the table and set the column headers.
        """
        self.ui.sales_table.clear()

        col_1 = ['  Product Line  ', '  Month  ', '  Year End  ', '  Quantity  ',
        '  Average Price Each ($000)  ', '  Total Sales ($000) ']

        col_2 = ['  Product Line  ', '  Quarter  ', '  Year End  ', '  Quantity  ',
        '  Average Price Each ($000)  ', '  Total Sales ($000) ']

        if self.ui.monthly_radio.isChecked():
            col = col_1
        elif self.ui.quarterly_radio.isChecked():
            col = col_2

        self.ui.sales_table.setHorizontalHeaderLabels(col)        
        self._adjust_column_widths()

    def _initialize_table_location(self):
        """
        Clear the table and set the column headers.
        """
        self.ui.sales_table_location.clear()

        col_1 = [' Country ', ' City ', ' Product Line ', ' Month ', ' Year End ', ' Quantity ',
        'Average Price Each ($000)', 'Total Sales ($000)']

        col_2 = [' Country ', ' City ', ' Product Line ', ' Quarter ', ' Year End ', ' Quantity ',
        'Average Price Each ($000)', 'Total Sales ($000)']

        if self.ui.monthly_radio_location.isChecked():
            col = col_1
        elif self.ui.quarterly_radio_location.isChecked():
            col = col_2
        self.ui.sales_table_location.setHorizontalHeaderLabels(col)        
        self._adjust_column_widths_location()
        
    def _enter_product_lines_data(self):    
        """
        Enter monthly/quaterly sales data from the query into 
        the star schema and return quaterly sales per
        each product line.
        """    
        product_lines = self.ui.product_lines_cb.currentData()
        product_line = product_lines[0]
        
        sql_1 = ( """
            SELECT pl.productLineName, ca.month, ca.year, sum(sh.quantityOrdered), ROUND(avg(sh.priceEach), 2), sum(sh.quantityOrdered*sh.priceEach)
            FROM pinnacle_wh.shippedorders sh
            JOIN pinnacle_wh.productline pl ON pl.productLineID = sh.productLineID
            JOIN pinnacle_wh.calendar ca ON ca.calendar_key = sh.calendar_key
            WHERE pl.productLineName = '""" + product_line + """' 
            GROUP BY pl.productLineName, ca.month, ca.year
            ORDER BY pl.productLineName, ca.year, ca.month
            """ 
              )
        
        sql_2 = ( """
            SELECT pl.productLineName, ca.qtr, ca.year, sum(sh.quantityOrdered), ROUND(avg(sh.priceEach), 2), sum(sh.quantityOrdered*sh.priceEach)
            FROM pinnacle_wh.shippedorders sh
            JOIN pinnacle_wh.productline pl ON pl.productLineID = sh.productLineID
            JOIN pinnacle_wh.calendar ca ON ca.calendar_key = sh.calendar_key
            WHERE pl.productLineName = '""" + product_line + """' 
            GROUP BY pl.productLineName, ca.qtr, ca.year
            ORDER BY pl.productLineName, ca.year, ca.qtr
            """ 
              )

        if self.ui.monthly_radio.isChecked():
            sql = sql_1
        elif self.ui.quarterly_radio.isChecked():
            sql = sql_2              
        rows, _ = do_query(sql)
        
        # Set the student data into the table cells.
        print(rows)
        row_index = 0
        for row in rows:
            column_index = 0
            i = 0
            for data in row:
                string_item = str(data)
                if i >= 4:
                    string_item = "${:,.2f}".format(data)
                item = QTableWidgetItem(string_item)
                self.ui.sales_table.setItem(row_index, column_index, item)
                column_index += 1
                i += 1

            row_index += 1
                
        self._adjust_column_widths()

    def _enter_product_lines_data_location(self):    
        """
        Enter monthly/quaterly sales data from the query into 
        the star schema and return quaterly sales per
        each product line with selected location of clients.
        """    
        country = self.ui.country_cb.currentData()
        _country = country[0]

        city = self.ui.city_cb.currentData()
        _city = city[0]
        
        sql_1 = ( """
            SELECT cu.country, cu.city, pl.productLineName, ca.month, ca.year, sum(sh.quantityOrdered), ROUND(avg(sh.priceEach), 2), sum(sh.quantityOrdered*sh.priceEach)
            FROM pinnacle_wh.shippedorders sh
            JOIN pinnacle_wh.productline pl ON pl.productLineID = sh.productLineID
            JOIN pinnacle_wh.calendar ca ON ca.calendar_key = sh.calendar_key
            JOIN customers cu on cu.customerNumber = sh.customerNumber
            WHERE cu.country = '""" + _country + """' 
            AND cu.city = '""" + _city + """' 
            GROUP BY pl.productLineName, ca.month, ca.year
            ORDER BY pl.productLineName, ca.year, ca.month
            """ 
              )
        
        sql_2 = ( """
            SELECT cu.country, cu.city, pl.productLineName, ca.qtr, ca.year, sum(sh.quantityOrdered), ROUND(avg(sh.priceEach), 2), sum(sh.quantityOrdered*sh.priceEach)
            FROM pinnacle_wh.shippedorders sh
            JOIN pinnacle_wh.productline pl ON pl.productLineID = sh.productLineID
            JOIN pinnacle_wh.calendar ca ON ca.calendar_key = sh.calendar_key
            JOIN customers cu on cu.customerNumber = sh.customerNumber
            WHERE cu.country = '""" + _country + """' 
            AND cu.city = '""" + _city + """' 
            GROUP BY pl.productLineName, ca.qtr, ca.year
            ORDER BY pl.productLineName, ca.year, ca.qtr
            """ 
              )

        if self.ui.monthly_radio_location.isChecked():
            sql = sql_1
        elif self.ui.quarterly_radio_location.isChecked():
            sql = sql_2              
        rows, _ = do_query(sql)
        
        # Set the student data into the table cells.
        print(rows)
        row_index = 0
        for row in rows:
            column_index = 0
            i = 0
            for data in row:
                string_item = str(data)
                if i >= 6:
                    string_item = "${:,.2f}".format(data)
                item = QTableWidgetItem(string_item)
                self.ui.sales_table_location.setItem(row_index, column_index, item)
                column_index += 1
                i += 1

            row_index += 1
                
        self._adjust_column_widths_location()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ProductLinesDialog()
    form.show_dialog()
    sys.exit(app.exec_())