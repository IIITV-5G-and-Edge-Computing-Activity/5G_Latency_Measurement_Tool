.PHONY: proto
proto:
	python3 -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. ./protos/experiments5G/communication/grpc/grpc.proto

.PHONY: docker_build
docker_build:
	docker build -t experiments5g:latest -f Dockerfile .

.PHONY: docker_run
docker_run:
	docker run --rm \
				-it \
				-v $(CURDIR):/code \
				experiments:latest 

.PHONY: test
test:
	python3 tests/logger_tests.py
	python3 tests/interface_tests.py
