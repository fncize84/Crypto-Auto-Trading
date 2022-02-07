import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 

def send_final():
	sendEmail = "fncize@gmail.com"
	recvEmail = "fncize@gmail.com"
	password = "pw"
	smtpName = "smtp.gmail.com"
	smtpPort = 587

	msg = MIMEMultipart()

	msg['Subject'] ="Weekly Trading Record"
	msg['From'] = sendEmail 
	msg['To'] = recvEmail 

	text = "첨부."
	contentPart = MIMEText(text) #MIMEText(text , _charset = "utf8")
	msg.attach(contentPart) 

	etcFileName = 'trading_record.xlsx'
	with open(etcFileName, 'rb') as etcFD : 
	    etcPart = MIMEApplication( etcFD.read() )
	    etcPart.add_header('Content-Disposition','attachment', filename=etcFileName)
	    msg.attach(etcPart) 
    
	s=smtplib.SMTP( smtpName , smtpPort )
	s.starttls()
	s.login( sendEmail , password ) 
	s.sendmail( sendEmail, recvEmail, msg.as_string() )  
	s.close()

send_final()






