# COSC310 API

Developer-facing notes for the FastAPI backend. 

To install dependencies on your machine:

  1. Open terminal in project root, run 

```bash
    cd frontend
    npm install
    cd ..
    cd backend
    python -m venv myenv
    myenv\Scripts\activate
    cd ..
    pip install -r requirements.txt
  ```

To launch app:

  1. Open terminal in backend, run

```bash
uvicorn backend.main:app --reload
```

  2. Open a second terminal in backend, run 

```bash
npm run dev
```
Then follow the provided link to the website.


By default the API listens on `http://localhost:8000`. All responses are JSON. The service is stateless and persists to JSON files under `backend/data/`.

## Search
- `GET /search?q=<term>&limit=20&sort_by=title|rating|year&sort_order=asc|desc`
  - Example: `curl "http://localhost:8000/search?q=thor&limit=5"`
  - Response:
    ```json
    {"items":[{"title":"Thor","year":2011}], "total":1}
    ```

## Flags
- `POST /flags`
  - Body: `{"review_id":5,"flagger_id":12,"flagged_user_id":8,"reason":"abusive"}`
  - Response `201 Created`:
    ```json
    {
      "flag_id": 1,
      "review_id": 5,
      "flagger_id": 12,
      "flagged_user_id": 8,
      "reason": "abusive",
      "status": "pending",
      "date_created": "2025-10-27T23:51:13.300022"
    }
    ```
- `GET /flags` (optional `?status=pending|approved|rejected`)
- `GET /flags/pending`
- `PATCH /flags/{flag_id}/status`
  - Body: `{"status": "approved"}` → `404` if not found

## Penalties
- `POST /penalties`
  - Body: `{"user_id":8,"issued_by":99,"reason":"abusive","source_flag_id":55}`
  - Response `201 Created` with `penalty_id`, timestamps, and active state.
- `GET /penalties` (optional `?user_id=<id>` to filter)
- `POST /penalties/{penalty_id}/deactivate`
  - Body: `{"revoked_by": 101}` → `404` if penalty not active

## Users
> JWT-protected routes use the Authorization header: `Authorization: Bearer <token>`.

- `GET /users/` list users.
- `POST /users/register` body `UserCreate` → returns token + user.
- `POST /users/login` form/body `username` + `password` → returns token + user.
- `PUT /users/{user_id}` body `UserUpdate` (admin or self).
- `GET /users/search?username=<term>` returns matches or empty list.
- `GET /users/{user_id}` returns a single user.

## Admin
All require admin JWT (`Authorization: Bearer <token>`).

- `GET /admin/users` list all users.
- `DELETE /admin/users/{user_id}`
- `POST /admin/users/{user_id}/promote`
- `GET /admin/users/{user_id}/reviews`
- `DELETE /admin/users/{user_id}/reviews/delete?movie_id=<id>`
- `GET /admin/users/search?username=&email=&role=`
- Flags (duplicates flag service):
  - `GET /admin/flags`, `GET /admin/flags/pending`
  - `PUT /admin/flags/{flag_id}/status?new_status=approved|rejected|pending`
- Penalties:
  - `GET /admin/users/{user_id}/penalties`
  - `POST /admin/users/{user_id}/penalties?reason=<text>&flag_id=<id?>`
  - `PUT /admin/penalties/{penalty_id}/deactivate`

## Watchlist
`watchlist_router` is present but not mounted in `main.py`. If enabled, it would live under `/watchlist`; check `backend/routers/watchlist_router.py` before use.

## Common responses
- Validation errors: `422 Unprocessable Entity` with Pydantic error details.
- Not found: `404` (e.g., `flag not found`, inactive penalty).
- Unauthorized/Forbidden: `401/403` on JWT-protected routes when missing or lacking admin role.

## Example cURL (issue flag → list pending → approve → issue penalty)
```bash
curl -X POST http://localhost:8000/flags \
  -H "Content-Type: application/json" \
  -d '{"review_id":5,"flagger_id":12,"flagged_user_id":8,"reason":"abusive"}'

curl "http://localhost:8000/flags/pending"

curl -X PATCH http://localhost:8000/flags/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"approved"}'

curl -X POST http://localhost:8000/penalties \
  -H "Content-Type: application/json" \
  -d '{"user_id":8,"issued_by":99,"reason":"abusive","source_flag_id":1}'
```
