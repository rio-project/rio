cp frontend/index.html reflex/generated/index.html

npx parcel build frontend/style.scss \
    --log-level 1 \
    --out-dir reflex/generated \
    --out-file style.css

npx parcel build frontend/app.ts \
    --log-level 1 \
    --out-dir reflex/generated \
    --out-file app.js
