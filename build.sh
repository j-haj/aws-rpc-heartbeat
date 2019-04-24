#!/bin/bash

python3 -m grpc_tools.protoc -I./protos \
	--python_out=./python --grpc_python_out=./python \
	./protos/heartbeat.proto
