from fpdf import FPDF
import os
import tempfile
from config import Config

class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('DejaVu', '', Config.FONT_PATH, uni=True)
        self.set_font('DejaVu', '', 10)

def generate_payorder_pdf(bill_data):
    pdf = UnicodePDF()
    pdf.add_page()
    
    # [PDF generation implementation...]
    
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"PayOrder_{bill_data['bill_no']}.pdf")
    pdf.output(filename, 'F')
    return filename
