
cp frontend/index.html reflex/generated/index.html

npx parcel build \
    frontend/app.ts \
    frontend/style.scss \
    --log-level info \
    --dist-dir reflex/generated \
    --no-scope-hoist  # needed to avoid parcel bug
