# Part 7: Understanding Flask Mechanisms

1. **How is the logged in user being kept track of?**
   - Flask's session mechanism is used to track the logged-in user. Upon successful login, the user's ID is stored in the session under the key `CURR_USER_KEY`.

2. **What is Flask’s `g` object?**
   - Flask's `g` object is a global namespace for holding any data you want during a single app context. It is unique to each request, meaning it resets with each request.

3. **What is the purpose of `add_user_to_g`?**
   - The purpose of the `add_user_to_g` function is to ensure that the currently logged-in user, if any, is loaded and made accessible to the application during the request's lifecycle. It is designed to run before each request is processed.

4. **What does `@app.before_request` mean?**
   - The `@app.before_request` decorator in Flask is used to register a function that runs before each request to the application, regardless of which route is being requested. It's a tool for performing operations that are common to all requests.
