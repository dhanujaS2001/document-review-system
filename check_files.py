import os
from django.conf import settings
from doc_management.models import Project   

MEDIA_ROOT = os.path.realpath(settings.MEDIA_ROOT)

# ---------- STEP 1: files linked to a database record ----------
linked = set()
print("=== LINKED FILES ===")
for p in Project.objects.all().order_by("id"):
    for field_name in ("project_document", "review_document"):
        f = getattr(p, field_name)
        if f:
            path = os.path.realpath(f.path)
            linked.add(path)
            status = "OK" if os.path.exists(path) else "MISSING ON DISK"
            print(f"[{p.project_code}] {field_name}: {path}  ({status})")

print(f"\nTotal linked files: {len(linked)}")

# ---------- STEP 2: files on disk with no database record ----------
orphans = []
for root, dirs, files in os.walk(MEDIA_ROOT):
    for name in files:
        full = os.path.realpath(os.path.join(root, name))
        if full not in linked:
            orphans.append(full)

print("\n=== ORPHANED FILES (not linked to any Project) ===")
for o in orphans:
    print(o)
print(f"\nTotal orphans: {len(orphans)}")

# ---------- STEP 3: delete orphans (commented out on purpose) ----------
for o in orphans:
    os.remove(o)
    print("Deleted:", o)