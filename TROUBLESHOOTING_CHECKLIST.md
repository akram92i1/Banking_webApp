# 🔧 Troubleshooting Checklist - Port 8082 Fix

## ✅ **Fixed Issues:**
- Changed frontend API base URL from `localhost:8080` to `localhost:8082`
- Updated test scripts to use correct port

## 🚀 **Steps to Test the Fix:**

### 1. **Start Your Spring Boot Application**
```bash
cd banking-api/demo
./mvnw spring-boot:run
# OR
mvn spring-boot:run
```
**Expected output:** Look for `Tomcat started on port(s): 8082`

### 2. **Verify Spring Boot is Running**
Open browser and go to: `http://localhost:8082`
- You should see some response (even if it's an error page, it means the server is running)

### 3. **Check Database Connection**
Make sure your PostgreSQL database is running on port 5433:
```bash
# Check if PostgreSQL is running
netstat -an | findstr :5433
# OR check docker containers if using Docker
docker ps
```

### 4. **Test API Endpoints Directly**
Try these URLs in your browser (you might get auth errors, but that's expected):
- `http://localhost:8082/api/auth/test`
- `http://localhost:8082/api/bank-transactions/testConnectedUser`

### 5. **Start Your React Frontend**
```bash
cd finance_front_end
npm start
```
**Expected:** Frontend should start on `http://localhost:3000`

### 6. **Test the Fixed Frontend**
1. Login to your app
2. Check browser console for any new errors
3. Look for successful API calls to `localhost:8082`

## 🔍 **Common Issues to Check:**

### Issue: Spring Boot Won't Start
**Possible causes:**
- Database not running
- Port 8082 already in use
- Missing environment variable `JWT_SECRET`

**Solutions:**
- Start PostgreSQL database
- Change port in `application.properties` if needed
- Set JWT_SECRET environment variable

### Issue: Database Connection Failed
**Check:** Your `application.properties` shows:
```properties
spring.datasource.url=jdbc:postgresql://localhost:5433/my_finance_db
spring.datasource.username=bank_database_admin
spring.datasource.password=admin123
```

**Make sure:**
- PostgreSQL is running on port 5433
- Database `my_finance_db` exists
- User `bank_database_admin` exists with password `admin123`

### Issue: JWT_SECRET Missing
**Set environment variable:**
```bash
# Windows
set JWT_SECRET=your-secret-key-here

# Linux/Mac
export JWT_SECRET=your-secret-key-here
```

### Issue: CORS Errors
**If you see CORS errors, add to your Spring Boot configuration:**
```java
@CrossOrigin(origins = "http://localhost:3000")
```

## 🧪 **Quick API Test**
After login, run this in browser console:
```javascript
fetch('http://localhost:8082/api/bank-transactions/testConnectedUser', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(response => response.text())
.then(data => console.log('✅ API Response:', data))
.catch(error => console.log('❌ API Error:', error));
```

## 📝 **Expected Results After Fix:**
- ✅ No more `ERR_CONNECTION_REFUSED` errors
- ✅ Balance Card shows your account balance
- ✅ Transaction table populates with data
- ✅ API calls go to `localhost:8082` instead of `localhost:8080`

## 🆘 **If Still Having Issues:**
1. Check Spring Boot application logs for errors
2. Verify database connection
3. Test API endpoints directly in browser/Postman
4. Check browser network tab for actual request URLs