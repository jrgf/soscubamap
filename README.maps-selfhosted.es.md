# Mapa Self-Hosted (OSM) - Guia Rapida

Este documento explica como levantar un servidor de mapas self-hosted para `soscubamap` usando `docker-compose.maps.yml`.

## Objetivo

Montar un servidor de tiles OpenStreetMap local para no depender del tile server publico.

## Archivos relevantes

- `docker-compose.maps.yml`
- `data/maps/`

## Requisitos

- Docker y Docker Compose instalados
- Espacio en disco suficiente (varios GB, depende del PBF)
- Un archivo `.osm.pbf` de la zona que quieres servir

## Estructura esperada

Coloca el archivo PBF dentro de:

```text
./data/maps/
```

Ejemplo:

```text
./data/maps/cuba-latest.osm.pbf
```

## 1) Validar el compose de mapas

```bash
docker compose -f docker-compose.maps.yml config
```

Si no hay errores, la configuracion es valida.

## 2) Importar datos OSM (solo primera vez o cuando cambie el PBF)

Ejecuta el import con el profile `maps-import`:

```bash
docker compose -f docker-compose.maps.yml --profile maps-import run --rm maps-import
```

Notas:

- Este paso puede tardar bastante.
- Si vuelves a importar, reutilizara el volumen `osm-db-data` a menos que lo elimines.

## 3) Levantar el servidor de tiles

```bash
docker compose -f docker-compose.maps.yml up -d maps
```

El servicio queda publicado en:

- `http://localhost:8081`

## 4) Probar que responde

Abre en navegador (o usa curl):

```text
http://localhost:8081/tile/0/0/0.png
```

Si devuelve una imagen, el servidor esta activo.

## 5) Levantar junto con la app principal

Si quieres correr app + mapas:

```bash
docker compose -f docker-compose.yml -f docker-compose.maps.yml up -d
```

## 6) Parar servicios

Solo mapas:

```bash
docker compose -f docker-compose.maps.yml down
```

App + mapas:

```bash
docker compose -f docker-compose.yml -f docker-compose.maps.yml down
```

## 7) Reinicio limpio de datos de mapas (opcional)

Si necesitas reiniciar la base de tiles:

```bash
docker compose -f docker-compose.maps.yml down -v
```

Luego vuelve a ejecutar import y arranque.

## Troubleshooting rapido

- `No such file or directory` en import:
  - Verifica que el `.osm.pbf` exista dentro de `./data/maps/`.
- Import muy lento:
  - Normal para PBF grandes; revisa CPU/RAM y espacio libre.
- Puerto ocupado (`8081`):
  - Cambia el puerto en `docker-compose.maps.yml`.
- No cargan tiles en frontend:
  - Verifica URL de tiles y que `maps` este en estado `Up`.

## Recomendaciones

- Usa backups del volumen `osm-db-data` si es entorno productivo.
- Monitorea uso de disco y memoria.
- Si vas a publicar internet, agrega proxy y TLS (nginx/caddy).
