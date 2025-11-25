FROM python:3.13-slim

# 工作目錄，接下來工作的地方
WORKDIR /app

# 把全部都丟進去裡面
COPY requirements.txt .

# 是先設定好command，讓我在build時，就會自動幫我安裝所有需要的套件
# 連cache都不要
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# 做一個通道讓外面可以用到
EXPOSE 8000

# 一啟動這個image就做什麼事情
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]