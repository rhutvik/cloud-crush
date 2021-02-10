all: gateway kvs compose

gateway:
	docker build -t api-gateway ./api-gateway

kvs:
	docker build -t kvs ./kvs

up:
	COMPOSE_HTTP_TIMEOUT=200 docker-compose --verbose up --scale gateway=2 --scale kvs=5

down:
	docker-compose down

start:
	docker-compose start

stop:
	docker-compose stop

logs:
	docker-compose logs -f
