FROM python:3.13-slim

# 工作目錄，接下來工作的地方
WORKDIR /app

# 把全部都丟進去裡面
COPY ./requirements.txt /app/requirements.txt

# 是先設定好command，讓我在build時，就會自動幫我安裝所有需要的套件
# 連cache都不要
# The --no-cache-dir option tells pip to not save the downloaded packages locally, as that is only if pip was going to be run again to install the same packages, but that's not the case when working with containers.
# The file with the package requirements won't change frequently. So, by copying only that file, Docker will be able to use the cache for that step. And then, Docker will be able to use the cache for the next step that downloads and install those dependencies.
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# 做一個通道讓外面可以用到
# Documents which port the container uses, for documentations purposes
EXPOSE 8000

# 一啟動這個image就做什麼事情
# listen on port 8000 in the container
# main:app, main is main.py and app is the variable assigned to FastApi() in main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]