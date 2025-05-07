from config import settings

origins = [
  settings.FRONTEND_URL
]

methods = [
  "GET",
  "POST",
  "PUT",
  "DELETE",
  "PATCH"
]

headers = [
  "Authorization",
  "Content-Type",
  "X-Requested-With",
]