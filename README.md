**NEA PROJECT**
> API
>-
>needs to have following features.

1. On start

a) if no activation is already present in the config of the application:
POST to the server with key and hardware id, return success (bool) and a fresh activation token for this 'session'.

b) if an activation already exists in the config file of the application,
submit a GET request with the activation token and it will either return success or failure based on whether or not the application token/session is valid.

if a user wants to delete their activation, you can submit a DELETE request to same endpoint.

should all be under one given endpoint.