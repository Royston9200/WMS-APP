# WMS-APP

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**A simple Warehouse Management System (WMS) web application featuring:**

-  User management with MySQL
-  QR and barcode generation
-  Role-based access and session handling
-  Admin functionality to manage users

---

##  Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Royston9200/WMS-APP.git
   cd WMS-APP


pip install -r requirements.txt

**SET UP .env FILE:**

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=wms_db
SECRET_KEY=your_secret_key


**RUN THE APP**

python app.py


**ROLES**

*Role*	*Access*

Admin	Full access incl. user management
User	Limited access (home, scan, etc.)

**Test account setup (optional)**

INSERT INTO users (username, password, role)
VALUES ('admin', '<hashed_password>', 'admin');

**EXTRAS:**
Want a section with screenshots, an API overview, or a setup video? Let me know and I’ll add it!

**READY TO PUSH**  
IN TERMINAL (PowerShell or Git Bash):

```bash
git add README.md
git commit -m "Updated README with installation and setup"
git push

