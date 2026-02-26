1. in user -
   remove business type,
   ask for user_name not just name,
   remove notification if not going to use it,
   remove last active at,
   contact must be of 10 digits,
   ask for image as dropbox leter in user interface not at time of creation
   check if user with same email or contact already exists
2. in job -
   contact must be of 10 digits,
   email should be unique, we can create a metadata file that will have all emails for easy lookup in entire DB
3. pagination is yet to be implemented: use this payload
   {
   "data": [
   {
   "id": "uuid",
   "name": "MacBook Pro",
   "price": 120000,
   "stock": 5,
   "minimum_stock": 3,
   "category_id": "uuid",
   "deleted_at": null,
   "created_at": "2026-02-25T12:00:00Z"
   }
   ],
   "meta": {
   "page": 1,
   "limit": 20,
   "total": 154,
   "total_pages": 8,
   "has_next": true,
   "has_prev": false
   }
   }
