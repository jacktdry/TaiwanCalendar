# 台灣行政機關辦公日曆爬蟲系統

![JSDelivr](https://data.jsdelivr.com/v1/package/gh/jacktdry/TaiwanCalendar/badge)

這是一個以Vibe Coding製作的自動化爬蟲系統，用於從台灣政府開放資料平台下載行政機關辦公日曆資料，並將CSV格式轉換為結構化的JSON格式。

## 資料來源

本系統從以下政府開放資料平台獲取資料：

- **資料集**：中華民國政府行政機關辦公日曆表
- **網址**：<https://data.gov.tw/dataset/14718>
- **維護機關**：行政院人事行政總處
- **資料內容**：包含國定假日、補假日及放假日等完整辦公日曆資訊

## 自動更新機制

本專案透過GitHub Actions實現自動化資料更新：

- **更新頻率**：每月自動執行一次
- **自動化流程**：系統會定期從政府開放資料平台爬取最新的日曆資料
- **資料保持最新**：確保使用者隨時可以取得最新的行政機關辦公日曆資訊

## JSON格式

轉換後的JSON資料格式如下：

```json
[
  {
    "date": "2017-01-01",
    "week": "日",
    "isHoliday": true,
    "description": "開國紀念日"
  },
  {
    "date": "2017-01-02",
    "week": "一",
    "isHoliday": true,
    "description": "補假"
  }
]
```

### 欄位說明

- `date`: ISO 8601格式的日期 (YYYY-MM-DD)
- `week`: 星期幾的中文表示
- `isHoliday`: 布林值，true表示放假，false表示上班
- `description`: 節日或特殊說明

## 資料取用連結

**CDN 連結** (需要替換年份):

<https://cdn.jsdelivr.net/gh/jacktdry/TaiwanCalendar/docs/{year}.json>

**2023 年度資料連結**:

<https://cdn.jsdelivr.net/gh/jacktdry/TaiwanCalendar/docs/2023.json>

## 本地部署使用方式

### 安裝相依套件

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 執行程式

```bash
# 執行完整流程（爬取 + 轉換）
python main.py

# 僅執行爬蟲
python crawler.py

# 僅執行轉換
python converter.py
```

### 使用說明

1. 執行後，原始CSV檔案會下載到 `origin/` 目錄
2. 轉換後的JSON檔案會儲存在 `docs/` 目錄
3. 系統會自動處理中文編碼和格式轉換
4. 支援批量處理多年份的日曆資料

## 參考來源

本專案在實作爬蟲功能時參考了以下開源專案的輸出格式：

- [TaiwanCalendar](https://github.com/ruyut/TaiwanCalendar)

## 授權

本專案採用 MIT 授權條款。
