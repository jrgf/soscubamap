import argparse

from app import create_app
from app.extensions import db
from app.models.post import Post
from app.services.geo_lookup import lookup_location


def main():
    parser = argparse.ArgumentParser(
        description="Actualiza provincia/municipio usando reverse geocode por lat/lng."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribe provincia/municipio existentes.",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        updated = 0
        for post in Post.query.all():
            if post.latitude is None or post.longitude is None:
                continue
            if not args.force and post.province and post.municipality:
                continue

            try:
                province, municipality = lookup_location(post.latitude, post.longitude)
            except Exception:
                continue

            changed = False
            if province and (args.force or not post.province):
                post.province = province
                changed = True
            if municipality and (args.force or not post.municipality):
                post.municipality = municipality
                changed = True

            if changed:
                updated += 1

        if updated:
            db.session.commit()
        print(f"Posts actualizados: {updated}")


if __name__ == "__main__":
    main()
