FROM python:3.8.16
COPY . /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
EXPOSE 8099
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "8099"]
