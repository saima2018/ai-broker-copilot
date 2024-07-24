#FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
FROM python:3.9

# apt 相关库
RUN apt update
RUN apt install -y python3 python3-pip wget git vim

# 安装python库
RUN pip install --upgrade pip
WORKDIR /workspace
ADD requirements.txt ./
RUN pip install -r requirements.txt

# 东八区问题
ENV TZ=Asia/Shanghai
COPY zoneinfo /usr/share/zoneinfo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 80 port
EXPOSE 80 8867 10242
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# add project folder
ADD ./ /workspace/

WORKDIR /workspace

# docker启动运行默认命令
CMD ["python3", "app.py"]
