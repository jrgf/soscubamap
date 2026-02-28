from app import create_app
from app.extensions import db
from app.models.post import Post
from app.services.geo_lookup import lookup_location


def main():
    app = create_app()
    with app.app_context():
        updated = 0
        for post in Post.query.all():
            if post.latitude is None or post.longitude is None:
                continue
            try:
                province, municipality = lookup_location(post.latitude, post.longitude)
            except Exception:
                continue

            changed = False
            if province and not post.province:
                post.province = province
                changed = True
            if municipality and not post.municipality:
                post.municipality = municipality
                changed = True

            if changed:
                updated += 1

        if updated:
            db.session.commit()
        print(f"Posts actualizados: {updated}")


if __name__ == "__main__":
    main()
