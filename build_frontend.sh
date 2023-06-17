cp frontend/index.html generated/index.html

npx parcel build frontend/style.scss \
    --log-level 1 \
    --out-dir generated \
    --out-file style.css \
    --no-minify

npx parcel build frontend/app.ts \
    --log-level 1 \
    --out-dir generated \
    --out-file app.js \
    --no-minify
