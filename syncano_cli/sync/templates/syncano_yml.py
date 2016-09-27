
syncano_yml = """
classes:
  book:
    fields:
      author: string
      categories: array
      holder: relation
      pages: integer
      premiere_date: datetime
      title: string
      used: boolean
    group_permissions: create_objects
    other_permissions: create_objects
  user_profile:
    fields: {}
    group_permissions: create_objects
    other_permissions: create_objects
scripts: []
# - label: test
#   runtime: python_library_v5.0
#   script: scripts/test.py
"""
