# app.py
import os
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from datetime import datetime, date, timedelta
from collections import Counter

# 導入您現有的新聞抓取邏輯
from multithread_fetcher import fetch_rss_news

# --- Flask App 設定 ---

# 建立一個靜態資料夾來存放前端檔案
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="/static")


# --- API 路由 ---


@app.route("/api/news", methods=["GET"])
def get_news():
    """
    提供新聞資料的 API 端點
    接收 GET 參數: keyword, days, logic
    """
    try:
        # 1. 從請求中獲取參數
        keyword = request.args.get("keyword", "台灣")
        logic = request.args.get("logic", "OR")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        # 2. 設定日期範圍
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:  # 如果沒有提供日期，則使用預設的最近7天
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

        # 3. 呼叫抓取函式
        news_list = fetch_rss_news(keyword, start_date, end_date, logic)

        # 4. 產生來源統計資料
        stats = {}
        if news_list:
            source_counts = Counter(item["來源"] for item in news_list)
            # 將 Counter 物件轉換為按數量降序排列的字典
            stats = dict(source_counts.most_common())

        # 5. 回傳 JSON 格式的結果
        return jsonify(
            {
                "success": True,
                "count": len(news_list),
                "data": news_list,
                "stats": stats,
            }
        )

    except Exception as e:
        print(f"API 錯誤: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# --- 前端頁面路由 ---


@app.route("/")
def index():
    """
    提供主頁面 (index.html)
    """
    # 直接提供靜態的 index.html 檔案，而不是將其作為 Jinja2 樣板渲染
    return send_from_directory(FRONTEND_FOLDER, "index.html")


# --- 主程式執行 ---

if __name__ == "__main__":
    print(f"啟動伺服器，請在瀏覽器打開 http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
