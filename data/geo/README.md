# GeoJSON de provincias y municipios

Coloca aqui los GeoJSON que usara el backend para resolver provincia/municipio
con point-in-polygon (Opcion B).

Ejemplo de variables en `.env`:

```
GEOJSON_PROVINCES_PATH=/ruta/absoluta/soscubamap/data/geo/cuba_provinces.geojson
GEOJSON_MUNICIPALITIES_PATH=/ruta/absoluta/soscubamap/data/geo/cuba_municipios.geojson
```

Si tus propiedades tienen claves distintas, define las listas con comas:

```
GEOJSON_PROVINCE_KEYS=NAME_1,ADM1_ES,provincia
GEOJSON_MUNICIPALITY_KEYS=NAME_2,ADM2_ES,municipio
GEOJSON_MUNICIPALITY_PROVINCE_KEYS=NAME_1,ADM1_ES,provincia
```

Notas:
- El backend usa los nombres canonicos definidos en `app/services/cuba_locations.py`.
- Si no hay GeoJSON configurado, se usan las listas estaticas como fallback.
