mkdir logs logs/db logs/django logs/ldap_go logs/nginx 
docker-compose -f docker-compose.yml down -v
docker-compose -f docker-compose.yml up -d --build
docker-compose -f docker-compose.yml exec djangoapp python ./manage.py migrate
docker-compose -f docker-compose.yml exec djangoapp python /code/manage.py docker_init x x