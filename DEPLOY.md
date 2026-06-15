# คู่มือ Deploy TVHUB ด้วย Docker `.tar`

คู่มือนี้ใช้สำหรับนำ image ที่ build แล้วจากเครื่อง dev ไปขึ้น server ด้วยไฟล์ `tvhub-online_2026-06-15.tar`

## ไฟล์ที่ต้องอัปขึ้น server

ให้อัปไฟล์เหล่านี้ไปไว้ในโฟลเดอร์เดียวกันบน server:

```bash
tvhub-online_2026-06-15.tar
deploy_server.sh
.env.production.example
```

ตัวอย่างโฟลเดอร์บน server:

```bash
/opt/tvhub
```

## สิ่งที่ server ต้องมี

ติดตั้ง Docker ให้พร้อมก่อน:

```bash
docker --version
```

ถ้ายังไม่มี Docker ให้ติดตั้งก่อน แล้วตรวจว่า service ทำงานอยู่:

```bash
sudo systemctl status docker
```

## ขั้นตอน Deploy ครั้งแรก

เข้าโฟลเดอร์ที่อัปไฟล์ไว้:

```bash
cd /opt/tvhub
```

สร้างไฟล์ environment จริงจากตัวอย่าง:

```bash
cp .env.production.example .env.production
nano .env.production
```

แก้ค่าใน `.env.production` ให้ตรงกับ server จริง:

```env
FLASK_SECRET_KEY=change-this-secret
ADMIN_PASSWORD=change-this-admin-password
SITE_NAME=TVHUB.ONLINE
BASE_URL=https://tvhub.online
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=tvhub
DB_PASS=change-this-db-password
DB_NAME=tvhub
GEMINI_API_KEY=
```

หมายเหตุ:

- `FLASK_SECRET_KEY` ควรเป็นข้อความสุ่มยาว ๆ
- `ADMIN_PASSWORD` คือรหัสผ่านหน้า admin
- `BASE_URL` ต้องเป็น domain จริง เช่น `https://tvhub.online`
- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME` ต้องตรงกับฐานข้อมูลบน server

ให้สิทธิ์รันสคริปต์:

```bash
chmod +x deploy_server.sh
```

รัน deploy:

```bash
./deploy_server.sh tvhub-online_2026-06-15.tar
```

ถ้าสำเร็จจะเห็นประมาณนี้:

```bash
Deploy complete: http://127.0.0.1:5000/
```

## ตรวจสอบหลัง Deploy

เช็ก container:

```bash
docker ps
```

ดู log:

```bash
docker logs -f tvhub-online
```

ทดสอบหน้าเว็บจาก server:

```bash
curl -I http://127.0.0.1:5000/
curl -I http://127.0.0.1:5000/live/ch3
curl http://127.0.0.1:5000/robots.txt
```

ควรได้ HTTP `200` สำหรับหน้าเว็บหลัก

## คำสั่งดูแลระบบ

หยุดเว็บ:

```bash
docker stop tvhub-online
```

เปิดเว็บใหม่:

```bash
docker start tvhub-online
```

restart:

```bash
docker restart tvhub-online
```

ลบ container:

```bash
docker rm -f tvhub-online
```

ดู image:

```bash
docker images tvhub-online
```

## Deploy เวอร์ชันใหม่

เมื่อมีไฟล์ `.tar` เวอร์ชันใหม่ ให้อัปไฟล์ใหม่ไปแทน แล้วรัน:

```bash
./deploy_server.sh tvhub-online_2026-06-15.tar
```

สคริปต์จะทำงานให้เอง:

- `docker load` image จาก `.tar`
- หยุดและลบ container เก่า
- start container ใหม่
- เช็กว่าเว็บตอบกลับได้

## ใช้ Port อื่น

ค่าเริ่มต้นคือเปิดเว็บที่ port `5000`

ถ้าต้องการใช้ port อื่น เช่น `8080`:

```bash
HOST_PORT=8080 ./deploy_server.sh tvhub-online_2026-06-15.tar
```

แล้วเข้าเว็บผ่าน:

```bash
http://SERVER_IP:8080/
```

## ใช้ไฟล์ env ชื่ออื่น

ค่าเริ่มต้นคือ `.env.production`

ถ้าต้องการใช้ไฟล์อื่น:

```bash
ENV_FILE=.env.server HOST_PORT=5000 ./deploy_server.sh tvhub-online_2026-06-15.tar
```

## ตั้ง Reverse Proxy ด้วย Nginx

ตัวอย่าง config:

```nginx
server {
    listen 80;
    server_name tvhub.online www.tvhub.online;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

หลังแก้ config:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

ถ้าใช้ HTTPS ให้ตั้ง Certbot/SSL เพิ่มบน Nginx

## ตรวจสอบ SEO หลังขึ้นจริง

หลัง domain ใช้งานได้ ให้เช็ก:

```bash
curl https://tvhub.online/robots.txt
curl https://tvhub.online/sitemap.xml
curl -I https://tvhub.online/live/ch3
```

จากนั้นนำ sitemap ไป submit ใน Google Search Console:

```text
https://tvhub.online/sitemap.xml
```

## ปัญหาที่พบบ่อย

ถ้าเว็บไม่ขึ้น:

```bash
docker logs --tail 100 tvhub-online
```

ถ้า port ชน:

```bash
sudo lsof -i :5000
```

หรือ deploy ด้วย port อื่น:

```bash
HOST_PORT=8080 ./deploy_server.sh tvhub-online_2026-06-15.tar
```

ถ้าต่อฐานข้อมูลไม่ได้ ให้ตรวจค่าใน `.env.production`:

```bash
cat .env.production
```

และตรวจว่า MySQL/MariaDB เปิดรับ connection จาก container ได้

## Checksum ไฟล์ tar

ไฟล์ build ปัจจุบัน:

```text
tvhub-online_2026-06-15.tar
```

SHA256:

```text
2702041830C347DAE87D8613D6A81699D7B5A798789B3AE2A0FCA44679454650
```

ตรวจบน server:

```bash
sha256sum tvhub-online_2026-06-15.tar
```
