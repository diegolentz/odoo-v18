# odoo-v18
customizando odoo

levantar docker
docker compose up -d

si no tiene volúmenes, docker compose up -d + este comando
docker exec -it odoo odoo -d odoo -i base --stop-after-init

reset odoo
docker restart odoo

reset modulo + odoo
docker exec -it odoo odoo -d odoo -u custom_crm --stop-after-init
docker restart odoo

scafold
docker exec -it odoo odoo scaffold custom_crm /mnt/extra-addons

lenguaje
docker exec -it odoo odoo -d odoo --load-language=es_AR

documentación odoo
https://www.odoo.com/documentation/18.0/es_419/index.html







docker compose exec odoo odoo -u legos18 -d odoo --stop-after-init


cambio de labels
docker compose exec odoo odoo -u legos18 -d odoo --stop-after-init 2>&1 | Select-String "legos18|ERROR"


