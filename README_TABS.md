# การแยก Tab ออกเป็นไฟล์แยก - TVHUB

## โครงสร้างไฟล์ใหม่

ได้แยก tab ต่างๆ ออกจากไฟล์ `homepage.html` เป็นไฟล์แยกใน folder `templates/tabs/` เพื่อความง่ายในการจัดการ

### ไฟล์หลัก

- `homepage_new.html` - ไฟล์หลักใหม่ที่ใช้ include แทนการเขียนทุกอย่างในไฟล์เดียว
- `homepage.html` - ไฟล์เดิม (backup)

### โฟลเดอร์ `templates/tabs/`

#### ไฟล์ Navigation

- `category_navigation.html` - Navigation bar สำหรับหมวดหมู่ต่างๆ (หนังสือพิมพ์, บันเทิง, วาไรตี้, ฯลฯ)
- `tv_navigation.html` - Navigation bar สำหรับช่องทีวี (ทีวีไทย, ทีวีต่างประเทศ, กีฬา, การ์ตูน)

#### ไฟล์ Content Container

- `category_content.html` - รวม include ของ tab หมวดหมู่ทั้งหมด
- `tv_content.html` - รวม include ของ tab ทีวีทั้งหมด

#### ไฟล์ Tab แยกตามหมวดหมู่

1. **หนังสือพิมพ์** - `news_tab.html`
2. **บันเทิง** - `entertainment_tab.html`
3. **วาไรตี้** - `variety_tab.html`
4. **กีฬา** - `sports_tab.html`
5. **เด็ก** - `kids_tab.html`
6. **เพลง** - `music_tab.html`
7. **วิทยุ** - `radio_tab.html`
8. **ตรวจหวย** - `lottery_tab.html`
9. **เช็คพัสดุ** - `parcel_tab.html`
10. **ไลฟ์สไตล์** - `lifestyle_tab.html`

#### ไฟล์ Tab ทีวี

11. **ทีวีไทย** - `thai_tv_tab.html`
12. **ทีวีต่างประเทศ** - `international_tv_tab.html`
13. **ทีวีกีฬา** - `sports_tv_tab.html`
14. **ทีวีการ์ตูน** - `cartoon_tv_tab.html`

## วิธีการใช้งาน

### แทนที่ไฟล์เดิม

```bash
# สำรองไฟล์เดิม
mv homepage.html homepage_old.html

# ใช้ไฟล์ใหม่
mv homepage_new.html homepage.html
```

### การแก้ไข Content

**แก้ไขลิงก์หนังสือพิมพ์:**

```bash
# แก้ไขไฟล์
nano templates/tabs/news_tab.html
```

**เพิ่มช่องทีวีไทยใหม่:**

```bash
# แก้ไขไฟล์
nano templates/tabs/thai_tv_tab.html
```

**แก้ไขลิงก์กีฬา:**

```bash
# แก้ไขไฟล์
nano templates/tabs/sports_tab.html
```

## ข้อดีของการแยกไฟล์

### 1. **ง่ายต่อการจัดการ**

- แก้ไขเฉพาะส่วนที่ต้องการโดยไม่ต้องหาในไฟล์ใหญ่
- ลดความผิดพลาดในการแก้ไข

### 2. **การทำงานเป็นทีม**

- หลายคนแก้ไขไฟล์ต่างกันได้พร้อมกัน
- ลด conflict ใน Git

### 3. **การบำรุงรักษา**

- Code สะอาดและอ่านง่าย
- Debug ง่ายขึ้น

### 4. **การนำกลับมาใช้ใหม่ (Reusability)**

- สามารถนำ tab ไปใช้ในหน้าอื่นได้
- ใช้ซ้ำในส่วนต่างๆ ของเว็บไซต์

## ตัวอย่างการแก้ไข

### เพิ่มหนังสือพิมพ์ใหม่

แก้ไขไฟล์ `templates/tabs/news_tab.html`:

```html
<a
  class="btn btn-outline-danger"
  href="https://www.example.com/"
  type="button"
  target="_blank"
>
  <i class="bi bi-newspaper me-1"></i>หนังสือพิมพ์ใหม่
</a>
```

### เพิ่มช่องทีวีใหม่

แก้ไขไฟล์ `templates/tabs/thai_tv_tab.html`:

```html
<div class="col">
  <div class="card h-100 shadow-sm text-center">
    <img
      src="/static/img/new-channel.png"
      class="card-img-top p-3"
      alt="ช่องใหม่"
      style="height: 80px; object-fit: contain;"
    />
    <div class="card-body">
      <h6 class="card-title">ช่องใหม่</h6>
      <p>Official</p>
      <a
        href="https://www.new-channel.com/live"
        target="_blank"
        class="btn btn-outline-primary btn-sm"
      >
        <i class="bi bi-play-fill me-1"></i>ดูสด
      </a>
    </div>
  </div>
</div>
```

## การ Backup และ Restore

### Backup

```bash
# สำรองโฟลเดอร์ tabs ทั้งหมด
cp -r templates/tabs/ templates/tabs_backup/
```

### Restore

```bash
# คืนค่าจาก backup
rm -rf templates/tabs/
cp -r templates/tabs_backup/ templates/tabs/
```

## หมายเหตุ

- ไฟล์ทั้งหมดใช้ Jinja2 template syntax ของ Flask
- ใช้ Bootstrap 5.3 สำหรับ CSS Framework
- ใช้ Bootstrap Icons สำหรับไอคอน
- รองรับ responsive design สำหรับมือถือ
