#!/usr/bin/env bash

build_tag=ai_broker_copilot

# 停止运行的docker 服务
sudo docker rm -f $build_tag
# 生成容器
sudo docker build -t $build_tag ./ --network host -f Dockerfile

# 启动容器
sudo docker run \
-d \
--rm \
--name=$build_tag \
--env LC_ALL=C.UTF-8 \
--env LANG=C.UTF-8 \
--net=host \
-v `pwd`:/workspace \
$build_tag

echo "started container $build_tag"
