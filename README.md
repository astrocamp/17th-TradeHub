# TradeHub

### 技術使用

- 前端：Tailwindcss, DaisyUI, Alpine.js
- 後端：Python, Django
- 資料庫：PostgreSQL
- 版本控制：Git
- 電子信箱：tradehub17th@gmail.com
- 部署：AWS EC2/RDS

### TradeHub Team

陳俊道
https://github.com/toshi0809

康珮萱
https://github.com/KangPeiHsuan

賴奕浤
https://github.com/Roger-0227

陳政杰
https://github.com/jaychen1007

劉哲明
https://github.com/Liu-Che-Ming

### 安裝步驟

1. `poetry shell` 建虛擬環境
2. `poetry install` 下載 相應套件
3. `npm install` 下載 前端 相應套件
4. 使用`.env.example` 建立`.env`檔

### 執行檔案

1. `npm run dev` 執行 esbuild 和 tailwind
2. Win: `python manage.py runserver` Mac: `make server` 開啟伺服器

### Git 上傳前操作

1. Win: `pre-commit run --all-files` Mac: `make lint`
2. git add
3. Win: `cz commit` Mac: `make commit`
