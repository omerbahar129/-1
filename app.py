from flask import Flask, request, jsonify
from fpdf import FPDF
import tempfile
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

def create_pdf(data):
    annual_revenue = float(data['annual_revenue'])
    net_profit = float(data['net_profit'])
    return_rate = float(data['return_rate'])
    roi_years = float(data['roi_years'])
    system_size = float(data['system_size'])
    purchase_price = float(data['purchase_price'])
    total_25_years = annual_revenue * 25

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "דו"ח תשואה למערכת סולארית - HORIZON", 0, 1, 'C')
    pdf.ln(10)

    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"📊 גודל מערכת: {system_size} קילוואט", 0, 1, 'R')
    pdf.cell(0, 8, f"💰 עלות מערכת: {purchase_price:,.2f} ₪", 0, 1, 'R')
    pdf.cell(0, 8, f"📈 רווח שנתי נטו משוער: {net_profit:,.2f} ₪", 0, 1, 'R')
    pdf.cell(0, 8, f"📉 תשואה שנתית: {return_rate:.2f}%", 0, 1, 'R')
    pdf.cell(0, 8, f"⏳ החזר השקעה: {roi_years:.1f} שנים", 0, 1, 'R')
    pdf.cell(0, 8, f"💼 רווח מצטבר ל-25 שנים: {total_25_years:,.2f} ₪", 0, 1, 'R')

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

def send_email(to_email, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = 'הדו"ח שלך ממחשבון התשואה הסולארית'
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = to_email
    msg.set_content("המצורף הוא דו"ח התשואה שלך. תודה שבחרת ב-HORIZON!")

    with open(pdf_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="solar_report.pdf")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        smtp.send_message(msg)

@app.route('/api/send-report', methods=['POST'])
def send_report():
    data = request.json
    try:
        pdf_path = create_pdf(data)
        send_email(data['email'], pdf_path)
        os.remove(pdf_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))