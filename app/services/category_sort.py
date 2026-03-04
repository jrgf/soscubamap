def sort_categories_for_forms(categories):
    priority = {"accion-represiva": 0, "movimiento-tropas": 1}
    return sorted(categories, key=lambda c: (priority.get(c.slug, 99), c.name))
