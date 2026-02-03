# TODO
- use modal and schema of user to create basic service and route
- then give all auth related code and tell to generate middleware
- use this middleware for user. check that different usser are unable to login with same credentials

---

- now we have to make every model and integerate it into user model
- our task is to make a new user. for this we need to see all tables in supabase and for that we need to setup alembic.

Here’s the correct progression for your project:

1️⃣ Users (auth, profile, subscription, stats)
2️⃣ Categories
3️⃣ Category Fields
4️⃣ Products
5️⃣ Sales (affects product stock)
6️⃣ Jobs (mostly independent)
7️⃣ Teams
8️⃣ Payments (subscription logic)