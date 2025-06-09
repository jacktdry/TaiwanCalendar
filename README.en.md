# Taiwan Government Office Calendar Crawler System

[![jsDelivr Package](https://data.jsdelivr.com/v1/package/gh/jacktdry/TaiwanCalendar/badge)](https://www.jsdelivr.com/package/gh/jacktdry/TaiwanCalendar)

English Version | [中文版](./README.md)

This is an automated crawler system developed by Vibe Coding for downloading the official government office calendar data from the Taiwan Government Open Data Platform and converting CSV files into structured JSON format.

## Data Source

- **Dataset**: Taiwan Government Office Calendar
- **URL**: <https://data.gov.tw/dataset/14718>
- **Maintainer**: Directorate-General of Personnel Administration, Executive Yuan
- **Content**: Complete calendar information including national holidays, make-up workdays, and days off

## Auto Update Mechanism

- **Update Frequency**: Monthly
- **Automation**: The system periodically crawls the latest calendar data from the open data platform
- **Always Up-to-date**: Ensures users always get the latest government office calendar

## JSON Format

Example:

```json
[
  {
    "date": "2017-01-01",
    "week": "Sun",
    "isHoliday": true,
    "description": "Founding Day"
  },
  {
    "date": "2017-01-02",
    "week": "Mon",
    "isHoliday": true,
    "description": "Make-up Holiday"
  }
]
```

### Fields

- `date`: Date in ISO 8601 format (YYYY-MM-DD)
- `week`: Day of the week in Chinese
- `isHoliday`: Boolean, true for holiday, false for workday
- `description`: Holiday or special note

## Data Access Links

**CDN Link** (replace {year}):
<https://cdn.jsdelivr.net/gh/jacktdry/TaiwanCalendar/docs/{year}.json>

**2023 Data**:
<https://cdn.jsdelivr.net/gh/jacktdry/TaiwanCalendar/docs/2023.json>

## Local Deployment

### Install dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Full process (crawl + convert)
python main.py

# Only crawl
python crawler.py

# Only convert
python converter.py
```

### Usage

1. The original CSV files will be downloaded to the `origin/` directory.
2. Converted JSON files will be saved in the `docs/` directory.
3. The system automatically handles Chinese encoding and format conversion.
4. Supports batch processing for multiple years.

## Reference

This project refers to the output format of the following open-source project:

- [TaiwanCalendar](https://github.com/ruyut/TaiwanCalendar)

## License

The source code of this project is licensed under the MIT License. The data content is provided under the [Government Open Data License, Version 1.0](https://data.gov.tw/license). See [LICENSE.en](./LICENSE.en) and [中文版 LICENSE](./LICENSE) for details.

- Source code: Free to use, copy, modify, and distribute under the MIT License.
- Data: Free to use, adapt, reproduce, and distribute, with attribution and no distortion, under the Government Open Data License.
- Both are subject to applicable laws and provided without any express or implied warranties.
