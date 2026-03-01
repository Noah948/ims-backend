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
3. while making sale contact must be of 10 digits
4. pagination is yet to be implemented: use this payload
   {
   "data": [
   {1},{2},{3},{4},{5},{6},{7},{8},{9},{10}
   ],
   "meta": {
   "page": 1,
   "limit": 10,
   "total": 150,
   "total_pages": 15,
   "has_next": true,
   "has_prev": false
   }
   }
