import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QHeaderView
from mydbutils import do_query

class EmployeesDialog(QDialog):
    '''
    The employees dialog
    '''
    
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('employees_dialog.ui')

        # Employees menu and query button event handlers.
        self.ui.employees_cb.currentIndexChanged.connect(self._initialize_table)
        self.ui.query_button.clicked.connect(self._enter_quaterly_sales_data)
        
        # Initialize the teacher menu and the salesrepemployee table.
        self._initialize_employees_menu()
        self._initialize_table()
        self.ui.monthly_radio.toggled.connect(self._initialize_table)
        self.ui.quarterly_radio.toggled.connect(self._initialize_table)
        
    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()
    
    def _initialize_employees_menu(self):
        """
        Initialize the salesrepemployee menu with names from the database.
        """
        sql = """
            SELECT firstName, lastName FROM pinnacle_wh.salesrepemployee
            ORDER BY firstName, lastName
            """
        rows, _ = do_query(sql)

        # Set the menu items to the teacher names.
        for row in rows:
            name = row[0] + ' ' + row[1]
            self.ui.employees_cb.addItem(name, row)     
            
    def _adjust_column_widths(self):
        """
        Adjust the column widths of the sales table to fit the contents.
        """
        header = self.ui.sales_table.horizontalHeader();
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
    def _initialize_table(self):
        """
        Clear the table and set the column headers.
        """
        self.ui.sales_table.clear()

        col_1 = ['  First Name  ', '  Last Name  ', '  Manager Name  ', '  Month  ',
        '  Year End  ', '  Revenue ($000) ']

        col_2 = ['  First Name  ', '  Last Name  ', '  Manager Name  ', '  Quater  ',
        '  Year End  ', '  Revenue ($000) ']

        if self.ui.monthly_radio.isChecked():
            col = col_1
        elif self.ui.quarterly_radio.isChecked():
            col = col_2
        self.ui.sales_table.setHorizontalHeaderLabels(col)        
        self._adjust_column_widths()
        
    def _enter_quaterly_sales_data(self):    
        """
        Enter monthly/quaterly sales data from the query into 
        the star schema and return quaterly sales per
        each employee.
        """    
        name = self.ui.employees_cb.currentData()
        first_name = name[0]
        last_name = name[1]

        sql_1 = ( """
            SELECT sa.firstName, sa.lastName, sa.managerName, ca.month, ca.year, sum(sh.quantityOrdered*sh.priceEach)
            FROM shippedorders sh
            JOIN salesrepemployee sa ON sa.employeeNumber = sh.salesRepEmployeeNumber
            JOIN calendar ca ON ca.calendar_key = sh.calendar_key
            WHERE sa.firstName = '""" + first_name + """'
            AND sa.lastName = '""" + last_name + """'
            GROUP BY sa.firstName, sa.lastName, sa.managerName, ca.month, ca.year
            ORDER BY sa.firstName, sa.lastName, ca.year, ca.month
            """ 
              )
        
        sql_2 = ( """
            SELECT sa.firstName, sa.lastName, sa.managerName, ca.qtr, ca.year, sum(sh.quantityOrdered*sh.priceEach)
            FROM shippedorders sh
            JOIN salesrepemployee sa ON sa.employeeNumber = sh.salesRepEmployeeNumber
            JOIN calendar ca ON ca.calendar_key = sh.calendar_key
            WHERE sa.firstName = '""" + first_name + """'
            AND sa.lastName = '""" + last_name + """'
            GROUP BY sa.firstName, sa.lastName, sa.managerName, ca.qtr, ca.year
            ORDER BY sa.firstName, sa.lastName, ca.year, ca.qtr
            """ 
              )

        if self.ui.monthly_radio.isChecked():
            sql = sql_1
        elif self.ui.quarterly_radio.isChecked():
            sql = sql_2
        
        rows, count = do_query(sql)
        
        # Set the sales data into the table cells.
        row_index = 0
        for row in rows:
            print(row)
            column_index = 0
            i = 0
            for data in row:
                string_item = str(data)
                if i == 5:
                    string_item = "${:,.2f}".format(data)
                item = QTableWidgetItem(string_item)
                self.ui.sales_table.setItem(row_index, column_index, item)
                column_index += 1
                i += 1

            row_index += 1
                
        self._adjust_column_widths()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = EmployeesDialog()
    form.show_dialog()
    sys.exit(app.exec_())        