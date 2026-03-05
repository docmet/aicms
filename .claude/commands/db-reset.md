# Reset Database

Wipe and reseed the development database.

**Warning: This destroys all data.** Only use in development.

Steps:
1. Ask the user to confirm: "This will destroy all database data and reseed with test data. Confirm? (yes/no)"
2. If confirmed, run: `./cli.sh db:reset`
3. Verify seed worked by checking:
   - `curl -s -X POST http://localhost/api/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=client@docmet.com&password=password123" | jq .`
4. Report: migration ran, seed data loaded, test login works

Test credentials after reset:
- Admin: norbi@docmet.com / password123
- Client: client@docmet.com / password123
