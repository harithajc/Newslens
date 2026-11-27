# NewsLens API contract

## Stories

`GET /api/stories` returns story objects with the existing story fields plus:

- `comic_available` (boolean): true only when the cleaned summary contains at least 40 characters and is not the title after ignoring case, spaces, and punctuation.
- `sensitive` (boolean): true for serious, political, or religious stories.

The frontend must hide **See as comic** when `comic_available` is false or `sensitive` is true.

## Comics

Existing comic routes and response fields remain available. The v2 comic responses include the additional `sensitive` boolean.